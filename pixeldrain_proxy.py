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

    # Forward Range header (VERY IMPORTANT)
    if "range" in request.headers:
        headers["Range"] = request.headers["range"]

    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.get(
            pixeldrain_url,
            headers=headers,
            stream=True
        )

    # Copy REQUIRED headers for video players
    response_headers = {}

    for h in [
        "content-type",
        "content-length",
        "content-range",
        "accept-ranges"
    ]:
        if h in response.headers:
            response_headers[h] = response.headers[h]

    async def video_stream():
        async for chunk in response.aiter_bytes():
            yield chunk

    return StreamingResponse(
        video_stream(),
        status_code=response.status_code,  # 200 or 206
        headers=response_headers
    )