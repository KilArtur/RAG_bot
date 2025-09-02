from enum import Enum

class ScenarioState(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    AWAITING_ANSWER = "awaiting_answer"
    COMPLETED = "completed"