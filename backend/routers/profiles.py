from typing import List, Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument

from ..db import get_database
from ..models import (
    UserProfileCreate,
    UserProfileRead,
    UserProfileUpdate,
)


router = APIRouter(prefix="/profiles", tags=["Profiles"])


def _normalize_id(document: Optional[dict]) -> Optional[dict]:
    if not document:
        return document
    doc = dict(document)
    if "_id" in doc and not isinstance(doc["_id"], str):
        doc["_id"] = str(doc["_id"])  # ensure CORS-safe JSON primitives
    return doc


@router.get("/", response_model=List[UserProfileRead])
async def list_profiles(
    db: AsyncIOMotorDatabase = Depends(get_database),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
):
    cursor = db["profiles"].find({}, projection=None).skip(skip).limit(limit)
    results: List[UserProfileRead] = []
    async for doc in cursor:
        results.append(UserProfileRead.model_validate(_normalize_id(doc)))
    return results


@router.get("/{profile_id}", response_model=UserProfileRead)
async def get_profile(
    profile_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    doc = await db["profiles"].find_one({"_id": profile_id})
    if not doc:
        # attempt ObjectId fallback if documents were inserted with ObjectId
        if ObjectId.is_valid(profile_id):
            doc = await db["profiles"].find_one({"_id": ObjectId(profile_id)})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return UserProfileRead.model_validate(_normalize_id(doc))


@router.post("/", response_model=UserProfileRead, status_code=status.HTTP_201_CREATED)
async def create_profile(
    payload: UserProfileCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    # Generate string _id server-side for consistency
    doc = payload.model_dump()
    doc.setdefault("_id", str(ObjectId()))
    await db["profiles"].insert_one(doc)
    return UserProfileRead.model_validate(_normalize_id(doc))


@router.patch("/{profile_id}", response_model=UserProfileRead)
async def update_profile(
    profile_id: str,
    payload: UserProfileUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
    if not updates:
        # nothing to update; return current doc if exists
        return await get_profile(profile_id, db)

    doc = await db["profiles"].find_one_and_update(
        {"_id": profile_id},
        {"$set": updates},
        return_document=ReturnDocument.AFTER,
    )
    if not doc and ObjectId.is_valid(profile_id):
        doc = await db["profiles"].find_one_and_update(
            {"_id": ObjectId(profile_id)},
            {"$set": updates},
            return_document=ReturnDocument.AFTER,
        )
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return UserProfileRead.model_validate(_normalize_id(doc))


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    profile_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    result = await db["profiles"].delete_one({"_id": profile_id})
    if result.deleted_count == 0 and ObjectId.is_valid(profile_id):
        result = await db["profiles"].delete_one({"_id": ObjectId(profile_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return None


