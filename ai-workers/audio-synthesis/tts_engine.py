from __future__ import annotations

import asyncio
from pathlib import Path


class TTSEngine:
    """Edge-TTS implementation; replace with a licensed provider when needed."""

    async def synthesize(self, text: str, output_path: str, voice: str = "en-US-AriaNeural") -> str:
        try:
            import edge_tts
        except ImportError as exc:
            raise RuntimeError("Install edge-tts to enable TTS") from exc

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(path))
        return str(path)
