"""Hardware Module"""
import json
from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from starlette import status

from database import get_redis_connection, close_redis_connection, invalidate_redis_cache
from definitions import DESC_EXACT_MATCH, DESC_404, DESC_BRAND_404, DESC_CATEGORY_404
from dependencies import db_dependency, user_dependency
from models import Hardware, HardwareRequest, HardwareCategory, HardwareBrand, HardwareBrandRequest, \
    HardwareCategoryRequest, Tag, HardwareTag, ComponentTypeRequest, ComponentType
from tools import actionlog
from tools.common import validate_user, validate_admin

TAG_TYPE = "hardware"

router = APIRouter(
    prefix='/hardware',
    tags=['hardware']
)


def format_hardware_response(hardware_model, db_session):
    tags = db_session.query(Tag.name).join(HardwareTag).filter(
        HardwareTag.hardware_id == hardware_model.id,
        Tag.tag_type == TAG_TYPE
    ).all()
    tags_list = [tag[0] for tag in tags]

    component_type_name = db_session.query(ComponentType.name).filter(
        ComponentType.id == hardware_model.component_type_id).scalar()

    return {
        "id": hardware_model.id,
        "category": hardware_model.category.name,
        "component_type": component_type_name,
        "brand": hardware_model.brand.name,
        "model": hardware_model.model,
        "condition": hardware_model.condition,
        "quantity": hardware_model.quantity,
        "location": hardware_model.location,
        "is_new": hardware_model.is_new,
        "purchase_date": hardware_model.purchase_date,
        "purchased_from": hardware_model.purchased_from,
        "store_link": hardware_model.store_link,
        "photos": hardware_model.photos,
        "user_manual": hardware_model.user_manual,
        "invoice": hardware_model.invoice,
        "barcode": hardware_model.barcode,
        "repair_history": hardware_model.repair_history,
        "notes": hardware_model.notes,
        "tags": tags_list
    }


def search_any_match(db: db_dependency, tags: List[str]):
    hardware_items = db.query(Hardware). \
        join(HardwareTag). \
        join(Tag). \
        filter(
        Tag.name.in_(tags),
        Tag.tag_type == TAG_TYPE
    ). \
        all()

    return [format_hardware_response(item, db) for item in hardware_items]


def search_all_match(db: db_dependency, tags: List[str]):
    matching_hardware_ids = db.query(HardwareTag.hardware_id) \
        .join(Tag) \
        .filter(
        Tag.name.in_(tags),
        Tag.tag_type == TAG_TYPE
    ) \
        .group_by(HardwareTag.hardware_id) \
        .having(func.count(Tag.id) == len(tags)) \
        .subquery()

    hardware_items = db.query(Hardware) \
        .join(HardwareTag) \
        .filter(Hardware.id == matching_hardware_ids.c.hardware_id) \
        .group_by(Hardware.id) \
        .having(func.count(HardwareTag.tag_id) == len(tags)) \
        .all()

    return [format_hardware_response(item, db) for item in hardware_items]


@router.get("/get_all", status_code=status.HTTP_200_OK)
async def get_all(db: db_dependency, user: user_dependency):
    validate_user(user)

    redis = await get_redis_connection()
    try:
        cached_hardware = await redis.get("cache:all_hardware")
        if cached_hardware:
            print("\033[92m########## CACHE HIT ##########\033[0m")
            return json.loads(cached_hardware)

        hardware_list = (
            db.query(Hardware)
            .options(joinedload(Hardware.brand), joinedload(Hardware.category))
            .all()
        )

        result = [format_hardware_response(hardware, db) for hardware in hardware_list]

        await redis.set("cache:all_hardware", json.dumps(result), ex=3600)

        return result

    finally:
        await close_redis_connection(redis)


