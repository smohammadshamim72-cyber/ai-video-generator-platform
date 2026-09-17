from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Iterable, Optional


class FFmpegStitcher:
    """Real FFmpeg integration boundary.

    Each chunk must have compatible codec, dimensions, frame rate, and audio
    settings. The caller should pass trusted local paths only.
    """

    def __init__(self, output_dir: str = "/tmp/ai-video-jobs") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def stitch(self, chunk_paths: Iterable[str], job_id: str) -> str:
        chunks = list(chunk_paths)
        if not chunks:
            raise ValueError("At least one video chunk is required")

        concat_file = self.output_dir / f"{job_id}.concat.txt"
        output = self.output_dir / f"{job_id}.mp4"
        concat_file.write_text("\n".join(f"file '{Path(path).resolve()}'" for path in chunks), encoding="utf-8")

        process = await asyncio.create_subprocess_exec(
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
            "-c", "copy", str(output),
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await process.communicate()
        if process.returncode != 0:
            raise RuntimeError(f"FFmpeg stitch failed: {stderr.decode(errors='replace')[-2000:]}")
        return str(output)

    async def mix_audio(self, video_path: str, voice_path: Optional[str] = None, music_path: Optional[str] = None) -> str:
        if not voice_path and not music_path:
            return video_path

        output = Path(video_path).with_name(f"{Path(video_path).stem}-mixed.mp4")
        inputs = ["-i", video_path]
        filters = []
        labels = []
        if voice_path:
            inputs += ["-i", voice_path]
            filters.append("[1:a]volume=1.0[voice]")
            labels.append("[voice]")
        if music_path:
            inputs += ["-i", music_path]
            music_index = 2 if voice_path else 1
            filters.append(f"[{music_index}:a]volume=0.18[music]")
            labels.append("[music]")

        audio = ";".join(filters) + (";" if filters else "") + f"{''.join(labels)}amix=inputs={len(labels)}:duration=first[aout]"
        command = ["ffmpeg", "-y", *inputs, "-filter_complex", audio, "-map", "0:v:0", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", str(output)]
        process = await asyncio.create_subprocess_exec(*command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        _, stderr = await process.communicate()
        if process.returncode != 0:
            raise RuntimeError(f"FFmpeg audio mix failed: {stderr.decode(errors='replace')[-2000:]}")
        return str(output)
