import os
import tempfile
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
import psycopg2
from whoosh.analysis import StemmingAnalyzer
from whoosh.filedb.filestore import FileStorage
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser, MultifieldParser, PhrasePlugin

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
            parser = MultifieldParser(["text"], schema=self.index.schema)
            parser.add_plugin(PhrasePlugin())
            query_obj = parser.parse(query)
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

if __name__ == "__main__":
    from whoosh.index import create_in
    from whoosh.fields import Schema, ID, TEXT
    from whoosh.qparser import QueryParser
    import os

    # Схема с измененным текстовым полем
    schema = Schema(
        id=ID(stored=True, unique=True),
        text=TEXT(stored=True, analyzer=None),  # Анализатор не используется для простоты
        link=ID(stored=True)
    )

    # Создание индекса
    if not os.path.exists("indexdir"):
        os.mkdir("indexdir")

    ix = create_in("indexdir", schema)

    # Добавление документов
    writer = ix.writer()
    writer.add_document(id="1", text="The quick brown fox jumps over the lazy dog.", link="http://example.com/1")
    writer.add_document(id="2", text="Python is a versatile programming language.", link="http://example.com/2")
    writer.add_document(id="3", text="Search engines like Whoosh are very useful.", link="http://example.com/3")
    writer.add_document(id="4", text="Four score and seven years ago.", link="http://example.com/4")
    writer.commit()


    # Функция поиска
    def search(query_str):
        with ix.searcher() as searcher:
            # Использование QueryParser для поля text
            parser = QueryParser("text", ix.schema)
            query = parser.parse(query_str)

            print(f"Parsed Query: {query}")  # Для отладки
            results = searcher.search(query)

            # Вывод результатов
            if results:
                for result in results:
                    print(f"ID: {result['id']}, Link: {result['link']}, Text: {result['text']}")
            else:
                print("Ничего не найдено.")


    # Пример запроса из 4 слов
    query_string = "Python versatile useful language"
    search(query_string)
