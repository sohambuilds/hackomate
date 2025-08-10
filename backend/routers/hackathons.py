from typing import List, Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument

from ..db import get_database
from ..models import (
    HackathonCreate,
    HackathonDraft,
    HackathonRead,
    HackathonUpdate,
    HackathonPlan,
)

router = APIRouter(prefix="/hackathons", tags=["Hackathons"])


def _normalize_id(document: Optional[dict]) -> Optional[dict]:
    if not document:
        return document
    doc = dict(document)
    if "_id" in doc and not isinstance(doc["_id"], str):
        doc["_id"] = str(doc["_id"])  # ensure CORS-safe JSON primitives
    return doc


@router.get("/", response_model=List[HackathonRead])
async def list_hackathons(
    db: AsyncIOMotorDatabase = Depends(get_database),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
):
    cursor = db["hackathons"].find({}, projection=None).skip(skip).limit(limit)
    results: List[HackathonRead] = []
    async for doc in cursor:
        results.append(HackathonRead.model_validate(_normalize_id(doc)))
    return results


@router.get("/{hackathon_id}", response_model=HackathonRead)
async def get_hackathon(
    hackathon_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    doc = await db["hackathons"].find_one({"_id": hackathon_id})
    if not doc and ObjectId.is_valid(hackathon_id):
        doc = await db["hackathons"].find_one({"_id": ObjectId(hackathon_id)})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hackathon not found")
    return HackathonRead.model_validate(_normalize_id(doc))


@router.post("/", response_model=HackathonRead, status_code=status.HTTP_201_CREATED)
async def create_hackathon(
    payload: HackathonCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    doc = payload.model_dump()
    doc.setdefault("_id", str(ObjectId()))
    await db["hackathons"].insert_one(doc)
    return HackathonRead.model_validate(_normalize_id(doc))


@router.patch("/{hackathon_id}", response_model=HackathonRead)
async def update_hackathon(
    hackathon_id: str,
    payload: HackathonUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
    if not updates:
        return await get_hackathon(hackathon_id, db)

    doc = await db["hackathons"].find_one_and_update(
        {"_id": hackathon_id},
        {"$set": updates},
        return_document=ReturnDocument.AFTER,
    )
    if not doc and ObjectId.is_valid(hackathon_id):
        doc = await db["hackathons"].find_one_and_update(
            {"_id": ObjectId(hackathon_id)},
            {"$set": updates},
            return_document=ReturnDocument.AFTER,
        )
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hackathon not found")
    return HackathonRead.model_validate(_normalize_id(doc))


@router.delete("/{hackathon_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hackathon(
    hackathon_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    result = await db["hackathons"].delete_one({"_id": hackathon_id})
    if result.deleted_count == 0 and ObjectId.is_valid(hackathon_id):
        result = await db["hackathons"].delete_one({"_id": ObjectId(hackathon_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hackathon not found")
    return None


# ---------- Plan generation via Gemini ----------
import os
import asyncio
from dotenv import load_dotenv
import google.generativeai as genai
from agents.outreach_agent import send_email_via_gmail


def _configure_gemini(api_key: Optional[str]) -> None:
    if not api_key:
        raise HTTPException(status_code=400, detail="GOOGLE_API_KEY is required for plan generation")
    genai.configure(api_key=api_key)


PLAN_PROMPT = (
    """
You are an expert hackathon organizer. Given the inputs, produce a structured JSON plan with the following shape:
{
  "target_audience": string,
  "location": string,
  "dates": string,
  "workshops": [ {"title": string, "description": string} ],
  "agenda": [ {"time": string, "title": string, "description": string} ]
}
Inputs:
- Topic: {topic}
- Description: {description}
- Target audience: {audience}
- Location: {location}
- Dates: {dates}

Output only JSON, no extra text.
"""
).strip()


@router.post("/generate-plan", response_model=HackathonRead)
async def generate_plan(
    draft: HackathonDraft,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Generate a hackathon plan with Gemini and persist a new hackathon document."""
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    _configure_gemini(api_key)

    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = PLAN_PROMPT.format(
        topic=draft.topic,
        description=draft.description or "",
        audience=draft.target_audience or "",
        location=draft.location or "",
        dates=((draft.start_date or "") + (" - " + draft.end_date if draft.end_date else "")),
    )

    # Run blocking call in thread
    resp = await asyncio.to_thread(model.generate_content, prompt)
    text = resp.text if hasattr(resp, "text") else str(resp)
    import json
    try:
        plan_dict = json.loads(text)
    except Exception:
        raise HTTPException(status_code=502, detail="Failed to parse plan JSON from Gemini")

    # Compose hackathon doc and persist
    doc = {
        "_id": str(ObjectId()),
        "topic": draft.topic,
        "description": draft.description,
        "target_audience": draft.target_audience or plan_dict.get("target_audience"),
        "location": draft.location or plan_dict.get("location"),
        "start_date": draft.start_date,
        "end_date": draft.end_date,
        "status": "planned",
        "plan": plan_dict,
    }
    await db["hackathons"].insert_one(doc)
    return HackathonRead.model_validate(_normalize_id(doc))


# ---------- Invitations ----------
@router.post("/{hackathon_id}/invite", response_model=int)
async def invite_profiles(
    hackathon_id: str,
    limit: int = Query(20, ge=1, le=200),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Create outreach messages referencing this hackathon for recent profiles.

    Returns the number of messages generated.
    """
    # Check hackathon exists
    hack = await db["hackathons"].find_one({"_id": hackathon_id})
    if not hack and ObjectId.is_valid(hackathon_id):
        hack = await db["hackathons"].find_one({"_id": ObjectId(hackathon_id)})
    if not hack:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hackathon not found")

    # Fetch recent profiles
    cursor = db["profiles"].find({}).sort("_id", -1).limit(limit)
    profiles: List[dict] = []
    async for p in cursor:
        profiles.append(p)

    # Create outreach messages tied to this hackathon
    created = 0
    for p in profiles:
        await db["outreach_messages"].insert_one(
            {
                "profile_id": str(p.get("_id")),
                "hackathon_id": str(hack.get("_id")),
                "channel": "email",
                "message": f"You're invited to our hackathon on '{hack.get('topic', '')}' at {hack.get('location', '')}. Join us!",
                "status": "generated",
            }
        )
        created += 1

    return created


@router.post("/{hackathon_id}/send-emails", response_model=int)
async def send_emails_for_hackathon(
    hackathon_id: str,
    limit: int = Query(20, ge=1, le=200),
    dry_run: bool = Query(True),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """Send email invites for messages generated for this hackathon.

    Returns number of emails attempted (sent or dry-run). Requires Gmail env vars.
    """
    # Validate hackathon exists
    hack = await db["hackathons"].find_one({"_id": hackathon_id})
    if not hack and ObjectId.is_valid(hackathon_id):
        hack = await db["hackathons"].find_one({"_id": ObjectId(hackathon_id)})
    if not hack:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hackathon not found")

    # Fetch pending messages for this hackathon
    cursor = (
        db["outreach_messages"]
        .find({"status": "generated", "hackathon_id": hackathon_id})
        .sort("_id", 1)
        .limit(limit)
    )
    messages: List[dict] = []
    async for m in cursor:
        messages.append(m)

    from datetime import datetime, timezone

    sent = 0
    for m in messages:
        profile = await db["profiles"].find_one({"_id": m.get("profile_id")})
        to_email = (profile or {}).get("email", "")
        status_value = "skipped"
        error: Optional[str] = None
        if to_email:
            if dry_run:
                status_value = "dry_run"
                sent += 1
            else:
                try:
                    send_email_via_gmail(
                        to_email=to_email,
                        subject=f"You're invited: {hack.get('topic', 'Hackathon')}",
                        message=m.get("message", "You're invited!"),
                    )
                    status_value = "sent"
                    sent += 1
                except Exception as e:  # pragma: no cover - network side effects
                    status_value = "error"
                    error = str(e)

        await db["outreach_logs"].insert_one(
            {
                "profile_id": m.get("profile_id"),
                "hackathon_id": hackathon_id,
                "channel": "email",
                "status": status_value,
                "error": error,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        await db["outreach_messages"].update_one(
            {"_id": m["_id"]},
            {"$set": {"status": status_value}},
        )

    return sent


