"""Software Module"""
import json
from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from starlette import status

from database import get_redis_connection, close_redis_connection, invalidate_redis_cache
from definitions import DESC_FUZZY
from dependencies import db_dependency, user_dependency
from models import Software, SoftwareRequest, SoftwareCategory, SoftwareCategoryRequest, SoftwarePublisher, \
    SoftwarePublisherRequest, SoftwareDeveloper, SoftwareDeveloperRequest, SoftwarePlatform, SoftwarePlatformRequest, \
    SoftwareMediaType, SoftwareMediaTypeRequest, SoftwareTag, Tag
from tools import actionlog
from tools.common import validate_user, validate_admin

TAG_TYPE = "software"

router = APIRouter(
    prefix='/software',
    tags=['software']
)


def search_any_match(db: db_dependency, tags: List[str]):
    software_items = db.query(Software). \
        join(SoftwareTag). \
        join(Tag). \
        filter(
        Tag.name.in_(tags),
        Tag.tag_type == TAG_TYPE
    ). \
        all()

    return [format_software_response(item, db) for item in software_items]


def search_all_match(db: db_dependency, tags: List[str]):
    matching_software_ids = db.query(SoftwareTag.software_id) \
        .join(Tag) \
        .filter(
        Tag.name.in_(tags),
        Tag.tag_type == TAG_TYPE
    ) \
        .group_by(SoftwareTag.software_id) \
        .having(func.count(Tag.id) == len(tags)) \
        .subquery()

    software_items = db.query(Software) \
        .join(SoftwareTag) \
        .filter(Software.id == matching_software_ids.c.software_id) \
        .group_by(Software.id) \
        .having(func.count(SoftwareTag.tag_id) == len(tags)) \
        .all()

    return [format_software_response(item, db) for item in software_items]


def format_software_response(software_model, db_session):
    tags = db_session.query(Tag.name).join(SoftwareTag).filter(
        SoftwareTag.software_id == software_model.id,
        Tag.tag_type == TAG_TYPE
    ).all()
    tags_list = [tag[0] for tag in tags]

    return {
        "id": software_model.id,
        "name": software_model.name,
        "year": software_model.year,
        "barcode": software_model.barcode,
        "location": software_model.location,
        "media_count": software_model.media_count,
        "condition": software_model.condition,
        "product_key": software_model.product_key,
        "photo": software_model.photo,
        "multiple_copies": software_model.multiple_copies,
        "multicopy_id": software_model.multicopy_id,
        "image_backups": software_model.image_backups,
        "image_backup_location": software_model.image_backup_location,
        "redump_disk_ids": software_model.redump_disk_ids,
        "notes": software_model.notes,
        "tags": tags_list,
        "category": software_model.category.name if software_model.category else None,
        "publisher": software_model.publisher.name if software_model.publisher else None,
        "developer": software_model.developer.name if software_model.developer else None,
        "platform": software_model.platform.name if software_model.platform else None,
        "media_type": software_model.media_type.name if software_model.media_type else None
    }


@router.get("/get_all_categories", status_code=status.HTTP_200_OK)
async def get_all_categories(user: user_dependency, db: db_dependency):
    validate_user(user)

    cache_key = "cache:all_sw_categories"
    redis = await get_redis_connection()
    try:
        cached_categories = await redis.get(cache_key)

        if cached_categories:
            print("\033[92m########## CACHE HIT ##########\033[0m")
            return json.loads(cached_categories)

        categories = db.query(SoftwareCategory).order_by(SoftwareCategory.name).all()
        categories_data = [{"id": category.id, "name": category.name} for category in categories]

        await redis.set(cache_key, json.dumps(categories_data), ex=3600)

        return categories_data
    finally:
        await close_redis_connection(redis)


@router.get("/get_category_by_name", status_code=status.HTTP_200_OK)
async def get_category_by_name(db: db_dependency, user: user_dependency,
                               category_name: str = Query(..., description="The name of the category to be retrieved")):
    validate_user(user)
    category = db.query(SoftwareCategory).filter(func.lower(SoftwareCategory.name) == func.lower(category_name)).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return {"id": category.id, "name": category.name}


@router.post("/add_category", status_code=status.HTTP_201_CREATED)
async def add_category(
        user: user_dependency,
        db: db_dependency,
        category_request: SoftwareCategoryRequest
):
    category_name_lower = category_request.name.lower()

    existing_category = db.query(SoftwareCategory).filter(
        func.lower(SoftwareCategory.name) == category_name_lower).first()
    if existing_category:
        raise HTTPException(status_code=400, detail="Category name already exists")

    category_instance = SoftwareCategory(name=category_request.name)
    db.add(category_instance)
    try:
        db.commit()

        await invalidate_redis_cache('cache:all_sw_categories')

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error adding category")

    db.refresh(category_instance)

    actionlog.add_log(
        "New software category",
        "{} added at {}".format(category_instance.name, datetime.now().strftime("%H:%M:%S")),
        user.get('username')
    )

    return {"message": "Category added successfully", "id": category_instance.id, "name": category_instance.name}


