from fastapi import APIRouter, Request
from config import DJANGO_URL
from services.route_forwarding import forward_request

router = APIRouter(prefix='/users')


@router.get("/profile/")
async def get_user(request: Request):
    return await forward_request(request, f"{DJANGO_URL}/users/profile/")


@router.patch("/profile/")
async def update_user(request: Request):
    return await forward_request(request, f"{DJANGO_URL}/users/profile/")


@router.post("/profile/")
async def upload_user_media(request: Request):
    return await forward_request(request, f"{DJANGO_URL}/users/profile/")
