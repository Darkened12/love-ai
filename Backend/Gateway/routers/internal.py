from fastapi import APIRouter, Request, Response

from config import DJANGO_URL
from dependencies import get_client
from services.route_forwarding import forward_request

router = APIRouter(prefix="/internal")

from fastapi import Response


@router.patch("/create_chat_title")
async def create_chat_title(request: Request):
    client = get_client(request)

    chat_ownership_response = await client.get(
        f"{DJANGO_URL}/chats/check_chat_ownership/?{request.url.query}"
    )

    if chat_ownership_response.status_code == 200:
        title_response = await client.patch(
            f"{DJANGO_URL}/chats/create_chat_title/",
            json={
                "chat_id": request.query_params.get("chat_id"),
                "title": request.query_params.get("title"),
            },
        )

        return Response(
            content=title_response.content,
            status_code=title_response.status_code,
            media_type=title_response.headers.get("content-type"),
        )

    return Response(
        content=chat_ownership_response.content,
        status_code=chat_ownership_response.status_code,
        media_type=chat_ownership_response.headers.get("content-type"),
    )
