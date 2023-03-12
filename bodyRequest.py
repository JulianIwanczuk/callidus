from pydantic import BaseModel
from fastapi import Form
from typing import Optional
import datetime

class LoginBodyRequest(BaseModel): 
    username: str
    password: str

class DocumentBodyRequest(BaseModel):
    file: object

class UserBodyRequest(BaseModel):
    username: str
    password: str
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