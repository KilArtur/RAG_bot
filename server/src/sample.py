import re
import json

from typing import Optional

from openai import OpenAI
from pydantic import BaseModel, Field

url = "http://localhost:8000/v1"

model_name = "hugging-quants/Meta-Llama-3.1-8B-Instruct-AWQ-INT4"

client = OpenAI(
    base_url=url,
    api_key=''
)

class OtherInfo(BaseModel):
    city_of_residence: Optional[str] = Field(default=None, description="Город проживания человека")
    years_of_residence: Optional[int] = Field(default=None, description="Количество лет проживания человека в городе")
    mother_name: Optional[str] = Field(default=None, description="Имя матери пользователя")

class PersonInfo(BaseModel):
    name: Optional[str] = Field(default=None, description="Имя человека")
    birth_city: Optional[str] = Field(default=None, description="Город рождения")
    age: Optional[int] = Field(default=None, description="Возраст в годах")
    other_info: OtherInfo

prompt = """Меня зовут Артур, я из города Сургута (это мой родной город), мне 19 лет. 
Я учусь на программиста в городе Санкт-Петербург и проживаю в нем уже 3 года.

Извлеки всю доступную информацию:
- Имя
- Город рождения (откуда родом)
- Текущий город проживания (где живет сейчас)
- Количество лет проживания в текущем городе
- Возраст
- Имя матери пользователя

ВАЖНО: Если информация отсутствует в тексте, используй null"""

response = client.chat.completions.create(
    model=model_name,
    messages=[
        {"role": "user", "content": prompt}
    ],
    temperature=0.0,
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "person_info",
            "schema": PersonInfo.model_json_schema(),
            "strict": True
        }
    }
)

content = response.choices[0].message.content
parsed_data = json.loads(content)
print(json.dumps(parsed_data, ensure_ascii=False, indent=2))