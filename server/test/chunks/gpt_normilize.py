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

semaphore = asyncio.Semaphore(20)

async def process_text_with_gpt(text, model="text-davinci-003", max_tokens=512):
    prompt = (
        f"""Ты пишешь справочник, для студентов университета ГУАП.
На вход тебе придёт текст со страницы сайта университета.
Твоя задача разбить текст на не большие смысловые блоки, где должен быть краткий контекст от куда этот блок и сама информация. 
Каждый блок не должен превышать 512 токенов. Блоки должны быть чётко разграничены. 
В ответ должен идти просто текст с информацией в блоке и символы для разграничения.
ВАЖНО блок должен иметь контекст от куда он был взят если мы например говорим о какой то группе например в ВК надо указать что это за группа кто ей управляет (если есть такая информация).
Пример:
'
По вопросам поступления в магистратуру ГУАП можно обратится в кабинет 1234 по адресу ул. Большая Морская, д. 67, лит. А, Санкт-Петербург, 190000, Россия ответственный по вопросам кто то.

___

Центр карьеры ГУАП занимается подготовкой высококвалифицированных кадров для стратегических отраслей российской экономики, таких как авиастроение и космическая отрасль. Он направлен на повышение конкурентоспособности выпускников университета и развитие партнерских отношений с ведущими работодателями.

'

Текст с сайта:\n\n{text}"""
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


async def process_file(file_name, input_folder, output_folder):
    input_file_path = os.path.join(input_folder, file_name)
    output_file_name = f"processed_{file_name}"
    output_file_path = os.path.join(output_folder, output_file_name)

    if os.path.isfile(input_file_path):
        try:
            async with semaphore:
                with open(input_file_path, "r", encoding="utf-8") as file:
                    text = file.read()

                processed_text = await process_text_with_gpt(text)

                if processed_text:
                    with open(output_file_path, "w", encoding="utf-8") as output_file:
                        output_file.write(processed_text)
                    print(f"Файл {file_name} успешно обработан.")
                else:
                    print(f"Файл {file_name} не удалось обработать.")
        except Exception as e:
            print(f"Ошибка при обработке файла {file_name}: {e}")

async def process_files(input_folder, output_folder):
    tasks = [
        process_file(file_name, input_folder, output_folder)
        for file_name in os.listdir(input_folder)
    ]
    await asyncio.gather(*tasks)



if __name__ == "__main__":
    asyncio.run(process_files(input_folder, output_folder))