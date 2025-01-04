import ast
from markdownify import markdownify
import requests
from bs4 import BeautifulSoup
from jinja2 import Template
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from services.GPTService import GPTService
from services.RAGService import RAGService, RAGInfo
from services.registry import REGISTRY
import yaml
import re

from utils.logger import get_logger

prompt_file_path = 'prompts.yml'
with open(prompt_file_path, 'r', encoding='utf-8') as file:
    data = yaml.safe_load(file)

agent_prompt = Template(data['agent_prompt'])

log = get_logger("QueryService")


class QueryService:

    def __init__(self):
        self.gpt_service: GPTService = REGISTRY.get(GPTService)
        self.rag_service: RAGService = REGISTRY.get(RAGService)

    def extract_action(self, output):
        match = re.search(r"Действие:\s*(\w+)\((.*?)\)", output)
        if match:
            action_name = match.group(1)
            action_input = match.group(2).strip()
            log.info(f"call tool: {action_name}, arguments: {action_input}")
            return action_name, action_input
        log.info(f"not found tool calling")
        return None, None

    def web_search(self, query: str):
        try:
            query = query if "гуап" in query.lower() else "ГУАП " + query
            search_url = "https://www.google.com/search"
            params = {
                "q": query
            }
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
            }
            response = requests.get(search_url, params=params, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            search_div = soup.find("div", id="search")

            first_link_tags = search_div.find_all("a")
            for first_link_tag in first_link_tags:
                if not first_link_tag:
                    continue

                first_link: str = first_link_tag.get("href", "")

                if not first_link:
                    continue

                if not first_link.startswith('http'):
                    continue
                page_response = requests.get(first_link, headers=headers)
                page_response.raise_for_status()
                content_type = page_response.headers.get('Content-Type', '')
                if 'text/html' in content_type:
                    page_response.encoding = 'utf-8'

                    soup = BeautifulSoup(page_response.text, 'html.parser')
                    for img in soup.find_all('img'):
                        img.decompose()  # Удаляет тег изображения из дерева DOM

                    # Преобразование оставшегося HTML в Markdown
                    markdown_content = markdownify(str(soup)).strip()

                    markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content)

                    return RAGInfo(id =100, text=markdown_content, link=first_link, rank=1)
        except Exception as e:
            log.error(f"Query: {query}, web_search dosent work", exc_info=e)
            return RAGInfo(id =100, text=f"Ошибка: {e}", link='', rank=1)

    async def action(self, history, info: list[RAGInfo], max_iterations=5):
        text = ""
        response = await self.gpt_service.fetch_completion_history(history)
        for _ in range(max_iterations):
            history.append({'role': 'assistant', 'content': response})
            trace = ""
            action_name, action_input = self.extract_action(response)
            if not action_name:
                trace += "Error: No action detected\n"
                history.append({'role': 'system', 'content': trace})
            elif action_name == "web_search":
                observation = self.web_search(action_input[1:-1])
                info.append(observation)
                trace += f"Observation: Информация:\n{len(info)}. {observation.text}\n"
                history.append({'role': 'system', 'content': trace})
            elif action_name == "final_answer":
                answer = action_input[1:-1]
                history.append({'role': 'system', 'content': f"Какая информация помогла ответить на вопрос?"})
                text = answer
                # return answer
            elif action_name == "helpful_infos":
                answer = action_input
                # history.append({'role': 'system', 'content': f"Какая информация помогла ответить на вопрос?"})
                ids = ast.literal_eval(answer)
                res = [info[id - 1] for id in ids if id in range(len(info)+1)]
                unique_links = set()
                unique_res = []

                for obj in res:
                    if obj.link not in unique_links:
                        unique_links.add(obj.link)
                        unique_res.append(obj)
                return text, unique_res
            elif action_name == "insult_in_request":
                answer = "Ваш запрос содержит оскорбления. Пожалуйста, избегайте такого языка."
                history.append({'role': 'system', 'content': f"Final Answer: {answer}"})
                return answer, []
            elif action_name == "off_topic_question":
                answer = "Ваш запрос не относится к теме этого бота."
                history.append({'role': 'system', 'content': f"Final Answer: {answer}"})
                return answer, []
            else:
                trace += f"Error: Unknown action: {action_name}\n"
                history.append({'role': 'system', 'content': trace})
            log.info(f"Agent trace: {trace}")
            response = await self.gpt_service.fetch_completion_history(history)

        return "Ответ не удалось получить за указанное число итераций.", []

    async def process(self, message: str, update: Update, context: CallbackContext):
        info = self.rag_service.find(message)
        log.info(f"Find info: {info}")
        current_prompt = agent_prompt.render(user_question=message, data=info[0])
        log.info(f"Agent prompt: {current_prompt}")
        response = await self.action([{'role': 'user', 'content': current_prompt}], info[0])
        log.info(f"Agent response text:\n{response[0]}\nhelpful info: {response[1]}")
        buttons = []
        for index, rag_info in enumerate(response[1][:5]):
            print(index, rag_info)
            if "@" not in rag_info.link:
                buttons.append(InlineKeyboardButton(text=f"Ссылка {index + 1}", url=rag_info.link))

        keyboard = []
        for i in range(0, len(buttons), 2):
            keyboard.append(buttons[i:i + 2])

        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=response[0], reply_markup=InlineKeyboardMarkup(keyboard))