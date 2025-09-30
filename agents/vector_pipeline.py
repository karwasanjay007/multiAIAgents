"""Vector store indexing and retrieval agents using LanceDB with chunking and metadata."""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd
import pyarrow as pa

try:
    import lancedb
except ImportError:  # pragma: no cover - optional dependency
    lancedb = None

try:
    import tiktoken
except ImportError:  # pragma: no cover - optional dependency
    tiktoken = None

from sentence_transformers import SentenceTransformer

from graph.state import ResearchState

_DB_DIR = Path(__file__).resolve().parents[2] / "data" / "vector_store"
_TABLE_NAME = "research_chunks"
_EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_CHUNK_SIZE_TOKENS = 350
_CHUNK_OVERLAP_TOKENS = 70
_RETRIEVAL_TOP_K = 12
_embedder: SentenceTransformer | None = None
_db: Any = None
_encoder = None


def initialize_vector_store() -> None:
    """Ensure the LanceDB database and table exist exactly once."""
    global _db
    if lancedb is None:
        return
    if not _DB_DIR.exists():
        _DB_DIR.mkdir(parents=True, exist_ok=True)
    if _db is None:
        _db = lancedb.connect(str(_DB_DIR))
    if _TABLE_NAME not in _db.table_names():
        schema = pa.schema([
            pa.field("id", pa.string()),
            pa.field("text", pa.string()),
            pa.field("source", pa.string()),
            pa.field("agent", pa.string()),
            pa.field("metadata", pa.string()),
            pa.field("chunk_index", pa.int32()),
            pa.field("embedding", lancedb.vector(384)),
        ])
        _db.create_table(_TABLE_NAME, data=[], schema=schema)


def _get_embedder() -> SentenceTransformer:
    """Return a cached sentence-transformer instance for embedding text chunks."""
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(_EMBED_MODEL_NAME)
    return _embedder


def _get_encoder():
    """Resolve the token encoder used for chunk sizing (tiktoken fallback)."""
    global _encoder
    if _encoder is None:
        if tiktoken is None:
            _encoder = "char"
        else:
            _encoder = tiktoken.get_encoding("cl100k_base")
    return _encoder


def _encode_tokens(text: str) -> List[int]:
    """Encode *text* into integer tokens using the configured encoder."""
    encoder = _get_encoder()
    if encoder == "char":
        return list(text.encode("utf-8"))
    return encoder.encode(text)


def _decode_tokens(tokens: List[int]) -> str:
    """Decode integer *tokens* back into a string."""
    encoder = _get_encoder()
    if encoder == "char":
        return bytes(tokens).decode("utf-8", errors="ignore")
    return encoder.decode(tokens)


def _open_table():
    """Initialise LanceDB (if needed) and return the working table."""
    initialize_vector_store()
    if lancedb is None or _db is None:
        return None
    return _db.open_table(_TABLE_NAME)


def _chunk_text(text: str) -> List[str]:
    """Split long text into overlapping chunks sized for embedding."""
    tokens = _encode_tokens(text)
    if len(tokens) <= _CHUNK_SIZE_TOKENS:
        return [text]
    chunks: List[str] = []
    start = 0
    while start < len(tokens):
        end = start + _CHUNK_SIZE_TOKENS
        chunk_tokens = tokens[start:end]
        chunks.append(_decode_tokens(chunk_tokens))
        if end >= len(tokens):
            break
        start = max(0, end - _CHUNK_OVERLAP_TOKENS)
    return chunks


def _collect_text_chunks(state: ResearchState) -> List[Dict[str, Any]]:
    """Extract chunkable text segments from relevant agent outputs in *state*."""
    collected: List[Dict[str, Any]] = []
    agent_keys = [
        "web_results",
        "academic_results",
        "news_results",
        "social_sentiment",
        "financial_data",
        "perplexity_results",
        "youtube_results",
    ]
    for key in agent_keys:
        result = state.get(key)
        if isinstance(result, dict):
            for source in result.get("sources", []):
                source_name = source.get("name", "source")
                metadata = json.dumps(source.get("metadata", {}), ensure_ascii=False)
                items = source.get("items", [])
                for idx, item in enumerate(items):
                    if isinstance(item, str):
                        text = item
                    else:
                        text = json.dumps(item, ensure_ascii=False)
                    text = text.strip()
                    if not text:
                        continue
                    for chunk_index, chunk_text in enumerate(_chunk_text(text)):
                        collected.append(
                            {
                                "agent": key,
                                "source": source_name,
                                "metadata": metadata,
                                "original_index": idx,
                                "chunk_index": chunk_index,
                                "text": chunk_text,
                                "token_count": len(_encode_tokens(chunk_text)),
                            }
                        )
    final_report = state.get("final_report")
    if isinstance(final_report, str) and final_report.strip():
        for chunk_index, chunk_text in enumerate(_chunk_text(final_report.strip())):
            collected.append(
                {
                    "agent": "final_report",
                    "source": "final_report",
                    "metadata": "{}",
                    "original_index": 0,
                    "chunk_index": chunk_index,
                    "text": chunk_text,
                    "token_count": len(_encode_tokens(chunk_text)),
                }
            )
    return collected


