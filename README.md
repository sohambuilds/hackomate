## Hackathon Twin – Backend (Hours 0–2)

This repo now has a FastAPI backend scaffolded with MongoDB integration and CRUD for core entities. It is ready for local run and manual testing.

### What’s implemented
- FastAPI app with CORS and health check
- Environment-driven config via `pydantic-settings`
- MongoDB connection using Motor, with graceful shutdown via lifespan
- Collections and indexes ensured at startup
  - `profiles(email unique)`, `profiles(linkedin_url)`
  - `challenges(title)`
  - `teams(challenge_id)`
- Pydantic v2 models (create/update/read) for:
  - `UserProfile`
  - `Challenge`
  - `Team`
- Routers and endpoints
  - `GET /health`
  - `CRUD /profiles`
  - `CRUD /challenges`
  - `CRUD /teams`
  - Team member management: `POST /teams/{team_id}/members/{user_id}`, `DELETE /teams/{team_id}/members/{user_id}`

### Project structure (relevant to backend)
```
backend/
  config.py          # env-backed settings
  db.py              # Mongo client, DB dependency, lifespan
  main.py            # FastAPI app, CORS, routers
  models.py          # Pydantic v2 schemas
  routers/           # Profiles/Challenges/Teams routers
  utils/indexes.py   # Startup index creation
agents/              # (placeholder)
shared/              # (placeholder)
frontend/            # (placeholder)
```

### Requirements and setup
1) Python deps (using uv):
```bash
uv add fastapi uvicorn motor pydantic-settings python-dotenv
```

2) Environment file (`.env`):
```dotenv
MONGODB_URI=<your-mongodb-uri>
DB_NAME=hackathon_twin
```

3) Run the server:
```bash
uvicorn backend.main:app --reload --port 8000
```

4) Health check:
```bash
curl http://localhost:8000/health
```

### Quick manual testing (cURL)

Base URL: `http://localhost:8000`

#### Profiles
- Create
```bash
curl -sS -X POST http://localhost:8000/profiles \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ada Lovelace",
    "email": "ada@example.com",
    "skills": ["python", "ml", "llm"],
    "location": "London",
    "linkedin_url": "https://linkedin.com/in/adalovelace",
    "status": "scraped"
  }'
```

- List
```bash
curl -sS "http://localhost:8000/profiles?skip=0&limit=20"
```

- Get by id (replace ID)
```bash
curl -sS http://localhost:8000/profiles/ID
```

- Update (partial)
```bash
curl -sS -X PATCH http://localhost:8000/profiles/ID \
  -H "Content-Type: application/json" \
  -d '{"status": "invited"}'
```

- Delete
```bash
curl -sS -X DELETE http://localhost:8000/profiles/ID
```

#### Challenges
- Create
```bash
curl -sS -X POST http://localhost:8000/challenges \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Build LLM-Powered Finance Bot",
    "description": "Create a conversational agent for personal finance insights.",
    "difficulty": "medium",
    "participants": []
  }'
```

- List
```bash
curl -sS "http://localhost:8000/challenges?skip=0&limit=20"
```

- Get by id
```bash
curl -sS http://localhost:8000/challenges/ID
```

- Update
```bash
curl -sS -X PATCH http://localhost:8000/challenges/ID \
  -H "Content-Type: application/json" \
  -d '{"difficulty": "hard"}'
```

- Delete
```bash
curl -sS -X DELETE http://localhost:8000/challenges/ID
```

#### Teams
- Create
```bash
curl -sS -X POST http://localhost:8000/teams \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Vector Wizards",
    "members": [],
    "skills_needed": ["python", "react", "mlops"],
    "challenge_id": null
  }'
```

- List (all or filtered by challenge)
```bash
curl -sS "http://localhost:8000/teams?skip=0&limit=20"
curl -sS "http://localhost:8000/teams?challenge_id=CHALLENGE_ID"
```

- Get by id
```bash
curl -sS http://localhost:8000/teams/ID
```

- Update
```bash
curl -sS -X PATCH http://localhost:8000/teams/ID \
  -H "Content-Type: application/json" \
  -d '{"skills_needed": ["python", "react", "ml"]}'
```

- Add/remove member (replace TEAM_ID and USER_ID)
```bash
curl -sS -X POST http://localhost:8000/teams/TEAM_ID/members/USER_ID
curl -sS -X DELETE http://localhost:8000/teams/TEAM_ID/members/USER_ID
```

- Delete
```bash
curl -sS -X DELETE http://localhost:8000/teams/ID
```

### Notes
- `_id` is stored internally in Mongo; API responses expose it as a string.
- Indexes are created at startup automatically.
- CORS allows `http://localhost:3000` and optional `FRONTEND_ORIGIN`.


