"""Central registry and tracking utilities for LLM usage."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Dict, Optional, Tuple

from langchain_openai import ChatOpenAI

from utils.config_loader import get_openrouter_api_key

try:
    import tiktoken  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    tiktoken = None

_OPENROUTER_BASE = "https://openrouter.ai/api/v1"
_TOKEN_ENCODERS: Dict[str, Any] = {}
_SAFETY_BUFFER_TOKENS = 512


@dataclass(frozen=True)
class LLMConfig:
    """Configuration metadata for an LLM."""

    name: str
    model: str
    temperature: float
    max_input_tokens: int
    max_output_tokens: int
    prompt_cost_per_1k: float
    completion_cost_per_1k: float
    default_kwargs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMCallMetrics:
    """Metrics captured for each LLM invocation."""

    name: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost: float
    duration: float
    truncated: bool

    def as_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "model": self.model,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "cost": self.cost,
            "duration": self.duration,
            "truncated": self.truncated,
        }


_LLM_CONFIGS: Dict[str, LLMConfig] = {
    "finance_intent_checker": LLMConfig(
        name="finance_intent_checker",
        model="gpt-4o-mini",
        temperature=0.0,
        max_input_tokens=128_000,
        max_output_tokens=4_096,
        prompt_cost_per_1k=0.00015,
        completion_cost_per_1k=0.0006,
    ),
    "research_assistant": LLMConfig(
        name="research_assistant",
        model="gpt-4o",
        temperature=0.0,
        max_input_tokens=128_000,
        max_output_tokens=4_096,
        prompt_cost_per_1k=0.005,
        completion_cost_per_1k=0.015,
    ),
    "synthesiser": LLMConfig(
        name="synthesiser",
        model="gpt-4o",
        temperature=0.2,
        max_input_tokens=128_000,
        max_output_tokens=8_192,
        prompt_cost_per_1k=0.005,
        completion_cost_per_1k=0.015,
    ),

    "youtube_summarizer": LLMConfig(
        name="youtube_summarizer",
        model="gpt-4o-mini",
        temperature=0.2,
        max_input_tokens=64000,
        max_output_tokens=2048,
        prompt_cost_per_1k=0.00015,
        completion_cost_per_1k=0.0006,
    ),    "gemini_flash": LLMConfig(
        name="gemini_flash",
        model="google/gemini-flash-1.5",
        temperature=0.2,
        max_input_tokens=1_000_000,
        max_output_tokens=8_192,
        prompt_cost_per_1k=0.00035,
        completion_cost_per_1k=0.0007,
    ),
    "gemini_pro": LLMConfig(
        name="gemini_pro",
        model="google/gemini-pro-1.5",
        temperature=0.2,
        max_input_tokens=2_000_000,
        max_output_tokens=8_192,
        prompt_cost_per_1k=0.007,
        completion_cost_per_1k=0.021,
    ),
    "deep_research": LLMConfig(
        name="deep_research",
        model="o1-mini",
        temperature=0.0,
        max_input_tokens=128_000,
        max_output_tokens=8_192,
        prompt_cost_per_1k=0.003,
        completion_cost_per_1k=0.009,
        default_kwargs={"reasoning": {"effort": "medium"}},
    ),
}


def get_llm_config(name: str) -> LLMConfig:
    """Return the registered configuration for *name* or raise if unknown."""
    if name not in _LLM_CONFIGS:
        raise KeyError(f"Unknown LLM config '{name}'")
    return _LLM_CONFIGS[name]


@lru_cache(maxsize=None)
def _build_client(model: str, temperature: float) -> ChatOpenAI:
    """Construct and cache a chat client for the given OpenRouter model."""
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        openai_api_key=get_openrouter_api_key(),
        openai_api_base=_OPENROUTER_BASE,
    )


def get_llm(name: str, **overrides: Any) -> ChatOpenAI:
    """Return a cached ChatOpenAI instance for compatibility."""
    config = get_llm_config(name)
    temperature = overrides.get("temperature", config.temperature)
    return _build_client(config.model, temperature)


def _get_encoder(model: str):
    """Return a tokenizer encoding for *model*, caching the lookup."""
    if tiktoken is None:
        return None
    if model in _TOKEN_ENCODERS:
        return _TOKEN_ENCODERS[model]
    try:
        encoder = tiktoken.encoding_for_model(model)
    except KeyError:
        encoder = tiktoken.get_encoding("cl100k_base")
    _TOKEN_ENCODERS[model] = encoder
    return encoder


def _count_tokens(text: str, model: str) -> int:
    """Estimate token usage for *text* under the supplied *model*."""
    encoder = _get_encoder(model)
    if encoder is None:
        return max(1, len(text) // 4)
    return len(encoder.encode(text))


def _truncate_to_limit(text: str, config: LLMConfig, limit_tokens: int) -> Tuple[str, bool, int]:
    """Trim *text* to fit within *limit_tokens*, returning (text, truncated?, count)."""
    encoder = _get_encoder(config.model)
    if encoder is None:
        approx_tokens = max(1, len(text) // 4)
        if approx_tokens <= limit_tokens:
            return text, False, approx_tokens
        max_chars = max(4, limit_tokens * 4)
        truncated = text[-max_chars:]
        return truncated, True, max(1, len(truncated) // 4)

    tokens = encoder.encode(text)
    if len(tokens) <= limit_tokens:
        return text, False, len(tokens)
    truncated_tokens = tokens[-limit_tokens:]
    truncated_text = encoder.decode(truncated_tokens)
    return truncated_text, True, len(truncated_tokens)


def invoke_llm(
    name: str,
    prompt: str,
    *,
    temperature: Optional[float] = None,
    max_output_tokens: Optional[int] = None,
    **call_kwargs: Any,
):
    """Invoke an LLM by configuration name while tracking metrics and enforcing limits."""
    config = get_llm_config(name)
    temperature = temperature if temperature is not None else config.temperature
    llm = _build_client(config.model, temperature)

    desired_output = max(16, min(max_output_tokens or config.max_output_tokens, config.max_output_tokens))
    prompt_limit = max(16, config.max_input_tokens - desired_output - _SAFETY_BUFFER_TOKENS)
    truncated_prompt, truncated, prompt_tokens_est = _truncate_to_limit(prompt, config, prompt_limit)

    prompt_tokens_actual = _count_tokens(truncated_prompt, config.model)
    available_for_completion = max(
        16,
        min(
            desired_output,
            config.max_input_tokens - prompt_tokens_actual - _SAFETY_BUFFER_TOKENS,
            config.max_output_tokens,
        ),
    )

    call_params = {
        **config.default_kwargs,
        **call_kwargs,
        "max_tokens": available_for_completion,
    }

    start = time.perf_counter()
    response = llm.invoke(truncated_prompt, **call_params)
    duration = time.perf_counter() - start

    metadata: Dict[str, Any] = getattr(response, "response_metadata", {}) or {}
    token_usage = metadata.get("token_usage", {})

    prompt_tokens = int(token_usage.get("prompt_tokens", prompt_tokens_actual))
    completion_tokens = int(
        token_usage.get("completion_tokens", token_usage.get("generation_tokens", 0))
    )
    total_tokens = int(token_usage.get("total_tokens", prompt_tokens + completion_tokens))

    cost = (
        (prompt_tokens / 1000) * config.prompt_cost_per_1k
        + (completion_tokens / 1000) * config.completion_cost_per_1k
    )

    metrics = LLMCallMetrics(
        name=name,
        model=config.model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        cost=cost,
        duration=duration,
        truncated=truncated or prompt_tokens_actual != prompt_tokens_est,
    )

    return response, metrics


def zero_metrics(name: str) -> LLMCallMetrics:
    """Return an empty metrics object for *name* when no call was made."""
    config = get_llm_config(name)
    return LLMCallMetrics(
        name=name,
        model=config.model,
        prompt_tokens=0,
        completion_tokens=0,
        total_tokens=0,
        cost=0.0,
        duration=0.0,
        truncated=False,
    )

