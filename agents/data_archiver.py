"""Agent that archives the research state to disk."""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict

from graph.state import ResearchState

_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "json"


def _slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value)
    return value.strip("_") or "untitled"


def archive_state(state: ResearchState) -> Dict[str, str]:
    """Write the current research state to a JSON file and return its path."""
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    topic = state.get("topic", "research") or "research"
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"{timestamp}_{_slugify(topic)}.json"
    filepath = _DATA_DIR / filename

    with filepath.open("w", encoding="utf-8") as handle:
        json.dump(state, handle, ensure_ascii=False, indent=2, default=str)

    return {"archive_path": str(filepath.relative_to(Path(__file__).resolve().parents[2]))}
