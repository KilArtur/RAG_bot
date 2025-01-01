import asyncio
from dataclasses import dataclass

import requests
import yaml
from bs4 import BeautifulSoup
from googlesearch import search
from jinja2 import Template

from services.GPTService import GPTService
from services.RAGService import RAGService


@dataclass
class PointerData:
    link: str
    name: str

@dataclass
class ResponseData:
    text: str
    pointers: list[PointerData]

gpt_service = GPTService()
# rag_service = RAGService()

prompt_file_path = 'prompts.yml'
with open(prompt_file_path, 'r', encoding='utf-8') as file:
    data = yaml.safe_load(file)

agent_prompt = Template(data['agent_prompt'])

import re

def extract_action(output):
    match = re.search(r"Действие:\s*(\w+)\((.*?)\)", output)
    if match:
        action_name = match.group(1)
        action_input = match.group(2).strip()
        return action_name, action_input
    return None, None


def web_search(query: str):
    try:
        query = query if "гуап" in query.lower() else "ГУАП"+query
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
        if not search_div:
            return "Не удалось найти div с id='search'."


        first_link_tag = search_div.find("a")
        if not first_link_tag:
            return "Не удалось найти первую ссылку в div с id='search'."


        first_link = first_link_tag.get("href", "")

        if not first_link:
            return "Не удалось найти первую ссылку."

        page_response = requests.get(first_link, headers=headers)
        page_response.raise_for_status()

        page_soup = BeautifulSoup(page_response.text, "html.parser")
        page_text = page_soup.get_text(separator="\n").strip()

        return page_text
    except Exception as e:
        return f"Ошибка: {e}"

async def action(history, max_iterations=5):
    response = await gpt_service.fetch_completion_history(history)
    for _ in range(max_iterations):
        history.append({'role': 'assistant', 'content': response})
        trace = ""
        action_name, action_input = extract_action(response)

        if not action_name:
            trace += "Error: No action detected\n"
            history.append({'role': 'system', 'content': trace})
        elif action_name == "web_search":
            observation = web_search(action_input)
            trace += f"Observation: {observation}\n"
            history.append({'role': 'system', 'content': trace})
        elif action_name == "final_answer":
            answer = action_input
            history.append({'role': 'system', 'content': f"Final Answer: {answer}"})
            return answer
        elif action_name == "insult_in_request":
            answer = "Ваш запрос содержит оскорбления. Пожалуйста, избегайте такого языка."
            history.append({'role': 'system', 'content': f"Final Answer: {answer}"})
            return answer
        elif action_name == "bad_request":
            answer = "Ваш запрос не относится к теме этого бота."
            history.append({'role': 'system', 'content': f"Final Answer: {answer}"})
            return answer
        else:
            trace += f"Error: Unknown action: {action_name}\n"
            history.append({'role': 'system', 'content': trace})

        response = await gpt_service.fetch_completion_history(history)

    return "Ответ не удалось получить за указанное число итераций."


# async def agent(history):
#     response = await gpt_service.fetch_completion_history(history)
#     return action(response, history)

async def process_query(query: str):
    current_prompt = agent_prompt.render(user_question=query, data=[])
    response = await action([{'role': 'user', 'content': current_prompt}])
    print(response)

if __name__ == "__main__":
    query = "Кто такая Татарникова?"
    asyncio.run(process_query(query))
    # print(response)
    # for pointer in response.pointers:
    #     print(f"{pointer.name} -> {pointer.link}")