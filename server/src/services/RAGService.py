from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from utils.logger import get_logger
import json
import urllib3

log = get_logger("RAGService")


@dataclass
class RAGInfo:
    id: str
    text: str
    link: str
    rank: float


class RAGService:
    def __init__(self):
        self.model = SentenceTransformer("intfloat/multilingual-e5-large")
        self.top_k = 20
        username = "elastic"  # замените на свой логин
        password = "password"  # замените на свой пароль
        es_host = "http://localhost:9200"  # используйте нужный URL и порт


        self.es = Elasticsearch(
            es_host,
            # connection_class=RequestsHttpConnection,
            http_auth=(username, password),
            timeout=10
        )

        self.index_name = "rag_index"

        # Create index if it doesn't exist
        if not self.es.indices.exists(index=self.index_name):
            self.es.indices.create(index=self.index_name, body={
                "mappings": {
                    "properties": {
                        "id": {"type": "keyword"},
                        "text": {"type": "text"},
                        "link": {"type": "keyword"},
                        "embedding": {"type": "dense_vector", "dims": 1024}
                    }
                }
            })
        log.info("RAGService initialized")

    def vector_search(self, query: str):
        query_embedding = self._get_embedding(query)

        script_query = {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                    "params": {"query_vector": query_embedding}
                }
            }
        }

        response = self.es.search(index=self.index_name, body={
            "size": self.top_k,
            "query": script_query
        })

        results = [
            RAGInfo(
                id=hit["_id"],
                text=hit["_source"]["text"],
                link=hit["_source"]["link"],
                rank=hit["_score"]
            )
            for hit in response.body["hits"]["hits"]
        ]

        # log.info(f"Vector search result: {json.dumps(results, indent=2, ensure_ascii=False)}")
        return results

    def text_search(self, query: str):
        response = self.es.search(index=self.index_name, body={
            "size": self.top_k,
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["text"]
                }
            }
        })

        results = [
            RAGInfo(
                id=hit["_id"],
                text=hit["_source"]["text"],
                link=hit["_source"]["link"],
                rank=hit["_score"]
            )
            for hit in response["hits"]["hits"]
        ]

        # log.info(f"Text search result: {json.dumps(results, indent=2, ensure_ascii=False)}")
        return results

    def add_record(self, text: str, link: str):
        embedding = self._get_embedding(text, is_query=False)

        doc = {
            "text": text,
            "link": link,
            "embedding": embedding
        }

        response = self.es.index(index=self.index_name, document=doc)
        log.info(f"Added record to Elasticsearch: {response['_id']}")

    def find(self, query: str):
        result = []
        result.extend(self.vector_search(query))
        result.extend(self.vector_search(query))
        return result

    def _get_embedding(self, text: str, is_query=True) -> list:
        formatted_text =  text if is_query else text
        embedding = self.model.encode(formatted_text, normalize_embeddings=True)
        return embedding.tolist()
