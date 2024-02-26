# dependencies.py

from typing import Annotated

from fastapi import Depends
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import get_db
from routers.auth import get_current_user

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
