import asyncio
import os
from pathlib import Path
import yaml
from jinja2 import Template
import fitz
from services.LLMService import LLMService
from utils.logger import get_logger

log = get_logger("PDFToChunks")


class PDFChunkProcessor:
    def __init__(self):
        self.llm_service = LLMService()
        self.load_prompts()

    def load_prompts(self):
        prompt_file_path = 'prompts.yml'
        with open(prompt_file_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        self.chunks_prompt = Template(data['chunks_promt'])

    def extract_text_from_pdf(self, pdf_path: str) -> list[str]:
        log.info(f"Читаю PDF файл: {pdf_path}")
        pages_text = []

        try:
            pdf_document = fitz.open(pdf_path)
            for page_num in range(pdf_document.page_count):
                page = pdf_document.load_page(page_num)
                text = page.get_text()
                if text.strip():
                    if len(text) > 1000:
                        pages_text.append(text)
                        log.info(f"Страница {page_num + 1}: извлечено {len(text)} символов")
                    else:
                        log.info(f"Страницу {page_num + 1} не извлекаем, мало информации")
            pdf_document.close()
        except Exception as e:
            log.error(f"Ошибка при чтении PDF: {e}")
            raise

        log.info(f"Всего извлечено {len(pages_text)} страниц с текстом")
        return pages_text

    async def process_page_to_chunks(self, page_text: str) -> list[str]:
        if not page_text.strip():
            return []

        prompt = self.chunks_prompt.render(text_to_chunks=page_text)
        log.info(f"Отправляю запрос на разбивку чанков для текста длиной {len(page_text)} символов")

        try:
            response = await self.llm_service.fetch_completion(prompt)

            chunks = []
            lines = response.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('Чанк') and len(line) > 20:
                    chunks.append(line)

            log.info(f"Получено {len(chunks)} чанков")
            return chunks

        except Exception as e:
            log.error(f"Ошибка при обработке через LLM: {e}")
            return []

    def save_chunks(self, chunks: list[str], output_dir: str):
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        for i, chunk in enumerate(chunks, 1):
            chunk_filename = output_path / f"chunk_{i}.txt"
            with open(chunk_filename, 'w', encoding='utf-8') as f:
                f.write(chunk)
            log.info(f"Сохранен чанк {i}: {len(chunk)} символов в файл {chunk_filename}")

    async def process_pdf(self, pdf_path: str, output_dir: str):
        log.info(f"Начинаю обработку PDF: {pdf_path}")

        pages_text = self.extract_text_from_pdf(pdf_path)

        all_chunks = []

        for page_num, page_text in enumerate(pages_text, 1):
            log.info(f"Обрабатываю страницу {page_num}")
            page_chunks = await self.process_page_to_chunks(page_text)
            all_chunks.extend(page_chunks)

        log.info(f"Всего получено {len(all_chunks)} чанков")

        self.save_chunks(all_chunks, output_dir)

        log.info("Обработка завершена!")


async def main():
    pdf_path = "../../data/book_sample.pdf"
    output_dir = "../../data/chunks"

    processor = PDFChunkProcessor()
    await processor.process_pdf(pdf_path, output_dir)


if __name__ == "__main__":
    asyncio.run(main())