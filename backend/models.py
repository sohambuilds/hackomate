from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


# -----------------------------
# Shared helpers / base configs
# -----------------------------
class MongoReadModel(BaseModel):
    """Base model for MongoDB read responses using `_id` as a string.

    The `id` attribute is exposed in JSON as `_id`.
    """

    id: str = Field(alias="_id")

    model_config = {
        "populate_by_name": True,
        "str_strip_whitespace": True,
    }


# -----------------------------
# UserProfile
# -----------------------------
class UserProfileBase(BaseModel):
    name: str
    email: EmailStr
    skills: List[str]
    location: str
    linkedin_url: str
    status: str

    model_config = {
        "str_strip_whitespace": True,
    }


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    skills: Optional[List[str]] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    status: Optional[str] = None

    model_config = {
        "str_strip_whitespace": True,
    }


class UserProfileRead(MongoReadModel, UserProfileBase):
    # Allow documents without email/linkedin_url (e.g., scraped profiles) to validate on read
    email: Optional[EmailStr] = None
    linkedin_url: Optional[str] = None


# -----------------------------
# Challenge
# -----------------------------
class ChallengeBase(BaseModel):
    title: str
    description: str
    difficulty: str
    participants: List[str] = Field(default_factory=list)

    model_config = {
        "str_strip_whitespace": True,
    }


class ChallengeCreate(ChallengeBase):
    pass


class ChallengeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[str] = None
    participants: Optional[List[str]] = None

    model_config = {
        "str_strip_whitespace": True,
    }


class ChallengeRead(MongoReadModel, ChallengeBase):
    pass


# -----------------------------
# Team
# -----------------------------
class TeamBase(BaseModel):
    name: str
    members: List[str] = Field(default_factory=list)
    skills_needed: List[str]
    challenge_id: Optional[str] = None

    model_config = {
        "str_strip_whitespace": True,
    }


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    members: Optional[List[str]] = None
    skills_needed: Optional[List[str]] = None
    challenge_id: Optional[str] = None

    model_config = {
        "str_strip_whitespace": True,
    }


class TeamRead(MongoReadModel, TeamBase):
    pass


# -----------------------------
# Hackathon
# -----------------------------
class AgendaItem(BaseModel):
    time: Optional[str] = None
    title: str
    description: Optional[str] = None

    model_config = {
        "str_strip_whitespace": True,
    }


class Workshop(BaseModel):
    title: str
    description: Optional[str] = None

    model_config = {
        "str_strip_whitespace": True,
    }


class ProblemStatement(BaseModel):
    title: str
    description: str
    difficulty: Optional[str] = None
    skills_required: List[str] = Field(default_factory=list)

    model_config = {
        "str_strip_whitespace": True,
    }


class HackathonPlan(BaseModel):
    target_audience: Optional[str] = None
    location: Optional[str] = None
    dates: Optional[str] = None
    workshops: List[Workshop] = Field(default_factory=list)
    agenda: List[AgendaItem] = Field(default_factory=list)
    problem_statements: List[ProblemStatement] = Field(default_factory=list)

    model_config = {
        "str_strip_whitespace": True,
    }


class HackathonBase(BaseModel):
    topic: str
    description: Optional[str] = None
    target_audience: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: str = "planned"
    plan: Optional[HackathonPlan] = None

    model_config = {
        "str_strip_whitespace": True,
    }


class HackathonDraft(BaseModel):
    topic: str
    description: Optional[str] = None
    target_audience: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    model_config = {
        "str_strip_whitespace": True,
    }


class HackathonCreate(HackathonBase):
    pass


class HackathonUpdate(BaseModel):
    topic: Optional[str] = None
    description: Optional[str] = None
    target_audience: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: Optional[str] = None
    plan: Optional[HackathonPlan] = None

    model_config = {
        "str_strip_whitespace": True,
    }


class HackathonRead(MongoReadModel, HackathonBase):
    pass


__all__ = [
    # UserProfile
    "UserProfileBase",
    "UserProfileCreate",
    "UserProfileUpdate",
    "UserProfileRead",
    # Challenge
    "ChallengeBase",
    "ChallengeCreate",
    "ChallengeUpdate",
    "ChallengeRead",
    # Team
    "TeamBase",
    "TeamCreate",
    "TeamUpdate",
    "TeamRead",
    # Hackathon
    "AgendaItem",
    "Workshop",
    "ProblemStatement",
    "HackathonPlan",
    "HackathonBase",
    "HackathonDraft",
    "HackathonCreate",
    "HackathonUpdate",
    "HackathonRead",
]


