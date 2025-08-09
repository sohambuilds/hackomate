"""
Outreach agent (free, email-only via Gmail SMTP).

Reads pending messages from `outreach_messages` and sends via email, logging
results to `outreach_logs`. Supports dry-run to avoid sending.

CLI:
  python -m agents.outreach_agent --limit 5 --dry-run
"""

from __future__ import annotations

import argparse
import asyncio
import os
from datetime import datetime, timezone
from typing import List

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv


async def _fetch_pending_messages(db, limit: int) -> List[dict]:
    cursor = (
        db["outreach_messages"]
        .find({"status": "generated"})
        .sort("_id", 1)
        .limit(limit)
    )
    docs: List[dict] = []
    async for d in cursor:
        docs.append(d)
    return docs


def send_email_via_gmail(to_email: str, subject: str, message: str) -> None:
    user = os.getenv("GMAIL_USER")
    app_password = os.getenv("GMAIL_APP_PASSWORD")
    if not user or not app_password:
        raise RuntimeError("GMAIL_USER and GMAIL_APP_PASSWORD are required for sending emails.")

    msg = MIMEMultipart()
    msg["From"] = user
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(user, app_password)
        server.sendmail(user, [to_email], msg.as_string())


async def process_outreach_messages(limit: int, dry_run: bool) -> int:
    from backend.config import get_settings

    # load env vars from .env if present
    load_dotenv()
    settings = get_settings()
    client = AsyncIOMotorClient(settings.mongodb_uri)
    try:
        db = client[settings.db_name]
        messages = await _fetch_pending_messages(db, limit)
        sent = 0
        for m in messages:
            # Attempt to find profile email to send to
            profile = await db["profiles"].find_one({"_id": m.get("profile_id")})
            to_email = (profile or {}).get("email", "")

            status = "skipped"
            error = None
            if to_email:
                if dry_run:
                    status = "dry_run"
                else:
                    try:
                        send_email_via_gmail(
                            to_email=to_email,
                            subject="You're invited to our AI hackathon!",
                            message=m.get("message", ""),
                        )
                        status = "sent"
                        sent += 1
                    except Exception as e:
                        status = "error"
                        error = str(e)

            await db["outreach_logs"].insert_one(
                {
                    "profile_id": m.get("profile_id"),
                    "channel": "email",
                    "status": status,
                    "error": error,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            )

            # Update message status
            await db["outreach_messages"].update_one(
                {"_id": m["_id"]},
                {"$set": {"status": status}},
            )
        return sent
    finally:
        client.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Outreach agent (email-only)")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    load_dotenv()
    sent = asyncio.run(process_outreach_messages(args.limit, args.dry_run))
    print(f"Processed {args.limit} messages; sent: {sent}; dry_run={args.dry_run}")


if __name__ == "__main__":
    main()

