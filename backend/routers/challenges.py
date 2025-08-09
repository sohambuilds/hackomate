from typing import List, Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument

from ..db import get_database
from ..models import (
    ChallengeCreate,
    ChallengeRead,
    ChallengeUpdate,
)


router = APIRouter(prefix="/challenges", tags=["Challenges"])


def _normalize_id(document: Optional[dict]) -> Optional[dict]:
    if not document:
        return document
    doc = dict(document)
    if "_id" in doc and not isinstance(doc["_id"], str):
        doc["_id"] = str(doc["_id"])  # ensure CORS-safe JSON primitives
    # ensure participants exists and is a list
    doc.setdefault("participants", [])
    return doc


@router.get("/", response_model=List[ChallengeRead])
async def list_challenges(
    db: AsyncIOMotorDatabase = Depends(get_database),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
):
    cursor = db["challenges"].find({}, projection=None).skip(skip).limit(limit)
    results: List[ChallengeRead] = []
    async for doc in cursor:
        results.append(ChallengeRead.model_validate(_normalize_id(doc)))
    return results


@router.get("/{challenge_id}", response_model=ChallengeRead)
async def get_challenge(
    challenge_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    doc = await db["challenges"].find_one({"_id": challenge_id})
    if not doc and ObjectId.is_valid(challenge_id):
        doc = await db["challenges"].find_one({"_id": ObjectId(challenge_id)})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")
    return ChallengeRead.model_validate(_normalize_id(doc))


@router.post("/", response_model=ChallengeRead, status_code=status.HTTP_201_CREATED)
async def create_challenge(
    payload: ChallengeCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    doc = payload.model_dump()
    doc.setdefault("participants", [])
    doc.setdefault("_id", str(ObjectId()))
    await db["challenges"].insert_one(doc)
    return ChallengeRead.model_validate(_normalize_id(doc))


@router.patch("/{challenge_id}", response_model=ChallengeRead)
async def update_challenge(
    challenge_id: str,
    payload: ChallengeUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
    if not updates:
        return await get_challenge(challenge_id, db)

    doc = await db["challenges"].find_one_and_update(
        {"_id": challenge_id},
        {"$set": updates},
        return_document=ReturnDocument.AFTER,
    )
    if not doc and ObjectId.is_valid(challenge_id):
        doc = await db["challenges"].find_one_and_update(
            {"_id": ObjectId(challenge_id)},
            {"$set": updates},
            return_document=ReturnDocument.AFTER,
        )
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")
    return ChallengeRead.model_validate(_normalize_id(doc))


@router.delete("/{challenge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_challenge(
    challenge_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    result = await db["challenges"].delete_one({"_id": challenge_id})
    if result.deleted_count == 0 and ObjectId.is_valid(challenge_id):
        result = await db["challenges"].delete_one({"_id": ObjectId(challenge_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")
    return None