@router.put("/update_category", status_code=status.HTTP_200_OK)
async def update_category(db: db_dependency, user: user_dependency,
                          category_request: SoftwareCategoryRequest,
                          category_id: int = Query(..., description="The ID of the category to be updated")):
    validate_admin(user)

    category_name_lower = category_request.name.lower()

    existing_category = db.query(SoftwareCategory).filter(
        func.lower(SoftwareCategory.name) == category_name_lower,
        SoftwareCategory.id != category_id
    ).first()

    if existing_category:
        raise HTTPException(status_code=400, detail="Category name already exists with another ID")

    category_to_update = db.query(SoftwareCategory).filter(SoftwareCategory.id == category_id).first()
    if not category_to_update:
        raise HTTPException(status_code=404, detail="Category not found")

    category_to_update.name = category_request.name
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error updating category")

    db.refresh(category_to_update)

    actionlog.add_log(
        "Updated software category",
        "{} updated to {} at {}".format(category_to_update.name, category_request.name,
                                        datetime.now().strftime("%H:%M:%S")),
        user.get('username')
    )

    # Invalidate cache
    await invalidate_redis_cache('cache:all_sw_categories')

    return {"message": "Category updated successfully", "id": category_to_update.id, "name": category_to_update.name}


@router.delete("/remove_category/{category_id}", status_code=status.HTTP_200_OK)
async def remove_category(category_id: int, db: db_dependency, user: user_dependency):
    validate_admin(user)

    category_to_delete = db.query(SoftwareCategory).filter(SoftwareCategory.id == category_id).first()
    if not category_to_delete:
        raise HTTPException(status_code=404, detail="Category not found")

    associated_software = db.query(Software).filter(Software.category_id == category_id).all()
    if associated_software:
        associated_software_details = [{"id": software.id, "name": software.name} for software in associated_software]
        return {"message": "Cannot delete category with associated software items",
                "associated_software": associated_software_details}

    db.delete(category_to_delete)
    db.commit()

    await invalidate_redis_cache('cache:all_sw_categories')

    return {"message": "Category removed successfully"}


@router.get("/get_all_publishers", status_code=status.HTTP_200_OK)
async def get_all_publishers(user: user_dependency, db: db_dependency):
    validate_user(user)

    cache_key = "cache:all_publishers"
    redis = await get_redis_connection()
    try:
        cached_publishers = await redis.get(cache_key)

        if cached_publishers:
            print("\033[92m########## CACHE HIT ##########\033[0m")
            return json.loads(cached_publishers)

        publishers = db.query(SoftwarePublisher).order_by(SoftwarePublisher.name).all()
        publishers_data = [{"id": publisher.id, "name": publisher.name} for publisher in publishers]

        await redis.set(cache_key, json.dumps(publishers_data), ex=3600)

        return publishers_data
    finally:
        await close_redis_connection(redis)


@router.get("/get_publisher_by_name", status_code=status.HTTP_200_OK)
async def get_publisher_by_name(db: db_dependency, user: user_dependency,
                                publisher_name: str = Query(...,
                                                            description="The name of the publisher to be retrieved")):
    validate_user(user)
    publisher = db.query(SoftwarePublisher).filter(
        func.lower(SoftwarePublisher.name) == func.lower(publisher_name)).first()

    if not publisher:
        raise HTTPException(status_code=404, detail="Publisher not found")

    return {"id": publisher.id, "name": publisher.name}


@router.post("/add_publisher", status_code=status.HTTP_201_CREATED)
async def add_publisher(
        user: user_dependency,
        db: db_dependency,
        publisher_request: SoftwarePublisherRequest
):
    publisher_name_lower = publisher_request.name.lower()

    existing_publisher = db.query(SoftwarePublisher).filter(
        func.lower(SoftwarePublisher.name) == publisher_name_lower).first()
    if existing_publisher:
        raise HTTPException(status_code=400, detail="Publisher name already exists")

    publisher_instance = SoftwarePublisher(name=publisher_request.name)
    db.add(publisher_instance)
    try:
        db.commit()

        await invalidate_redis_cache('cache:all_publishers')

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error adding publisher")

    db.refresh(publisher_instance)

    actionlog.add_log(
        "New software publisher",
        "{} added at {}".format(publisher_instance.name, datetime.now().strftime("%H:%M:%S")),
        user.get('username')
    )

    return {"message": "Publisher added successfully", "id": publisher_instance.id, "name": publisher_instance.name}


