"""Langfuse tracing setup for v4.

Import `observe` and `get_langfuse` from here so .env is always
loaded before the Langfuse client initializes.
"""

from __future__ import annotations

from dotenv import load_dotenv
from langfuse import get_client, observe

load_dotenv()


def get_langfuse():
    """Return the initialized Langfuse client."""
    return get_client()


__all__ = ["observe", "get_langfuse"]