@router.get("/get_by_id/", status_code=status.HTTP_200_OK)
async def get_by_id(db: db_dependency, user: user_dependency, hw_id: int):
    validate_user(user)

    hardware_model = (
        db.query(Hardware)
        .options(joinedload(Hardware.brand), joinedload(Hardware.category))
        .filter(Hardware.id == hw_id)
        .first()
    )

    if hardware_model is None:
        raise HTTPException(status_code=404, detail=DESC_404)

    response = format_hardware_response(hardware_model, db)
    return response


@router.get("/get_by_barcode/{barcode}", status_code=status.HTTP_200_OK)
async def get_by_barcode(db: db_dependency, user: user_dependency, barcode: str):
    validate_user(user)

    hardware_model = (
        db.query(Hardware)
        .options(joinedload(Hardware.brand), joinedload(Hardware.category))
        .filter(Hardware.barcode == barcode)
        .first()
    )

    if hardware_model is None:
        raise HTTPException(status_code=404, detail=DESC_404)

    response = format_hardware_response(hardware_model, db)
    return response


@router.get("/get_by_model/{model}")
async def get_by_model(user: user_dependency, db: db_dependency, model: str,
                       exact_match: bool = Query(False, description=DESC_EXACT_MATCH)):
    validate_user(user)

    hardware_models = (
        db.query(Hardware)
        .options(joinedload(Hardware.brand), joinedload(Hardware.category))
        .filter(Hardware.model == model if exact_match else Hardware.model.ilike(f"%{model}%"))
        .all()
    )

    if not hardware_models:
        raise HTTPException(status_code=404, detail=DESC_404)

    responses = [format_hardware_response(hardware_model, db) for hardware_model in hardware_models]

    return responses


@router.get("/get_by_brand/{brand}")
async def get_by_brand(user: user_dependency, db: db_dependency, brand: str,
                       exact_match: bool = Query(False, description=DESC_EXACT_MATCH)):
    validate_user(user)

    hardware_models = (
        db.query(Hardware)
        .join(Hardware.brand)
        .join(Hardware.category)
        .options(joinedload(Hardware.brand), joinedload(Hardware.category))
        .filter(HardwareBrand.name == brand if exact_match else HardwareBrand.name.ilike(f"%{brand}%"))
        .all()
    )

    if not hardware_models:
        raise HTTPException(status_code=404, detail=DESC_404)

    responses = [format_hardware_response(hardware_model, db) for hardware_model in hardware_models]

    return responses


@router.get("/get_by_category/{category}")
async def get_by_category(user: user_dependency, db: db_dependency, category: str,
                          exact_match: bool = Query(False, description=DESC_EXACT_MATCH)):
    validate_user(user)

    hardware_models = (
        db.query(Hardware)
        .join(Hardware.category)
        .options(joinedload(Hardware.brand), joinedload(Hardware.category))
        .filter(HardwareCategory.name == category if exact_match else HardwareCategory.name.ilike(f"%{category}%"))
        .all()
    )

    if not hardware_models:
        raise HTTPException(status_code=404, detail=DESC_404)

    responses = [format_hardware_response(hardware_model, db) for hardware_model in hardware_models]

    return responses


# Hard limit 1000 - maybe too low. I need to check
@router.get("/search/")
async def hardware_search(
        db: db_dependency,
        user: user_dependency,
        category: str = None,
        brand: str = None,
        model: str = None,
        condition: str = None,
        purchased_from: str = None,
        is_new: bool = None,
        component_type: str = None,
        limit: int = Query(100, description="Limit the number of results", le=1000)
):
    validate_user(user)

    filters = []
    if category:
        filters.append(Hardware.category.has(HardwareCategory.name.ilike(f"%{category}%")))
    if brand:
        filters.append(Hardware.brand.has(HardwareBrand.name.ilike(f"%{brand}%")))
    if model:
        filters.append(func.lower(Hardware.model).ilike(f"%{model.lower()}%"))
    if condition:
        filters.append(func.lower(Hardware.condition).ilike(f"%{condition.lower()}%"))
    if purchased_from:
        filters.append(func.lower(Hardware.purchased_from).ilike(f"%{purchased_from.lower()}%"))
    if is_new is not None:
        filters.append(Hardware.is_new == is_new)
    if component_type:
        filters.append(Hardware.component_type.has(ComponentType.name.ilike(f"%{component_type}%")))

    if not filters:
        hardware_models = db.query(Hardware).order_by(Hardware.id.desc()).limit(10).all()
    else:
        hardware_models = (
            db.query(Hardware)
            .options(joinedload(Hardware.brand), joinedload(Hardware.category), joinedload(Hardware.component_type))
            .filter(*filters)
            .limit(limit)
            .all()
        )

    responses = [format_hardware_response(hardware_model, db) for hardware_model in hardware_models]
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


