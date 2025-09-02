from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from endpoints.models.scenario_state import ScenarioState
from endpoints.models.question_state import QuestionState

@dataclass
class UserScenario:
    scenario_name: str
    state: ScenarioState
    current_question_index: int
    questions: List[QuestionState]
    final_summary: Optional[str] = None