from enum import Enum

class ScenarioState(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    BIOMETRIC_BASELINE_1 = "biometric_baseline_1"
    BIOMETRIC_BASELINE_2 = "biometric_baseline_2"
    AWAITING_ANSWER = "awaiting_answer"
    AWAITING_AGENT_MODE_RESPONSE = "awaiting_agent_mode_response"
    COMPLETED = "completed"