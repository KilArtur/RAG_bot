import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from endpoints.api import main_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(main_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)