@router.put("/update_publisher", status_code=status.HTTP_200_OK)
async def update_publisher(db: db_dependency, user: user_dependency,
                           publisher_request: SoftwarePublisherRequest,
                           publisher_id: int = Query(..., description="The ID of the publisher to be updated")):
    validate_admin(user)

    publisher_name_lower = publisher_request.name.lower()

    existing_publisher = db.query(SoftwarePublisher).filter(
        func.lower(SoftwarePublisher.name) == publisher_name_lower,
        SoftwarePublisher.id != publisher_id
    ).first()

    if existing_publisher:
        raise HTTPException(status_code=400, detail="Publisher name already exists with another ID")

    publisher_to_update = db.query(SoftwarePublisher).filter(SoftwarePublisher.id == publisher_id).first()
    if not publisher_to_update:
        raise HTTPException(status_code=404, detail="Publisher not found")

    publisher_to_update.name = publisher_request.name
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error updating publisher")

    db.refresh(publisher_to_update)

    actionlog.add_log(
        "Updated software publisher",
        "{} updated to {} at {}".format(publisher_to_update.name, publisher_request.name,
                                        datetime.now().strftime("%H:%M:%S")),
        user.get('username')
    )

    # Invalidate cache
    await invalidate_redis_cache('cache:all_publishers')

    return {"message": "Publisher updated successfully", "id": publisher_to_update.id, "name": publisher_to_update.name}


@router.delete("/remove_publisher/{publisher_id}", status_code=status.HTTP_200_OK)
async def remove_publisher(publisher_id: int, db: db_dependency, user: user_dependency):
    validate_admin(user)

    publisher_to_delete = db.query(SoftwarePublisher).filter(SoftwarePublisher.id == publisher_id).first()
    if not publisher_to_delete:
        raise HTTPException(status_code=404, detail="Publisher not found")

    associated_software = db.query(Software).filter(Software.publisher_id == publisher_id).all()
    if associated_software:
        associated_software_details = [{"id": software.id, "name": software.name} for software in associated_software]
        return {"message": "Cannot delete publisher with associated software items",
                "associated_software": associated_software_details}

    db.delete(publisher_to_delete)
    db.commit()

    await invalidate_redis_cache('cache:all_publishers')

    return {"message": "Publisher removed successfully"}


@router.get("/get_all_developers", status_code=status.HTTP_200_OK)
async def get_all_developers(user: user_dependency, db: db_dependency):
    validate_user(user)

    cache_key = "cache:all_developers"
    redis = await get_redis_connection()
    try:
        cached_developers = await redis.get(cache_key)

        if cached_developers:
            print("\033[92m########## CACHE HIT ##########\033[0m")
            return json.loads(cached_developers)

        developers = db.query(SoftwareDeveloper).order_by(SoftwareDeveloper.name).all()
        developers_data = [{"id": developer.id, "name": developer.name} for developer in developers]

        await redis.set(cache_key, json.dumps(developers_data), ex=3600)

        return developers_data
    finally:
        await close_redis_connection(redis)


@router.get("/get_developer_by_name", status_code=status.HTTP_200_OK)
async def get_developer_by_name(db: db_dependency, user: user_dependency,
                                developer_name: str = Query(...,
                                                            description="The name of the developer to be retrieved")):
    validate_user(user)
    developer = db.query(SoftwareDeveloper).filter(
        func.lower(SoftwareDeveloper.name) == func.lower(developer_name)).first()

    if not developer:
        raise HTTPException(status_code=404, detail="Developer not found")

    return {"id": developer.id, "name": developer.name}


@router.post("/add_developer", status_code=status.HTTP_201_CREATED)
async def add_developer(
        user: user_dependency,
        db: db_dependency,
        developer_request: SoftwareDeveloperRequest
):
    developer_name_lower = developer_request.name.lower()

    existing_developer = db.query(SoftwareDeveloper).filter(
        func.lower(SoftwareDeveloper.name) == developer_name_lower).first()
    if existing_developer:
        raise HTTPException(status_code=400, detail="Developer name already exists")

    developer_instance = SoftwareDeveloper(name=developer_request.name)
    db.add(developer_instance)
    try:
        db.commit()

        await invalidate_redis_cache('cache:all_developers')

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error adding developer")

    db.refresh(developer_instance)

    actionlog.add_log(
        "New software developer",
        "{} added at {}".format(developer_instance.name, datetime.now().strftime("%H:%M:%S")),
        user.get('username')
    )

    return {"message": "Developer added successfully", "id": developer_instance.id, "name": developer_instance.name}


@router.put("/update_developer", status_code=status.HTTP_200_OK)
async def update_developer(db: db_dependency, user: user_dependency,
                           developer_request: SoftwareDeveloperRequest,
                           developer_id: int = Query(..., description="The ID of the developer to be updated")):
    validate_admin(user)

    developer_name_lower = developer_request.name.lower()

    existing_developer = db.query(SoftwareDeveloper).filter(
        func.lower(SoftwareDeveloper.name) == developer_name_lower,
        SoftwareDeveloper.id != developer_id
    ).first()

    if existing_developer:
        raise HTTPException(status_code=400, detail="Developer name already exists with another ID")

    developer_to_update = db.query(SoftwareDeveloper).filter(SoftwareDeveloper.id == developer_id).first()
    if not developer_to_update:
        raise HTTPException(status_code=404, detail="Developer not found")

    developer_to_update.name = developer_request.name
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error updating developer")

    db.refresh(developer_to_update)

    actionlog.add_log(
        "Updated software developer",
        "{} updated to {} at {}".format(developer_to_update.name, developer_request.name,
                                        datetime.now().strftime("%H:%M:%S")),
        user.get('username')
    )

    # Invalidate cache
    await invalidate_redis_cache('cache:all_developers')

    return {"message": "Developer updated successfully", "id": developer_to_update.id, "name": developer_to_update.name}


