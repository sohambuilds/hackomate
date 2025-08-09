"""
Recruitment agent (free version placeholder).

Attempts to run a headless Selenium search (best-effort), parse with BeautifulSoup,
and persist discovered profiles into MongoDB. If scraping fails or yields
insufficient results, falls back to synthesizing simple profiles based on the
query terms to keep the demo flow unblocked.

CLI:
  python -m agents.recruitment_agent --query "AI developer" --limit 10
"""

from __future__ import annotations

import argparse
import asyncio
import random
import re
from dataclasses import dataclass
from typing import Iterable, List

from bs4 import BeautifulSoup
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from motor.motor_asyncio import AsyncIOMotorClient

# Selenium (optional, may fail in constrained environments)
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    SELENIUM_AVAILABLE = True
except Exception:
    SELENIUM_AVAILABLE = False


# -----------------------------
# Data structures
# -----------------------------
@dataclass
class Profile:
    name: str
    email: str
    skills: List[str]
    location: str
    linkedin_url: str
    status: str = "scraped"


# -----------------------------
# Helpers
# -----------------------------
def _random_name() -> str:
    first = random.choice([
        "Alex", "Jordan", "Taylor", "Morgan", "Casey", "Sam", "Jamie", "Riley",
        "Avery", "Dakota", "Reese", "Rowan",
    ])
    last = random.choice([
        "Smith", "Johnson", "Lee", "Chen", "Patel", "Garcia", "Brown", "Davis",
        "Wilson", "Martinez",
    ])
    return f"{first} {last}"


def _fallback_profiles(query: str, limit: int) -> List[Profile]:
    keywords = [w for w in re.split(r"\W+", query) if w]
    possible_skills = list({
        "Python", "Machine Learning", "Deep Learning", "NLP", "LLMs", "LangChain",
        "TensorFlow", "PyTorch", "Data Engineering", "React", "TypeScript",
    } | set(keywords))
    cities = [
        "San Francisco, CA", "New York, NY", "London, UK", "Berlin, DE",
        "Bengaluru, IN", "Toronto, CA",
    ]
    profiles: List[Profile] = []
    for i in range(limit):
        name = _random_name()
        skills = random.sample(possible_skills, k=min(3, len(possible_skills)))
        loc = random.choice(cities)
        profiles.append(
            Profile(
                name=name,
                email="",  # unknown from scraping; omit at insert time to avoid unique index
                skills=skills,
                location=loc,
                # leave empty to allow insertion uniqueness by _id; we'll drop falsy at insert
                linkedin_url="",
            )
        )
    return profiles


def _run_selenium_search(query: str, limit: int) -> List[Profile]:
    if not SELENIUM_AVAILABLE:
        return []
    try:
        options = ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(options=options)
    except Exception:
        return []

    try:
        # Best-effort generic search (not LinkedIn directly to avoid blocks)
        from urllib.parse import quote_plus, urljoin

        base_url = "https://duckduckgo.com/"
        driver.get(f"{base_url}?q={quote_plus(query + ' developer profile')}")
        driver.implicitly_wait(3)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        links = [a.get("href") for a in soup.select("a[href]")]
        links = [l for l in links if isinstance(l, str)]
        # normalize to absolute URLs; drop javascript/mailto
        normalized: List[str] = []
        for l in links:
            if l.startswith("javascript:") or l.startswith("mailto:"):
                continue
            if l.startswith("/"):
                l = urljoin(base_url, l)
            normalized.append(l)

        extracted: List[Profile] = []
        seen = set()
        for href in normalized:
            if len(extracted) >= limit:
                break
            # Simple heuristics for demo; real logic would parse target pages
            if any(k in href.lower() for k in ["github", "portfolio", "blog", "linkedin"]):
                if href in seen:
                    continue
                seen.add(href)
                extracted.append(
                    Profile(
                        name=_random_name(),
                        email="",
                        skills=["Python", "Machine Learning", "LLMs"],
                        location=random.choice(["Remote", "London, UK", "New York, NY"]),
                        linkedin_url=href,
                    )
                )
        return extracted
    finally:
        try:
            driver.quit()
        except Exception:
            pass


def _fetch_github_users(query: str, limit: int) -> List[Profile]:
    """Fetch developer profiles from GitHub Search API (unauthenticated, low volume).

    Uses only one API call to stay within rate limits. Falls back silently on errors.
    """
    try:
        q = f"{query} in:bio type:user"
        params = {
            "q": q,
            "per_page": min(30, max(1, limit)),
            "page": 1,
        }
        url = f"https://api.github.com/search/users?{urlencode(params)}"
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "hackathon-twin-agent",
        }
        # Optional token for higher rate limits
        import os

        token = os.getenv("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"

        req = Request(url, headers=headers)
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        items = data.get("items", [])
        results: List[Profile] = []
        for it in items[:limit]:
            html_url = it.get("html_url", "")
            login = it.get("login", "Developer")
            results.append(
                Profile(
                    name=login,
                    email="",
                    skills=["Python", "Machine Learning", "LLMs"],
                    location="",
                    linkedin_url=html_url or "",
                )
            )
        return results
    except Exception:
        return []


async def _upsert_profiles(client: AsyncIOMotorClient, db_name: str, profiles: Iterable[Profile]) -> int:
    db = client[db_name]
    col = db["profiles"]
    inserted = 0
    async for session in _aiter([(p.__dict__) for p in profiles]):
        doc = dict(session)
        # Generate a simple string id (ObjectId string) for consistency
        from bson import ObjectId

        doc.setdefault("_id", str(ObjectId()))
        # Drop empty email to avoid triggering partial unique index conditions
        if not doc.get("email"):
            doc.pop("email", None)
        if not doc.get("linkedin_url"):
            doc.pop("linkedin_url", None)
        # Deduplicate by linkedin_url if present
        query = {"linkedin_url": doc.get("linkedin_url")} if doc.get("linkedin_url") else {"_id": doc["_id"]}
        result = await col.update_one(query, {"$setOnInsert": doc}, upsert=True)
        if result.upserted_id is not None:
            inserted += 1
    return inserted


async def _aiter(items: Iterable[dict]):
    for item in items:
        yield item


async def main_async(query: str, limit: int) -> None:
    from backend.config import get_settings

    settings = get_settings()
    client = AsyncIOMotorClient(settings.mongodb_uri)
    try:
        candidates = _run_selenium_search(query, limit)
        # If Selenium finds too few, try GitHub API to supplement real profiles
        if len(candidates) < limit:
            gh_needed = limit - len(candidates)
            github_candidates = _fetch_github_users(query, gh_needed)
            candidates.extend(github_candidates)
        scraped_count = len(candidates)
        if scraped_count < limit:
            fallback_needed = limit - scraped_count
            fallback = _fallback_profiles(query, fallback_needed)
            candidates.extend(fallback)
        inserted = await _upsert_profiles(client, settings.db_name, candidates)
        fallback_count = max(0, len(candidates) - scraped_count)
        print(f"Scraped: {scraped_count}, Fallback: {fallback_count}, Inserted: {inserted}")
    finally:
        client.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Recruitment agent (free version)")
    parser.add_argument("--query", required=True, help="Search query, e.g. 'AI developer'")
    parser.add_argument("--limit", type=int, default=10, help="Max profiles to collect")
    args = parser.parse_args()
    asyncio.run(main_async(args.query, args.limit))


if __name__ == "__main__":
    main()


