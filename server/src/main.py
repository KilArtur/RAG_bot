import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json

from endpoints.api import main_router

app = FastAPI()

app.default_response_class = JSONResponse

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
            "http://localhost:7001",
            "http://54.88.62.150:7001", 
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
        timeout_keep_alive=300,
        timeout_graceful_shutdown=30
    )