@router.delete("/remove_developer/{developer_id}", status_code=status.HTTP_200_OK)
async def remove_developer(developer_id: int, db: db_dependency, user: user_dependency):
    validate_admin(user)

    developer_to_delete = db.query(SoftwareDeveloper).filter(SoftwareDeveloper.id == developer_id).first()
    if not developer_to_delete:
        raise HTTPException(status_code=404, detail="Developer not found")

    associated_software = db.query(Software).filter(Software.developer_id == developer_id).all()
    if associated_software:
        associated_software_details = [{"id": software.id, "name": software.name} for software in associated_software]
        return {"message": "Cannot delete developer with associated software items",
                "associated_software": associated_software_details}

    db.delete(developer_to_delete)
    db.commit()

    await invalidate_redis_cache('cache:all_developers')

    return {"message": "Developer removed successfully"}


@router.get("/get_all_platforms", status_code=status.HTTP_200_OK)
async def get_all_platforms(user: user_dependency, db: db_dependency):
    validate_user(user)

    cache_key = "cache:all_platforms"
    redis = await get_redis_connection()
    try:
        cached_platforms = await redis.get(cache_key)

        if cached_platforms:
            print("\033[92m########## CACHE HIT ##########\033[0m")
            return json.loads(cached_platforms)

        platforms = db.query(SoftwarePlatform).order_by(SoftwarePlatform.name).all()
        platforms_data = [{"id": platform.id, "name": platform.name} for platform in platforms]

        await redis.set(cache_key, json.dumps(platforms_data), ex=3600)

        return platforms_data
    finally:
        await close_redis_connection(redis)


@router.get("/get_platform_by_name", status_code=status.HTTP_200_OK)
async def get_platform_by_name(db: db_dependency, user: user_dependency,
                               platform_name: str = Query(..., description="The name of the platform to be retrieved")):
    validate_user(user)
    platform = db.query(SoftwarePlatform).filter(func.lower(SoftwarePlatform.name) == func.lower(platform_name)).first()

    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")

    return {"id": platform.id, "name": platform.name}


@router.post("/add_platform", status_code=status.HTTP_201_CREATED)
async def add_platform(
        user: user_dependency,
        db: db_dependency,
        platform_request: SoftwarePlatformRequest
):
    platform_name_lower = platform_request.name.lower()

    existing_platform = db.query(SoftwarePlatform).filter(
        func.lower(SoftwarePlatform.name) == platform_name_lower).first()
    if existing_platform:
        raise HTTPException(status_code=400, detail="Platform name already exists")

    platform_instance = SoftwarePlatform(name=platform_request.name)
    db.add(platform_instance)
    try:
        db.commit()

        await invalidate_redis_cache('cache:all_platforms')  # Invalidate cache

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error adding platform")

    db.refresh(platform_instance)

    actionlog.add_log(
        "New software platform",
        "{} added at {}".format(platform_instance.name, datetime.now().strftime("%H:%M:%S")),
        user.get('username')
    )

    return {"message": "Platform added successfully", "id": platform_instance.id, "name": platform_instance.name}


@router.put("/update_platform", status_code=status.HTTP_200_OK)
async def update_platform(db: db_dependency, user: user_dependency,
                          platform_request: SoftwarePlatformRequest,
                          platform_id: int = Query(..., description="The ID of the platform to be updated")):
    validate_admin(user)

    platform_name_lower = platform_request.name.lower()

    existing_platform = db.query(SoftwarePlatform).filter(
        func.lower(SoftwarePlatform.name) == platform_name_lower,
        SoftwarePlatform.id != platform_id
    ).first()

    if existing_platform:
        raise HTTPException(status_code=400, detail="Platform name already exists with another ID")

    platform_to_update = db.query(SoftwarePlatform).filter(SoftwarePlatform.id == platform_id).first()
    if not platform_to_update:
        raise HTTPException(status_code=404, detail="Platform not found")

    platform_to_update.name = platform_request.name
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error updating platform")

    db.refresh(platform_to_update)

    actionlog.add_log(
        "Updated software platform",
        "{} updated to {} at {}".format(platform_to_update.name, platform_request.name,
                                        datetime.now().strftime("%H:%M:%S")),
        user.get('username')
    )

    # Invalidate cache
    await invalidate_redis_cache('cache:all_platforms')

    return {"message": "Platform updated successfully", "id": platform_to_update.id, "name": platform_to_update.name}


@router.delete("/remove_platform/{platform_id}", status_code=status.HTTP_200_OK)
async def remove_platform(platform_id: int, db: db_dependency, user: user_dependency):
    validate_admin(user)

    platform_to_delete = db.query(SoftwarePlatform).filter(SoftwarePlatform.id == platform_id).first()
    if not platform_to_delete:
        raise HTTPException(status_code=404, detail="Platform not found")

    associated_software = db.query(Software).filter(Software.platform_id == platform_id).all()
    if associated_software:
        associated_software_details = [{"id": software.id, "name": software.name} for software in associated_software]
        return {"message": "Cannot delete platform with associated software items",
                "associated_software": associated_software_details}

    db.delete(platform_to_delete)
    db.commit()

    await invalidate_redis_cache('cache:all_platforms')

    return {"message": "Platform removed successfully"}


