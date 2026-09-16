# AI Video Generation Platform

A full-stack AI video generation platform for creating long-form videos (1–24 minutes) using:
- Agentic AI for planning scripts, scenes, and visual prompts
- Autoregressive video continuation for smooth transition between scenes
- FFmpeg/MoviePy for stitching, audio sync, and final rendering
- Real-time WebSocket updates for frontend progress streaming

## Architecture

This repository is structured into three major layers:

1. Frontend: Next.js + Tailwind dashboard for prompt entry, timeline updates, and final video preview
2. Backend: FastAPI service for orchestration, API endpoints, and WebSocket progress streaming
3. AI Workers: specialized pipeline for scene planning, video continuation, and media synthesis

## Repository structure

```text
ai-video-generator-platform/
├── README.md
├── .gitignore
├── backend/
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       ├── main.py
│       └── pipeline.py
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.mjs
│   ├── postcss.config.js
│   ├── tailwind.config.ts
│   ├── .env.example
│   ├── app/
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   └── components/
│       └── video-generator-dashboard.tsx
└── docs/
    └── architecture.md
```

## Core Components

### Agentic AI Layer
The backend agent accepts a long-form user prompt and decomposes it into a structured list of scenes. Each scene includes:
- narrative text
- visual prompt
- individual duration

### Autoregressive Continuation Pipeline
The pipeline treats each scene as a sequential continuation of the previous one. It uses the last frames of the previous scene as context to simulate visual continuity and reduce drift.

### Video Stitching & Audio Sync
This final stage combines generated video chunks, applies TTS narration, syncs background music, and renders the final MP4.

## Local setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Then open:
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

## Example request

```bash
curl -X POST http://localhost:8000/api/generate-video \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A cinematic documentary about a futuristic city where robots and humans coexist under a glowing sky.",
    "target_duration_minutes": 4
  }'
```

## Notes

This repository is designed as a production-ready scaffold with realistic architecture. The mock LLM and diffusion pipeline are intentionally clean and modular so they can later be replaced with LangChain, AutoGen, Diffusers, FFmpeg, TTS, and cloud storage services.
