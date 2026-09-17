from typing import Any

import httpx
from fastapi import Request, Response
from fastapi.responses import StreamingResponse
from dependencies import get_client

HOP_HEADERS = {
    "host",
    "content-length",
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
}


async def forward_request(request: Request, url: str) -> Response:
    body = await request.body()

    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in HOP_HEADERS
    }

    client = get_client(request)
    resp = await client.request(
        method=request.method,
        url=url,
        content=body,
        headers=headers,
    )

    response = Response(
        content=resp.content,
        status_code=resp.status_code,
        media_type=resp.headers.get("content-type"),
    )

    for k, v in resp.headers.items():
        if k.lower() not in HOP_HEADERS:
            response.headers[k] = v

    return response


async def forward_json(
    method: str,
    url: str,
    data,
    client: httpx.AsyncClient,
    extra: dict[str, Any] | None = None,
) -> Response:
    payload = data.model_dump()
    if extra:
        payload.update(extra)

    resp = await client.request(
        method=method,
        url=url,
        json=payload,
    )

    return Response(
        content=resp.content,
        status_code=resp.status_code,
        media_type=resp.headers.get("content-type"),
    )


async def forward_stream_request(request: Request, url: str) -> StreamingResponse:
    # 1. Read the request body (if any)
    body = await request.body()

    # 2. Forward-safe headers
    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in HOP_HEADERS
    }
    headers["x-forwarded-for"] = request.client.host
    headers["x-forwarded-proto"] = request.url.scheme

    # 3. Build the request and send it with stream=True
    client = get_client(request)
    req = client.build_request(
        method=request.method,
        url=url,
        headers=headers,
        content=body,
    )
    upstream_response = await client.send(req, stream=True)

    # 4. Create an async generator that yields bytes AND properly closes upstream
    async def stream_bytes():
        try:
            async for chunk in upstream_response.aiter_bytes():
                yield chunk
        finally:
            # Crucial: close the upstream connection when done or on error
            await upstream_response.aclose()

    # 5. Return the streaming response
    return StreamingResponse(
        stream_bytes(),
        status_code=upstream_response.status_code,
        headers={
            k: v for k, v in upstream_response.headers.items()
            if k.lower() not in HOP_HEADERS
        },
        media_type=upstream_response.headers.get("content-type"),
    )


async def forward_stream_json(
    method: str,
    url: str,
    data,
    client: httpx.AsyncClient,
    extra: dict[str, Any] | None = None,
):
    payload = data.model_dump()
    if extra:
        payload.update(extra)

    req = client.build_request(
        method=method,
        url=url,
        json=payload,
    )
    resp = await client.send(req, stream=True)

    async def stream():
        try:
            async for chunk in resp.aiter_bytes():
                yield chunk
        finally:
            await resp.aclose()

    return StreamingResponse(
        stream(),
        status_code=resp.status_code,
        media_type=resp.headers.get("content-type"),
    )
