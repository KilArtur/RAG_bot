from jinja2 import Template
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from services.GPTService import GPTService
from services.RAGService import RAGService
from services.registry import REGISTRY
import yaml

prompt_file_path = 'prompts.yml'
with open(prompt_file_path, 'r', encoding='utf-8') as file:
    data = yaml.safe_load(file)

validation_prompt = Template(data['validation_prompt'])
find_useful_info_prompt = Template(data['find_useful_info'])
answer_on_question_prompt = Template(data['answer_on_question'])

class QueryService:

    def __init__(self):
        self.gpt_service: GPTService = REGISTRY.get(GPTService)
        self.rag_service: RAGService = REGISTRY.get(RAGService)


    async def process(self, message: str, update: Update, context: CallbackContext):
        if await self.query_validation(message, update, context):
            return
        info = self.rag_service.find(message)
        await self.answer_on_question(message, info, update, context)


    async def query_validation(self, message, update: Update, context: CallbackContext):
        current_prompt = validation_prompt.render(message=message)
        response = await self.gpt_service.fetch_completion(current_prompt,
                                                           {"max_tokens": 100})
        lines = response.split("\n")
        profanity_check = lines[0].split()[1]
        relevance_check = lines[1].split()[1]

        if profanity_check.lower() == "да":
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Ваш запрос содержит оскорбления. Пожалуйста, избегайте такого языка.")
            return True
        elif relevance_check.lower() == "нет":
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text="Ваш запрос не относится к теме этого бота.")
            return True
        return False

    async def check_info_for_answer(self, message, info):
        data = []
        data.extend(info[0])
        data.extend(info[1])
        current_prompt = find_useful_info_prompt.render(message=message, data=data)

        response = await self.gpt_service.fetch_completion(current_prompt,
                                                           {"max_tokens": 250})

        def parse_response(response):
            if "Нет ответа" in response:
                return {"found": False, "query": response.split(":")[-1].strip()}
            else:
                try:
                    indices = [int(num.strip()) for num in response.split(",") if num.strip().isdigit()]
                    return {"found": True, "indices": indices}
                except ValueError:
                    return {"found": False, "error": "Некорректный формат ответа"}

        parsed_response = parse_response(response)
        if parsed_response["found"]:
            indices = parsed_response["indices"]
            fragments = [data[i - 1] for i in indices]
            return {
                "answer": await self.generate_answer(message, fragments),
                "links": [fragment.link for fragment in fragments],
                "source": "Локальная информация"
            }
        # else:
            # internet_result = await self.search_online(parsed_response.get("query", message))
            # return {
            #     "answer": internet_result,
            #     "source": "Интернет"
            # }

    async def generate_answer(self, message, fragments):
        current_prompt = answer_on_question_prompt.render(message=message, data = fragments)
        response = await self.gpt_service.fetch_completion(current_prompt, {"max_tokens": 300})
        return response.strip()

    async def answer_on_question(self, message, info, update, context):
        relevant_info = await self.check_info_for_answer(message, info)

        arr = []
        for index, link in enumerate(relevant_info["links"]):
            print(index, link)
            if "@" not in link:
                arr.append([InlineKeyboardButton(text=f"Ссылка {index + 1}", url=link)])
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=relevant_info["answer"], reply_markup=InlineKeyboardMarkup(arr))
