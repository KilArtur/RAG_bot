from dataclasses import dataclass
import psycopg2
from sentence_transformers import SentenceTransformer

from config.Config import CONFIG

@dataclass
class RAGInfo:
    text: str
    link: str
    rank: float

class RAGService:
    def __init__(self):
        self.model = SentenceTransformer("intfloat/multilingual-e5-large")
        self.top_k = 5
        DB_PARAMS = {
            "dbname": CONFIG.db.name,
            "user": CONFIG.db.user,
            "password": CONFIG.db.password,
            "host": CONFIG.db.host,
            "port": CONFIG.db.port
        }
        self.conn = psycopg2.connect(**DB_PARAMS)

    # def __del__(self):
    #     self.conn.close()

    def vector_search(self, query: str):
        """Искать похожие тексты"""
        query_embedding = self._get_embedding(query)
        query_embedding_str = ",".join(map(str, query_embedding))

        with self.conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT text, link, 1 - (embedding <=> '[{query_embedding_str}]'::vector) AS similarity
                FROM texts
                ORDER BY similarity DESC
                LIMIT %s
                """,
                (self.top_k,)
            )
            results = cur.fetchall()
        return [RAGInfo(text=row[0], link=row[1], rank=row[2]) for row in results]

    def text_search(self, query):
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT text, link, ts_rank_cd(tsv, plainto_tsquery('russian', %s)) AS rank
                FROM texts
                WHERE tsv @@ plainto_tsquery('russian', %s)
                ORDER BY rank DESC
                LIMIT %s;
                """,
                (query, query, self.top_k)
            )
            results = cur.fetchall()
            return [RAGInfo(text=row[0], link=row[1], rank=row[2]) for row in results]

    def find(self, query):
        return self.vector_search(query), self.text_search(query)

    def _get_embedding(self, text: str) -> list:
        """Получить векторное представление текста"""
        formatted_text = 'query: ' + text  # Используем `query:` для текстов запроса
        embedding = self.model.encode(formatted_text, normalize_embeddings=True)
        return embedding.tolist()