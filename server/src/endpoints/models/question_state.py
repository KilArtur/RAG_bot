from dataclasses import dataclass
from typing import Dict, List, Optional, Any

@dataclass
class QuestionState:
    question: str
    answer: Optional[str] = None
    attempts: int = 0
    is_satisfied: bool = False