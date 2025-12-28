from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
import httpx

app = FastAPI()

BASE_URL = "https://pixeldrain.dev/api/file"

COMMON_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://pixeldrain.dev/"
}

# -------- HEAD SUPPORT (CRITICAL) --------
@app.head("/stream/{file_id}")
async def head_video(file_id: str, request: Request):
    url = f"{BASE_URL}/{file_id}"

    headers = COMMON_HEADERS.copy()
    if "range" in request.headers:
        headers["Range"] = request.headers["range"]

    async with httpx.AsyncClient(timeout=None) as client:
        r = await client.head(url, headers=headers)

    response = Response(status_code=r.status_code)
    for h in [
        "content-type",
        "content-length",
        "accept-ranges",
        "content-range"
    ]:
        if h in r.headers:
            response.headers[h] = r.headers[h]

    return response


# -------- STREAM SUPPORT --------
@app.get("/stream/{file_id}")
async def stream_video(file_id: str, request: Request):
    url = f"{BASE_URL}/{file_id}"

    headers = COMMON_HEADERS.copy()
    if "range" in request.headers:
        headers["Range"] = request.headers["range"]

    async def generator():
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("GET", url, headers=headers) as r:
                async for chunk in r.aiter_bytes():
                    yield chunk

    return StreamingResponse(
        generator(),
        status_code=206 if "range" in request.headers else 200,
        headers={
            "Accept-Ranges": "bytes"
        }
    )