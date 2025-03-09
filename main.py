import os 
import bcrypt
import jwt
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from schemas import UserCreate, UserResponse, ResetPassword
from database import users_collection
from auth import get_current_user, revoke_token, oauth2_scheme, verify_reset_token
from auth_models import update_user_password


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "rahil")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_admin_user(user: dict = Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

@app.post("/auth/reset-password")
async def reset_password(request: ResetPassword):
    email = verify_reset_token(request.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    await update_user_password(email, request.new_password)
    return {"message": "Password updated successfully"}

@app.post("/auth/forgot-password")
async def forgot_password(request: UserEmail):
    user = await get_user_raw_email(request.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reset_token = create_reset_token(request.email)
    return {"reset_token": reset_token}

@app.post("/auth/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    await revoke_token(token)
    return {"message": "Successfully logged out"}


@app.get("/admin/dashboard", dependencies=[Depends(check_role("admin"))])
async def admin_dashboard():
    return {"message": "Welcome Admin"}


@app.get("/auth/me", response_model=UserResponse, dependencies=[Depends(get_current_user)])
async def get_profile(user: dict = Depends(get_current_user)):
    return UserResponse(id=str(user["_id"]), username=user["username"], email=user["email"])

@app.post("/auth/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    existing_user = await users_collection.find_one({"email": user.email})

    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already present")
    
    hashed_password = hash_password(user.password)
    new_user = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow(),
    }

    await users_collection.insert_one(new_user)

    return UserResponse(id=str(new_user["_id"]), username=new_user["username"], email=new_user["email"])


@app.post("/auth/login", response_model=dict)
async def login_user(user: UserCreate):
    existing_user = await users_collection.find_one({"email": user.email})

    if not existing_user or not verify_password(user.password, existing_user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    access_token = create_access_token({"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