@router.get("/get_all_brands", status_code=status.HTTP_200_OK)
async def get_all_brands(user: user_dependency, db: db_dependency):
    validate_user(user)

    cache_key = "cache:all_brands"
    redis = await get_redis_connection()
    try:
        cached_brands = await redis.get(cache_key)

        if cached_brands:
            print("\033[92m########## CACHE HIT ##########\033[0m")
            return json.loads(cached_brands)

        brands = db.query(HardwareBrand).order_by(HardwareBrand.name).all()
        brands_data = [{"id": brand.id, "name": brand.name} for brand in brands]

        await redis.set(cache_key, json.dumps(brands_data), ex=3600)

        return brands_data
    finally:
        await close_redis_connection(redis)


@router.get("/get_brand_by_name", status_code=status.HTTP_200_OK)
async def get_brand_by_name(db: db_dependency, user: user_dependency,
                            brand_name: str = Query(..., description="The name of the brand to be retrieved"), ):
    validate_user(user)
    brand = db.query(HardwareBrand).filter(func.lower(HardwareBrand.name) == func.lower(brand_name)).first()

    if not brand:
        raise HTTPException(status_code=404, detail=DESC_BRAND_404)

    return {"id": brand.id, "name": brand.name}


@router.post("/add_brand", status_code=status.HTTP_201_CREATED)
async def add_hardware_brand(
        user: user_dependency,
        db: db_dependency,
        hardware_brand: HardwareBrandRequest
):
    brand_name_lower = hardware_brand.name.lower()

    existing_brand = db.query(HardwareBrand).filter(func.lower(HardwareBrand.name) == brand_name_lower).first()
    if existing_brand:
        raise HTTPException(status_code=400, detail="Brand name already exists")

    brand_instance = HardwareBrand(name=hardware_brand.name)
    db.add(brand_instance)
    try:
        db.commit()

        await invalidate_redis_cache('cache:all_brands')

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error adding brand")

    db.refresh(brand_instance)

    actionlog.add_log(
        "New hardware brand",
        "{} added at {}".format(brand_instance.name, datetime.now().strftime("%H:%M:%S")),
        user.get('username')
    )

    return {"message": "Brand added successfully", "id": brand_instance.id, "name": brand_instance.name}


@router.put("/update_brand", status_code=status.HTTP_200_OK)
async def update_brand(db: db_dependency, user: user_dependency,
                       hardware_brand: HardwareBrandRequest,
                       brand_id: int = Query(..., description="The ID of the brand to be updated"),

                       ):
    validate_admin(user)

    brand_name_lower = hardware_brand.name.lower()

    existing_brand = db.query(HardwareBrand).filter(
        func.lower(HardwareBrand.name) == brand_name_lower,
        HardwareBrand.id != brand_id
    ).first()

    if existing_brand:
        raise HTTPException(status_code=400, detail="Brand name already exists with another ID")

    brand_to_update = db.query(HardwareBrand).filter(HardwareBrand.id == brand_id).first()
    if not brand_to_update:
        raise HTTPException(status_code=404, detail=DESC_BRAND_404)

    brand_to_update.name = hardware_brand.name
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error updating brand")

    db.refresh(brand_to_update)

    actionlog.add_log(
        "Updated hardware brand",
        "{} updated to {} at {}".format(brand_to_update.name, hardware_brand.name, datetime.now().strftime("%H:%M:%S")),
        user.get('username')
    )

    # Invalidate cache
    await invalidate_redis_cache('cache:all_brands')

    return {"message": "Brand updated successfully", "id": brand_to_update.id, "name": brand_to_update.name}


