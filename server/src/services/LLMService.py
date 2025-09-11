import json

from openai import AsyncOpenAI

from config.Config import CONFIG
from utils.logger import get_logger

log = get_logger("LLMService")


class LLMService:
    def __init__(self):
        self.openai = AsyncOpenAI(
            api_key=CONFIG.llm.token,
            base_url=CONFIG.llm.url
        )
        self.request_counter = 0
        self.total_input_token = 0
        self.total_output_token = 0

    async def fetch_completion(self, prompt: str, response_format = None, args=None) -> str:
        self.request_counter += 1
        request_id = self.request_counter
        log.info(f"Запрос к llm ({request_id}): {prompt}")

        counter = 0
        while True:
            try:
                res = await self.__fetch_completion(prompt, response_format, args or {})
                log.info(f"Ответ от llm ({request_id}): {res}")

                return res
            except Exception as e:
                counter += 1
                if counter < 3:
                    pass
                    log.warning(f"Ошибка при запросе к llm: {str(e)}")
                else:
                    raise e

    async def __fetch_completion(self, prompt: str, response_format: None, args) -> str:
        try:
            res = await self.openai.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=CONFIG.llm.model,
                temperature=0,
                top_p=0.5,
                response_format = response_format,
                stream=False,
                **args
            )

            if res.usage:
                self.total_input_token += int(res.usage.prompt_tokens)
                self.total_output_token += int(res.usage.completion_tokens)
            else:
                log.warning("No usage info")

            if not res.choices or not res.choices[0].message or not res.choices[0].message.content:
                log.error("LLM returned empty response")
                raise Exception("LLM returned empty response")

            content = str(res.choices[0].message.content)
            if not content.strip():
                log.error("LLM returned empty content")
                raise Exception("LLM returned empty content")

            content = self._sanitize_content(content)
            
            log.debug(f"Обработанный контент, длина: {len(content)}")
            return content

        except Exception as e:
            log.error(f"Ошибка в __fetch_completion: {str(e)}")
            if "401" in str(e) and "User not found" in str(e):
                log.error("OpenRouter API токен недействителен или истек")
                if "express a direct desire to become vegetarian" in prompt.lower():
                    return "NO"
                else:
                    return "Sorry, the service is temporarily unavailable. Please try again later."
            if "Expecting value" in str(e) or "JSON" in str(e):
                log.error("JSON parsing error in OpenAI response - возможно ответ обрезан")
            raise e

    async def fetch_completion_history(self, history, args=None) -> str:
        self.request_counter += 1
        request_id = self.request_counter
        log.info(f"Запрос к llm ({request_id}): {str(json.dumps(history, indent=2, ensure_ascii=False))}")

        counter = 0
        while True:
            try:
                res = await self.__fetch_completion_history(history, args or {})
                log.info(f"Ответ от llm ({request_id}): {res}")

                return res
            except Exception as e:
                counter += 1
                if counter < 3:
                    pass
                    log.warning(f"Ошибка при запросе к gpt: {str(e)}")
                else:
                    raise e

    async def __fetch_completion_history(self, history, args) -> str:
        res = await self.openai.chat.completions.create(
            messages=history,
            model=CONFIG.llm.model,
            temperature=0,
            top_p=0.5,
            stream=False,
            **args
        )

        if res.usage:
            self.total_input_token += int(res.usage.prompt_tokens)
            self.total_output_token += int(res.usage.completion_tokens)
        else:
            log.warning("No usage info")
            pass

        return str(res.choices[0].message.content)
    
    def _sanitize_content(self, content: str) -> str:
        if not content:
            return content

        content = content.replace('\x00', '')
        content = content.replace('\ufeff', '')  # BOM символ

        content = content.strip()

        try:
            json.dumps(content, ensure_ascii=False)
        except (TypeError, ValueError) as e:
            log.warning(f"Проблема с JSON сериализацией: {e}")
            content = ''.join(char for char in content if ord(char) < 128 or (0x400 <= ord(char) <= 0x4FF))
        
        return content