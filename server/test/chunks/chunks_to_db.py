import pandas as pd
import psycopg2
import numpy as np
from sentence_transformers import SentenceTransformer

from config.Config import CONFIG
from services.RAGService import RAGService

# DB_PARAMS = {
#     "dbname": CONFIG.db.name,
#     "user": CONFIG.db.user,
#     "password": CONFIG.db.password,
#     "host": CONFIG.db.host,
#     "port": CONFIG.db.port
# }
#
# model = SentenceTransformer("intfloat/multilingual-e5-large")
#
# def get_embedding(text: str) -> list:
#     """Получить векторное представление текста"""
#     # Префикс для E5-модели
#     formatted_text = f"{text}"  # Используем `query:` для текстов запроса
#     embedding = model.encode(formatted_text, normalize_embeddings=True)
#     return embedding.tolist()
#
# def add_text_to_db(conn, text: str):
#     """Добавить текст и его векторное представление в базу данных"""
#     embedding = get_embedding(text)
#     with conn.cursor() as cur:
#         cur.execute(
#             "INSERT INTO texts (text, embedding, link) VALUES (%s, %s, %s)",
#             (text, embedding)
#         )
#     conn.commit()
#
# def search_similar_texts(conn, query: str, top_k: int = 5):
#     """Искать похожие тексты"""
#     query_embedding = get_embedding(query)
#     query_embedding_str = ",".join(map(str, query_embedding))
#
#     with conn.cursor() as cur:
#         cur.execute(
#             f"""
#             SELECT text, 1 - (embedding <=> '[{query_embedding_str}]'::vector) AS similarity
#             FROM texts
#             ORDER BY similarity DESC
#             LIMIT %s
#             """,
#             (top_k,)
#         )
#         results = cur.fetchall()
#
#     return results
#
# def main():
#     conn = psycopg2.connect(**DB_PARAMS)
#
#     text = "This is a multilingual test example."
#     print(f"Adding text: {text}")
#     add_text_to_db(conn, text)
#
#     query = "multilingual example"
#     print(f"Searching for texts similar to: {query}")
#     results = search_similar_texts(conn, query)
#     for rank, (text, similarity) in enumerate(results, start=1):
#         print(f"{rank}. {text} (similarity: {similarity:.4f})")
#
#     conn.close()

if __name__ == "__main__":
    rag_service = RAGService()
    print("load_rag")
    # rag_service.add_record("Пример текста", "http://example.com")
    path_to_csv = "chunks/chunks.csv"
    df = pd.read_csv(path_to_csv).dropna()
    print(df.info())
    for index, row in df.iterrows():
        print(index, row['link'])
        if row['question'] != 'nan':
            rag_service.add_record(row['question'], row['link'])

    # main()


