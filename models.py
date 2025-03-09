import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from enum import Enum

class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"

class User(BaseModel):
    id: str = str(uuid.uuid4())
    username: str
    email: EmailStr
    hashed_password: str
    role: str = "user"
    created_at: datetime = datetime.utcnow()

    class Config:
        orm_mode = True

class SubscriptionPlan(BaseModel):
    id: str = str(uuid.uuid4())
    name: str
    price: float
    features: List[str]
    created_at: datetime = datetime.utcnow()

    class Config:
        orm_mode = True

class Subscription(BaseModel):
    id: str = str(uuid.uuid4())
    user_id: str
    plan_id: str
    start_date: datetime = datetime.utcnow()
    end_date: datetime
    active: bool = True

    class Config:
        orm_mode = True

class Payment(BaseModel):
    id: str = str(uuid.uuid4())
    user_id: str
    amount: float
    payment_date: datetime = datetime.utcnow()
    status: str

    class Config:
        orm_mode = True