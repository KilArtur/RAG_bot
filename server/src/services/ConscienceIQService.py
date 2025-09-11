import os
import PyPDF2
from typing import Optional
from utils.logger import get_logger

log = get_logger("ConscienceIQService")

class ConscienceIQService:
    def __init__(self):
        self.conscience_principles = self._load_conscience_iq_instructions()
    
    def _load_conscience_iq_instructions(self) -> str:
        """Загружает инструкции из PDF файла"""
        try:
            current_dir = os.path.dirname(__file__)
            pdf_path = os.path.join(current_dir, "..", "..", "data", "AI Model - Instructional.pdf")
            pdf_path = os.path.abspath(pdf_path)
            
            if not os.path.exists(pdf_path):
                log.warning(f"PDF файл с инструкциями не найден: {pdf_path}")
                return self._get_default_principles()
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = ""
                
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"
                
                log.info(f"Загружены инструкции Conscience IQ из PDF, длина: {len(text_content)} символов")
                return text_content.strip()
                
        except Exception as e:
            log.error(f"Ошибка при загрузке PDF инструкций: {e}")
            return self._get_default_principles()

    def _get_default_principles(self) -> str:
        return """
        Core Ethical AI Principles:
        1. Prioritize human dignity over efficiency
        2. Fairness and bias prevention
        3. Transparency and accountability
        4. Diversity and inclusion
        5. Support for human well-being and growth
        6. Ethical responsibility in all decisions
        """

    def get_enhanced_prompt(self, original_prompt: str, context_type: str = "general") -> str:

        conscience_context = self._get_context_specific_guidance(context_type)

        enhanced_prompt = f"""You are an AI assistant that follows the ethical artificial intelligence principles of Conscience IQ.

    KEY PRINCIPLES:
    {conscience_context}

    CORE RULE: If a decision affects people, prioritize dignity over efficiency.

    TASK:
    {original_prompt}

    When responding, you must:
    - Consider cultural diversity and avoid Western-centric assumptions
    - Support human dignity, well-being, and growth
    - Be transparent in your recommendations
    - Check your responses for bias
    - Provide advice that empowers people rather than limits them"""

        return enhanced_prompt

    def _get_context_specific_guidance(self, context_type: str) -> str:

        base_principles = """
    - Human dignity over efficiency
    - Fairness and bias prevention
    - Representation of marginalized voices and cultures
    - Support for growth, well-being, and autonomy
    - Transparency and accountability in decisions
    """

        if context_type == "health":
            return base_principles + """
    - Prevent racial and cultural biases in medical recommendations
    - Consider placebo effects and the influence of beliefs on health
    - Prioritize patient dignity
    """
        elif context_type == "scenario":
            return base_principles + """
    - Ask questions that empower rather than suppress
    - Consider various cultural contexts and life situations
    - Support human growth and self-determination
    """
        elif context_type == "plan":
            return base_principles + """
    - Create plans that account for individual circumstances
    - Avoid standardized "one-size-fits-all" approaches
    - Consider socio-economic factors and constraints
    - Provide recommendations that empower people
    """
        else:
            return base_principles

    def conscience_check(self, response: str, context: str = "") -> bool:
        """
        Checks if the response aligns with Conscience IQ principles
        Returns True if the response meets ethical standards
        """

        # Basic checks
        concerning_patterns = [
            "only one right way",
            "everyone must",
            "this is wrong for everyone",
            "standard approach",
            "ignore cultural differences"
        ]

        response_lower = response.lower()

        # Check for potentially problematic patterns
        for pattern in concerning_patterns:
            if pattern in response_lower:
                log.warning(f"Conscience check: detected problematic pattern '{pattern}' in response")
                return False

        # Check for positive indicators
        positive_patterns = [
            "considering your",
            "depending on",
            "may vary",
            "individual",
            "personalized"
        ]

        positive_score = sum(1 for pattern in positive_patterns if pattern in response_lower)

        if positive_score > 0:
            log.info(f"Conscience check: found {positive_score} positive indicators")
            return True

        # Default to passing if no explicit problems found
        return True

    def get_principles_summary(self) -> str:
        """Returns a summary of principles for logging"""
        return """
        Conscience IQ Framework:
        1. Dignity > Efficiency
        2. Fairness and inclusivity
        3. Transparency and accountability
        4. Support for human well-being
        5. Cultural diversity
        6. Ethical review of all decisions
        """