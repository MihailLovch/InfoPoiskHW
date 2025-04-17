import os
import json
import re
from collections import defaultdict


class BooleanSearchEngine:
    def __init__(self, tokens_dir, index_file='inverted_index.json'):
        self.tokens_dir = tokens_dir
        self.index_file = index_file
        self.index = defaultdict(set)
        self.documents = set()

        self.build_index()
        self.save_index()

    def build_index(self):
        print("Построение инвертированного индекса...")
        for filename in os.listdir(self.tokens_dir):
            if filename.endswith('.txt'):
                doc_id = filename.split('.')[0]
                self.documents.add(doc_id)

                with open(os.path.join(self.tokens_dir, filename), 'r', encoding='utf-8') as f:
                    tokens = f.read().split()
                    for token in tokens:
                        self.index[token].add(doc_id)
        print(f"Индекс построен. Документов: {len(self.documents)}, Уникальных терминов: {len(self.index)}")

    def save_index(self):
        index_to_save = {term: list(docs) for term, docs in self.index.items()}

        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump({
                'documents': list(self.documents),
                'index': index_to_save
            }, f, ensure_ascii=False, indent=2)
        print(f"Индекс сохранен в {self.index_file}")

    def search(self, query):
        self.temp_results = {}

        try:
            query = query.lower().strip()
            if not query:
                return set()

            result = self._parse_expression(query)
            return result
        except Exception as e:
            print(f"Ошибка при обработке запроса: {e}")
            return set()

    def _parse_expression(self, expression):
        expression = expression.strip()
        while expression.startswith('(') and expression.endswith(')'):
            expression = expression[1:-1].strip()

        tokens = self._tokenize(expression)
        tokens = self._process_operator(tokens, 'not')
        tokens = self._process_operator(tokens, 'and')
        tokens = self._process_operator(tokens, 'or')

        if len(tokens) != 1:
            raise ValueError(f"Некорректное выражение: {expression}")

        return self._get_docs_for_token(tokens[0])

    def _tokenize(self, expression):
        tokens = []
        current = []
        paren_level = 0

        for char in expression:
            if char == '(':
                paren_level += 1
                current.append(char)
            elif char == ')':
                paren_level -= 1
                current.append(char)
            elif char.isspace() and paren_level == 0:
                if current:
                    tokens.append(''.join(current))
                    current = []
            else:
                current.append(char)

        if current:
            tokens.append(''.join(current))

        return tokens

    def _process_operator(self, tokens, operator):
        i = 0
        while i < len(tokens):
            if tokens[i] == operator:
                if operator == 'not':
                    if i == len(tokens) - 1:
                        raise ValueError(f"Оператор NOT требует аргумента")

                    arg = tokens[i + 1]
                    docs = self._get_docs_for_token(arg)
                    result = self.documents - docs

                    temp_id = f"temp_{len(self.temp_results)}"
                    self.temp_results[temp_id] = result
                    tokens[i:i + 2] = [temp_id]
                else:
                    if i == 0 or i == len(tokens) - 1:
                        raise ValueError(f"Оператор {operator} требует два аргумента")

                    left = tokens[i - 1]
                    right = tokens[i + 1]
                    left_docs = self._get_docs_for_token(left)
                    right_docs = self._get_docs_for_token(right)

                    if operator == 'and':
                        result = left_docs & right_docs
                    else:  # OR
                        result = left_docs | right_docs

                    temp_id = f"temp_{len(self.temp_results)}"
                    self.temp_results[temp_id] = result
                    tokens[i - 1:i + 2] = [temp_id]
                    i -= 1
            i += 1

        return tokens

    def _get_docs_for_token(self, token):
        if token.startswith('temp_'):
            return self.temp_results.get(token, set())

        if '(' in token or ')' in token:
            return self._parse_expression(token)

        return self.index.get(token, set())

    def pretty_search(self, query):
        results = self.search(query)
        print(f"\nРезультаты поиска для запроса: '{query}'")
        print(f"Найдено документов: {len(results)}")
        if results:
            print("Документы:", ", ".join(sorted(results)))
        return results


if __name__ == "__main__":
    TOKENS_DIR = "./lemmas_tokens"
    INDEX_FILE = "inverted_index.json"

    search_engine = BooleanSearchEngine(TOKENS_DIR, INDEX_FILE)

    print("\nБулев поиск по инвертированному индексу")
    print("Поддерживаемые операторы: AND, OR, NOT (в нижнем регистре)")
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