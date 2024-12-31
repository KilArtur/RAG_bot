import os
import pandas as pd
import re

input_directory = 'processed_output'
output_csv = 'output_blocks.csv'

def clean_text(text):
    """Очищает текст от лишних символов и улучшает форматирование."""
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s,.]', '', text)
    text = text.strip()
    text = re.sub(r'([,.])([^\s])', r'\1 \2', text)
    return text

def clean_link(link):
    link = re.sub(r'\)?\.?$', '', link)
    return link.strip()

def extract_blocks_and_links(text):
    blocks = text.split('-------')
    extracted_data = []

    for block in blocks:
        block = block.strip()
        if block:
            link_match = re.search(r'(https?://[^\s)]+)', block)
            link = clean_link(link_match.group(0)) if link_match else ''
            cleaned_block = clean_text(block)
            extracted_data.append({'text': cleaned_block, 'link': link})

    return extracted_data

data = []

for filename in os.listdir(input_directory):
    if filename.endswith('.txt'):
        with open(os.path.join(input_directory, filename), 'r', encoding='utf-8') as file:
            text = file.read()

            blocks_and_links = extract_blocks_and_links(text)

            for item in blocks_and_links:
                data.append(item)

df = pd.DataFrame(data)
df.to_csv(output_csv, index=False, encoding='utf-8-sig')
print(f"Блоки успешно сохранены в CSV: {output_csv}")
