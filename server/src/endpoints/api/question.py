from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import uuid
import json

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

@router.post("/v1/question")
async def question_post(request_data: dict):
    question = request_data.get("question")
    user_id = request_data.get("user_id")
    
    if not question:
        raise HTTPException(status_code=400, detail="Вопрос обязателен")
    
    return await question_logic(question, user_id)

@router.get("/v1/question")
async def question(question: str, user_id: Optional[str] = None):
    return await question_logic(question, user_id)

async def question_logic(question: str, user_id: Optional[str] = None):
    scenario_service = get_scenario_service()

    if not user_id:
        user_id = f"temp_{str(uuid.uuid4())[:8]}"

    active_scenario = scenario_service.get_user_scenario_state(user_id)
    
    if active_scenario:
        scenario_response = await scenario_service.process_user_response(user_id, question)
        if scenario_response:
            log.info(f"Размер ответа сценария: {len(scenario_response)} символов")
            try:
                test_json = json.dumps({"test": scenario_response}, ensure_ascii=False)
                log.info(f"JSON тест прошёл успешно, размер JSON: {len(test_json)}")
            except (TypeError, ValueError, UnicodeDecodeError) as e:
                log.error(f"Ошибка сериализации ответа сценария: {e}")
                scenario_response = "Извините, ответ содержит символы, которые не могут быть переданы. Попробуйте задать вопрос проще."

            updated_scenario = scenario_service.get_user_scenario_state(user_id)
            is_completed = updated_scenario and updated_scenario.state.value == "completed"
            
            response_data = {
                "response": scenario_response,
                "scenario_active": True,
                "scenario_name": active_scenario.scenario_name,
                "user_id": user_id,
                "source": "scenario"
            }

            if is_completed:
                response_data["scenario_completed"] = True
                scenario_service.cleanup_completed_scenario(user_id)
            
            return response_data

    scenario_name = await scenario_service.detect_scenario_trigger(question)
    if scenario_name:
        scenario_response = scenario_service.start_scenario(user_id, scenario_name)
        response_data = {
            "response": scenario_response,
            "scenario_active": True,
            "scenario_name": scenario_name,
            "user_id": user_id,
            "source": "scenario"
        }
        return response_data

    try:
        llm = LLMService()
        result = await llm.fetch_completion(question)
        log.info(f"RAG ответ получен для пользователя {user_id}, длина: {len(result) if result else 0}")

        try:
            json.dumps(result, ensure_ascii=False)
        except (TypeError, ValueError) as e:
            log.warning(f"Проблема с сериализацией ответа: {e}, обрезаем контент")
            result = result[:5000] + "..." if len(result) > 5000 else result
        
        response_data = {
            "response": result,
            "scenario_active": False,
            "user_id": user_id,
            "source": "rag"
        }
        
        return response_data
    except Exception as e:
        log.error(f"Ошибка при получении RAG ответа для {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка при генерации ответа: {str(e)}")