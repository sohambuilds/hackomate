from motor.motor_asyncio import AsyncIOMotorDatabase


async def _ensure_profiles_email_unique_index(db: AsyncIOMotorDatabase) -> None:
    """Ensure unique email index with a partial filter; replace conflicting index if needed."""
    col = db["profiles"]
    desired_name = "uniq_email"
    desired_key = {"email": 1}
    desired_unique = True
    desired_partial = {"email": {"$exists": True}}

    existing = await col.list_indexes().to_list(length=None)
    existing_named = next((i for i in existing if i.get("name") == desired_name), None)

    def _keys_equal(a: dict, b: dict) -> bool:
        return list(a.items()) == list(b.items())

    needs_replace = False
    if existing_named is not None:
        key_ok = _keys_equal(existing_named.get("key", {}), desired_key)
        unique_ok = bool(existing_named.get("unique", False)) == desired_unique
        partial_ok = existing_named.get("partialFilterExpression") == desired_partial
        if not (key_ok and unique_ok and partial_ok):
            needs_replace = True

    if needs_replace:
        await col.drop_index(desired_name)

    if existing_named is None or needs_replace:
        await col.create_index(
            list(desired_key.items()),
            name=desired_name,
            unique=desired_unique,
            partialFilterExpression=desired_partial,
        )


async def ensure_indexes(db: AsyncIOMotorDatabase) -> None:
    """Create required indexes if they don't already exist."""
    # profiles
    await _ensure_profiles_email_unique_index(db)
    await db["profiles"].create_index("linkedin_url", name="idx_linkedin_url")

    # challenges
    await db["challenges"].create_index("title", name="idx_title")

    # teams
    await db["teams"].create_index("challenge_id", name="idx_challenge_id")

    # hackathons
    await db["hackathons"].create_index("topic", name="idx_hack_topic")


__all__ = ["ensure_indexes"]


