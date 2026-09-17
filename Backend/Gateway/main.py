import httpx
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from routers.auth import router as auth_router
from routers.llm import router as llm_router
from routers.chats import router as chats_router
from routers.users import router as users_router
from routers.internal import router as internal_router
from services.route_forwarding import forward_request
from config import DJANGO_URL

app = FastAPI(
    title='Microservices Gateway/BFF',
    description='Hybrid Gateway to proxy requests to internal services.',
    version='1.0.0',
    contact={
        "name": "Darkened12",
        "email": 'https://github.com/Darkened12'
    },
    license_info={
        "name": "MIT",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(llm_router)
app.include_router(chats_router)
app.include_router(users_router)
app.include_router(internal_router)

@app.on_event("startup")
async def startup():
    app.extra["client"] = httpx.AsyncClient(timeout=None, follow_redirects=True)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.get('/user/')
@app.get('/user')
async def get_user(request: Request):
    return await forward_request(request, f'{DJANGO_URL}/auth/user/')


@app.on_event("shutdown")
async def shutdown():
    await app.extra["client"].aclose()
