from fastapi import APIRouter, Depends, Request
from models import TokenAccessRequest, TokenRefreshRequest
from dependencies import get_client
from services.route_forwarding import forward_json
from config import DJANGO_URL

router = APIRouter(prefix='/auth')


@router.post('/token/')
@router.post('/token')
async def get_refresh_token(request: TokenRefreshRequest, client=Depends(get_client)):
    return await forward_json('POST', f'{DJANGO_URL}/auth/token/', request, client)


@router.post('/token/refresh/')
@router.post('/token/refresh')
async def get_access_token(request: TokenAccessRequest, client=Depends(get_client)):
    return await forward_json(
        'POST', f'{DJANGO_URL}/auth/token/refresh/', request, client
    )
