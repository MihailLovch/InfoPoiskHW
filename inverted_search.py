import os
import re
from collections import defaultdict


class BooleanSearch:
    def __init__(self, tokens_dir):
        self.index = defaultdict(set)
        self.documents = set()
        self.load_tokens(tokens_dir)

    def load_tokens(self, tokens_dir):
        for filename in os.listdir(tokens_dir):
            if filename.endswith('.txt'):
                doc_id = filename.split('.')[0]
                self.documents.add(doc_id)

                with open(os.path.join(tokens_dir, filename), 'r', encoding='utf-8') as file:
                    tokens = file.read().split()
                    for token in tokens:
                        self.index[token].add(doc_id)

    def parse_query(self, query):
        query = query.lower().strip()

        while True:
            match = re.search(r'\(([^()]+)\)', query)
            if not match:
                break
            subquery = match.group(1)
            subresult = self.parse_query(subquery)
            temp_id = f"temp_{len(self.temp_results)}"
            self.temp_results[temp_id] = subresult
            query = query.replace(f'({subquery})', temp_id)

        tokens = re.split(r'(and|or|not|\(|\))', query)
        tokens = [t.strip() for t in tokens if t.strip()]

        i = 0
        while i < len(tokens):
            if tokens[i] == 'not':
                if i + 1 >= len(tokens):
                    raise ValueError("NOT должен иметь аргумент")
                term = tokens[i + 1]
                if term in self.temp_results:
                    result = self.documents - self.temp_results[term]
                else:
                    result = self.documents - self.index.get(term, set())
                temp_id = f"temp_{len(self.temp_results)}"
                self.temp_results[temp_id] = result
                tokens[i:i + 2] = [temp_id]
            else:
                i += 1

        i = 1
        while i < len(tokens):
            if tokens[i] == 'and':
                if i == 0 or i == len(tokens) - 1:
                    raise ValueError("AND должен иметь аргументы с обеих сторон")
                left = tokens[i - 1]
                right = tokens[i + 1]

                left_set = self.get_set(left)
                right_set = self.get_set(right)

                result = left_set & right_set
                temp_id = f"temp_{len(self.temp_results)}"
                self.temp_results[temp_id] = result
                tokens[i - 1:i + 2] = [temp_id]
            else:
                i += 1

        i = 1
        while i < len(tokens):
            if tokens[i] == 'or':
                if i == 0 or i == len(tokens) - 1:
                    raise ValueError("OR должен иметь аргументы с обеих сторон")
                left = tokens[i - 1]
                right = tokens[i + 1]

                left_set = self.get_set(left)
                right_set = self.get_set(right)

                result = left_set | right_set
                temp_id = f"temp_{len(self.temp_results)}"
                self.temp_results[temp_id] = result
                tokens[i - 1:i + 2] = [temp_id]
            else:
                i += 1

        if len(tokens) != 1:
            raise ValueError("Некорректный запрос")

        return self.get_set(tokens[0])

    def get_set(self, term):
        if term.startswith('temp_'):
            return self.temp_results.get(term, set())
        return self.index.get(term, set())

    def search(self, query):
        self.temp_results = {}
        try:
            return self.parse_query(query)
        except ValueError as e:
            print(f"Ошибка в запросе: {e}")
            return set()

    def pretty_search(self, query):
        results = self.search(query)
        print(f"\nРезультаты поиска для запроса: '{query}'")
        print(f"Найдено документов: {len(results)}")
        if results:
            print("Документы:", ", ".join(sorted(results)))
        return results


if __name__ == "__main__":
    tokens_directory = "./lemmas_tokens"

    search_engine = BooleanSearch(tokens_directory)

    print("Булев поиск по инвертированному индексу")
    print("Поддерживаемые операторы: AND, OR, NOT (все в нижнем регистре)")
    print("Примеры запросов:")
    print("  клеопатра and цезарь")
    print("  клеопатра or цезарь")
    print("  not клеопатра")
    print("  (клеопатра and цезарь) or антоний")
    print("  not (клеопатра or цезарь) and антоний")
    print("Введите 'exit' для выхода")

    while True:
        query = input("\nВведите поисковый запрос: ").strip()
        if query.lower() == 'exit':
            break
        search_engine.pretty_search(query)