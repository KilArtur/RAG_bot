import asyncio
import os
from openai import AsyncOpenAI


input_folder = "output"
output_folder = "processed_output"
os.makedirs(output_folder, exist_ok=True)

openai = AsyncOpenAI(
            api_key="",
            base_url="https://caila.io/api/adapters/openai"
        )

async def process_text_with_gpt(text, model="text-davinci-003", max_tokens=512):
    prompt = (
        "Разбей этот текст на информативные блоки, которые можно использовать для RAG системы"
        "Каждый блок должен содержать до 512 токенов и четко разграничивать информацию "
        "Блоки должны быть комплексными и информативными, чтобы обеспечить максимальную ценность для справочной информации об университете "
        "Пожалуйста, придерживайся следующих правил:\n"
        "1) Каждый блок должен быть темой и максимально содержательным; наличие информации должно быть актуальным и распространяемым.\n"
        "2) Убедись, что каждый блок имеет четкое название, включая основную тему, и он должен четко указывать на содержание блока.\n"
        "3) В каждом блоке обязательно указывай ссылку на источник информации, чтобы можно было получить дополнительную информацию. "
        "4) Блоки обязательно должны разделяться с помощью -------"
        "5) Все названия и конец блока должны начинаться и заканчиваться с ###"
        "Важно если тебе не дали никакого текста для разбивки, возвращай позитивные отзывы об университете ГУАП которые подходят под вышеуказанный стандарт"
        f"Вот текст для разбивки:\n\n{text}"
    )
    try:
        response = await openai.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="just-ai/openai-proxy/gpt-4o-mini",
            temperature=0,
            top_p=0.5,
            stream=False,
        )

        # if response.usage:
        #     total_input_token += int(response.usage.prompt_tokens)
        #     total_output_token += int(response.usage.completion_tokens)
        # else:
        #     log.warning("No usage info")

        return response.choices[0].message.content
    except Exception as e:
        print(f"Ошибка при обработке текста: {e}")
        return None


async def process_files(input_folder, output_folder):
    с = 0
    for file_name in os.listdir(input_folder):
        input_file_path = os.path.join(input_folder, file_name)

        # Проверяем, что это файл, а не папка
        if os.path.isfile(input_file_path):
            with open(input_file_path, "r", encoding="utf-8") as file:
                text = file.read()

            # Обрабатываем текст через GPT
            processed_text = await process_text_with_gpt(text)

            if processed_text:
                # Генерируем путь для сохранения нового файла
                output_file_name = f"processed_{file_name}"
                output_file_path = os.path.join(output_folder, output_file_name)

                with open(output_file_path, "w", encoding="utf-8") as output_file:
                    output_file.write(processed_text)
                print(f"Файл {file_name} успешно обработан.")
                # с += 1
                # if с > 5:
                #     break
            else:
                print(f"Файл {file_name} не удалось обработать.")
                # с += 1
                # if с > 5:
                #     break



if __name__ == "__main__":
    asyncio.run(process_files(input_folder, output_folder))