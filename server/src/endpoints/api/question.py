from fastapi import APIRouter
from typing import Optional
import uuid

from services.LLMService import LLMService
from services.ScenarioService import ScenarioService
from utils.logger import get_logger

router = APIRouter()
log = get_logger("question_endpoint")

_scenario_service = None

def get_scenario_service():
    global _scenario_service
    if _scenario_service is None:
        _scenario_service = ScenarioService()
    return _scenario_service

@router.get("/v1/question")
async def question(question: str, user_id: Optional[str] = None):
    scenario_service = get_scenario_service()

    if not user_id:
        user_id = f"temp_{str(uuid.uuid4())[:8]}"

    active_scenario = scenario_service.get_user_scenario_state(user_id)
    
    if active_scenario:
        # Есть активный сценарий - обрабатываем в его контексте
        scenario_response = await scenario_service.process_user_response(user_id, question)
        if scenario_response:
            return {
                "response": scenario_response,
                "scenario_active": True,
                "scenario_name": active_scenario.scenario_name,
                "user_id": user_id,
                "source": "scenario"
            }
    
    # Проверяем триггеры для запуска сценария
    scenario_name = scenario_service.detect_scenario_trigger(question)
    if scenario_name:
        scenario_response = scenario_service.start_scenario(user_id, scenario_name)
        return {
            "response": scenario_response,
            "scenario_active": True,
            "scenario_name": scenario_name,
            "user_id": user_id,
            "source": "scenario"
        }
    
    # Обычный RAG ответ
    llm = LLMService()
    result = await llm.fetch_completion(question)

    return {
        "response": result,
        "scenario_active": False,
        "user_id": user_id,
        "source": "rag"
    }