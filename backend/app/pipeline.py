from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence


@dataclass
class SceneSpec:
    text: str
    visual_prompt: str
    duration: float


class Agent:
    """Mock LLM-backed agent that converts a long prompt into a scene plan."""

    async def plan_scenes(
        self,
        prompt: str,
        target_duration_minutes: int,
        style: str = "cinematic",
    ) -> List[SceneSpec]:
        await asyncio.sleep(0.4)

        total_seconds = max(60, target_duration_minutes * 60)
        scene_count = min(12, max(4, target_duration_minutes * 2))
        per_scene = total_seconds / scene_count

        scenes: List[SceneSpec] = []
        for index in range(int(scene_count)):
            scenes.append(
                SceneSpec(
                    text=(
                        f"Scene {index + 1}: {prompt}. "
                        f"Continue the narrative with rising tension, cinematic action, and emotional resolution."
                    ),
                    visual_prompt=(
                        f"{style} video frame, highly detailed environment, character motion, smooth camera movement, "
                        f"consistent color grading, dramatic lighting, story-driven composition, {prompt}"
                    ),
                    duration=round(per_scene, 2),
                )
            )

        return scenes


class AutoregressiveVideoPipeline:
    """Mock autoregressive generation loop that uses previous frame context for continuity."""

    async def generate_scene(
        self,
        scene: SceneSpec,
        context_frames: Optional[Sequence[str]] = None,
    ) -> Dict[str, Any]:
        await asyncio.sleep(0.8)

        base_frames = [
            f"frame_{scene.visual_prompt[:12].replace(' ', '_')}_01.png",
            f"frame_{scene.visual_prompt[:12].replace(' ', '_')}_02.png",
            f"frame_{scene.visual_prompt[:12].replace(' ', '_')}_03.png",
        ]

        generated_frames = list(base_frames)
        return {
            "scene": scene,
            "context_frames": list(context_frames) if context_frames else ["initial_context_01.png"],
            "generated_frames": generated_frames,
            "continuation_status": "smooth auto-regressive continuation",
            "output_path": f"/tmp/{scene.text[:18].replace(' ', '_')}.mp4",
        }

    async def run(self, scenes: Sequence[SceneSpec]) -> List[Dict[str, Any]]:
        outputs: List[Dict[str, Any]] = []
        previous_context: Optional[List[str]] = None

        for scene in scenes:
            result = await self.generate_scene(scene, previous_context)
            outputs.append(result)
            previous_context = result["generated_frames"]

        return outputs


__all__ = ["Agent", "AutoregressiveVideoPipeline", "SceneSpec"]
