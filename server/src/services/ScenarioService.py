import os
import yaml
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from utils.logger import get_logger
from services.LLMService import LLMService

log = get_logger("ScenarioService")


class ScenarioState(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress" 
    AWAITING_ANSWER = "awaiting_answer"
    COMPLETED = "completed"


@dataclass
class QuestionState:
    question: str
    answer: Optional[str] = None
    attempts: int = 0
    is_satisfied: bool = False


@dataclass
class UserScenario:
    scenario_name: str
    state: ScenarioState
    current_question_index: int
    questions: List[QuestionState]
    final_summary: Optional[str] = None


class ScenarioService:
    def __init__(self):
        self.llm_service = LLMService()
        self.active_scenarios: Dict[str, UserScenario] = {}
        self.scenario_configs = self._load_scenarios()
        self.prompts = self._load_prompts()
    
    def _load_scenarios(self) -> Dict[str, List[str]]:
        """Загружает все сценарии из папки scenarios"""
        scenarios = {}
        # Ищем папку scenarios относительно текущего файла
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
        """Загружает промпты из файла prompts.yml"""
        try:
            # Ищем prompts.yml относительно текущего файла
            current_dir = os.path.dirname(__file__)
            prompts_path = os.path.join(current_dir, "..", "prompts.yml")
            prompts_path = os.path.abspath(prompts_path)
            
            with open(prompts_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            log.error(f"Ошибка загрузки промптов: {e}")
            return {}
    
    def detect_scenario_trigger(self, user_message: str) -> Optional[str]:
        """Определяет, запускает ли сообщение пользователя какой-то сценарий"""
        user_message_lower = user_message.lower()
        
        # Простая система триггеров для вегетарианства
        vegan_triggers = [
            "хочу стать вегетариан", "хочу стать вегатериан", "хочу быть вегетариан",
            "стать вегетариан", "стать вегатериан", "стать веган",
            "перейти на вегетарианство", "перейти на вегатерианство",
            "вегетарианская диета", "вегатерианская диета",
            "отказаться от мяса", "не есть мясо", "без мяса",
            "растительное питание", "растительная диета"
        ]
        
        for trigger in vegan_triggers:
            if trigger in user_message_lower:
                return "vegans"
        
        return None
    
    def start_scenario(self, user_id: str, scenario_name: str) -> str:
        """Запускает сценарий для пользователя"""
        if scenario_name not in self.scenario_configs:
            return f"Сценарий {scenario_name} не найден"
        
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
        
        # Возвращаем первый вопрос
        return self._get_next_question_prompt(user_id)
    
    async def process_user_response(self, user_id: str, user_response: str) -> str:
        """Обрабатывает ответ пользователя в рамках активного сценария"""
        if user_id not in self.active_scenarios:
            return None
            
        scenario = self.active_scenarios[user_id]
        
        if scenario.state != ScenarioState.AWAITING_ANSWER:
            return None
        
        current_question = scenario.questions[scenario.current_question_index]
        current_question.answer = user_response
        current_question.attempts += 1
        
        # Проверяем качество ответа
        is_satisfactory = await self._evaluate_answer_quality(
            current_question.question, user_response
        )
        
        if is_satisfactory:
            current_question.is_satisfied = True
            scenario.current_question_index += 1
            
            # Проверяем, есть ли еще вопросы
            if scenario.current_question_index >= len(scenario.questions):
                return await self._complete_scenario(user_id)
            else:
                return self._get_next_question_prompt(user_id)
        else:
            # Ответ неудовлетворительный, переспрашиваем
            if current_question.attempts >= 3:
                # После 3 попыток переходим к следующему вопросу
                current_question.is_satisfied = False
                scenario.current_question_index += 1
                
                if scenario.current_question_index >= len(scenario.questions):
                    return await self._complete_scenario(user_id)
                else:
                    return self._get_next_question_prompt(user_id)
            else:
                return self._get_clarification_prompt(current_question.question, user_response)
    
    async def _evaluate_answer_quality(self, question: str, answer: str) -> bool:
        """Оценивает качество ответа пользователя"""
        prompt = self.prompts.get('evaluate_answer_quality', '').format(
            question=question, 
            answer=answer
        )
        
        try:
            result = await self.llm_service.fetch_completion(prompt)
            return "да" in result.lower() or "подходящ" in result.lower()
        except Exception as e:
            log.warning(f"Ошибка при оценке качества ответа: {e}")
            # В случае ошибки считаем ответ подходящим
            return len(answer.strip()) > 5
    
    def _get_next_question_prompt(self, user_id: str) -> str:
        """Формирует промпт для следующего вопроса"""
        scenario = self.active_scenarios[user_id]
        current_question = scenario.questions[scenario.current_question_index]
        
        scenario.state = ScenarioState.AWAITING_ANSWER
        
        prompt_template = self.prompts.get('ask_question', '')
        return prompt_template.format(
            question=current_question.question,
            question_number=scenario.current_question_index + 1,
            total_questions=len(scenario.questions)
        )
    
    def _get_clarification_prompt(self, question: str, previous_answer: str) -> str:
        """Формирует промпт для переспроса"""
        prompt_template = self.prompts.get('clarify_answer', '')
        return prompt_template.format(
            question=question,
            previous_answer=previous_answer
        )
    
    async def _complete_scenario(self, user_id: str) -> str:
        """Завершает сценарий и генерирует итоговый план"""
        scenario = self.active_scenarios[user_id]
        scenario.state = ScenarioState.COMPLETED
        
        # Собираем все ответы
        answers_summary = ""
        for i, q in enumerate(scenario.questions):
            answers_summary += f"Вопрос {i+1}: {q.question}\nОтвет: {q.answer or 'Не получен'}\n\n"
        
        # Генерируем итоговый план
        prompt_template = self.prompts.get('generate_final_plan', '')
        final_prompt = prompt_template.format(
            scenario_name=scenario.scenario_name,
            answers_summary=answers_summary
        )
        
        try:
            log.info(f"Генерируем финальный план для пользователя {user_id}")
            scenario.final_summary = await self.llm_service.fetch_completion(final_prompt)
            
            if scenario.final_summary and scenario.final_summary.strip():
                log.info(f"Финальный план успешно создан для пользователя {user_id}")
                # НЕ удаляем сценарий сразу - он будет удален после отправки ответа
                return scenario.final_summary
            else:
                log.error(f"Финальный план пуст для пользователя {user_id}")
                return "К сожалению, не удалось создать персонализированный план. Попробуйте обратиться позже или запросите общие рекомендации по вегетарианству."
                
        except Exception as e:
            log.error(f"Ошибка при генерации финального плана для {user_id}: {str(e)}")
            # В случае ошибки возвращаем базовые рекомендации
            return """К сожалению, произошла ошибка при создании персонализированного плана. 
            
Общие рекомендации для перехода на вегетарианство:
• Начните постепенно - замените одно мясное блюдо в день на растительное
• Включите в рацион бобовые (чечевица, нут, фасоль) как источник белка
• Добавьте орехи и семена для получения полезных жиров
• Употребляйте разнообразные овощи и фрукты
• Рассмотрите прием витамина B12 в виде добавок
• Проконсультируйтесь с врачом перед кардинальной сменой рациона

Попробуйте запросить персонализированный план позже."""
    
    def get_user_scenario_state(self, user_id: str) -> Optional[UserScenario]:
        """Возвращает текущее состояние сценария пользователя"""
        return self.active_scenarios.get(user_id)
    
    def cancel_scenario(self, user_id: str) -> bool:
        """Отменяет активный сценарий пользователя"""
        if user_id in self.active_scenarios:
            del self.active_scenarios[user_id]
            return True
        return False
    
    def cleanup_completed_scenario(self, user_id: str) -> bool:
        """Удаляет завершённый сценарий после отправки финального плана"""
        if user_id in self.active_scenarios:
            scenario = self.active_scenarios[user_id]
            if scenario.state == ScenarioState.COMPLETED and scenario.final_summary:
                del self.active_scenarios[user_id]
                log.info(f"Завершённый сценарий для пользователя {user_id} удалён из памяти")
                return True
        return False