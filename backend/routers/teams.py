from typing import List, Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument

from ..db import get_database
from ..models import TeamCreate, TeamRead, TeamUpdate


router = APIRouter(prefix="/teams", tags=["Teams"])


def _normalize_id(document: Optional[dict]) -> Optional[dict]:
    if not document:
        return document
    doc = dict(document)
    if "_id" in doc and not isinstance(doc["_id"], str):
        doc["_id"] = str(doc["_id"])  # ensure CORS-safe JSON primitives
    doc.setdefault("members", [])
    return doc


@router.get("/", response_model=List[TeamRead])
async def list_teams(
    db: AsyncIOMotorDatabase = Depends(get_database),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    challenge_id: Optional[str] = Query(default=None),
):
    query = {}
    if challenge_id is not None:
        query["challenge_id"] = challenge_id
    cursor = db["teams"].find(query).skip(skip).limit(limit)
    results: List[TeamRead] = []
    async for doc in cursor:
        results.append(TeamRead.model_validate(_normalize_id(doc)))
    return results


@router.get("/{team_id}", response_model=TeamRead)
async def get_team(
    team_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    doc = await db["teams"].find_one({"_id": team_id})
    if not doc and ObjectId.is_valid(team_id):
        doc = await db["teams"].find_one({"_id": ObjectId(team_id)})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    return TeamRead.model_validate(_normalize_id(doc))


@router.post("/", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
async def create_team(
    payload: TeamCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    doc = payload.model_dump()
    doc.setdefault("members", [])
    doc.setdefault("_id", str(ObjectId()))
    await db["teams"].insert_one(doc)
    return TeamRead.model_validate(_normalize_id(doc))


@router.patch("/{team_id}", response_model=TeamRead)
async def update_team(
    team_id: str,
    payload: TeamUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
    if not updates:
        return await get_team(team_id, db)

    doc = await db["teams"].find_one_and_update(
        {"_id": team_id},
        {"$set": updates},
        return_document=ReturnDocument.AFTER,
    )
    if not doc and ObjectId.is_valid(team_id):
        doc = await db["teams"].find_one_and_update(
            {"_id": ObjectId(team_id)},
            {"$set": updates},
            return_document=ReturnDocument.AFTER,
        )
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    return TeamRead.model_validate(_normalize_id(doc))


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(
    team_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    result = await db["teams"].delete_one({"_id": team_id})
    if result.deleted_count == 0 and ObjectId.is_valid(team_id):
        result = await db["teams"].delete_one({"_id": ObjectId(team_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    return None


@router.post("/{team_id}/members/{user_id}", response_model=TeamRead)
async def add_team_member(
    team_id: str,
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    doc = await db["teams"].find_one_and_update(
        {"_id": team_id},
        {"$addToSet": {"members": user_id}},
        return_document=ReturnDocument.AFTER,
    )
    if not doc and ObjectId.is_valid(team_id):
        doc = await db["teams"].find_one_and_update(
            {"_id": ObjectId(team_id)},
            {"$addToSet": {"members": user_id}},
            return_document=ReturnDocument.AFTER,
        )
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    return TeamRead.model_validate(_normalize_id(doc))


@router.delete("/{team_id}/members/{user_id}", response_model=TeamRead)
async def remove_team_member(
    team_id: str,
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    doc = await db["teams"].find_one_and_update(
        {"_id": team_id},
        {"$pull": {"members": user_id}},
        return_document=ReturnDocument.AFTER,
    )
    if not doc and ObjectId.is_valid(team_id):
        doc = await db["teams"].find_one_and_update(
            {"_id": ObjectId(team_id)},
            {"$pull": {"members": user_id}},
            return_document=ReturnDocument.AFTER,
        )
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    return TeamRead.model_validate(_normalize_id(doc))


