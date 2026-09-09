# SkillPilot — Personalized Course Pathways

An agentic AI course-pathway coach powered by **IBM Granite** (watsonx.ai) with a **React** frontend, **Node/Express** backend, and **IBM Cloudant** persistence. Deployed as a native agent on **watsonx Orchestrate**.

---

## Architecture

```
┌─────────────────────────────────┐
│   React + Tailwind Frontend     │  http://localhost:3000
│   (Chat UI + Roadmap Dashboard) │
└──────────────┬──────────────────┘
               │ REST
┌──────────────▼──────────────────┐
│   Node/Express Backend API      │  http://localhost:3001
│   /api/onboarding               │
│   /api/roadmap                  │
│   /api/progress                 │
│   /api/chat                     │
└──────┬───────────────┬──────────┘
       │ IBM Granite   │ Cloudant
       ▼               ▼
  watsonx.ai       IBM Cloud
  (Granite-4-H)    (NoSQL DB)

           ┌──────────────────────────┐
           │  watsonx Orchestrate     │
           │  Native Agent: skillpilot│
           │  Tools:                  │
           │  • onboard_student       │
           │  • generate_roadmap      │
           │  • update_progress       │
           │  • get_progress          │
           │  • chat_with_skillpilot  │
           └──────────────────────────┘
```

---

## Quick Start

### 1. Backend

```bash
cd skillpilot/backend
cp .env.example .env       # fill in CLOUDANT_URL and CLOUDANT_APIKEY
npm install
npm run dev                # starts on http://localhost:3001
```

**Required `.env` values:**

| Variable | Value |
|---|---|
| `WATSONX_API_KEY` | `ao9qLDOFvi_lV13f0PzSQfPkqVp40v7Y_JlMGCQVJX_5` |
| `WATSONX_PROJECT_ID` | `2c02dcad-09a1-4ba9-9b3d-d29f964ee048` |
| `WATSONX_MODEL_ID` | `ibm/granite-4-h-small` |
| `CLOUDANT_URL` | Your IBM Cloudant instance URL |
| `CLOUDANT_APIKEY` | Your IBM Cloudant API key |

### 2. Frontend

```bash
cd skillpilot/frontend
npm install
npm start                  # starts on http://localhost:3000
```

### 3. watsonx Orchestrate Tools & Agent

The agent `skillpilot` and all 5 tools are already deployed to the WXO instance.

To point the WXO tools at your running backend, set the environment variable:

```
SKILLPILOT_BACKEND_URL=https://your-public-backend.example.com
```

> **Note:** WXO tool sandboxes run in IBM Cloud and cannot reach `localhost`. You must deploy the backend to a public URL (e.g. IBM Code Engine, Cloud Foundry, Railway, Render) and update `SKILLPILOT_BACKEND_URL` in each tool.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/onboarding/start` | Start/continue student onboarding |
| GET  | `/api/onboarding/profile/:userId` | Get student profile |
| POST | `/api/roadmap/generate` | Generate week-by-week roadmap |
| GET  | `/api/roadmap/:userId` | Get saved roadmap |
| POST | `/api/progress/update` | Update module status + recalculate |
| GET  | `/api/progress/:userId` | Get current progress |
| POST | `/api/chat/message` | Chat with SkillPilot coach |
| GET  | `/api/chat/history/:convId` | Get conversation history |

---

## WXO Agent Tools

| Tool | Purpose |
|------|---------|
| `onboard_student` | Identify career goal via Granite |
| `generate_roadmap` | Create week-by-week roadmap via Granite |
| `update_progress` | Log module completion + AI recalculation |
| `get_progress` | Retrieve current progress summary |
| `chat_with_skillpilot` | Context-aware coaching chat |

---

## Conversation Flow

1. Agent greets → asks if student has a goal
2. If no goal → asks interest area + skill level → calls `onboard_student` → recommends job role
3. Presents: timeline, required skills, tools/tech, project + cert suggestion
4. Asks timeline & hours/day → calls `generate_roadmap`
5. If unrealistic → presents `adjustmentNote` + offers alternative
6. Displays week-by-week roadmap
7. Check-ins: student marks modules → `update_progress` → AI recalculates

---

## IBM Cloud Services Used

- **IBM watsonx.ai** — IBM Granite-4-H-Small for all AI reasoning
- **IBM Cloudant** — NoSQL persistence for profiles, roadmaps, progress, conversations
- **watsonx Orchestrate** — Native agent orchestration with ReAct reasoning
