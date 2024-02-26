"""Authentication Module"""
import logging
import os
import uuid
from datetime import timedelta, datetime
from typing import Annotated

from dotenv import load_dotenv
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_limiter.depends import RateLimiter
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status
from starlette.exceptions import HTTPException

from database import get_db, get_redis_connection
from models import Users, Token
from tools.config_loader import load_config

config = load_config()
load_dotenv()

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
REFRESH_TOKEN_EXPIRE_HOURS = os.getenv("REFRESH_TOKEN_EXPIRE_HOURS")

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')
logging.getLogger('passlib').setLevel(logging.ERROR)

db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    db.close()
    return user


def is_unique_username_and_email(user_name: str, email: str, db):
    existing_username = db.query(Users).filter(Users.username == user_name).first()
    existing_email = db.query(Users).filter(Users.email == email).first()
    db.close()
    return existing_username is None and existing_email is None


def create_access_token(username: str, user_id: int, is_admin: bool, expires_delta: timedelta):
    jti = str(uuid.uuid4())
    to_encode = {'sub': username, 'id': user_id, 'is_admin': is_admin, 'jti': jti}
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_bearer), redis=Depends(get_redis_connection)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        is_admin: bool = payload.get('is_admin')
        jti: str = payload.get('jti')
        expiration: int = payload.get('exp')

        if username is None or user_id is None or jti is None or expiration is None:
            raise credentials_exception

        if await redis.exists(f"blacklist:{jti}"):
            raise HTTPException(status_code=401, detail="Token revoked")

        return {'username': username, 'id': user_id, 'is_admin': is_admin, 'jti': jti, 'exp': expiration}

    except JWTError:
        raise credentials_exception


@router.post("/token", response_model=Token,
             status_code=status.HTTP_200_OK,
             dependencies=[Depends(RateLimiter(times=1, seconds=5))])
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Authentication Failed')

    access_token_expires = timedelta(minutes=float(ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token_expires = timedelta(hours=float(REFRESH_TOKEN_EXPIRE_HOURS))

    access_token = create_access_token(user.username, user.id, user.is_admin, expires_delta=access_token_expires)
    refresh_token = create_access_token(user.username, user.id, user.is_admin, expires_delta=refresh_token_expires)
    db.close()
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/token/refresh",
             status_code=status.HTTP_200_OK,
             dependencies=[Depends(RateLimiter(times=1, seconds=10))])
async def refresh_access_token(request_data: dict):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if "refresh_token" not in request_data:
        raise HTTPException(status_code=404, detail="Missing refresh token")

    refresh_token = request_data["refresh_token"]
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        is_admin: bool = payload.get('is_admin')
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    access_token_expires = timedelta(minutes=float(ACCESS_TOKEN_EXPIRE_MINUTES))
    access_token = create_access_token(username, user_id, is_admin, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(user: dict = Depends(get_current_user),
                 redis=Depends(get_redis_connection)):
    jti = user.get("jti")
    expiration = user.get("exp")
    if expiration is None:
        raise HTTPException(status_code=401, detail="Token expiration time missing")

    expiration_seconds = expiration - datetime.utcnow().timestamp()
    if expiration_seconds > 0:
        await redis.setex(f"blacklist:{jti}", int(expiration_seconds), "true")
    return {"message": "User logged out successfully"}
