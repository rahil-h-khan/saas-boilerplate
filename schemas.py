from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    created_at: datetime

class SubscriptionPlanCreate(BaseModel):
    name: str
    price: float
    features: List[str]

class SubscriptionPlanResponse(BaseModel):
    id: str
    name: str
    price: str
    features: List[str]
    created_at: datetime

class SubscriptionCreate(BaseModel):
    user_id: str
    plan_id: str
    end_date: datetime

class SubscriptionResponse(BaseModel):
    id: str
    user_id: str
    plan_id: str
    start_date: datetime
    end_date: datetime
    active: bool

class PaymentCreate(BaseModel):
    user_id: str
    amount: float

class PaymentResponse(BaseModel):
    id: str
    user_id: str
    amount: float
    payment_date: datetime
    status: str
    