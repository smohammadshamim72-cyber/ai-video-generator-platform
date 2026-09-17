# Production Configuration

## Run locally

```bash
cp backend/.env.example backend/.env
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

## Run with Docker

```bash
docker compose up --build
```

## Real services

The repository now has integration boundaries for:

- Redis-backed job persistence
- Edge-TTS speech synthesis
- FFmpeg scene concatenation and audio mixing
- GPU continuation workers
- Frontend-to-backend job creation and WebSocket progress

The default `MODEL_PROVIDER=mock` is deliberate. Set up a licensed model worker and replace `AutoregressiveVideoPipeline._generate_with_model` before production use. Add authentication, signed object-storage URLs, rate limits, queue retries, metrics, and a persistent database before public deployment.