@router.delete("/remove_brand/{brand_id}", status_code=status.HTTP_200_OK)
async def remove_brand(brand_id: int, db: db_dependency, user: user_dependency):
    validate_admin(user)

    brand_to_delete = db.query(HardwareBrand).filter(HardwareBrand.id == brand_id).first()
    if not brand_to_delete:
        raise HTTPException(status_code=404, detail=DESC_BRAND_404)

    if db.query(Hardware).filter(Hardware.brand_id == brand_id).first():
        raise HTTPException(status_code=400, detail="Cannot delete brand with associated hardware items")

    db.delete(brand_to_delete)
    db.commit()

    # Invalidate cache
    await invalidate_redis_cache('cache:all_brands')

    return {"message": "Brand removed successfully"}


@router.get("/get_all_categories", status_code=status.HTTP_200_OK)
async def get_all_categories(user: user_dependency, db: db_dependency):
    validate_user(user)

    cache_key = "cache:all_categories"
    redis = await get_redis_connection()
    try:
        cached_categories = await redis.get(cache_key)
        if cached_categories:
            print("\033[92m########## CACHE HIT ##########\033[0m")
            return json.loads(cached_categories)
    finally:
        await close_redis_connection(redis)

    categories = db.query(HardwareCategory).order_by(HardwareCategory.name).all()
    categories_list = [{"id": category.id, "name": category.name} for category in categories]

    redis = await get_redis_connection()
    try:
        await redis.set(cache_key, json.dumps(categories_list), ex=3600)
    finally:
        await close_redis_connection(redis)

    return categories_list


@router.get("/get_category_by_name", status_code=status.HTTP_200_OK)
async def get_category_by_name(db: db_dependency, user: user_dependency,
                               category_name: str = Query(..., description="The name of the category to be retrieved")
                               ):
    validate_user(user)
    category = db.query(HardwareCategory).filter(func.lower(HardwareCategory.name) == func.lower(category_name)).first()

    if not category:
        raise HTTPException(status_code=404, detail=DESC_CATEGORY_404)

    return {"id": category.id, "name": category.name}


@router.post("/add_category", status_code=status.HTTP_201_CREATED)
async def add_hardware_category(
        user: user_dependency,
        db: db_dependency,
        hardware_category: HardwareCategoryRequest
):
    category_instance = HardwareCategory(name=hardware_category.name)
    db.add(category_instance)
    db.commit()
    db.refresh(category_instance)

    actionlog.add_log(
        "New hardware category",
        "{} added at {}".format(category_instance.name, datetime.now().strftime("%H:%M:%S")),
        user.get('username')
    )

    # Invalidate cache
    await invalidate_redis_cache('cache:all_categories')

    return status.HTTP_201_CREATED


@router.put("/update_category", status_code=status.HTTP_200_OK)
async def update_category(db: db_dependency,
                          user: user_dependency,
                          hardware_category: HardwareCategoryRequest,
                          category_id: int = Query(..., description="The ID of the category to be updated"),

                          ):
    validate_admin(user)

    existing_category = db.query(HardwareCategory).filter(
        func.lower(HardwareCategory.name) == hardware_category.name.lower(),
        HardwareCategory.id != category_id
    ).first()

    if existing_category:
        raise HTTPException(status_code=400, detail="Category name already exists with another ID")

    category_to_update = db.query(HardwareCategory).filter(HardwareCategory.id == category_id).first()
    if not category_to_update:
        raise HTTPException(status_code=404, detail=DESC_CATEGORY_404)

    category_to_update.name = hardware_category.name
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error updating category")

    db.refresh(category_to_update)

    actionlog.add_log(
        "Updated hardware category",
        "{} updated to {} at {}".format(category_to_update.name, hardware_category.name,
                                        datetime.now().strftime("%H:%M:%S")),
        user.get('username')
    )
    # Invalidate cache
    await invalidate_redis_cache('cache:all_categories')

    return {"message": "Category updated successfully", "id": category_to_update.id, "name": category_to_update.name}


