"""Shared Gemini call helper: retries transient errors and falls back across models.

Free-tier quotas are enforced per model, so when one model returns 429/503 the
next model in the chain is tried. Override the chain with GEMINI_MODELS
(comma-separated, in priority order).
"""

import os
import time

DEFAULT_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.7-flash",
    "gemini-3.5-flash",
    "gemini-2.5-flash",
    "gemini-3.8-flash",
]

_RETRYABLE = ("503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "TIMEOUT", "TIMED OUT", "DEADLINE", "404", "NOT_FOUND")


def model_chain() -> list:
    env = os.getenv("GEMINI_MODELS", "")
    models = [m.strip() for m in env.split(",") if m.strip()]
    return models or DEFAULT_MODELS


def generate_with_fallback(client, contents, config=None):
    """Call generate_content, moving to the next model on transient/quota errors."""
    last_error = None

    for model in model_chain():
        for attempt in range(2):
            try:
                kwargs = {"model": model, "contents": contents}
                if config is not None:
                    kwargs["config"] = config
                response = client.models.generate_content(**kwargs)
                print(f"[Gemini] answered by {model}")
                return response
            except Exception as exc:
                last_error = exc
                text = str(exc).upper()
                if not any(code in text for code in _RETRYABLE):
                    raise
                # Quota/not-found won't recover by retrying the same model.
                if "429" in text or "RESOURCE_EXHAUSTED" in text or "404" in text:
                    break
                time.sleep(1.5 * (attempt + 1))

    raise RuntimeError(f"All Gemini models failed: {last_error}")
