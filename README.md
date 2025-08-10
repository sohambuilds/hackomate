## Hackathon Twin – Backend (Progress Hours 0–4)

This repo now has a FastAPI backend scaffolded with MongoDB integration and CRUD for core entities (Hours 0–2), plus the Recruitment Twin (free version) agents wired for message generation and email outreach (Hours 2–4).

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
  - `Hackathons`:
    - CRUD `/hackathons`
    - Generate plan (Gemini) and create: `POST /hackathons/generate-plan`
    - Create invites (messages): `POST /hackathons/{hackathon_id}/invite?limit=20`
    - Send emails (Gmail SMTP): `POST /hackathons/{hackathon_id}/send-emails?limit=20&dry_run=true`

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

### Requirements and setup (backend)
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
# Simple deployment (production)
uv run main.py

# Development with reload
uv run uvicorn backend.main:app --reload --port 8000

# Alternative using script entry point
uv run serve
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
curl -sS -X POST http://localhost:8000/challenges/ \
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
curl -sS "http://localhost:8000/challenges/?skip=0&limit=20"
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

#### Hackathons
- Generate plan (and create)
```bash
curl -sS -X POST http://localhost:8000/hackathons/generate-plan \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "AI for Finance",
    "description": "Build tools for personal finance insights.",
    "target_audience": "Developers, data scientists",
    "location": "London",
    "start_date": "2025-10-10",
    "end_date": "2025-10-12"
  }'
```

- List
```bash
curl -sS "http://localhost:8000/hackathons/?limit=20"
```

- Create invites for recent profiles
```bash
curl -sS -X POST "http://localhost:8000/hackathons/HACK_ID/invite?limit=10"
```

- Send emails (dry run by default)
```bash
curl -sS -X POST "http://localhost:8000/hackathons/HACK_ID/send-emails?limit=10&dry_run=true"
```

### Notes
- `_id` is stored internally in Mongo; API responses expose it as a string.
- Indexes are created at startup automatically.
- CORS allows `http://localhost:3000` and optional `FRONTEND_ORIGIN`.

---

## Recruitment Twin (Hours 2–4, Free Version)

We implemented the recruitment pipeline without paid services (Gemini + Gmail SMTP).

### Install additional dependencies
```bash
uv add google-generativeai beautifulsoup4 selenium tenacity
```

### Environment variables (.env)
```dotenv
# Backend
MONGODB_URI=<your-mongodb-uri>
DB_NAME=hackathon_twin

# Gemini (free tier)
GOOGLE_API_KEY=<your_gemini_api_key>

# Gmail SMTP (App Password required)
GMAIL_USER=<your_email@gmail.com>
GMAIL_APP_PASSWORD=<your_app_password>
```

Gmail setup:
1) Enable 2‑Step Verification in your Google Account
2) Create an App Password for "Mail"
3) Use it as `GMAIL_APP_PASSWORD`

### Agents
- `python -m agents.recruitment_agent --query "AI developer" --limit 5`
  - Headless Selenium + BeautifulSoup (best‑effort) and GitHub user search supplement; falls back to seeded realistic profiles if needed
  - Writes to `profiles` collection (`status` = `scraped`)
- `python -m agents.message_generator --limit 5 --model gemini-1.5-flash`
  - Uses Gemini to produce personalized invites; stores in `outreach_messages`
- `python -m agents.outreach_agent --limit 3 --dry-run`
  - Sends (or simulates) emails via Gmail SMTP; logs results in `outreach_logs`

### End‑to‑end quick test
```bash
# Run API
uv run main.py

# 1) Collect profiles
python -m agents.recruitment_agent --query "AI developer" --limit 5

# 2) Generate messages (Gemini)
python -m agents.message_generator --limit 5

# 3) Outreach (dry run first)
python -m agents.outreach_agent --limit 3 --dry-run

# 4) Verify via API
curl -sS "http://localhost:8000/profiles/?limit=10"
```

### Known limitations (for later improvement)
- Headless Selenium yields few real links in some Windows setups. Mitigations in place:
  - GitHub Search API supplement (set `GITHUB_TOKEN` for higher limits)
  - Fallback seed generation to keep demo flow unblocked
  - Relative URL normalization and duplicate filtering
  - Chrome flags (`--disable-gpu`, `--no-sandbox`) set; further tuning may be needed


---

## Frontend (Hours 4–8) – Design Plan and Feature Map

We are building a premium, black/white, translucent “glass” interface inspired by Apple’s design language.

### Design system
- Colors: deep black background, soft white text, muted gray, bright white accents
- Surfaces: translucent glass panels with blur, subtle borders, soft elevated shadows
- Typography: Geist Sans/Mono, generous letter‑spacing for headings
- Layout: centered content (`max-width: 1200px`), sticky glass navbar, large section paddings
- Interactions: clear focus rings, smooth hover/active states, skeleton loaders

### Core UI components (to build and reuse)
- Card (glass surface container)
- SectionHeader (title + description)
- Stat (compact metric with label)
- Table/List (rows with subtle dividers)
- Badge/Chip (small highlight labels)
- Button (glass variant + subtle hover)
- Skeleton (loading shimmer/blocks)

### Pages and features (accessible via navbar)
- Dashboard (/dashboard)
  - Key stats: total profiles, invites generated/sent (basic), teams, challenges
  - Recent activity preview (latest profiles/challenges/teams)
  - Quick actions: “Find AI Developers”, “Generate Challenge”, “Send Outreach (dry)”
- Community (/community)
  - Real‑time/polled feed: joins, team formations, challenge posts
  - Member directory (basic list, search later)
- Challenges (/challenges)
  - Challenge board listing: title, difficulty, participants count
  - Detail view (later): description, requirements, criteria
- Teams (/teams)
  - Team discovery: list with filters (by challenge)
  - Join/Create flows (UI scaffolding first)

### Data integration plan
- Use `NEXT_PUBLIC_API_BASE_URL` to call the FastAPI backend
- Phase 1: client components fetch lists (first page) and show counts/rows
- Phase 2: add server actions or dedicated backend count endpoints for accurate metrics
- Phase 3: WebSocket/polling for community feed

### Implementation roadmap
1) Design tokens, glass utilities, navbar, home CTA – done
2) Scaffolding pages: dashboard, community, challenges, teams – next
3) Build core UI components (Card, SectionHeader, Stat, Skeleton, Table) – next
4) Wire API calls for lists; show loaders and errors – next
5) Add filters/search; refine layouts and empty states – later
6) Charts for dashboard (Chart.js) – later