@router.delete("/remove_category/{category_id}", status_code=status.HTTP_200_OK)
async def remove_category(category_id: int, db: db_dependency, user: user_dependency):
    validate_admin(user)

    category_to_delete = db.query(HardwareCategory).filter(HardwareCategory.id == category_id).first()
    if not category_to_delete:
        raise HTTPException(status_code=404, detail=DESC_CATEGORY_404)

    if db.query(Hardware).filter(Hardware.category_id == category_id).first():
        raise HTTPException(status_code=400, detail="Cannot delete category with associated hardware items")

    db.delete(category_to_delete)
    db.commit()

    # Invalidate cache
    await invalidate_redis_cache('cache:all_categories')

    return {"message": "Category removed successfully"}


@router.get("/component_types/by_hardware_category/{hardware_category_id}")
async def get_component_types_by_hardware_category(hardware_category_id: int, db: db_dependency, user: user_dependency):
    validate_admin(user)

    redis = await get_redis_connection()
    try:
        cache_key = f"cache:component_types_{hardware_category_id}"
        cached_component_types = await redis.get(cache_key)
        if cached_component_types:
            print("\033[92m########## CACHE HIT ##########\033[0m")
            return json.loads(cached_component_types)

        component_types = db.query(ComponentType).filter(
            ComponentType.hardware_category_id == hardware_category_id
        ).order_by(ComponentType.name).all()

        result = [{"id": this_type.id, "name": this_type.name} for this_type in component_types]
        await redis.set(cache_key, json.dumps(result), ex=3600)

        return result
    finally:
        await close_redis_connection(redis)


@router.post("/component_type/add")
async def add_component_type(request: ComponentTypeRequest, db: db_dependency, user: user_dependency):
    validate_admin(user)
    hardware_category = db.query(HardwareCategory).filter(HardwareCategory.id == request.hardware_category_id).first()
    if not hardware_category:
        raise HTTPException(status_code=404, detail="Hardware category not found")

    component_type = ComponentType(
        name=request.name,
        hardware_category_id=request.hardware_category_id
    )
    db.add(component_type)
    db.commit()
    await invalidate_redis_cache("cache:component_types_*")
    db.refresh(component_type)
    return {"id": component_type.id, "name": component_type.name}


@router.put("/component_type/update/{component_type_id}")
async def update_component_type(component_type_id: int, request: ComponentTypeRequest, db: db_dependency,
                                user: user_dependency):
    validate_admin(user)
    component_type = db.query(ComponentType).filter(ComponentType.id == component_type_id).first()
    if not component_type:
        raise HTTPException(status_code=404, detail="Component type not found")

    hardware_category = db.query(HardwareCategory).filter(HardwareCategory.id == request.hardware_category_id).first()
    if not hardware_category:
        raise HTTPException(status_code=404, detail="Hardware category not found")

    component_type.name = request.name
    component_type.hardware_category_id = request.hardware_category_id
    db.commit()
    await invalidate_redis_cache("cache:component_types_*")
    return {"id": component_type.id, "name": component_type.name}


@router.delete("/component_type/delete/{component_type_id}")
async def delete_component_type(component_type_id: int, db: db_dependency, user: user_dependency):
    validate_admin(user)
    component_type = db.query(ComponentType).filter(ComponentType.id == component_type_id).first()
    if not component_type:
        raise HTTPException(status_code=404, detail="Component type not found")

    # Check if the component type is associated with any hardware
    associated_hardware = db.query(Hardware).filter(Hardware.component_type_id == component_type_id).first()
    if associated_hardware:
        raise HTTPException(status_code=400, detail="Cannot delete component type associated with existing hardware")

    db.delete(component_type)
    db.commit()
    await invalidate_redis_cache("cache:component_types_*")
    return {"message": "Component type deleted successfully"}


