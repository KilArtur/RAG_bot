import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import uuid

from utils.logger import get_logger
from config.Config import CONFIG

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter
from sentence_transformers import SentenceTransformer

log = get_logger("QdrantService")

class QdrantService:
    def __init__(self):
        self.host = CONFIG.qdrant.host
        self.port = CONFIG.qdrant.port
        self.collection_name = CONFIG.qdrant.collection_name
        self.model_name = CONFIG.qdrant.model_name
        self.vector_size = CONFIG.qdrant.vector_size
        self.top_samples = CONFIG.qdrant.top_samples

        try:
            self.client = QdrantClient(host=self.host, port=self.port)
            log.info(f"Подключение к Qdrant установлено: {self.host}:{self.port}")
        except Exception as e:
            log.error(f"Ошибка подключения к Qdrant: {e}")
            raise

        try:
            self.model = SentenceTransformer(self.model_name)
            log.info(f"Модель {self.model_name} загружена успешно")
        except Exception as e:
            log.error(f"Ошибка загрузки модели {self.model_name}: {e}")
            raise

        self._ensure_collection_exists()

    def _ensure_collection_exists(self) -> None:
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]

            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                log.info(f"Коллекция '{self.collection_name}' создана")
            else:
                log.info(f"Коллекция '{self.collection_name}' уже существует")

        except Exception as e:
            log.error(f"Ошибка при создании коллекции: {e}")
            raise

    def clear_all_chunks(self) -> bool:
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            log.info(f"Коллекция '{self.collection_name}' удалена")

            self._ensure_collection_exists()

            log.info("Все чанки успешно удалены из Qdrant")
            return True

        except Exception as e:
            log.error(f"Ошибка при очистке чанков: {e}")
            return False

    def add_vectorized_chunks(self, chunks_dir) -> bool:
        try:
            chunks_path = Path(chunks_dir)
            if not chunks_path.exists():
                log.error(f"Директория {chunks_dir} не существует")
                return False

            chunk_files = list(chunks_path.glob("chunk_*.txt"))

            if not chunk_files:
                log.warning(f"Не найдено файлов чанков в директории {chunks_dir}")
                return False

            log.info(f"Найдено {len(chunk_files)} файлов чанков")

            points = []

            for chunk_file in chunk_files:
                try:
                    with open(chunk_file, 'r', encoding='utf-8') as f:
                        text_content = f.read().strip()

                    if not text_content:
                        log.warning(f"Файл {chunk_file.name} пустой, пропускаем")
                        continue

                    embedding = self.model.encode(text_content).tolist()

                    point = PointStruct(
                        id=str(uuid.uuid4()),
                        vector=embedding,
                        payload={
                            "text": text_content,
                            "filename": chunk_file.name,
                            "chunk_id": chunk_file.stem
                        }
                    )

                    points.append(point)

                except Exception as e:
                    log.error(f"Ошибка при обработке файла {chunk_file}: {e}")
                    continue

            if not points:
                log.error("Не удалось обработать ни одного файла чанков")
                return False

            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

            log.info(f"Успешно добавлено {len(points)} чанков в Qdrant")
            return True

        except Exception as e:
            log.error(f"Ошибка при добавлении чанков: {e}")
            return False

    def get_collection_info(self) -> Dict[str, Any]:
        try:
            collection_info = self.client.get_collection(self.collection_name)

            log.debug(f"Collection info type: {type(collection_info)}")
            log.debug(f"Collection info attributes: {dir(collection_info)}")

            return {
                "name": self.collection_name,
                "vectors_count": collection_info.vectors_count,
                "points_count": collection_info.points_count,
                "status": collection_info.status
            }
        except Exception as e:
            log.error(f"Ошибка при получении информации о коллекции: {e}")
            return {}

    def search_similar(self, query: str) -> List[Dict[str, Any]]:
        try:
            query_embedding = self.model.encode(query).tolist()

            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=self.top_samples
            )

            results = []
            for result in search_results:
                results.append({
                    "id": result.id,
                    "score": result.score,
                    "text": result.payload.get("text", ""),
                    "filename": result.payload.get("filename", ""),
                    "chunk_id": result.payload.get("chunk_id", "")
                })

            return results

        except Exception as e:
            log.error(f"Ошибка при поиске: {e}")
            return []


if __name__ == "__main__":
    qdrant_service = QdrantService()

    print("\nИнформация о коллекции:")
    info = qdrant_service.get_collection_info()
    print(info)

    if info.get("points_count", 0) > 0:
        print("\nПример поиска по запросу:")

        query = "Что необходимо понять, если в жизни я хочу благополучия и стабильности для своей семьи?"

        results = qdrant_service.search_similar(query)
        for i, result in enumerate(results, 1):
            print(f"{i}. Score: {result['score']:.3f}, File: {result['filename']}")
            print(f"Text: {result['text'][:100]}...")