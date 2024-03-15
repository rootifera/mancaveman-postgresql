import os
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter
from starlette import status
from starlette.exceptions import HTTPException

from database import get_redis_connection, close_redis_connection
from dependencies import db_dependency, user_dependency, bcrypt_context
from models import CreateUserRequest, Users, Hardware, Software
from tools import actionlog
from tools.common import validate_admin
from tools.config_manager import first_start_config, inject_sql_data
from tools.config_manager_redis import get_hostname, get_email_credentials, get_health_check_key, is_app_passwd_valid, \
    is_hostname_valid, set_hostname, set_email_credentials
from .auth import is_unique_username_and_email

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)


@router.post("/create_user", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, user: user_dependency,
                      create_user_request: CreateUserRequest):
    validate_admin(user)
    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        is_admin=create_user_request.is_admin,
        hashed_password=bcrypt_context.hash(create_user_request.password)
    )
    if is_unique_username_and_email(create_user_model.username, create_user_model.email, db):
        db.add(create_user_model)
        db.commit()
        actionlog.add_log("New User", "{} added at {}".format(create_user_model.username,
                                                              datetime.now().strftime("%H:%M:%S")), "System")
        return {"account": create_user_model.username + ' created.'}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Username or email already exists. Choose a different username or email.')


@router.delete("/delete_user/{username}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(db: db_dependency, user: user_dependency, username: str):
    validate_admin(user)

    user_to_delete = db.query(Users).filter(Users.username == username).first()

    if user_to_delete is None:
        raise HTTPException(status_code=404, detail='User Not Found')

    if user_to_delete.username == 'admin':
        raise HTTPException(status_code=403, detail='Cannot delete admin')

    db.delete(user_to_delete)
    db.commit()

    actionlog.add_log(
        "User Deleted",
        f"User {user_to_delete.username} deleted at {datetime.now().strftime('%H:%M:%S')}",
        "System"
    )


@router.post("/invalidate_all_caches")
async def invalidate_all_caches(user: user_dependency):
    validate_admin(user)
    redis = await get_redis_connection()
    try:
        cache_keys = await redis.keys("cache:*")
        if cache_keys:
            await redis.delete(*cache_keys)
    finally:
        await close_redis_connection(redis)

    return {"message": "All caches have been invalidated successfully"}


@router.post("/cleanup_orphaned_files", dependencies=[Depends(RateLimiter(times=2, seconds=60))])
async def cleanup_orphaned_files(db: db_dependency, user: user_dependency):
    validate_admin(user)

    images_dir = "uploads/images"
    documents_dir = "uploads/documents"

    files_to_ignore = {"favicon.ico", "DOCUMENTS"}

    hardware_files = db.query(Hardware.photos, Hardware.user_manual, Hardware.invoice).all()
    software_files = db.query(Software.photo).all()

    db_files = [os.path.basename(file) for sublist in hardware_files + software_files for file in sublist if file]

    disk_files_images = [f for f in os.listdir(images_dir) if os.path.isfile(os.path.join(images_dir, f))]
    disk_files_documents = [f for f in os.listdir(documents_dir) if os.path.isfile(os.path.join(documents_dir, f))]

    orphaned_files = (set(disk_files_images + disk_files_documents) - set(db_files)) - files_to_ignore

    if not orphaned_files:
        return {"message": "No orphaned files found"}

    deleted_files = []

    for file in orphaned_files:
        file_path_images = os.path.join(images_dir, file)
        file_path_documents = os.path.join(documents_dir, file)
        if os.path.exists(file_path_images):
            os.remove(file_path_images)
            deleted_files.append(f"Deleted {file} from Images directory")
        elif os.path.exists(file_path_documents):
            os.remove(file_path_documents)
            deleted_files.append(f"Deleted {file} from Documents directory")

    actionlog.add_log("Cleanup Orphaned Files", f"Deleted {len(orphaned_files)} orphaned files", "System")

    return {"orphaned_files": list(orphaned_files), "deleted_files": deleted_files}


@router.get("/get_server_config")
async def get_server_config(user: user_dependency):
    validate_admin(user)
    email_user, _ = await get_email_credentials()
    host_name = await get_hostname()
    health_key = await get_health_check_key()

    return {"gmail_username": email_user, "hostname": host_name, "health_check_key": health_key}


@router.post("/set_server_config")
async def set_server_config(user: user_dependency, host_name: str, email_user: str, email_app_passwd: str):
    validate_admin(user)

    host_name = host_name.strip().lower()
    email_app_passwd = email_app_passwd.strip().lower()

    if not is_hostname_valid(host_name):
        return {"error": "invalid hostname"}
    if not is_app_passwd_valid(email_app_passwd):
        return {"error": "invalid app password."}

    await set_hostname(host_name)
    await set_email_credentials(email_user, email_app_passwd)


@router.post("/import-sql/")
async def import_sql(user: user_dependency, prefixes: List[str]):
    validate_admin(user)
    try:
        inject_sql_data(prefixes)
        return {"message": "SQL files imported successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/first_run", dependencies=[Depends(RateLimiter(times=1, seconds=60))])
async def first_run():
    try:
        if first_start_config():
            return {'message': 'database configured successfully.'}
        else:
            return {'message': 'already configured'}
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred during database configuration.")
