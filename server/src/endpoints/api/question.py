from fastapi import APIRouter

from services.LLMService import LLMService
from utils.logger import get_logger

router = APIRouter()
log = get_logger("question_endpoint")

@router.get("/v1/question")
async def question(question: str):
    llm = LLMService()
    result = await llm.fetch_completion(question)

    return {
        "response: ":  result
    }