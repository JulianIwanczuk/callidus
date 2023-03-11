from pydantic import BaseModel

class LoginBodyRequest(BaseModel): 
    username: str
    password: str


class DocumentBodyRequest(BaseModel):
    file: object