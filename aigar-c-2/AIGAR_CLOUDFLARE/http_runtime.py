"""HTTP response, CORS and request-body helpers for the Cloudflare Worker."""
from __future__ import annotations

import json
from workers import Response

def cors_headers(origin=None):
    allowed_origins = {
        "https://delyone.com",
        "https://www.delyone.com",
        "https://aigar-api.dr-delyone.workers.dev",
    }
    allowed = origin if origin in allowed_origins else "https://delyone.com"
    return {
        "Access-Control-Allow-Origin": allowed,
        "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Filename,X-File-SHA256",
        "Access-Control-Max-Age": "86400",
        "Vary": "Origin",
    }


def make_response(data, status=200, origin=None):
    headers = {"Content-Type": "application/json; charset=utf-8", **cors_headers(origin)}
    return Response(json.dumps(data, ensure_ascii=False), status=status, headers=headers)


def _request_origin(request):
    try:
        return request.headers.get("Origin")
    except Exception:
        return None


async def _json_body(request):
    try:
        body = await request.json()
        return body if isinstance(body, dict) else {}
    except Exception:
        return {}
