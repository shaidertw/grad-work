from typing import Optional, List
from pydantic import BaseModel, Field

from src.schemas import DefaultResponse

class UserRequest(BaseModel):
    name: str = Field(max_length=255)

class User(BaseModel):
    id: int
    username: str = Field(max_length=255)
    source_ip: str
    org_name: str
    ntlm_hash: str

class ListUser(BaseModel):
    count: int = Field(ge=0)
    users_list: List[User] = []

class UserResponse(DefaultResponse):
    payload: Optional[str]

class ListUserResponse(DefaultResponse):
    payload: ListUser = []
