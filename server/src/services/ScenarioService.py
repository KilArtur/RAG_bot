import os
import yaml

from typing import Dict, List, Optional, Any

from utils.logger import get_logger
from services.LLMService import LLMService
from services.ConscienceIQService import ConscienceIQService
from endpoints.models.user_scenario import UserScenario
from endpoints.models.scenario_state import ScenarioState
from endpoints.models.question_state import QuestionState

log = get_logger("ScenarioService")

class ScenarioService:
    def __init__(self):
        self.llm_service = LLMService()
        self.conscience_service = ConscienceIQService()
        self.active_scenarios: Dict[str, UserScenario] = {}
        self.scenario_configs = self._load_scenarios()
        self.prompts = self._load_prompts()
    
    def _load_scenarios(self) -> Dict[str, List[str]]:
        scenarios = {}
        current_dir = os.path.dirname(__file__)
        scenarios_dir = os.path.join(current_dir, "..", "scenarios")
        scenarios_dir = os.path.abspath(scenarios_dir)
        
        if not os.path.exists(scenarios_dir):
            log.warning(f"Папка сценариев {scenarios_dir} не найдена")
            return scenarios
            
        for filename in os.listdir(scenarios_dir):
            if filename.endswith('.txt'):
                scenario_name = filename.replace('.txt', '')
                filepath = os.path.join(scenarios_dir, filename)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    questions = [line.strip() for line in f.readlines() if line.strip()]
                    scenarios[scenario_name] = questions
                    log.info(f"Загружен сценарий {scenario_name} с {len(questions)} вопросами")
        
        return scenarios
    
    def _load_prompts(self) -> Dict[str, str]:
        try:
            current_dir = os.path.dirname(__file__)
            prompts_path = os.path.join(current_dir, "..", "prompts.yml")
            prompts_path = os.path.abspath(prompts_path)
            
            with open(prompts_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            log.error(f"Ошибка загрузки промптов: {e}")
            return {}
    
    async def detect_scenario_trigger(self, user_message: str) -> Optional[str]:
        prompt = self.prompts.get('trigger_prompt', '').format(user_message=user_message)
        
        try:
            result = await self.llm_service.fetch_completion(prompt)
            if "yes" in result.lower():
                return "vegans"
        except Exception as e:
            log.warning(f"Ошибка при определении триггера сценария: {e}")
        
        return None
    
    def start_scenario(self, user_id: str, scenario_name: str) -> str:
        if scenario_name not in self.scenario_configs:
            return f"Scenario {scenario_name} not found"
        
        questions_text = self.scenario_configs[scenario_name]
        questions = [QuestionState(question=q) for q in questions_text]
        
        scenario = UserScenario(
            scenario_name=scenario_name,
            state=ScenarioState.IN_PROGRESS,
            current_question_index=0,
            questions=questions
        )
        
        self.active_scenarios[user_id] = scenario
        
        log.info(f"Запущен сценарий {scenario_name} для пользователя {user_id}")

        return self._get_next_question_prompt(user_id)
    
    async def process_user_response(self, user_id: str, user_response: str) -> str:
        if user_id not in self.active_scenarios:
            return None
            
        scenario = self.active_scenarios[user_id]
        
        if scenario.state != ScenarioState.AWAITING_ANSWER:
            return None
        
        current_question = scenario.questions[scenario.current_question_index]
        current_question.answer = user_response
        current_question.attempts += 1

        is_satisfactory = await self._evaluate_answer_quality(
            current_question.question, user_response
        )
        
        if is_satisfactory:
            current_question.is_satisfied = True
            scenario.current_question_index += 1

            if scenario.current_question_index >= len(scenario.questions):
                return await self._complete_scenario(user_id)
            else:
                return self._get_next_question_prompt(user_id)
        else:
            if current_question.attempts >= 3:
                current_question.is_satisfied = False
                scenario.current_question_index += 1
                
                if scenario.current_question_index >= len(scenario.questions):
                    return await self._complete_scenario(user_id)
                else:
                    return self._get_next_question_prompt(user_id)
            else:
                return self._get_clarification_prompt(current_question.question, user_response)
    
    async def _evaluate_answer_quality(self, question: str, answer: str) -> bool:
        base_prompt = self.prompts.get('evaluate_answer_quality', '').format(
            question=question, 
            answer=answer
        )
        
        # Используем Conscience IQ для этичной оценки ответов
        enhanced_prompt = self.conscience_service.get_enhanced_prompt(
            base_prompt, context_type="scenario"
        )
        
        try:
            result = await self.llm_service.fetch_completion(enhanced_prompt)
            return "yes" in result.lower() or "suitable" in result.lower()
        except Exception as e:
            log.warning(f"Ошибка при оценке качества ответа: {e}")
            return len(answer.strip()) > 5
    
    def _get_next_question_prompt(self, user_id: str) -> str:
        scenario = self.active_scenarios[user_id]
        current_question = scenario.questions[scenario.current_question_index]
        
        scenario.state = ScenarioState.AWAITING_ANSWER
        
        # Для первого вопроса сценария vegans используем специальный промпт с инструкциями
        if scenario.scenario_name == "vegans" and scenario.current_question_index == 0:
            prompt_template = self.prompts.get('ask_first_question_vegans', '')
        else:
            prompt_template = self.prompts.get('ask_question', '')
            
        return prompt_template.format(question=current_question.question)
    
    def _get_clarification_prompt(self, question: str, previous_answer: str) -> str:
        prompt_template = self.prompts.get('clarify_answer', '')
        return prompt_template.format(
            question=question,
            previous_answer=previous_answer
        )
    
    async def _complete_scenario(self, user_id: str) -> str:
        scenario = self.active_scenarios[user_id]
        scenario.state = ScenarioState.COMPLETED

        answers_summary = ""
        for i, q in enumerate(scenario.questions):
            answers_summary += f"Question {i+1}: {q.question}\nAnswer: {q.answer or 'Not received'}\n\n"

        base_prompt = self.prompts.get('generate_final_plan', '').format(
            scenario_name=scenario.scenario_name,
            answers_summary=answers_summary
        )
        
        # Используем Conscience IQ для создания этичного и персонализированного плана
        enhanced_prompt = self.conscience_service.get_enhanced_prompt(
            base_prompt, context_type="plan"
        )
        
        try:
            log.info(f"Генерируем финальный план для пользователя {user_id} с учетом Conscience IQ")
            scenario.final_summary = await self.llm_service.fetch_completion(enhanced_prompt)
            
            # Проверяем план на соответствие этическим принципам
            if scenario.final_summary and scenario.final_summary.strip():
                conscience_check = self.conscience_service.conscience_check(
                    scenario.final_summary, f"План перехода на вегетарианство для пользователя {user_id}"
                )
                
                if conscience_check:
                    log.info(f"Финальный план прошел проверку Conscience IQ для пользователя {user_id}")
                    return scenario.final_summary
                else:
                    log.warning(f"Финальный план не прошел проверку Conscience IQ для пользователя {user_id}")
                    # Возвращаем план, но логируем предупреждение
                    return scenario.final_summary
            else:
                log.error(f"Финальный план пуст для пользователя {user_id}")
                return "Unfortunately, it was not possible to create a personalized plan. Please try again later or request general recommendations for vegetarianism."
                
        except Exception as e:
            log.error(f"Ошибка при генерации финального плана для {user_id}: {str(e)}")
            return self.prompts.get('error_complete_scenario', '')
    
    def get_user_scenario_state(self, user_id: str) -> Optional[UserScenario]:
        return self.active_scenarios.get(user_id)
    
    def cancel_scenario(self, user_id: str) -> bool:
        if user_id in self.active_scenarios:
            del self.active_scenarios[user_id]
            return True
        return False
    
    def cleanup_completed_scenario(self, user_id: str) -> bool:
        if user_id in self.active_scenarios:
            scenario = self.active_scenarios[user_id]
            if scenario.state == ScenarioState.COMPLETED and scenario.final_summary:
                del self.active_scenarios[user_id]
                log.info(f"Завершённый сценарий для пользователя {user_id} удалён из памяти")
                return True
        return False
    
    def detect_stop_command(self, message: str) -> bool:
        stop_keywords = [
            "stop survey",
            "stop the survey",
            "exit survey",
            "quit survey",
            "end survey",
            "cancel survey",
            "abort survey"
        ]
        
        message_lower = message.lower().strip()
        return any(keyword in message_lower for keyword in stop_keywords)
    
    def stop_scenario_with_message(self, user_id: str) -> str:
        if user_id in self.active_scenarios:
            scenario_name = self.active_scenarios[user_id].scenario_name
            del self.active_scenarios[user_id]
            log.info(f"Сценарий {scenario_name} остановлен по команде пользователя {user_id}")
            return "Survey stopped. The next time you start, it will begin from the first question."
        else:
            return "There is currently no active survey to stop."