@router.delete("/component_types/delete_by_category/{hardware_category_id}", status_code=200)
async def delete_component_types_by_category(hardware_category_id: int, db: db_dependency, user: user_dependency,
                                             delete_category: bool = False):
    validate_admin(user)

    hardware_items = db.query(Hardware).join(ComponentType).filter(
        ComponentType.hardware_category_id == hardware_category_id).all()
    if hardware_items:
        items_details = [{"id": item.id, "name": item.model, "component_type": item.component_type.name} for item in
                         hardware_items]
        return {"message": "Cannot delete category as it's being used by hardware items", "items": items_details}

    component_types_to_delete = db.query(ComponentType).filter(
        ComponentType.hardware_category_id == hardware_category_id).all()

    for component_type in component_types_to_delete:
        db.delete(component_type)

    if delete_category:
        category_to_delete = db.query(HardwareCategory).filter(HardwareCategory.id == hardware_category_id).first()
        if category_to_delete:
            db.delete(category_to_delete)
            await invalidate_redis_cache('cache:all_categories')
        else:
            raise HTTPException(status_code=404, detail="Hardware category not found")

    db.commit()

    await invalidate_redis_cache("cache:component_types_*")

    return {"message": "Deletion successful"}


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add_hardware(user: user_dependency, db: db_dependency, hardware_request: HardwareRequest):
    validate_user(user)
    validate_admin(user)

    category_instance = db.query(HardwareCategory).filter_by(id=hardware_request.category_id).first()
    brand_instance = db.query(HardwareBrand).filter_by(id=hardware_request.brand_id).first()
    component_type_instance = db.query(ComponentType).filter_by(id=hardware_request.component_type_id).first()

    if not (category_instance and brand_instance and component_type_instance):
        raise HTTPException(status_code=400, detail="Category, brand, or component type not found")

    hardware_model = Hardware(
        category_id=hardware_request.category_id,
        component_type_id=hardware_request.component_type_id,
        brand_id=hardware_request.brand_id,
        model=hardware_request.model,
        condition=hardware_request.condition,
        quantity=hardware_request.quantity,
        location=hardware_request.location,
        is_new=hardware_request.is_new,
        purchase_date=hardware_request.purchase_date,
        purchased_from=hardware_request.purchased_from,
        store_link=hardware_request.store_link,
        photos=hardware_request.photos,
        user_manual=hardware_request.user_manual,
        invoice=hardware_request.invoice,
        barcode=hardware_request.barcode,
        repair_history=hardware_request.repair_history,
        notes=hardware_request.notes
    )
    db.add(hardware_model)
    db.flush()

    for tag_name in hardware_request.tags:
        tag = db.query(Tag).filter(Tag.name == tag_name, Tag.tag_type == TAG_TYPE).first()
        if not tag:
            tag = Tag(name=tag_name, tag_type=TAG_TYPE)
            db.add(tag)
            db.flush()

        existing_association = db.query(HardwareTag).filter(
            HardwareTag.hardware_id == hardware_model.id,
            HardwareTag.tag_id == tag.id
        ).first()

        if not existing_association:
            hardware_tag = HardwareTag(hardware_id=hardware_model.id, tag_id=tag.id)
            db.add(hardware_tag)

    db.commit()

    await invalidate_redis_cache('cache:all_hardware')
    await invalidate_redis_cache('cache:tags:*')

    actionlog.add_log(
        "New hardware added",
        f"Hardware {hardware_request.model} (Brand ID: {hardware_request.brand_id}, Component Type ID: "
        f"{hardware_request.component_type_id}) with ID {hardware_model.id} "
        f"added at {datetime.now().strftime('%H:%M:%S')}",
        user.get('username')
    )

    return {"message": "Hardware added successfully", "id": hardware_model.id}


