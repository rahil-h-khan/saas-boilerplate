import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv


load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")


client = AsyncIOMotorClient(MONGO_URI)
db = client.get_database("saas_db")
users_collection = db.get_collection("users")

async def get_radis():
    return await aioredis.from_url(REDIS_URL, decode_responses=True)