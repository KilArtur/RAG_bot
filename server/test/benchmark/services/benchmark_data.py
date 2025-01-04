from dataclasses import dataclass
from typing import List
import pandas as pd
from services.RAGService import RAGService, RAGInfo
from sklearn.metrics import accuracy_score


@dataclass
class Result:
    answer: str
    arr_links: List[str]

class Benchmark:
    def __init__(self):
        self.data = pd.read_csv('../data/data_for_bench.csv')
        self.way_to_save = '../output'
        self.rag_service = RAGService()

    def info_data(self):
        print(self.data.info())
        print(self.data.head())

    def metrics(self):
        expected_ids = []
        predicted_ids = []

        for index in range(self.data.shape[0]):
            bench_question = self.data['question'].iloc[index]
            bench_answer = self.data['answer'].iloc[index]
            link = bench_answer.split()[-1]

            print(f'Вопрос: {bench_question}')
            print(f'Ссылка: {link}')

            result = self.__get_result(bench_question)

            expected_ids.append(self.data['expected_ids'].iloc[index])
            predicted_ids.append([r.id for r in result])

        flat_predicted_ids = [item for sublist in predicted_ids for item in sublist]

        accuracy = accuracy_score(expected_ids, flat_predicted_ids)
        print(f'Accuracy: {accuracy}')

    def __get_result(self, question: str) -> List[RAGInfo]:
        res = self.rag_service.vector_search(question)
        return res


Benchmark().metrics()
