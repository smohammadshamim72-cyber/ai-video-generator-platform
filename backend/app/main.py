from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import asyncio
import json
from datetime import datetime

app = FastAPI(title="AI Video Generator API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SceneSchema(BaseModel):
    text: str = Field(..., description="Narrative script for the scene")
    visual_prompt: str = Field(..., description="Image/video generation prompt")
    duration: float = Field(..., gt=0, description="Scene duration in seconds")


class GenerateVideoRequest(BaseModel):
    prompt: str = Field(..., min_length=10)
    target_duration_minutes: int = Field(..., ge=1, le=24)
    style: Optional[str] = "cinematic"


class MockLLMAgent:
    """Mock LLM agent that converts a user prompt into scene breakdowns."""

    async def generate_scenes(self, prompt: str, target_duration_minutes: int) -> List[SceneSchema]:
        await asyncio.sleep(0.5)

        total_seconds = target_duration_minutes * 60
        scenes_count = max(3, min(12, target_duration_minutes))
        base_per_scene = total_seconds / scenes_count

        scenes: List[SceneSchema] = []
        for i in range(scenes_count):
            duration = round(base_per_scene, 2)
            scenes.append(
                SceneSchema(
                    text=f"Scene {i + 1}: {prompt[:120]} - narrative beat {i + 1} focusing on cinematic motion and progression.",
                    visual_prompt=(
                        f"Cinematic long-form video scene {i + 1}, highly detailed, story-driven composition, "
                        f"consistent lighting, smooth motion, visual continuity, dramatic camera movement, {prompt[:100]}"
                    ),
                    duration=duration,
                )
            )

        return scenes


class AutoregressiveVideoPipeline:
    """Simulates the continuation loop between scenes using context from the previous scene."""

    async def generate_scene(self, scene: SceneSchema, previous_context_frames: Optional[List[str]] = None) -> Dict[str, Any]:
        await asyncio.sleep(0.7)

        context_summary = "continuous visual continuity" if previous_context_frames else "fresh scene initialization"
        return {
            "scene_index": 0,
            "scene": scene,
            "context_frames": previous_context_frames or ["frame_01.png", "frame_02.png"],
            "continuation_mode": context_summary,
            "rendered_video_path": f"/tmp/scene_{scene.text[:8]}.mp4",
            "status": "generated",
        }

    async def generate_all(self, scenes: List[SceneSchema]) -> List[Dict[str, Any]]:
        outputs: List[Dict[str, Any]] = []
        context_frames: Optional[List[str]] = None

        for idx, scene in enumerate(scenes, start=1):
            generated = await self.generate_scene(scene, context_frames)
            generated["scene_index"] = idx
            outputs.append(generated)
            context_frames = generated["context_frames"]

        return outputs


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_progress(self, websocket: WebSocket, message: str):
        await websocket.send_text(json.dumps({"type": "progress", "message": message, "timestamp": datetime.utcnow().isoformat()}))

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(json.dumps({"type": "progress", "message": message, "timestamp": datetime.utcnow().isoformat()}))


manager = ConnectionManager()
agent = MockLLMAgent()
pipeline = AutoregressiveVideoPipeline()


@app.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "ok", "message": "AI Video Generator backend is running"}


@app.post("/api/generate-video")
async def generate_video(request: GenerateVideoRequest):
    """Create a long video generation job from a prompt and target duration."""
    scenes = await agent.generate_scenes(request.prompt, request.target_duration_minutes)
    generated_scenes = await pipeline.generate_all(scenes)

    return {
        "job_id": f"video_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}",
        "prompt": request.prompt,
        "target_duration_minutes": request.target_duration_minutes,
        "scene_count": len(scenes),
        "scenes": [
            {
                "text": scene.text,
                "visual_prompt": scene.visual_prompt,
                "duration": scene.duration,
            }
            for scene in scenes
        ],
        "generated_chunks": generated_scenes,
        "status": "ready_for_stitching",
        "output_url": "/tmp/final_video.mp4",
    }


@app.websocket("/ws/progress")
async def websocket_progress(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.websocket("/ws/generate")
async def websocket_generate(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if not data:
                continue

            prompt = data.get("prompt")
            target_duration_minutes = data.get("target_duration_minutes", 2)

            if not prompt:
                await manager.send_progress(websocket, "Prompt is required.")
                continue

            await manager.send_progress(websocket, "Agent is analyzing your prompt...")
            scenes = await agent.generate_scenes(prompt, int(target_duration_minutes))

            await manager.send_progress(websocket, f"Generated {len(scenes)} scenes for storyboarding.")

            previous_context_frames = None
            for index, scene in enumerate(scenes, start=1):
                await manager.send_progress(websocket, f"Scene {index}/{len(scenes)} generating...")
                generated = await pipeline.generate_scene(scene, previous_context_frames)
                previous_context_frames = generated["context_frames"]
                await asyncio.sleep(0.4)

            await manager.send_progress(websocket, "Stitching video and syncing audio...")
            await asyncio.sleep(0.8)
            await manager.send_progress(websocket, "Final rendering complete. Video ready.")

    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
