from __future__ import annotations

import os

from .._output import progress

_DEFAULT_API = "https://8.152.217.126/api/knowledge/search"


def search_knowledge(keywords: list[str], max_char_size: int = 5000) -> dict:
    import httpx

    api_url = os.environ.get("ADK_KNOWLEDGE_API", _DEFAULT_API)
    progress(f"搜索知识库: {', '.join(keywords)}")

    try:
        with httpx.Client(verify=False, timeout=15.0) as client:
            resp = client.post(api_url, json={"keywords": keywords, "maxCharSize": max_char_size})
            resp.raise_for_status()
            data = resp.json()
    except httpx.ConnectError:
        return {
            "status": "error", "command": "knowledge",
            "error_type": "connection_error",
            "message": f"知识库 API 不可达: {api_url}",
            "suggestion": "检查网络连接，或通过 ADK_KNOWLEDGE_API 环境变量指定替代 endpoint",
        }
    except httpx.TimeoutException:
        return {
            "status": "error", "command": "knowledge",
            "error_type": "timeout",
            "message": "知识库 API 请求超时（15s）",
        }
    except httpx.HTTPStatusError as e:
        return {
            "status": "error", "command": "knowledge",
            "error_type": "http_error",
            "message": f"HTTP {e.response.status_code}",
            "detail": e.response.text[:2000],
        }
    except Exception as e:
        return {
            "status": "error", "command": "knowledge",
            "error_type": "unknown_error",
            "message": str(e),
        }

    return {
        "status": "ok", "command": "knowledge",
        "keywords": keywords,
        "data": data,
    }
