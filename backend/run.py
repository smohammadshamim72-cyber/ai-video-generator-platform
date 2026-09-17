import asyncio
import os

from app.main import app


async def serve() -> None:
    import uvicorn
    config = uvicorn.Config(app, host=os.getenv("BACKEND_HOST", "0.0.0.0"), port=int(os.getenv("BACKEND_PORT", "8000")))
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(serve())
