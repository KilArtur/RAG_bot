from dataclasses import dataclass
from typing import List
import time

import pandas as pd
import asyncio
from concurrent.futures import ThreadPoolExecutor
from asyncio import Semaphore

from services.RAGService import RAGService, RAGInfo


@dataclass
class Result:
    answer: str
    arr_links: List[str]


class Benchmark:
    def __init__(self, data_path):
        self.data = pd.read_csv(data_path)
        self.rag_service = RAGService()
        self.semaphore = Semaphore(25)

    def info_data(self):
        print(self.data.info())
        print(self.data.head())

    async def _get_result_async(self, question: str) -> List[RAGInfo]:
        async with self.semaphore:
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(
                None, self.rag_service.find, question
            )

    async def metrics(self):
        start_time = time.time()
        expected_ids = []
        correct, total = 0, 0

        tasks = []
        results = []

        for index in range(self.data.shape[0]):
            bench_question = self.data['question'].iloc[index]
            link = self.data['link'].iloc[index]

            print(f'Вопрос: {bench_question}')
            print(f'Ссылка: {link}')

            tasks.append(self._get_result_async(bench_question))  # Сбор задач

        results = await asyncio.gather(*tasks)

        for index, result in enumerate(results):
            bench_question = self.data['question'].iloc[index]
            link = self.data['link'].iloc[index]
            total += 1
            true_links = [r.link for r in result]

            if link in true_links:
                correct += 1

        delta_time = time.time() - start_time


        print(f'Metric: {correct / total * 100:.2f}%')
        print(f'correct: {correct}, incorrect: {total - correct}, total: {total}')
        print(f'Time: {delta_time} секунд')

    def run(self):
        asyncio.run(self.metrics())


path_data = 'benchmark/questions.csv'

if __name__ == "__main__":
    Benchmark(path_data).run()