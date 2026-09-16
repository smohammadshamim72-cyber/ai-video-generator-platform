from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SceneSpec:
    text: str
    visual_prompt: str
    duration: float


@dataclass
class GenerationJob:
    job_id: str
    prompt: str
    target_duration_minutes: int
    status: str = "queued"
    scenes: Optional[List[SceneSpec]] = None
