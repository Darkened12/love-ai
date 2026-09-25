from fastapi import APIRouter, Request, Response

from config import DJANGO_URL
from dependencies import get_client
from services.route_forwarding import forward_request
from models import ReplyRequest
from connection_manager import connections

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


@router.get("/get_user_last_message_at")
async def get_user_last_message_at(request: Request):
    user_id = request.query_params.get('user_id')
    if user_id is None:
        return Response({"error": "user_id is required"}, status_code=400)

    return await forward_request(request, f"{DJANGO_URL}/users/get_user_last_message_at/?user_id={user_id}")


@router.get("/get_users_last_message_at")
async def get_users_last_message_at(request: Request):
    return await forward_request(request, f"{DJANGO_URL}/users/get_users_last_message_at/")

@router.get("/get_last_chat")
async def get_users_last_message_at(request: Request):
    user_id = request.query_params.get('user_id')
    if user_id is None:
        return Response({"error": "user_id is required"}, status_code=400)

    return await forward_request(request, f"{DJANGO_URL}/chats/get_last_chat/?user_id={user_id}")


@router.post("/reply")
async def receive_reply(data: ReplyRequest):
    websocket = connections.get(data.user_id)

    if websocket is None:
        return {"status": "user_offline"}

    try:
        await websocket.send_json({
            "type": "message",
            "chat_id": data.chat_id,
            "message": data.message,
        })
    except RuntimeError:
        if connections.get(data.user_id) is websocket:
            connections.pop(data.user_id)

        return {"status": "user_offline"}

    return {"status": "sent"}


