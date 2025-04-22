import os
from collections import defaultdict
from typing import List, Tuple, Dict, Any

import pymorphy3
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

OUTPUT_TF_IDF_RESULT_DIR = "output_lemmas"
EPSILON = 1e-6
URL_FOR_PARSE = "https://organiclawn.ru/page"

morph = pymorphy3.MorphAnalyzer()


def load_index() -> Dict[str, Dict[str, Tuple[float, float]]]:
    index = {}

    for filename in os.listdir(OUTPUT_TF_IDF_RESULT_DIR):
        doc_id = filename.split("_")[1].split('.')[0]
        index[doc_id] = {}

        with open(os.path.join(OUTPUT_TF_IDF_RESULT_DIR, filename), "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) != 3:
                    continue
                lemma, idf, tfidf = parts
                index[doc_id][lemma] = (float(idf), float(tfidf))

    return index


def compute_query_vector(query: str, index: Dict[str, Dict[str, Tuple[float, float]]]) -> Dict[str, float]:
    words = [word for word in query.split() if word.isalpha()]  # Фильтруем не-слова
    lemmatized_query = [morph.parse(word)[0].normal_form for word in words]
    query_tf = defaultdict(int)

    for lemma in lemmatized_query:
        query_tf[lemma] += 1

    max_tf = max(query_tf.values()) if query_tf else 1
    query_vector = {}

    for lemma, tf in query_tf.items():
        idf = next((index[doc][lemma][0] for doc in index if lemma in index[doc]), EPSILON)
        query_vector[lemma] = (tf / max_tf) * idf

    return query_vector


def search(query: str, index: Dict[str, Dict[str, Tuple[float, float]]]) -> List[Tuple[str, float]]:
    if not query or not index:
        return []

    query_vector = compute_query_vector(query, index)
    if not query_vector:
        return []

    all_lemmas = set(query_vector.keys())
    for doc in index.values():
        all_lemmas.update(doc.keys())
    all_lemmas = sorted(all_lemmas)

    query_array = np.array([query_vector.get(lemma, 0) for lemma in all_lemmas]).reshape(1, -1)

    doc_arrays = []
    doc_ids = []

    for doc_id, doc_data in index.items():
        doc_vector = {lemma: tfidf for lemma, (_, tfidf) in doc_data.items()}
        doc_array = np.array([doc_vector.get(lemma, 0) for lemma in all_lemmas])
        doc_arrays.append(doc_array)
        doc_ids.append(doc_id)

    if not doc_arrays:
        return []

    doc_matrix = np.vstack(doc_arrays)

    similarities = cosine_similarity(query_array, doc_matrix)[0]

    results = sorted(zip(doc_ids, similarities), key=lambda x: x[1], reverse=True)

    return [(doc_id, score) for doc_id, score in results if score > 0]


if __name__ == "__main__":
    index = load_index()
    print(f"Загружено {len(index)} документов в индекс")

    while True:
        query = input("\nВведите поисковый запрос (для выхода напишите stop): ").strip()
        if query.lower() == "stop":
            break

        results = search(query, index)

        if not results:
            print("Релевантных документов не найдено")
        else:
            print("\nРезультаты поиска (URL - оценка релевантности):")
            for doc_id, score in results:
                print(f"{URL_FOR_PARSE}/{doc_id} - {score:.4f}")