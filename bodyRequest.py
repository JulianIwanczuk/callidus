from pydantic import BaseModel
from fastapi import Form
from typing import Optional
import datetime

class TokenBodyRequest(BaseModel):
    letter: str = None

class LoginBodyRequest(BaseModel): 
    username: str = None
    email: str = None
    password: str

class DocumentBodyRequest(BaseModel):
    file: object

class UserBodyRequest(BaseModel):
    username: str = None
    password: str
    confirm: str = None
    fullname: str
    email: str
    category: int = 2
    is_active: bool = True
    business_name: str = None
    business_code: str = None

class SessionBodyRequest(BaseModel):
    id: int
    user_id: int
    token: str
    status: int
    date_create: datetime.datetime

class UcrBodyRequest(BaseModel):
    user_id: int = None
    crr_id: int = None
    date_crate: datetime.datetime = None
    message_spend: int = None
    cumulate: float = None