import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config import JWT_SECRET, ALGORITHM

def decode_token(token: str):
    if not JWT_SECRET:
        raise HTTPException(status_code=500, detail="JWT secret not configured")

    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


security = HTTPBearer()


def jwt_decode(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    return decode_token(credentials.credentials)
