# AI Video Generator Platform

A full-stack project for generating long-form AI videos (1–24 minutes) by combining an agentic script planner and autoregressive continuation pipeline.

## Project Structure

```text
ai-video-generator-platform/
├── README.md
├── LICENSE
├── backend/
│   ├── .env.example
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       ├── config.py
│       ├── main.py
│       └── pipeline.py
├── frontend/
│   ├── .env.example
│   ├── next.config.mjs
│   ├── package.json
│   ├── postcss.config.js
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── app/
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   └── components/
│       └── video-generator-dashboard.tsx
├── docs/
│   └── architecture.md
└── .gitignore
```

## Features

- Agentic script generation using a mock LLM planner
- Scene-by-scene generation loop with continuation context
- WebSocket progress streaming to frontend
- Tailwind-based dashboard with generation timeline
- Video preview placeholder for final MP4 output

## Start backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Start frontend

```bash
cd frontend
npm install
npm run dev
```

## API

POST /api/generate-video

Request body:

```json
{
  "prompt": "A cinematic futuristic city with flying cars and neon rain.",
  "target_duration_minutes": 4,
  "style": "cinematic"
}
```

WebSocket:

```text
ws://localhost:8000/ws/generate
```
