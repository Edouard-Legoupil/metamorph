from fastapi import Security, HTTPException, status, Request
from fastapi.security.api_key import APIKeyHeader
from app.core.config import settings

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_api_key(request: Request, api_key_header: str = Security(API_KEY_HEADER)):
    if api_key_header in settings.mcp_api_keys:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API key.",
    )


def require_mcp_key(endpoint_func):
    async def wrapper(*args, **kwargs):
        request = kwargs.get("request")
        api_key = request.headers.get("X-API-Key") if request else None
        if api_key in settings.mcp_api_keys:
            return await endpoint_func(*args, **kwargs)
        raise HTTPException(401, "Missing MCP API Key")

    return wrapper
