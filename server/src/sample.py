import re
import json

from openai import OpenAI
from pydantic import BaseModel

url = "http://localhost:5000/v1"

client = OpenAI(
    base_url=url,
    api_key='a'
)

prompt = "верни ответ на выражение: 4*23+3*21 и объяснение как ты решал"

json_schema = {
    "type": "object",
    "properties": {
        "answer": {"type": "number"},
        "reasoning": {"type": "string"}
    },
    "required": ["answer", "reasoning"]
}

response = client.chat.completions.create(
        model="Qwen/Qwen3-0.6B",
        messages=[
            {"role": "user", "content": prompt}
        ],
        extra_body={
                # "stop": ["<think>", "</think>"],
                "skip_special_tokens": False
            },
        # response_format={
        #     "type": "json_object",
        #     "schema": json_schema
        # },
        temperature=0.1,
    )

content = response.choices[0].message.content
print(content)
# clean_content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
#
# try:
#     result = json.loads(clean_content)
#     print("Результат:", result)
#     print("Ответ:", result.get("answer"))
#     print("Объяснение:", result.get("reasoning"))
# except json.JSONDecodeError:
#     print("Не удалось распарсить JSON:", clean_content)