@router.get("/get_all_media_types", status_code=status.HTTP_200_OK)
async def get_all_media_types(user: user_dependency, db: db_dependency):
    validate_user(user)

    cache_key = "cache:all_media_types"
    redis = await get_redis_connection()
    try:
        cached_media_types = await redis.get(cache_key)

        if cached_media_types:
            print("\033[92m########## CACHE HIT ##########\033[0m")
            return json.loads(cached_media_types)

        media_types = db.query(SoftwareMediaType).order_by(SoftwareMediaType.name).all()
        media_types_data = [{"id": media_type.id, "name": media_type.name} for media_type in media_types]

        await redis.set(cache_key, json.dumps(media_types_data), ex=3600)

        return media_types_data
    finally:
        await close_redis_connection(redis)


@router.get("/get_media_type_by_name", status_code=status.HTTP_200_OK)
async def get_media_type_by_name(db: db_dependency, user: user_dependency,
                                 media_type_name: str = Query(...,
                                                              description="The name of the media type to be retrieved")):
    validate_user(user)
    media_type = db.query(SoftwareMediaType).filter(
        func.lower(SoftwareMediaType.name) == func.lower(media_type_name)).first()

    if not media_type:
        raise HTTPException(status_code=404, detail="Media type not found")

    return {"id": media_type.id, "name": media_type.name}


@router.post("/add_media_type", status_code=status.HTTP_201_CREATED)
async def add_media_type(
        user: user_dependency,
        db: db_dependency,
        media_type_request: SoftwareMediaTypeRequest
):
    media_type_name_lower = media_type_request.name.lower()

    existing_media_type = db.query(SoftwareMediaType).filter(
        func.lower(SoftwareMediaType.name) == media_type_name_lower).first()
    if existing_media_type:
        raise HTTPException(status_code=400, detail="Media type name already exists")

    media_type_instance = SoftwareMediaType(name=media_type_request.name)
    db.add(media_type_instance)
    try:
        db.commit()

        await invalidate_redis_cache('cache:all_media_types')  # Invalidate cache

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error adding media type")

    db.refresh(media_type_instance)

    actionlog.add_log(
        "New software media type",
        "{} added at {}".format(media_type_instance.name, datetime.now().strftime("%H:%M:%S")),
        user.get('username')
    )

    return {"message": "Media type added successfully", "id": media_type_instance.id, "name": media_type_instance.name}


@router.put("/update_media_type", status_code=status.HTTP_200_OK)
async def update_media_type(db: db_dependency, user: user_dependency,
                            media_type_request: SoftwareMediaTypeRequest,
                            media_type_id: int = Query(..., description="The ID of the media type to be updated")):
    validate_admin(user)

    media_type_name_lower = media_type_request.name.lower()

    existing_media_type = db.query(SoftwareMediaType).filter(
        func.lower(SoftwareMediaType.name) == media_type_name_lower,
        SoftwareMediaType.id != media_type_id
    ).first()

    if existing_media_type:
        raise HTTPException(status_code=400, detail="Media type name already exists with another ID")

    media_type_to_update = db.query(SoftwareMediaType).filter(SoftwareMediaType.id == media_type_id).first()
    if not media_type_to_update:
        raise HTTPException(status_code=404, detail="Media type not found")

    media_type_to_update.name = media_type_request.name
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error updating media type")

    db.refresh(media_type_to_update)

    actionlog.add_log(
        "Updated software media type",
        "{} updated to {} at {}".format(media_type_to_update.name, media_type_request.name,
                                        datetime.now().strftime("%H:%M:%S")),
        user.get('username')
    )

    # Invalidate cache
    await invalidate_redis_cache('cache:all_media_types')

    return {"message": "Media type updated successfully", "id": media_type_to_update.id,
            "name": media_type_to_update.name}


@router.delete("/remove_media_type/{media_type_id}", status_code=status.HTTP_200_OK)
async def remove_media_type(media_type_id: int, db: db_dependency, user: user_dependency):
    validate_admin(user)

    media_type_to_delete = db.query(SoftwareMediaType).filter(SoftwareMediaType.id == media_type_id).first()
    if not media_type_to_delete:
        raise HTTPException(status_code=404, detail="Media type not found")

    associated_software = db.query(Software).filter(Software.media_type_id == media_type_id).all()
    if associated_software:
        associated_software_details = [{"id": software.id, "name": software.name} for software in associated_software]
        return {"message": "Cannot delete media type with associated software items",
                "associated_software": associated_software_details}

    db.delete(media_type_to_delete)
    db.commit()

    await invalidate_redis_cache('cache:all_media_types')

    return {"message": "Media type removed successfully"}


