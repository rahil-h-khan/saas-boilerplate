from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
import os
import aioredis
from dotenv import load_dotenv
from database import users_collection
from datetime import datetime, timedelta

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "rahil")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def create_reset_token(email: str):
    payload = {
        "sub": email,
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_reset_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithm=ALGORITHM)
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

async def revoke_token(token: str):
    redis = await get_redis()
    await redis.setex(token, 3600, "revoked")


async def is_token_revoked(token: str):
    redis = await get_redis()
    return await redis.exists(token)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    if await is_token_revoked(token):
        raise HTTPException(status_code=401, detail="Token revoked. Please log in again")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithm=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await users_collection.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")