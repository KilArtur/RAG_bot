from fastapi import APIRouter
from endpoints.api.health import router as health_router
from endpoints.api.question import router as question_router


main_router = APIRouter()

main_router.include_router(health_router)
main_router.include_router(question_router)