@router.get("/get_all", status_code=status.HTTP_200_OK)
async def get_all_software(db: db_dependency, user: user_dependency):
    validate_user(user)

    redis = await get_redis_connection()
    try:
        cached_software = await redis.get("cache:all_software")
        if cached_software:
            print("\033[92m########## CACHE HIT ##########\033[0m")
            return json.loads(cached_software)

        software_list = (
            db.query(Software)
            .options(joinedload(Software.category), joinedload(Software.publisher),
                     joinedload(Software.developer), joinedload(Software.platform),
                     joinedload(Software.media_type))
            .all()
        )

        result = [format_software_response(software, db) for software in software_list]

        await redis.set("cache:all_software", json.dumps(result), ex=3600)

        return result

    finally:
        await close_redis_connection(redis)


@router.get("/get_by_id/{id}", status_code=status.HTTP_200_OK)
async def get__by_id(db: db_dependency, user: user_dependency, id: int):
    validate_user(user)

    software_model = (
        db.query(Software)
        .options(joinedload(Software.category), joinedload(Software.publisher),
                 joinedload(Software.developer), joinedload(Software.platform),
                 joinedload(Software.media_type))
        .filter(Software.id == id)
        .first()
    )

    if software_model is None:
        raise HTTPException(status_code=404, detail="Software not found")

    response = format_software_response(software_model, db)
    return response


@router.get("/get_all_by_platform")
async def get_all_by_platform(user: user_dependency, db: db_dependency, platform_name: str,
                              exact_match: bool = Query(False, description="Enable exact match for platform name")):
    validate_user(user)

    platforms_query = db.query(SoftwarePlatform)
    if exact_match:
        platforms_query = platforms_query.filter(func.lower(SoftwarePlatform.name) == func.lower(platform_name))
    else:
        platforms_query = platforms_query.filter(SoftwarePlatform.name.ilike(f"%{platform_name}%"))

    platforms = platforms_query.all()
    platform_ids = [platform.id for platform in platforms]

    if not platform_ids:
        raise HTTPException(status_code=404, detail="No platforms found matching the criteria")

    software_records = (
        db.query(Software)
        .options(joinedload(Software.category), joinedload(Software.publisher),
                 joinedload(Software.developer), joinedload(Software.media_type))
        .filter(Software.platform_id.in_(platform_ids))
        .all()
    )

    responses = [format_software_response(software, db) for software in software_records]
    return responses


@router.get("/get_by_barcode/{barcode}", status_code=status.HTTP_200_OK)
async def get_software_by_barcode(db: db_dependency, user: user_dependency, barcode: str):
    validate_user(user)

    software_model = (
        db.query(Software)
        .options(joinedload(Software.category), joinedload(Software.publisher),
                 joinedload(Software.developer), joinedload(Software.platform),
                 joinedload(Software.media_type))
        .filter(Software.barcode == barcode)
        .first()
    )

    if software_model is None:
        raise HTTPException(status_code=404, detail="Software not found with the provided barcode")

    response = format_software_response(software_model, db)
    return response


@router.get("/get_by_name/{name}", status_code=status.HTTP_200_OK)
async def get_software_by_name(user: user_dependency, db: db_dependency, name: str,
                               exact_match: bool = Query(False, description=DESC_FUZZY)):
    validate_user(user)

    query = db.query(Software).options(joinedload(Software.category), joinedload(Software.publisher),
                                       joinedload(Software.developer), joinedload(Software.platform),
                                       joinedload(Software.media_type))
    if exact_match:
        software_models = query.filter(Software.name == name).all()
    else:
        software_models = query.filter(Software.name.ilike(f"%{name}%")).all()

    if not software_models:
        raise HTTPException(status_code=404, detail="Software not found with the specified name")

    responses = [format_software_response(software, db) for software in software_models]
    return responses


@router.get("/get_by_publisher/{publisher_name}", status_code=status.HTTP_200_OK)
async def get_by_publisher(user: user_dependency, db: db_dependency, publisher_name: str,
                           exact_match: bool = Query(False, description=DESC_FUZZY)):
    validate_user(user)

    publishers_query = db.query(SoftwarePublisher)
    if exact_match:
        publishers_query = publishers_query.filter(func.lower(SoftwarePublisher.name) == func.lower(publisher_name))
    else:
        publishers_query = publishers_query.filter(SoftwarePublisher.name.ilike(f"%{publisher_name}%"))

    publishers = publishers_query.all()
    publisher_ids = [publisher.id for publisher in publishers]

    if not publisher_ids:
        raise HTTPException(status_code=404, detail="No publishers found matching the criteria")

    software_records = (
        db.query(Software)
        .options(joinedload(Software.category), joinedload(Software.developer),
                 joinedload(Software.platform), joinedload(Software.media_type))
        .filter(Software.publisher_id.in_(publisher_ids))
        .all()
    )

    responses = [format_software_response(software, db) for software in software_records]
    return responses


