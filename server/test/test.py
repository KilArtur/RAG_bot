import psycopg2
import numpy as np
from sentence_transformers import SentenceTransformer


DB_PARAMS = {
    "dbname": "vector_db",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5436"
}

model = SentenceTransformer("intfloat/multilingual-e5-large")

def get_embedding(text: str) -> list:
    """Получить векторное представление текста"""
    # Префикс для E5-модели
    formatted_text = f"query: {text}"  # Используем `query:` для текстов запроса
    embedding = model.encode(formatted_text, normalize_embeddings=True)
    return embedding.tolist()

def add_text_to_db(conn, text: str):
    """Добавить текст и его векторное представление в базу данных"""
    embedding = get_embedding(text)
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO texts (text, embedding) VALUES (%s, %s)",
            (text, embedding)
        )
    conn.commit()

def search_similar_texts(conn, query: str, top_k: int = 5):
    """Искать похожие тексты"""
    query_embedding = get_embedding(query)
    query_embedding_str = ",".join(map(str, query_embedding))

    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT text, 1 - (embedding <=> '[{query_embedding_str}]'::vector) AS similarity
            FROM texts
            ORDER BY similarity DESC
            LIMIT %s
            """,
            (top_k,)
        )
        results = cur.fetchall()

    return results

def main():
    conn = psycopg2.connect(**DB_PARAMS)

    text = "This is a multilingual test example."
    print(f"Adding text: {text}")
    add_text_to_db(conn, text)

    query = "multilingual example"
    print(f"Searching for texts similar to: {query}")
    results = search_similar_texts(conn, query)
    for rank, (text, similarity) in enumerate(results, start=1):
        print(f"{rank}. {text} (similarity: {similarity:.4f})")

    conn.close()

if __name__ == "__main__":
    main()
