"""
Message generator using Gemini (free tier).

Generates personalized invitation messages for recently created/scraped
profiles and stores them into `outreach_messages` collection.

CLI:
  python -m agents.message_generator --limit 10 --model gemini-1.5-flash
"""

from __future__ import annotations

import argparse
import asyncio
import os
from datetime import datetime, timezone
from typing import List, Optional

import google.generativeai as genai
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv


INVITE_PROMPT = (
    """
Write a personalized hackathon invitation for:
Name: {name}
Skills: {skills}
Location: {location}

Make it exciting, mention AI focus, include hackathon benefits.
Keep under 150 words and professional tone.
"""
    .strip()
)


async def _fetch_recent_profiles(db, limit: int) -> List[dict]:
    cursor = (
        db["profiles"]
        .find({}, projection=None)
        .sort("_id", -1)
        .limit(limit)
    )
    docs: List[dict] = []
    async for d in cursor:
        docs.append(d)
    return docs


async def _store_message(db, profile_id: str, message: str) -> None:
    await db["outreach_messages"].insert_one(
        {
            "profile_id": profile_id,
            "channel": "email",
            "message": message,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "generated",
        }
    )


def _configure_gemini(api_key: Optional[str]) -> None:
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is required for Gemini API")
    genai.configure(api_key=api_key)


async def generate_message_for_profile(model_name: str, profile: dict) -> str:
    model = genai.GenerativeModel(model_name)
    prompt = INVITE_PROMPT.format(
        name=profile.get("name", "there"),
        skills=", ".join(profile.get("skills", [])),
        location=profile.get("location", ""),
    )
    resp = await asyncio.to_thread(model.generate_content, prompt)
    return resp.text.strip() if hasattr(resp, "text") else str(resp)


async def main_async(limit: int, model_name: str) -> None:
    from backend.config import get_settings

    # Load env from .env at repo root if present
    load_dotenv()
    settings = get_settings()
    _configure_gemini(os.getenv("GOOGLE_API_KEY"))

    client = AsyncIOMotorClient(settings.mongodb_uri)
    try:
        db = client[settings.db_name]
        profiles = await _fetch_recent_profiles(db, limit)
        for p in profiles:
            text = await generate_message_for_profile(model_name, p)
            await _store_message(db, str(p.get("_id")), text)
        print(f"Generated {len(profiles)} messages using {model_name}.")
    finally:
        client.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Gemini message generator")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--model", type=str, default="gemini-2.0-flash")
    args = parser.parse_args()
    # Ensure .env is loaded for CLI executions as well
    load_dotenv()
    asyncio.run(main_async(args.limit, args.model))


if __name__ == "__main__":
    main()