@router.get("/get_by_developer/{developer_name}", status_code=status.HTTP_200_OK)
async def get_by_developer(user: user_dependency, db: db_dependency, developer_name: str,
                           exact_match: bool = Query(False, description=DESC_FUZZY)):
    validate_user(user)

    developers_query = db.query(SoftwareDeveloper)
    if exact_match:
        developers_query = developers_query.filter(func.lower(SoftwareDeveloper.name) == func.lower(developer_name))
    else:
        developers_query = developers_query.filter(SoftwareDeveloper.name.ilike(f"%{developer_name}%"))

    developers = developers_query.all()
    developer_ids = [developer.id for developer in developers]

    if not developer_ids:
        raise HTTPException(status_code=404, detail="No developers found matching the criteria")

    software_records = (
        db.query(Software)
        .options(joinedload(Software.category), joinedload(Software.publisher),
                 joinedload(Software.platform), joinedload(Software.media_type))
        .filter(Software.developer_id.in_(developer_ids))
        .all()
    )

    responses = [format_software_response(software, db) for software in software_records]
    return responses


@router.get("/get_by_condition/{condition}", status_code=status.HTTP_200_OK)
async def get_software_by_condition(user: user_dependency, db: db_dependency, condition: str,
                                    exact_match: bool = Query(False, description="Enable exact match for condition")):
    validate_user(user)

    query = db.query(Software).options(joinedload(Software.category), joinedload(Software.publisher),
                                       joinedload(Software.developer), joinedload(Software.platform),
                                       joinedload(Software.media_type))
    if exact_match:
        software_models = query.filter(Software.condition == condition).all()
    else:
        software_models = query.filter(Software.condition.ilike(f"%{condition}%")).all()

    if not software_models:
        raise HTTPException(status_code=404, detail="No software found with the specified condition")

    responses = [format_software_response(software, db) for software in software_models]
    return responses


@router.get("/search/")
async def software_search(
        db: db_dependency,
        user: user_dependency,
        category: str = None,
        name: str = None,
        publisher: str = None,
        developer: str = None,
        condition: str = None,
        platform: str = None,
        limit: int = Query(100, description="Limit the number of results", le=1000)
):
    validate_user(user)

    filters = []
    if category:
        filters.append(Software.category.has(SoftwareCategory.name.ilike(f"%{category}%")))
    if name:
        filters.append(func.lower(Software.name).ilike(f"%{name.lower()}%"))
    if publisher:
        filters.append(Software.publisher.has(SoftwarePublisher.name.ilike(f"%{publisher}%")))
    if developer:
        filters.append(Software.developer.has(SoftwareDeveloper.name.ilike(f"%{developer}%")))
    if platform:
        filters.append(Software.platform.has(SoftwarePlatform.name.ilike(f"%{platform}%")))
    if condition:
        filters.append(func.lower(Software.condition).ilike(f"%{condition.lower()}%"))

    if not filters:
        software_models = db.query(Software).order_by(Software.id.desc()).limit(10).all()
    else:
        software_models = (
            db.query(Software)
            .options(joinedload(Software.category), joinedload(Software.publisher),
                     joinedload(Software.developer), joinedload(Software.platform),
                     joinedload(Software.media_type))
            .filter(*filters)
            .limit(limit)
            .all()
        )

    responses = [format_software_response(software, db) for software in software_models]
    return responses


@router.get("/search_by_tags", status_code=200)
async def search_by_tags(
        db: db_dependency,
        user: user_dependency,
        tags: List[str] = Query(...),
        match_type: str = Query("all", regex="^(all|any)$")
):
    validate_user(user)
    if match_type == "all":
        items = search_all_match(db, tags)
    else:
        items = search_any_match(db, tags)

    return items


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add_software(user: user_dependency, db: db_dependency, software_request: SoftwareRequest):
    validate_admin(user)

    category_instance = db.query(SoftwareCategory).filter_by(id=software_request.category_id).first()
    publisher_instance = db.query(SoftwarePublisher).filter_by(id=software_request.publisher_id).first()
    developer_instance = db.query(SoftwareDeveloper).filter_by(
        id=software_request.developer_id).first() if software_request.developer_id else None
    platform_instance = db.query(SoftwarePlatform).filter_by(
        id=software_request.platform_id).first() if software_request.platform_id else None
    media_type_instance = db.query(SoftwareMediaType).filter_by(
        id=software_request.media_type_id).first() if software_request.media_type_id else None

    if not (category_instance and publisher_instance and (
            software_request.developer_id is None or developer_instance) and (
                    software_request.platform_id is None or platform_instance) and (
                    software_request.media_type_id is None or media_type_instance)):
        raise HTTPException(status_code=400, detail="Category, publisher, developer, platform, or media type not found")

    software_model = Software(
        category_id=software_request.category_id,
        publisher_id=software_request.publisher_id,
        developer_id=software_request.developer_id,
        platform_id=software_request.platform_id,
        media_type_id=software_request.media_type_id,
        name=software_request.name,
        year=software_request.year,
        barcode=software_request.barcode,
        location=software_request.location,
        media_count=software_request.media_count,
        condition=software_request.condition,
        product_key=software_request.product_key,
        photo=software_request.photo,
        multiple_copies=software_request.multiple_copies,
        multicopy_id=software_request.multicopy_id,
        image_backups=software_request.image_backups,
        image_backup_location=software_request.image_backup_location,
        redump_disk_ids=software_request.redump_disk_ids,
        notes=software_request.notes
    )
    db.add(software_model)
    db.flush()

    for tag_name in software_request.tags:
        tag = db.query(Tag).filter(Tag.name == tag_name, Tag.tag_type == TAG_TYPE).first()
        if not tag:
            tag = Tag(name=tag_name, tag_type=TAG_TYPE)
            db.add(tag)
            db.flush()

        existing_association = db.query(SoftwareTag).filter(
            SoftwareTag.software_id == software_model.id,
            SoftwareTag.tag_id == tag.id
        ).first()

        if not existing_association:
            software_tag = SoftwareTag(software_id=software_model.id, tag_id=tag.id)
            db.add(software_tag)

    db.commit()

    await invalidate_redis_cache('cache:all_software')
    await invalidate_redis_cache('cache:tags:*')

    actionlog.add_log(
        "New software added",
        f"{software_request.name} added at {datetime.now().strftime('%H:%M:%S')}",
        user.get('username')
    )

    return {"message": "Software added successfully", "id": software_model.id}


