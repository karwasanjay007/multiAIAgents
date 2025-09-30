"""Cleanup agent to clear archived JSON files and vector store."""
from __future__ import annotations

import shutil
import time
from pathlib import Path
from typing import Dict, List

from src.agent.vector_pipeline import initialize_vector_store, _DB_DIR
from src.graph.state import ResearchState

_ARCHIVE_DIR = Path(__file__).resolve().parents[2] / "data" / "json"


def cleanup_archives(state: ResearchState) -> Dict[str, Dict]:
    """Remove JSON files and reset vector store from previous run."""
    start = time.time()
    removed: List[str] = []
    errors: List[str] = []

    if _ARCHIVE_DIR.exists():
        for file_path in _ARCHIVE_DIR.glob("*.json"):
            try:
                file_path.unlink()
                removed.append(file_path.name)
            except Exception as exc:  # pragma: no cover - filesystem failures
                errors.append(f"{file_path.name}: {exc}")

    vector_removed = False
    if _DB_DIR.exists():
        try:
            shutil.rmtree(_DB_DIR)
            vector_removed = True
        except Exception as exc:  # pragma: no cover - filesystem failures
            errors.append(f"Vector store: {exc}")

    if vector_removed:
        initialize_vector_store()

    elapsed = time.time() - start
    metadata = {
        "directory": str(_ARCHIVE_DIR),
        "removed_count": len(removed),
        "vector_store_cleared": vector_removed,
    }
    if errors:
        metadata["errors"] = errors

    payload = {
        "cleanup_result": {
            "sources": [
                {
                    "name": "cleanup",
                    "items": removed,
                    "metadata": metadata,
                }
            ],
            "elapsed": elapsed,
            "tokens": 0,
            "cost": 0.0,
            "details": {
                "note": "Removed archives and reset vector store before new run",
            },
        }
    }

    return payload