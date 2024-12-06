from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class Prompt(BaseModel):
    prompt: str


class Response(BaseModel):
    response: str

class FileResponse(BaseModel):
    id: int
    name: str
    type: str
    title: str

    class Config:
        from_attributes = True

class FileInfo(BaseModel):
    id: int
    name: str
    type: str
    size: str
    url: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None