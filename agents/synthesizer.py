"""LLM-backed synthesizer agent that composes the final report."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from src.graph.state import ResearchState
from src.utils.llm_registry import invoke_llm, zero_metrics


MAX_PROMPT_CHARS_EXTENDED = 65000
MAX_PROMPT_CHARS_SIMPLE = 20000

class _SafeFormatDict(dict):
    """Dictionary that leaves unknown placeholders untouched during formatting."""

    def __missing__(self, key: str) -> str:
        return '{' + key + '}'


def _truncate_agent_outputs(text: str, max_chars: int) -> tuple[str, bool]:
    if len(text) <= max_chars:
        return text, False
    slice_len = max_chars // 2
    truncated = text[:slice_len] + "\n\n... [truncated for length] ...\n\n" + text[-slice_len:]
    return truncated, True


def load_synthesizer_prompt(mode: str = 'extended', prompt_path: Optional[str] = None) -> str:
    """Return the report-writing prompt tailored to *mode*, allowing domain overrides."""
    candidate_paths = []
    if prompt_path:
        candidate_paths.append(Path(prompt_path))
    base_dir = Path(__file__).resolve().parent
    fallback = base_dir / ('../prompts/synthesizer_prompt_simple.txt' if mode == 'simple' else '../prompts/synthesizer_prompt.txt')
    candidate_paths.append(fallback.resolve())

    for candidate in candidate_paths:
        try:
            if candidate and candidate.exists():
                return candidate.read_text(encoding='utf-8')
        except (TypeError, ValueError):
            continue

    tried = [str(candidate) for candidate in candidate_paths if candidate]
    raise FileNotFoundError(f'Synthesizer prompt template not found. Tried: {tried}.')


def _serialize_for_prompt(value: object) -> str:
    """Convert nested agent output into a JSON string suitable for prompting."""
    try:
        return json.dumps(value, ensure_ascii=False, indent=2)
    except TypeError:
        return str(value)


def gather_agent_outputs(state: ResearchState) -> str:
    """Collect agent outputs from *state* in a markdown-friendly format."""
    sections = []
    for key, label in [
        ("research_plan", "Research Plan"),
        ("web_results", "Web Results"),
        ("academic_results", "Academic Results"),
        ("news_results", "News Results"),
        ("social_sentiment", "Social Sentiment"),
        ("financial_data", "Financial Data"),
        ("vector_store_result", "Vector Store"),
        ("rag_result", "RAG Context"),
    ]:
        value = state.get(key)
        if value:
            text = _serialize_for_prompt(value)
            sections.append(f"## {label}\n{text}")
    return "\n\n".join(sections)


def generate_final_report(state: ResearchState, mode: str = 'extended') -> dict:
    """Call the synthesiser LLM to produce the final report for *state*."""
    prompt_template = load_synthesizer_prompt(mode, state.get('synthesizer_prompt_path'))
    topic = state.get('topic', '')
    agent_outputs = gather_agent_outputs(state)
    max_chars = MAX_PROMPT_CHARS_SIMPLE if mode == 'simple' else MAX_PROMPT_CHARS_EXTENDED
    agent_outputs, prompt_truncated = _truncate_agent_outputs(agent_outputs, max_chars)
    context = _SafeFormatDict(topic=topic, query=topic, agent_outputs=agent_outputs)
    formatted_prompt = prompt_template.format_map(context)
    if '{agent_outputs' in prompt_template:
        prompt = formatted_prompt
    else:
        prompt = (
            f"{formatted_prompt}\n\n---\n"
            "Use only the research materials provided below. "
            "Synthesize the findings and do not perform new external research.\n\n"
            f"Provided Research Materials:\n{agent_outputs}"
        )

    temperature = 0.0 if mode == 'simple' else 0.2
    try:
        response, metrics = invoke_llm("synthesiser", prompt, temperature=temperature)
        report = response.content.strip()
    except Exception as exc:
        metrics = zero_metrics("synthesiser")
        result_payload = {
            "sources": [
                {
                    "name": "synthesizer",
                    "items": [],
                    "metadata": {"note": "Final report generation failed"},
                }
            ],
            "elapsed": metrics.duration,
            "tokens": metrics.total_tokens,
            "cost": metrics.cost,
            "details": {
                "model": metrics.model,
                "prompt_tokens": metrics.prompt_tokens,
                "completion_tokens": metrics.completion_tokens,
                "truncated": metrics.truncated,
                "prompt_chars": len(agent_outputs),
                "prompt_truncated": prompt_truncated,
                "error": str(exc),
            },
        }
        return {"synthesizer_result": result_payload}

    metadata_note = "See final report text"
    if prompt_truncated:
        metadata_note = "Prompt truncated to fit context window"

    result_payload = {
        "sources": [
            {
                "name": "synthesizer",
                "items": [],
                "metadata": {"note": metadata_note},
            }
        ],
        "elapsed": metrics.duration,
        "tokens": metrics.total_tokens,
        "cost": metrics.cost,
        "details": {
            "model": metrics.model,
            "prompt_tokens": metrics.prompt_tokens,
            "completion_tokens": metrics.completion_tokens,
            "truncated": metrics.truncated,
            "prompt_chars": len(agent_outputs),
            "prompt_truncated": prompt_truncated,
        },
    }

    return {"final_report": report, "synthesizer_result": result_payload}