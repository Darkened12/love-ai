from fastapi import APIRouter, Request, Depends
from fastapi.responses import Response, JSONResponse
from config import DJANGO_URL, LLM_URL
from dependencies import get_client
from services.jwt_decoding import jwt_decode
from services.route_forwarding import forward_request

router = APIRouter(prefix='/chats')


@router.get("/get_chats_list/")
async def gets_chats_list(request: Request, user=Depends(jwt_decode)):
    return await forward_request(request, f"{DJANGO_URL}/chats/get_chats_list/")


@router.get('/fetch_chat_history')
async def fetch_chat_history(request: Request, user=Depends(jwt_decode)) -> Response:
    """Only access JWT Bearer token"""
    chat_id = request.query_params['chat_id']
    if chat_id is not None:
        return await forward_request(request, f'{LLM_URL}/fetch_chat_history?chat_id={chat_id}')


@router.post("/create_chat/")
async def create_chat(request: Request, user=Depends(jwt_decode)):
    return await forward_request(request, f"{DJANGO_URL}/chats/create_chat/")


@router.patch("/update_chat_date")
async def update_chat_date(request: Request, user=Depends(jwt_decode)):
    chat_id = request.query_params.get('chat_id')
    if chat_id is None:
        return Response(status_code=400)

    return await forward_request(request, f"{DJANGO_URL}/chats/update_chat_date/?chat_id={chat_id}")


@router.patch("/rename_chat_title")
async def rename_chat_title(request: Request, user=Depends(jwt_decode)):
    return await forward_request(request, f"{DJANGO_URL}/chats/rename_chat_title/")


@router.delete("/delete_chat")
async def delete_chat(
        request: Request,
        user=Depends(jwt_decode)
) -> Response:
    chat_id = request.query_params.get('chat_id')
    if chat_id is None:
        return Response(status_code=400)

    django_url = f"{DJANGO_URL}/chats/delete_chat/?chat_id={chat_id}"
    client = get_client(request)
    resp = await client.delete(
        url=django_url,
        headers={"Authorization": request.headers.get("authorization")},
    )

    if resp.status_code == 404:
        return Response(status_code=resp.status_code, )
    if resp.status_code != 204:
        return JSONResponse(
            {"status": "only auth chat was deleted."},
            status_code=400
        )

    llm_url = f"{LLM_URL}/delete_chat?chat_id={chat_id}"

    llm_resp = await client.delete(
        url=llm_url
    )

    print("LLM RESPONSE STATUS:", llm_resp.status_code)

    return Response(status_code=204)
