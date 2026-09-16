from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
import asyncio

from app.pipeline import Agent, AutoregressiveVideoPipeline, SceneSpec

app = FastAPI(title="AI Video Generator API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SceneSchema(BaseModel):
    text: str
    visual_prompt: str
    duration: float = Field(..., gt=0)


class GenerateVideoRequest(BaseModel):
    prompt: str = Field(..., min_length=10)
    target_duration_minutes: int = Field(..., ge=1, le=24)
    style: Optional[str] = "cinematic"


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_progress(self, websocket: WebSocket, message: str) -> None:
        await websocket.send_json({"type": "progress", "message": message})


manager = ConnectionManager()
agent = Agent()
pipeline = AutoregressiveVideoPipeline()


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok", "service": "ai-video-generator"}


@app.post("/api/generate-video")
async def generate_video(payload: GenerateVideoRequest) -> Dict[str, Any]:
    scenes = await agent.plan_scenes(payload.prompt, payload.target_duration_minutes, payload.style or "cinematic")
    generated = await pipeline.run(scenes)

    return {
        "job_id": f"video_{payload.target_duration_minutes}m_{len(scenes)}scenes",
        "prompt": payload.prompt,
        "target_duration_minutes": payload.target_duration_minutes,
        "scene_count": len(scenes),
        "scenes": [
            {"text": scene.text, "visual_prompt": scene.visual_prompt, "duration": scene.duration}
            for scene in scenes
        ],
        "status": "ready_for_stitching",
        "output_url": "/tmp/final_video.mp4" if generated else None,
    }


@app.websocket("/ws/generate")
async def websocket_generate(websocket: WebSocket) -> None:
    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            prompt = data.get("prompt")
            target_duration_minutes = int(data.get("target_duration_minutes", 2))

            if not prompt:
                await manager.send_progress(websocket, "Prompt is required")
                continue

            await manager.send_progress(websocket, "Scripting...")
            scenes = await agent.plan_scenes(prompt, target_duration_minutes, "cinematic")

            await manager.send_progress(websocket, f"Storyboarding complete: {len(scenes)} scenes generated")

            previous_context_frames: Optional[List[str]] = None
            for index, scene in enumerate(scenes, start=1):
                await manager.send_progress(websocket, f"Scene {index}/{len(scenes)} generating...")
                result = await pipeline.generate_scene(scene, previous_context_frames)
                previous_context_frames = result["generated_frames"]
                await asyncio.sleep(0.2)

            await manager.send_progress(websocket, "Stitching audio...")
            await asyncio.sleep(0.3)
            await manager.send_progress(websocket, "Final rendering complete")
            await websocket.send_json({"type": "done", "output_url": "/tmp/final_video.mp4"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
