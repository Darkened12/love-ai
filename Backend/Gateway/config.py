import os

JWT_SECRET = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
LLM_URL = "http://llm:8000"
DJANGO_URL = "http://django-backend:8000"
DATABASE_USER = os.getenv("POSTGRES_USER")
DATABASE_PASSWORD = os.getenv("POSTGRES_PASSWORD")
