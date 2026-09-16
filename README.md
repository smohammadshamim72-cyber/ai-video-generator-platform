# AI Video Generation Platform

A full-stack platform for generating long-form AI videos (1 to 24 minutes) by combining:
- Agentic AI story planning and scene decomposition
- Autoregressive video continuation for smooth transitions across scenes
- Video stitching, audio synchronization, and TTS narration
- Real-time progress streaming through WebSockets
- Modern dashboard UI for prompt input, timeline monitoring, and preview

## Architecture Overview

This project is designed as a multi-layer system:

1. Frontend Layer
   - Next.js App Router
   - Tailwind CSS
   - Dashboard UI for prompt input and generation monitoring
   - Video preview player

2. Backend Layer
   - FastAPI REST API
   - Async orchestration for generation tasks
   - WebSocket streaming to frontend
   - Scene generation and job management

3. AI Worker Layer
   - Agentic script planner
   - Autoregressive video continuation pipeline
   - Stitching + speech + music synchronization

## Project Structure

```text
ai-video-generator-platform/
├── README.md
├── .gitignore
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
└── LICENSE
```

## Core Components

### 1. Agentic Story Planner
A backend agent receives a user input prompt and generates a sequence of scenes with:
- narrative text
- visual prompt
- per-scene duration

This simulates an LLM-driven narrative engine that expands a single long prompt into a storyboard.

### 2. Autoregressive Video Continuation
Each scene is generated using the previous scene's context frames, creating continuity between segments and reducing visual drift, cut mismatch, and color discontinuity.

### 3. Video Stitching and Audio Sync
The generated scene chunks are combined, TTS narration is added, background music is mixed in, and FFmpeg/MoviePy renders the final MP4.

### 4. Real-Time Progress Streaming
The backend pushes updates such as:
- Scripting...
- Storyboarding complete...
- Scene 1/10 Generating...
- Stitching audio...
- Final rendering complete.

## Local Setup

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

Open the app at:
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

## Example API Request

```bash
curl -X POST http://localhost:8000/api/generate-video \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A cinematic futuristic city with flying cars, neon rain, and a lone astronaut discovering a hidden archive in the sky.",
    "target_duration_minutes": 4
  }'
```

## Production Notes

This repo is intentionally structured as a clean, modular starter for a production-grade AI video generation platform. The mock agent and continuation pipeline are built so they can later be replaced with LangChain, AutoGen, Diffusers, FFmpeg, TTS, and cloud storage integrations.

## License

MIT License
