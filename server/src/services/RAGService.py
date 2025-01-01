import os
import tempfile
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
import psycopg2
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser

from config.Config import CONFIG


@dataclass
class RAGInfo:
    id: int
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

        self.index_path = "/tmp/rag_index"
        schema = Schema(id=ID(stored=True, unique=True), text=TEXT(stored=True), link=ID(stored=True))
        if not os.path.exists(self.index_path):
            os.mkdir(self.index_path)
            self.index = create_in(self.index_path, schema)
        else:
            self.index = open_dir(self.index_path)

    def vector_search(self, query: str):
        """Искать похожие тексты"""
        query_embedding = self._get_embedding(query)
        query_embedding_str = ",".join(map(str, query_embedding))

        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, text, link, 1 - (embedding <=> %s::vector) AS similarity
                FROM texts
                ORDER BY similarity DESC
                LIMIT %s
                """,
                (query_embedding, self.top_k)
            )
            results = cur.fetchall()
        return [RAGInfo(id=row[0], text=row[1], link=row[2], rank=row[3]) for row in results]

    def text_search(self, query):
        with self.index.searcher() as searcher:
            query_parser = QueryParser("text", schema=self.index.schema)
            query_obj = query_parser.parse(query)
            results = searcher.search(query_obj, limit=self.top_k)
            return [
                RAGInfo(id=int(result["id"]), text=result["text"], link=result["link"], rank=result.score)
                for result in results
            ]

    def add_record(self, text: str, link: str):
        embedding = self._get_embedding(text)

        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO texts (text, link, embedding)
                VALUES (%s, %s, %s)
                RETURNING id;
                """,
                (text, link, embedding)
            )
            record_id = cur.fetchone()[0]
        self.conn.commit()

        writer = self.index.writer()
        writer.update_document(id=str(record_id), text=text, link=link)
        writer.commit()

    def find(self, query):
        return self.vector_search(query), self.text_search(query)

    def _get_embedding(self, text: str) -> list:
        """Получить векторное представление текста"""
        formatted_text = 'query: ' + text
        embedding = self.model.encode(formatted_text, normalize_embeddings=True)
        return embedding.tolist()