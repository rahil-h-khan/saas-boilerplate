import bcrypt
from database import db

async def update_user_password(email: str, new_password):
    hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    await db["Users"].update_one({"email": email}, {"$set": {"hashed_password": hashed_password}})