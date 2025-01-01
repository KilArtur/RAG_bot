from openai import AsyncOpenAI

from config.Config import CONFIG


# log = get_logger("GPT")


class GPTService:
    def __init__(self):
        self.openai = AsyncOpenAI(
            api_key=CONFIG.gpt.token,
            base_url=CONFIG.gpt.url
        )
        self.request_counter = 0
        self.total_input_token = 0
        self.total_output_token = 0

    async def fetch_completion(self, prompt: str, args=None) -> str:
        # model_key - ключ модели (например, 'model_recalculate' или 'model_matching')
        self.request_counter += 1
        request_id = self.request_counter
        # log.info(f"Запрос к gpt ({request_id}): {prompt}")

        counter = 0
        while True:
            try:
                res = await self.__fetch_completion(prompt, args or {})
                # log.info(f"Ответ от gpt ({request_id}): {res}")

                return res
            except Exception as e:
                counter += 1
                if counter < 3:
                    pass
                    # log.warning(f"Ошибка при запросе к gpt: {str(e)}")
                else:
                    raise e

    async def __fetch_completion(self, prompt: str, args) -> str:
        res = await self.openai.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=CONFIG.gpt.model,
            temperature=0,
            top_p=0.5,
            stream=False,
            **args
        )

        if res.usage:
            self.total_input_token += int(res.usage.prompt_tokens)
            self.total_output_token += int(res.usage.completion_tokens)
        else:
            # log.warning("No usage info")
            pass

        return str(res.choices[0].message.content)

    async def fetch_completion_history(self, history, args=None) -> str:
        # model_key - ключ модели (например, 'model_recalculate' или 'model_matching')
        self.request_counter += 1
        request_id = self.request_counter
        # log.info(f"Запрос к gpt ({request_id}): {prompt}")

        counter = 0
        while True:
            try:
                res = await self.__fetch_completion_history(history, args or {})
                # log.info(f"Ответ от gpt ({request_id}): {res}")

                return res
            except Exception as e:
                counter += 1
                if counter < 3:
                    pass
                    # log.warning(f"Ошибка при запросе к gpt: {str(e)}")
                else:
                    raise e

    async def __fetch_completion_history(self, history, args) -> str:
        res = await self.openai.chat.completions.create(
            messages=history,
            model=CONFIG.gpt.model,
            temperature=0,
            top_p=0.5,
            stream=False,
            **args
        )

        if res.usage:
            self.total_input_token += int(res.usage.prompt_tokens)
            self.total_output_token += int(res.usage.completion_tokens)
        else:
            # log.warning("No usage info")
            pass

        return str(res.choices[0].message.content)
