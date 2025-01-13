import asyncio
import re

import pandas as pd
import requests
import yaml
from jinja2 import Template
from markdownify import markdownify
from services.GPTService import GPTService

gpt_service = GPTService()

prompt_file_path = 'prompts.yml'
with open(prompt_file_path, 'r', encoding='utf-8') as file:
    data = yaml.safe_load(file)

question_generation = Template(data['question_by_page'])

pattern = r'-> (.+)'

def get_page_content(link):
    """Получает содержимое страницы и конвертирует его в Markdown."""
    try:
        page_response = requests.get(link)
        page_response.raise_for_status()
        markdown_content = markdownify(page_response.text).strip()
        markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content)
        return markdown_content
    except requests.RequestException as e:
        print(f"Error: Ошибка при получении содержимого страницы {link}: {e}")
        return None

async def process_link(link, semaphore, results):
    """Обрабатывает каждую ссылку, создавая запрос к GPT и собирая результаты."""
    page_content = get_page_content(link)
    if not page_content:
        print(f"Пропускаем ссылку {link}, так как содержимое страницы недоступно.")
        return

    current_prompt = question_generation.render(page_text=page_content)
    async with semaphore:
        try:
            response = await gpt_service.fetch_completion(current_prompt)
            if "bad_info" in response.lower():
                print(f"BAD_LINK: Ссылка {link} некорректна или не содержит полезной информации.")
            elif "questions" in response.lower():
                lines = response.splitlines()
                for line in lines:
                    match = re.match(pattern, line)
                    if match:
                        results.append({"question": match.group(1), "link": link})
        except Exception as e:
            print(f"Error: Ошибка при обработке {link}: {e}")

async def main(file_path, output_csv):
    """Главная функция для обработки ссылок и сохранения результатов."""
    semaphore = asyncio.Semaphore(20)
    results = []  # Список для сбора данных

    with open(file_path, 'r') as file:
        links = [line.strip() for line in file if line.strip()]

    tasks = [process_link(link, semaphore, results) for link in links]
    await asyncio.gather(*tasks)

    # Сохраняем результаты в CSV через pandas
    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False, encoding='utf-8')

if __name__ == "__main__":
    asyncio.run(main("links.txt", "benchmark/questions.csv"))
