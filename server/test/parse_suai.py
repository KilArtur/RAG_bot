from langchain_community.document_loaders import WebBaseLoader
from bs4 import BeautifulSoup
import requests
import os
from concurrent.futures import ThreadPoolExecutor, as_completed


# Функция для извлечения всех ссылок с карты сайта
def extract_links_from_page(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Не удалось загрузить страницу: {response.status_code}")

    soup = BeautifulSoup(response.content, "html.parser")
    # Извлекаем все теги <a> с атрибутом href
    links = [a['href'] for a in soup.find_all("a", href=True)]
    return links


# Функция для сохранения текста в файл
def save_text_to_file(text, source_url, output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"{source_url.replace('https://', '').replace('/', '_')}.txt")
    with open(filename, "w", encoding="utf-8") as file:
        file.write(f"Источник: {source_url}\n\n")
        file.write(text)
    print(f"Сохранено: {filename}")


# Функция для обработки одной ссылки
def process_link(link: str, output_dir="output"):
    try:
        if not link.startswith('http'):
            link = "https://guap.ru" + link
        loader = WebBaseLoader(link)
        documents = loader.load()
        for doc in documents:
            save_text_to_file(doc.page_content, link, output_dir=output_dir)
    except Exception as e:
        print(f"Ошибка обработки {link}: {e}")


# Основной скрипт
def main():
    sitemap_url = "https://guap.ru/sitemap"
    output_dir = "output"
    max_threads = 10  # Установите количество потоков

    print("Загружаем ссылки из sitemap...")
    links = extract_links_from_page(sitemap_url)
    print(f"Найдено ссылок: {len(links)}")

    # Параллельная обработка ссылок
    with ThreadPoolExecutor(max_threads) as executor:
        future_to_link = {executor.submit(process_link, link, output_dir): link for link in links}

        for future in as_completed(future_to_link):
            link = future_to_link[future]
            try:
                future.result()  # Получение результата для отслеживания ошибок
            except Exception as e:
                print(f"Ошибка в обработке {link}: {e}")


if __name__ == "__main__":
    main()
