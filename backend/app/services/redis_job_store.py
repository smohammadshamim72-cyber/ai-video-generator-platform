from __future__ import annotations

import json
import os
from typing import Any, Optional


class RedisJobStore:
    """Redis-backed job store for multi-process deployments.

    Enable with JOB_STORE=redis and REDIS_URL. The in-memory store remains useful
    for local development and tests.
    """

    def __init__(self, redis_url: str) -> None:
        self.redis_url = redis_url
        self._client: Any = None

    async def connect(self) -> None:
        from redis.asyncio import Redis
        self._client = Redis.from_url(self.redis_url, decode_responses=True)
        await self._client.ping()

    async def create(self, job_id: str, prompt: str, duration: int) -> None:
        await self._client.hset(f"job:{job_id}", mapping={
            "job_id": job_id,
            "prompt": prompt,
            "target_duration_minutes": duration,
            "status": "queued",
            "progress": json.dumps([]),
        })
        await self._client.expire(f"job:{job_id}", int(os.getenv("JOB_TTL_SECONDS", "86400")))

    async def update(self, job_id: str, **values: Any) -> None:
        values = {key: json.dumps(value) if isinstance(value, (dict, list)) else str(value) for key, value in values.items()}
        await self._client.hset(f"job:{job_id}", mapping=values)

    async def get(self, job_id: str) -> Optional[dict[str, Any]]:
        data = await self._client.hgetall(f"job:{job_id}")
        if not data:
            return None
        for key in ("progress", "result"):
            if key in data:
                try:
                    data[key] = json.loads(data[key])
                except json.JSONDecodeError:
                    pass
        return data