@router.put("/update/{software_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_software(user: user_dependency, db: db_dependency, software_request: SoftwareRequest,
                          software_id: int):
    validate_admin(user)

    software_model = db.query(Software).filter(Software.id == software_id).first()
    if software_model is None:
        raise HTTPException(status_code=404, detail="Software not found")

    category_instance = db.query(SoftwareCategory).filter_by(id=software_request.category_id).first()
    publisher_instance = db.query(SoftwarePublisher).filter_by(id=software_request.publisher_id).first()
    developer_instance = db.query(SoftwareDeveloper).filter_by(
        id=software_request.developer_id).first() if software_request.developer_id else None
    platform_instance = db.query(SoftwarePlatform).filter_by(
        id=software_request.platform_id).first() if software_request.platform_id else None
    media_type_instance = db.query(SoftwareMediaType).filter_by(
        id=software_request.media_type_id).first() if software_request.media_type_id else None

    if not (category_instance and publisher_instance and (software_request.developer_id is None or developer_instance)
            and (software_request.platform_id is None or platform_instance)
            and (software_request.media_type_id is None or media_type_instance)):
        raise HTTPException(status_code=400, detail="Category, publisher, developer, platform, or media type not found")

    software_model.category_id = software_request.category_id
    software_model.publisher_id = software_request.publisher_id
    software_model.developer_id = software_request.developer_id
    software_model.platform_id = software_request.platform_id
    software_model.media_type_id = software_request.media_type_id
    software_model.name = software_request.name
    software_model.year = software_request.year
    software_model.barcode = software_request.barcode
    software_model.location = software_request.location
    software_model.media_count = software_request.media_count
    software_model.condition = software_request.condition
    software_model.product_key = software_request.product_key
    software_model.photo = software_request.photo
    software_model.multiple_copies = software_request.multiple_copies
    software_model.multicopy_id = software_request.multicopy_id
    software_model.image_backups = software_request.image_backups
    software_model.image_backup_location = software_request.image_backup_location
    software_model.redump_disk_ids = software_request.redump_disk_ids
    software_model.notes = software_request.notes

    existing_tag_ids = {tag_id for (tag_id,) in
                        db.query(SoftwareTag.tag_id).filter(SoftwareTag.software_id == software_id)}
    new_tag_ids = set()

    for tag_name in software_request.tags:
        tag = db.query(Tag).filter(Tag.name == tag_name, Tag.tag_type == TAG_TYPE).first()
        if not tag:
            tag = Tag(name=tag_name, tag_type=TAG_TYPE)
            db.add(tag)
            db.flush()
        new_tag_ids.add(tag.id)

    # Add new tags
    for tag_id in new_tag_ids - existing_tag_ids:
        software_tag = SoftwareTag(software_id=software_id, tag_id=tag_id)
        db.add(software_tag)

    # Remove old tags
    for tag_id in existing_tag_ids - new_tag_ids:
        software_tag = db.query(SoftwareTag).filter_by(software_id=software_id, tag_id=tag_id).first()
        if software_tag:
            db.delete(software_tag)

    db.commit()
    await invalidate_redis_cache('cache:all_software')
    await invalidate_redis_cache('cache:tags:*')

    return {"message": "Software updated successfully", "id": software_model.id}


@router.delete("/delete/{software_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_software(user: user_dependency, db: db_dependency, software_id: int):
    validate_user(user)
    validate_admin(user)

    software_model = db.query(Software).filter(Software.id == software_id).first()

    if software_model is None:
        raise HTTPException(status_code=404, detail='Software not found')

    db.query(SoftwareTag).filter(SoftwareTag.software_id == software_id).delete()

    db.delete(software_model)
    db.commit()

    await invalidate_redis_cache('cache:all_software')
    await invalidate_redis_cache('cache:tags:*')

    actionlog.add_log(
        "Software deleted",
        f"Software '{software_model.name}' with ID {software_id} deleted at {datetime.now().strftime('%H:%M:%S')}",
        user.get('username')
    )

    return {"message": "Software deleted successfully"}
