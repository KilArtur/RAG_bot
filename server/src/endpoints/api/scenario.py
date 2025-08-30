from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional

from services.ScenarioService import ScenarioService
from utils.logger import get_logger

router = APIRouter()
log = get_logger("scenario_endpoint")

_scenario_service = None

def get_scenario_service():
    global _scenario_service
    if _scenario_service is None:
        _scenario_service = ScenarioService()
    return _scenario_service

@router.post("/v1/scenario/message")
async def handle_scenario_message(user_id: str, message: str):
    try:
        scenario_service = get_scenario_service()
        active_scenario = scenario_service.get_user_scenario_state(user_id)
        
        if active_scenario:
            response = await scenario_service.process_user_response(user_id, message)
            if response:
                return {
                    "response": response,
                    "scenario_active": True,
                    "scenario_name": active_scenario.scenario_name,
                    "question_number": active_scenario.current_question_index + 1,
                    "total_questions": len(active_scenario.questions)
                }

        scenario_name = scenario_service.detect_scenario_trigger(message)
        if scenario_name:
            response = scenario_service.start_scenario(user_id, scenario_name)
            return {
                "response": response,
                "scenario_active": True,
                "scenario_name": scenario_name,
                "question_number": 1,
                "total_questions": len(scenario_service.scenario_configs[scenario_name])
            }

        return {
            "response": None,
            "scenario_active": False
        }
        
    except Exception as e:
        log.error(f"Ошибка при обработке сценария: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")

@router.get("/v1/scenario/status/{user_id}")
async def get_scenario_status(user_id: str):
    try:
        scenario_service = get_scenario_service()
        scenario = scenario_service.get_user_scenario_state(user_id)
        if scenario:
            return {
                "scenario_active": True,
                "scenario_name": scenario.scenario_name,
                "state": scenario.state.value,
                "current_question_index": scenario.current_question_index,
                "total_questions": len(scenario.questions),
                "questions_completed": sum(1 for q in scenario.questions if q.is_satisfied)
            }
        else:
            return {"scenario_active": False}
    except Exception as e:
        log.error(f"Ошибка при получении статуса сценария: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")

@router.delete("/v1/scenario/{user_id}")
async def cancel_scenario(user_id: str):
    try:
        scenario_service = get_scenario_service()
        success = scenario_service.cancel_scenario(user_id)
        return {
            "success": success,
            "message": "Сценарий отменен" if success else "Активный сценарий не найден"
        }
    except Exception as e:
        log.error(f"Ошибка при отмене сценария: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")