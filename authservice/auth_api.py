from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
import auth_utils
from typing import Optional
import json
import httpx
import os
from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
   username: str
   password: str
class UserResponse(BaseModel):
  id: str
  username: str
class User(UserResponse):
  hashed_password: str
class Token(BaseModel):
   access_token: str
   token_type: str

router = APIRouter()
#db_url = os.getenv("DB_URL", "http://localhost:8003")
main_url = "http://localhost:8001"
@router.post("/users", response_model=UserResponse)
async def register_user(user: UserCreate):
    async with httpx.AsyncClient() as client:
        
        response = await client.post(f"{main_urll}/create_user", json=user.model_dump())
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))
        return response.json()
        
@router.post("/token", response_model=Token)
async def login(userin :UserCreate):
  credentials_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Incorrect username or password"
     )
  async with httpx.AsyncClient() as client:
      username = userin.username
      response = await client.get(f"{main_urll}/users_by_username/{username}")
      if response.status_code != 200:
          raise credentials_exception
      user = response.json()
      if not auth_utils.verify_password(userin.password, User(**user).hashed_password):
         raise credentials_exception
      access_token = auth_utils.create_access_token(data={"sub": username})
  return Token(access_token=access_token, token_type="bearer")

@router.get("/user", response_model=UserResponse)
async def get_user(token: str):
   credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
   try:
      payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
      username: str = payload.get("sub")
      if username is None:
          raise credentials_exception
   except JWTError:
      raise credentials_exception
   async with httpx.AsyncClient() as client:
        response = await client.get(f"{main_url}/users_by_username/{username}")
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))
        return response.json()
