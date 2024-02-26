"""Logging Module"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func
from starlette import status

from dependencies import db_dependency, user_dependency
from models import ActionLog
from tools.common import validate_admin, validate_user

router = APIRouter(
    prefix='/logging',
    tags=['logging']
)


class ActionRequest(BaseModel):
    action: str
    log: str
    user: str


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all(db: db_dependency, user: user_dependency):
    validate_user(user)
    return db.query(ActionLog).all()


@router.get("/search/")
async def log_search(
        db: db_dependency,
        user: user_dependency,
        action: str = None,
        loguser: str = None,
        today: str = None,
        limit: int = Query(100, description="Limit the number of results", le=100)
):
    validate_user(user)

    filters = []
    if action:
        filters.append(func.lower(ActionLog.action).ilike(f"%{action.lower()}%"))
    if loguser:
        filters.append(func.lower(ActionLog.user).ilike(f"%{loguser.lower()}%"))
    if today:
        filters.append(ActionLog.today == today)

    return db.query(ActionLog).filter(*filters).limit(limit).all()


@router.post("/clear_logs")
async def clear_logs(db: db_dependency, user: user_dependency):
    validate_user(user)
    validate_admin(user)
    try:
        db.query(ActionLog).delete()
        notification_log = ActionLog(
            action="Logs Cleared",
            log="Logs Cleared",
            user=user.get('username')
        )
        db.add(notification_log)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while adding the log: {str(e)}"
        )
