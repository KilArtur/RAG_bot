import os
import pandas as pd

# Папка с txt файлами
folder_path = "processed_output"

# Результирующий DataFrame
data = {
    "text": [],
    "link": []
}

# Проходим по всем файлам в папке
for file_name in os.listdir(folder_path):
    if file_name.endswith(".txt"):
        file_path = os.path.join(folder_path, file_name)

        # Ссылка: удаляем префикс "processed_", заменяем "_" обратно на "/" и добавляем "https://"
        link = "https://" + file_name.replace("processed_", "").replace("_", "/").replace(".txt", "")

        # Читаем содержимое файла
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Делим содержимое по разделителю "___"
        records = content.split("___")

        # Добавляем записи в DataFrame
        for record in records:
            clean_record = record.strip()
            if clean_record:  # Пропускаем пустые строки
                data["text"].append(clean_record.replace("'", ""))
                data["link"].append(link)

# Создаем DataFrame
df = pd.DataFrame(data)

# Сохраняем в CSV
output_file = "output.csv"
df.to_csv(output_file, index=False, encoding="utf-8")

print(f"CSV файл '{output_file}' успешно создан.")