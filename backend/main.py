import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import lifespan
from .routers.challenges import router as challenges_router
from .routers.profiles import router as profiles_router
from .routers.teams import router as teams_router


def _allowed_origins() -> list[str]:
    origins = ["http://localhost:3000"]
    frontend_origin = os.getenv("FRONTEND_ORIGIN")
    if frontend_origin:
        origins.append(frontend_origin)
    return origins


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(profiles_router)
app.include_router(challenges_router)
app.include_router(teams_router)


