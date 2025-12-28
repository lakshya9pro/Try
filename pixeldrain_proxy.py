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

    if "range" in request.headers:
        headers["Range"] = request.headers["range"]

    async def video_stream():
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("GET", pixeldrain_url, headers=headers) as r:
                async for chunk in r.aiter_bytes():
                    yield chunk

    return StreamingResponse(
        video_stream(),
        headers={"Accept-Ranges": "bytes"}
    )