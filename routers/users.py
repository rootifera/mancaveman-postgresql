import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from models import Users
from tools.common import validate_user
from tools.gmail_reset_pw import send_pw_reset_email
from .auth import get_current_user

router = APIRouter(
    prefix='/user',
    tags=['user']
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


@router.get('/', status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    validate_user(user)
    return db.query(Users).filter(Users.id == user.get('id')).first()


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency,
                          user_verification: UserVerification):
    validate_user(user)
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail='Error on password change')
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()


@router.get("/password_reset")
async def password_reset(db: db_dependency, email: str):
    user_to_reset = db.query(Users).filter(Users.email == email).first()
    if user_to_reset is not None:
        receiver = user_to_reset.email
        reset_token = secrets.token_hex(16)
        user_to_reset.reset_token = reset_token
        send_pw_reset_email(receiver, reset_token)
        db.commit()
        db.close()
        return status.HTTP_202_ACCEPTED
    else:
        return {'ERROR': 'Email not found'}


@router.put("/forgot_password")
async def forgot_password(db: db_dependency, request_data: dict):
    email_token = request_data.get("email_token")
    new_password = request_data.get("new_password")

    if email_token is None or new_password is None:
        raise HTTPException(status_code=401, detail='Unauthorized')

    user_to_reset = db.query(Users).filter(Users.reset_token == email_token).first()

    if user_to_reset is None or user_to_reset.reset_token == 'NORESET':
        raise HTTPException(status_code=404, detail='Password reset request not found')
    else:
        user_to_reset.hashed_password = bcrypt_context.hash(new_password)
        user_to_reset.reset_token = 'NORESET'
        db.commit()
        db.close()
        return {'INFO': 'Password changed successfully'}


@router.put("/set_books_api_key", status_code=status.HTTP_204_NO_CONTENT)
async def set_books_api_key(user: user_dependency, db: db_dependency, api_key_data: str):
    validate_user(user)

    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    user_model.books_api_key = api_key_data

    db.add(user_model)
    db.commit()
