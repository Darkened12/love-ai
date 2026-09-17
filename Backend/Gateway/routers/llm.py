from urllib.parse import urlencode

from fastapi import Depends, APIRouter, Request
from fastapi.responses import Response, StreamingResponse
from models import MessageRequest, RegenerateMessageResponse
from services.jwt_decoding import jwt_decode
from services.route_forwarding import forward_request, forward_stream_json
from dependencies import get_client
from config import LLM_URL, DJANGO_URL

router = APIRouter(prefix='/llm')


@router.get("/fetch_user_facts")
async def fetch_user_facts(request: Request, user=Depends(jwt_decode)) -> Response:
    user_id = user.get("user_id") or user.get("sub")
    return await forward_request(request, f"{LLM_URL}/get_facts_list?user_id={user_id}")


@router.delete("/delete_memory")
async def delete_memory(
        request: Request,
        user=Depends(jwt_decode)
) -> Response:
    url = f"{LLM_URL}/delete_memory?{urlencode(request.query_params)}"
    return await forward_request(request, url)


@router.post('/fetch_message')
async def fetch_message(request: MessageRequest,
                        user=Depends(jwt_decode),
                        client=Depends(get_client)) -> StreamingResponse:
    if not request.tts:
        return await forward_stream_json(
            'POST', f'{LLM_URL}/fetch_message',
            request,
            client,
            extra={
                'chat_id': request.chat_id,
                'user_id': request.user_id
            }
        )


@router.post('/regenerate_message')
async def regenerate_message(request: RegenerateMessageResponse,
                             user=Depends(jwt_decode),
                             client=Depends(get_client)) -> StreamingResponse:
    return await forward_stream_json(
        'POST', f'{LLM_URL}/regenerate_message',
        request,
        client,
        extra={
            'chat_id': request.chat_id
        }
    )


@router.delete('/reset_relationship')
async def reset_relation(request: Request, user=Depends(jwt_decode)) -> Response:
    user_id = request.query_params.get("user_id")
    return await forward_request(request, f"{LLM_URL}/reset_relationship?user_id={user_id}")
