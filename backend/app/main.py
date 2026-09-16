from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.pipeline import Agent, AutoregressiveVideoPipeline

app = FastAPI(title="AI Video Generator API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SceneSchema(BaseModel):
    text: str = Field(..., description="Narrative text for the scene")
    visual_prompt: str = Field(..., description="Visual generation prompt")
    duration: float = Field(..., gt=0, description="Duration in seconds")


class GenerateVideoRequest(BaseModel):
    prompt: str = Field(..., min_length=10, description="Long-form user prompt")
    target_duration_minutes: int = Field(..., ge=1, le=24, description="Target duration in minutes")
    style: Optional[str] = Field(default="cinematic", description="Visual style")


class GenerateVideoResponse(BaseModel):
    job_id: str
    prompt: str
    target_duration_minutes: int
    scenes: List[SceneSchema]
    status: str
    output_url: Optional[str] = None


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_json(self, websocket: WebSocket, payload: Dict[str, Any]) -> None:
        await websocket.send_json(payload)

    async def broadcast(self, payload: Dict[str, Any]) -> None:
        for connection in list(self.active_connections):
            try:
                await connection.send_json(payload)
            except Exception:
                self.disconnect(connection)


manager = ConnectionManager()
agent = Agent()
pipeline = AutoregressiveVideoPipeline()


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok", "service": "ai-video-generator"}


@app.post("/api/generate-video", response_model=GenerateVideoResponse)
async def generate_video(payload: GenerateVideoRequest) -> GenerateVideoResponse:
    scenes = await agent.plan_scenes(payload.prompt, payload.target_duration_minutes, payload.style or "cinematic")
    generated = await pipeline.run(scenes)

    return GenerateVideoResponse(
        job_id=f"job_{payload.target_duration_minutes}m_{len(scenes)}s",
        prompt=payload.prompt,
        target_duration_minutes=payload.target_duration_minutes,
        scenes=[
            SceneSchema(text=scene.text, visual_prompt=scene.visual_prompt, duration=scene.duration)
            for scene in scenes
        ],
        status="rendering_complete" if generated else "queued",
        output_url="/tmp/final_video.mp4" if generated else None,
    )


@app.websocket("/ws/generate")
async def websocket_generate(websocket: WebSocket) -> None:
    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            prompt = data.get("prompt")
            target_duration_minutes = int(data.get("target_duration_minutes", 2))

            if not prompt:
                await manager.send_json(websocket, {"type": "error", "message": "Prompt is required."})
                continue

            await manager.send_json(websocket, {"type": "progress", "message": "Scripting..."})
            scenes = await agent.plan_scenes(prompt, target_duration_minutes, "cinematic")

            await manager.send_json(
                websocket,
                {"type": "progress", "message": f"Storyboarding complete: {len(scenes)} scenes generated."},
            )

            context_frames: Optional[List[str]] = None
            for index, scene in enumerate(scenes, start=1):
                await manager.send_json(
                    websocket,
                    {"type": "progress", "message": f"Scene {index}/{len(scenes)} generating..."},
                )

                generated = await pipeline.generate_scene(scene, context_frames)
                context_frames = generated["generated_frames"]

                await manager.send_json(
                    websocket,
                    {
                        "type": "scene",
                        "scene_index": index,
                        "message": f"Scene {index}/{len(scenes)} generated",
                        "visual_prompt": scene.visual_prompt,
                    },
                )

            await manager.send_json(websocket, {"type": "progress", "message": "Stitching audio..."})
            await manager.send_json(websocket, {"type": "progress", "message": "Final rendering complete."})
            await manager.send_json(websocket, {"type": "done", "output_url": "/tmp/final_video.mp4"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
