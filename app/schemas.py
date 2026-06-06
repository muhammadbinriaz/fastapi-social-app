from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Annotated


class PostBase(BaseModel):
  title: str
  content: str
  published: bool = True

class PostCreate(PostBase):
  pass

class Post(PostBase):
  id: int
  created_at: datetime
  owner_id : int
  owner: UserOut

  model_config = {
    "from_attributes": True
  }

class PostOut(BaseModel):
  Post: Post
  votes: int


class UserCreate(BaseModel):
  email: EmailStr
  password: str

class UserOut(BaseModel):
  id: int
  email: EmailStr
  created_at: datetime

  model_config = {
    "from_attributes": True
  }


class UserLogin(BaseModel):
  email: EmailStr
  password: str


class token(BaseModel):
  access_token: str
  token_type: str


class TokenData(BaseModel):
  id: str | None = None
  email: str | None = None  

class Vote(BaseModel):
  post_id: int
  dir: Annotated[int, Field(ge=0, le=1)]