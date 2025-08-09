from motor.motor_asyncio import AsyncIOMotorDatabase


async def ensure_indexes(db: AsyncIOMotorDatabase) -> None:
    """Create required indexes if they don't already exist."""
    # profiles
    await db["profiles"].create_index("email", name="uniq_email", unique=True)
    await db["profiles"].create_index("linkedin_url", name="idx_linkedin_url")

    # challenges
    await db["challenges"].create_index("title", name="idx_title")

    # teams
    await db["teams"].create_index("challenge_id", name="idx_challenge_id")


__all__ = ["ensure_indexes"]


