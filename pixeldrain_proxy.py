from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import httpx

app = FastAPI()

PIXELDRAIN_API = "https://pixeldrain.dev/api/file"

@app.get("/stream/{file_id}")
async def stream_video(file_id: str, request: Request):
    pixeldrain_url = f"{PIXELDRAIN_API}/{file_id}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://pixeldrain.dev/"
    }

    # Forward Range header (CRITICAL for players)
    if "range" in request.headers:
        headers["Range"] = request.headers["range"]

    async def video_stream():
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "GET",
                pixeldrain_url,
                headers=headers
            ) as response:

                async for chunk in response.aiter_bytes():
                    yield chunk

    # IMPORTANT: Do NOT set Content-Length manually
    return StreamingResponse(
        video_stream(),
        media_type="video/mp4",
        headers={
            "Accept-Ranges": "bytes"
        }
    )