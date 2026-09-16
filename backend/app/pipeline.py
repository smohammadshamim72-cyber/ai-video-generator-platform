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
    """Mock agent that converts a prompt into scene breakdowns."""

    async def plan_scenes(
        self,
        prompt: str,
        target_duration_minutes: int,
        style: str = "cinematic",
    ) -> List[SceneSpec]:
        await asyncio.sleep(0.4)

        total_seconds = max(60, target_duration_minutes * 60)
        scene_count = max(4, min(12, target_duration_minutes * 2))
        per_scene = total_seconds / scene_count

        scenes: List[SceneSpec] = []
        for index in range(int(scene_count)):
            scenes.append(
                SceneSpec(
                    text=(
                        f"Scene {index + 1}: {prompt}. "
                        f"Continue the story with cinematic progression, emotional payoff, and visual momentum."
                    ),
                    visual_prompt=(
                        f"{style} visual composition, richly detailed environment, dramatic lighting, smooth camera motion, "
                        f"consistent color grading, story-led framing, {prompt}"
                    ),
                    duration=round(per_scene, 2),
                )
            )

        return scenes


class AutoregressiveVideoPipeline:
    """Simulated continuation pipeline using previous context frames."""

    async def generate_scene(
        self,
        scene: SceneSpec,
        context_frames: Optional[Sequence[str]] = None,
    ) -> Dict[str, Any]:
        await asyncio.sleep(0.7)

        prompt_tag = scene.visual_prompt[:12].replace(" ", "_")
        generated_frames = [
            f"frame_{prompt_tag}_01.png",
            f"frame_{prompt_tag}_02.png",
            f"frame_{prompt_tag}_03.png",
        ]

        return {
            "scene": scene,
            "context_frames": list(context_frames) if context_frames else ["initial_context_01.png"],
            "generated_frames": generated_frames,
            "continuation_status": "smooth continuation using previous context",
            "output_path": f"/tmp/{prompt_tag}.mp4",
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
