from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import uuid
import json

from services.LLMService import LLMService
from services.ScenarioService import ScenarioService
from services.ConscienceIQService import ConscienceIQService
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
        raise HTTPException(status_code=400, detail="Question is required")
    
    return await question_logic(question, user_id)

@router.get("/v1/question")
async def question(question: str, user_id: Optional[str] = None):
    return await question_logic(question, user_id)

async def question_logic(question: str, user_id: Optional[str] = None):
    scenario_service = get_scenario_service()

    if not user_id:
        user_id = f"temp_{str(uuid.uuid4())[:8]}"

    if scenario_service.detect_stop_command(question):
        stop_message = scenario_service.stop_scenario_with_message(user_id)
        return {
            "response": stop_message,
            "scenario_active": False,
            "user_id": user_id,
            "source": "stop_command"
        }

    # Проверяем если пользователь в состоянии ожидания согласия или активного сценария
    if user_id in scenario_service.consent_pending or scenario_service.get_user_scenario_state(user_id):
        scenario_response = await scenario_service.process_user_response(user_id, question)
        if scenario_response:
            log.info(f"Размер ответа сценария: {len(scenario_response)} символов")
            try:
                test_json = json.dumps({"test": scenario_response}, ensure_ascii=False)
                log.info(f"JSON тест прошёл успешно, размер JSON: {len(test_json)}")
            except (TypeError, ValueError, UnicodeDecodeError) as e:
                log.error(f"Ошибка сериализации ответа сценария: {e}")
                scenario_response = "Sorry, the response contains characters that cannot be transmitted. Please try asking a simpler question."

            updated_scenario = scenario_service.get_user_scenario_state(user_id)
            is_completed = updated_scenario and updated_scenario.state.value == "completed"

            # Определяем название сценария
            if updated_scenario:
                scenario_name = updated_scenario.scenario_name
            elif user_id in scenario_service.consent_pending:
                scenario_name = scenario_service.consent_pending[user_id]
            else:
                scenario_name = "unknown"

            response_data = {
                "response": scenario_response,
                "scenario_active": True,
                "scenario_name": scenario_name,
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
        conscience_service = ConscienceIQService()
        enhanced_question = conscience_service.get_enhanced_prompt(question, context_type="general")
        
        llm = LLMService()
        result = await llm.fetch_completion(enhanced_question)

        conscience_check = conscience_service.conscience_check(result, f"RAG ответ для пользователя {user_id}")
        if not conscience_check:
            log.warning(f"RAG ответ не прошел проверку Conscience IQ для пользователя {user_id}")
        
        log.info(f"RAG ответ с Conscience IQ получен для пользователя {user_id}, длина: {len(result) if result else 0}")

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
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")