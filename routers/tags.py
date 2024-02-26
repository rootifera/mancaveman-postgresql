"""Tags Module"""

import json

from fastapi import APIRouter, HTTPException
from sqlalchemy import func

from database import get_redis_connection, close_redis_connection, invalidate_redis_cache
from definitions import DESC_TAG_404
from dependencies import db_dependency, user_dependency
from models import Tag, HardwareTag, SoftwareTag
from tools.common import validate_user, validate_admin

router = APIRouter(
    prefix='/tags',
    tags=['tags']
)


@router.get("/get_all")
async def get_all_tags(tag_type: str, db: db_dependency, user: user_dependency):
    validate_user(user)
    if tag_type not in ['hardware', 'software', 'all']:
        raise HTTPException(status_code=400, detail="Invalid tag_type. Must be 'hardware', 'software', or 'all'.")

    redis = await get_redis_connection()
    cache_key = f"cache:tags:{tag_type}"

    try:
        cached_tags = await redis.get(cache_key)
        if cached_tags:
            print("\033[92m########## CACHE HIT ##########\033[0m")
            return json.loads(cached_tags)

        if tag_type == 'all':
            tags = db.query(Tag).all()
        else:
            tags = db.query(Tag).filter(Tag.tag_type == tag_type).all()

        tag_list = [{"id": tag.id, "name": tag.name, "tag_type": tag.tag_type} for tag in tags]

        await redis.set(cache_key, json.dumps(tag_list), ex=3600)

        return tag_list

    finally:
        await close_redis_connection(redis)


@router.get("/get_tag_by_name")
async def get_tag_by_name(name: str, tag_type: str, db: db_dependency, user: user_dependency):
    validate_user(user)
    if tag_type not in ['hardware', 'software']:
        raise HTTPException(status_code=400, detail="Invalid tag_type. Must be 'hardware' or 'software'.")

    tag = db.query(Tag).filter(Tag.name == name, Tag.tag_type == tag_type).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found.")
    return {"id": tag.id, "name": tag.name, "tag_type": tag.tag_type}


@router.post("/add")
async def add_tag(tag_name: str, tag_type: str, db: db_dependency, user: user_dependency):
    validate_admin(user)

    if tag_type not in ['hardware', 'software']:
        raise HTTPException(status_code=400, detail="Invalid tag_type. Must be 'hardware' or 'software'.")

    standardized_tag_name = tag_name.strip().lower()

    existing_tag = db.query(Tag).filter(func.lower(Tag.name) == standardized_tag_name, Tag.tag_type == tag_type).first()
    if existing_tag:
        return {"message": "Tag already exists", "id": existing_tag.id, "name": existing_tag.name,
                "tag_type": existing_tag.tag_type}

    new_tag = Tag(name=standardized_tag_name, tag_type=tag_type)
    db.add(new_tag)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    await invalidate_redis_cache("cache:tags:*")
    db.refresh(new_tag)

    return {"message": "Tag added successfully", "id": new_tag.id, "name": new_tag.name, "tag_type": new_tag.tag_type}


@router.put("/update/{tag_id}")
async def update_tag(tag_id: int, tag_name: str, tag_type: str, db: db_dependency, user: user_dependency):
    validate_admin(user)

    if tag_type not in ['hardware', 'software']:
        raise HTTPException(status_code=400, detail="Invalid tag_type. Must be 'hardware' or 'software'.")

    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail=DESC_TAG_404)

    standardized_tag_name = tag_name.strip().lower()

    existing_tag = db.query(Tag).filter(Tag.id != tag_id, func.lower(Tag.name) == standardized_tag_name,
                                        Tag.tag_type == tag_type).first()
    if existing_tag:
        raise HTTPException(status_code=400, detail="A tag with the same name and type already exists.")

    tag.name = standardized_tag_name
    tag.tag_type = tag_type
    db.commit()
    await invalidate_redis_cache("cache:tags:*")

    return {"message": "Tag updated successfully", "id": tag.id, "name": tag.name, "tag_type": tag.tag_type}


@router.delete("/remove/{tag_id}")
async def remove_tag(tag_id: int, db: db_dependency, user: user_dependency):
    validate_admin(user)
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail=DESC_TAG_404)

    hardware_in_use = db.query(HardwareTag).filter(HardwareTag.tag_id == tag_id).first()
    software_in_use = db.query(SoftwareTag).filter(SoftwareTag.tag_id == tag_id).first()

    if hardware_in_use or software_in_use:
        raise HTTPException(status_code=400, detail="Cannot remove tag as it is currently in use")

    db.delete(tag)
    db.commit()
    await invalidate_redis_cache("cache:tags:*")

    return {"message": "Tag removed successfully", "id": tag_id}