@router.put("/update/{hardware_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_hardware(user: user_dependency, db: db_dependency, hardware_request: HardwareRequest,
                          hardware_id: int):
    validate_user(user)
    validate_admin(user)

    hardware_model = db.query(Hardware).filter(Hardware.id == hardware_id).first()

    if hardware_model is None:
        raise HTTPException(status_code=404, detail="Not found")

    category_instance = db.query(HardwareCategory).filter_by(id=hardware_request.category_id).first()
    brand_instance = db.query(HardwareBrand).filter_by(id=hardware_request.brand_id).first()
    component_type_instance = db.query(ComponentType).filter_by(id=hardware_request.component_type_id).first()

    if not (category_instance and brand_instance and component_type_instance):
        raise HTTPException(status_code=400, detail="Category, brand, or component type not found")

    hardware_model.category_id = hardware_request.category_id
    hardware_model.brand_id = hardware_request.brand_id
    hardware_model.component_type_id = hardware_request.component_type_id
    hardware_model.model = hardware_request.model
    hardware_model.condition = hardware_request.condition
    hardware_model.quantity = hardware_request.quantity
    hardware_model.location = hardware_request.location
    hardware_model.is_new = hardware_request.is_new
    hardware_model.purchase_date = hardware_request.purchase_date
    hardware_model.purchased_from = hardware_request.purchased_from
    hardware_model.store_link = hardware_request.store_link
    hardware_model.photos = hardware_request.photos
    hardware_model.user_manual = hardware_request.user_manual
    hardware_model.invoice = hardware_request.invoice
    hardware_model.barcode = hardware_request.barcode
    hardware_model.repair_history = hardware_request.repair_history
    hardware_model.notes = hardware_request.notes

    # Update tags
    existing_tag_ids = {tag_id for (tag_id,) in
                        db.query(HardwareTag.tag_id).filter(HardwareTag.hardware_id == hardware_id)}
    new_tag_ids = set()

    for tag_name in hardware_request.tags:
        tag = db.query(Tag).filter(Tag.name == tag_name, Tag.tag_type == TAG_TYPE).first()
        if not tag:
            tag = Tag(name=tag_name, tag_type=TAG_TYPE)
            db.add(tag)
            db.flush()
        new_tag_ids.add(tag.id)

    for tag_id in new_tag_ids - existing_tag_ids:
        hardware_tag = HardwareTag(hardware_id=hardware_id, tag_id=tag_id)
        db.add(hardware_tag)

    #
    for tag_id in existing_tag_ids - new_tag_ids:
        hardware_tag = db.query(HardwareTag).filter_by(hardware_id=hardware_id, tag_id=tag_id).first()
        if hardware_tag:
            db.delete(hardware_tag)

    db.commit()
    await invalidate_redis_cache('cache:all_hardware')
    await invalidate_redis_cache('cache:tags:*')
    return {"message": "Hardware updated successfully", "id": hardware_model.id}


@router.delete("/delete/{hardware_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_hardware(user: user_dependency, db: db_dependency, hardware_id: int):
    validate_user(user)
    validate_admin(user)

    hardware_model = db.query(Hardware).filter(Hardware.id == hardware_id).first()

    if hardware_model is None:
        raise HTTPException(status_code=404, detail='Not Found')

    # Deletes related entries in the hardware_tags table (feels like a good idea for now)
    db.query(HardwareTag).filter(HardwareTag.hardware_id == hardware_id).delete()

    db.delete(hardware_model)
    db.commit()

    await invalidate_redis_cache('cache:all_hardware')
    await invalidate_redis_cache('cache:tags:*')

    actionlog.add_log(
        "Hardware deleted",
        "Hardware with ID {} deleted at {}".format(
            hardware_id, datetime.now().strftime("%H:%M:%S")
        ),
        user.get('username')
    )

    return {"message": "Hardware deleted successfully"}