def _record_id(chunk: Dict[str, Any]) -> str:
    """Generate a deterministic identifier for a chunk to support upserts."""
    base = f"{chunk['agent']}::{chunk['source']}::{chunk['original_index']}::{chunk['chunk_index']}::{chunk['text']}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def _upsert_records(table, records: List[Dict[str, Any]]) -> Tuple[int, int]:
    """Upsert *records* into LanceDB, returning (upserted, deduped) counts."""
    if not records:
        return 0, 0
    upserted = 0
    deduped = 0
    for record in records:
        table.delete(f"id == '{record['id']}'")
        table.add(pd.DataFrame([record]))
        upserted += 1
        deduped += 1
    return upserted, deduped


def store_in_vector_db(state: ResearchState) -> Dict[str, Dict[str, Any]]:
    """Index agent outputs in LanceDB so they can be retrieved later."""
    start = time.time()
    if lancedb is None:
        elapsed = time.time() - start
        return {
            "vector_store_result": {
                "sources": [],
                "elapsed": elapsed,
                "tokens": 0,
                "cost": 0.0,
                "details": {"error": "lancedb package not installed"},
            }
        }

    table = _open_table()
    if table is None:
        elapsed = time.time() - start
        return {
            "vector_store_result": {
                "sources": [],
                "elapsed": elapsed,
                "tokens": 0,
                "cost": 0.0,
                "details": {"error": "Vector store unavailable"},
            }
        }

    chunks = _collect_text_chunks(state)
    if not chunks:
        elapsed = time.time() - start
        return {
            "vector_store_result": {
                "sources": [],
                "elapsed": elapsed,
                "tokens": 0,
                "cost": 0.0,
                "details": {"note": "No data available for indexing"},
            }
        }

    embedder = _get_embedder()
    embeddings = embedder.encode([c["text"] for c in chunks], normalize_embeddings=True)

    records: List[Dict[str, Any]] = []
    for chunk, embedding in zip(chunks, embeddings, strict=True):
        records.append({
            "id": _record_id(chunk),
            "text": chunk["text"],
            "source": chunk["source"],
            "agent": chunk["agent"],
            "metadata": chunk["metadata"],
            "chunk_index": chunk["chunk_index"],
            "embedding": embedding.tolist(),
        })

    df = pd.DataFrame(records).drop_duplicates(subset="id")
    total_tokens = sum(chunk["token_count"] for chunk in chunks)

    if not df.empty:
        table.delete("true")
        table.add(df)

    elapsed = time.time() - start
    return {
        "vector_store_result": {
            "sources": [
                {
                    "name": "vector_store",
                    "items": [f"Indexed {len(df)} chunks"],
                    "metadata": {
                        "db_path": str(_DB_DIR),
                        "table": _TABLE_NAME,
                        "agents": sorted({chunk["agent"] for chunk in chunks}),
                    },
                }
            ],
            "elapsed": elapsed,
            "tokens": total_tokens,
            "cost": 0.0,
            "details": {
                "mode": state.get("mode"),
                "chunk_count": int(len(df)),
            },
        }
    }


def retrieve_from_vector_db(state: ResearchState) -> Dict[str, Dict[str, Any]]:
    """Perform semantic search over the vector store for the current topic."""
    start = time.time()
    if lancedb is None:
        elapsed = time.time() - start
        return {
            "rag_result": {
                "sources": [],
                "elapsed": elapsed,
                "tokens": 0,
                "cost": 0.0,
                "details": {"error": "lancedb package not installed"},
            }
        }

    table = _open_table()
    if table is None:
        elapsed = time.time() - start
        return {
            "rag_result": {
                "sources": [],
                "elapsed": elapsed,
                "tokens": 0,
                "cost": 0.0,
                "details": {"error": "Vector store unavailable"},
            }
        }

    query = state.get("topic", "")
    if not query:
        elapsed = time.time() - start
        return {
            "rag_result": {
                "sources": [],
                "elapsed": elapsed,
                "tokens": 0,
                "cost": 0.0,
                "details": {"error": "Empty topic for retrieval"},
            }
        }

    embedder = _get_embedder()
    query_tokens = len(_encode_tokens(query))
    query_vec = embedder.encode([query], normalize_embeddings=True)[0]
    results = (
        table.search(query_vec)
        .select(['text', 'source', 'agent', 'metadata'])
        .limit(_RETRIEVAL_TOP_K)
        .to_pandas()
    )

    items = []
    for _, row in results.iterrows():
        info = json.loads(row.get('metadata', '{}') or '{}')
        info['source'] = row.get('source')
        info['agent'] = row.get('agent')
        items.append({
            'text': row.get('text'),
            'metadata': info,
        })

    elapsed = time.time() - start
    return {
        "rag_result": {
            "sources": [
                {
                    "name": "semantic_search",
                    "items": items,
                    "metadata": {
                        "db_path": str(_DB_DIR),
                        "table": _TABLE_NAME,
                        "result_count": len(items),
                        "requested_top_k": _RETRIEVAL_TOP_K,
                    },
                }
            ],
            "elapsed": elapsed,
            "tokens": query_tokens,
            "cost": 0.0,
            "details": {"query": query},
        }
    }


initialize_vector_store()
