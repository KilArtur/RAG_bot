from fastapi import APIRouter
from datetime import datetime

from utils.logger import get_logger

router = APIRouter()
log = get_logger("health_endpoint")

@router.get("/health")
async def health():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log.info(f"Health check выполнен в {current_time}")

    return {
        "status": "It's OK, nice work",
        "time": current_time
    }