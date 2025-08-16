from typing import Annotated
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Path
from pydantic import BaseModel, Field
from starlette import status
import models
from database import SessionLocal
from sqlalchemy.orm import Session
from .auth import get_current_user
from passlib.context import CryptContext



router = APIRouter(
    prefix="/users",
    tags=["users"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class UserVerification(BaseModel):
    password : str
    new_password: str = Field(min_length=6, max_length=100)

@router.get("/user", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_model = db.query(models.Users).filter(models.Users.id == user.get("id")).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user_model

@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, verification: UserVerification, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_model = db.query(models.Users).filter(models.Users.id == user.get("id")).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not bcrypt_context.verify(verification.password, user_model.hashed_password): # type: ignore
        raise HTTPException(status_code=401, detail="Invalid password")
    user_model.hashed_password = bcrypt_context.hash(verification.new_password) # type: ignore
    db.commit()
    return {"detail": "Password updated successfully"}

@router.put("/phonenumber/{phone_number}", status_code=status.HTTP_204_NO_CONTENT)
async def update_phone_number(
    user: user_dependency,
    db: db_dependency,
    phone_number: str):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_model = db.query(models.Users).filter(models.Users.id == user.get("id")).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_model.phone_number = phone_number # type: ignore
    db.commit()