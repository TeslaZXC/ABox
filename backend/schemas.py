from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class VerifyEmail(BaseModel):
    email: EmailStr
    code: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    email: EmailStr
    used_storage: int
    storage_quota: int
    access_key: Optional[str] = None
    secret_key: Optional[str] = None

    class Config:
        orm_mode = True

class FileArchiveRequest(BaseModel):
    file_ids: List[str]

class FileResponse(BaseModel):
    id: str
    name: str
    size: int
    mime_type: Optional[str] = None
    uploaded_at: datetime
    bucket_name: str
    key: str

    class Config:
        orm_mode = True

class SharedFileResponse(BaseModel):
    id: str
    name: str
    size: int
    mime_type: Optional[str] = None
    uploaded_at: datetime
    owner_email: str

    class Config:
        orm_mode = True
