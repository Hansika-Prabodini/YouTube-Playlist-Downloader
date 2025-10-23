"""Secret management utilities.

This module centralizes secure loading of the OPENAI_API_KEY and provides
helpers to safely mask and log messages that may contain secrets.

- get_openai_api_key: Fetch OPENAI_API_KEY from environment with dotenv fallback
- mask_secret: Mask a secret value, revealing only the last N characters
- safe_log: Log sanitized messages (never logs raw secrets)
"""
from __future__ import annotations

import logging
import os
from typing import Optional

try:
    # Lazy import; if not available, we handle absence gracefully until needed
    from dotenv import load_dotenv  # type: ignore
except Exception:  # pragma: no cover - optional dependency import guard
    load_dotenv = None  # type: ignore


def mask_secret(secret: str, show: int = 4, mask_char: str = "*") -> str:
    """Return a masked representation of a secret.

    Rules:
    - If length > show, return mask characters for all but the last `show` characters.
    - If length <= show, return mask_char repeated for the length of the secret.
    - The resulting length equals the original length when len(secret) > show.

    Examples:
        mask_secret("sk-12345678") -> "*****5678"

    Args:
        secret: The secret string to mask.
        show: Number of trailing characters to reveal (default 4).
        mask_char: The character to use for masking (default '*').

    Returns:
        Masked string per rules above.
    """
    if secret is None:
        return ""
    n = len(secret)
    if n <= 0:
        return ""
    if n <= show:
        return mask_char * n
    return (mask_char * (n - show)) + secret[-show:]


def get_openai_api_key(required: bool = True) -> Optional[str]:
    """Retrieve the OPENAI_API_KEY from environment with dotenv fallback.

    Behavior:
    1) Check os.environ["OPENAI_API_KEY"] first.
    2) If not set, load from .env via python-dotenv (load_dotenv with default behavior), then re-check.
    3) Return the key if found; if not found and required=True, raise EnvironmentError
       with a non-sensitive message; if required=False, return None.

    This function never prints or logs the raw key.

    Args:
        required: Whether to raise if key is missing (default True).

    Returns:
        The API key string or None if not required and missing.
    """
    key = os.environ.get("OPENAI_API_KEY")
    if not key and load_dotenv is not None:
        # Default behavior: search .env in current and parent dirs without overriding existing env vars
        try:
            load_dotenv()  # type: ignore[misc]
        except Exception:
            # Do not log secrets and do not fail loading here; proceed to re-check env
            pass
        key = os.environ.get("OPENAI_API_KEY")

    if not key:
        if required:
            raise EnvironmentError(
                "OPENAI_API_KEY is not set. Please set it in environment or .env file."
            )
        return None

    # Never log or print the raw key here.
    return key


def safe_log(message: str, logger: logging.Logger, level: int = logging.INFO) -> None:
    """Log sanitized messages safely.

    This function assumes the provided message has already been sanitized (e.g.,
    secrets masked using mask_secret). It will not attempt to inspect or alter
    the message content and will never log raw secrets by itself.

    Args:
        message: The already-sanitized message to log.
        logger: The logger to use.
        level: Logging level (default logging.INFO).
    """
    if not isinstance(logger, logging.Logger):
        raise TypeError("logger must be an instance of logging.Logger")
    logger.log(level, message)
