"""Cloudflare environment-binding access helper."""
from __future__ import annotations

def binding(env, name):
    try:
        return getattr(env, name)
    except Exception:
        return None
