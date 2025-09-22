import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import asyncio

from endpoints.api import main_router

app = FastAPI()

app.default_response_class = JSONResponse

@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    try:
        return await asyncio.wait_for(call_next(request), timeout=180.0)
    except asyncio.TimeoutError:
        return JSONResponse(
            status_code=408,
            content={"detail": "Request timeout after 3 minutes"}
        )

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
            "http://localhost:7001",
            "http://54.88.62.150:7001",
            "https://54.88.62.150:7001",
            "https://127.0.0.1:7001",
            "https://deeplogix.io",
            "http://deeplogix.io",
        ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(main_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7000,
        timeout_keep_alive=180,
        timeout_graceful_shutdown=180
    )