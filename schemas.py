from typing import Optional
from pydantic import BaseModel
from models import TransactionType

class UserCreate(BaseModel):
    name: str
    email: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True


class TransactionCreate(BaseModel):
    title: str
    amount: float
    type: TransactionType
    user_id: int


class TransactionUpdate(BaseModel):
    title: Optional[str] = None
    amount: Optional[float] = None
    type: Optional[TransactionType] = None
    user_id: Optional[int] = None


class TransactionResponse(BaseModel):
    id: int
    title: str
    amount: float
    type: TransactionType
    user_id: int

    class Config:
        from_attributes = True