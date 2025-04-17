import os
import math
from collections import defaultdict, Counter

# --- Константы ---
ARTICLES_COUNT = 100
TOKENS_DIR = 'lemmas_tokens'
OUTPUT_TERMS_DIR = 'output_tokens'
OUTPUT_LEMMAS_DIR = 'output_lemmas'

# --- Создание директорий ---
os.makedirs(OUTPUT_TERMS_DIR, exist_ok=True)
os.makedirs(OUTPUT_LEMMAS_DIR, exist_ok=True)

# --- Подготовка ---
doc_term_counts = []
doc_lemma_counts = []
term_df = defaultdict(int)
lemma_df = defaultdict(int)

# --- Обработка документов ---
for i in range(1, ARTICLES_COUNT + 1):
    tokens_path = os.path.join(TOKENS_DIR, f'tokens_{i}.txt')
    lemmas_path = os.path.join(TOKENS_DIR, f'lemmas_{i}.txt')

    # --- Чтение токенов ---
    with open(tokens_path, encoding='utf-8') as f:
        tokens = [line.strip().lower() for line in f if line.strip()]

    # --- Чтение лемм (первый столбец каждой строки) ---
    with open(lemmas_path, encoding='utf-8') as f:
        lemma_lines = [line.strip().split()[0].lower() for line in f if line.strip()]

    # --- Подсчёт частот ---
    term_count = Counter(tokens)
    lemma_count = Counter(lemma_lines)

    doc_term_counts.append(term_count)
    doc_lemma_counts.append(lemma_count)

    for term in term_count:
        term_df[term] += 1
    for lemma in lemma_count:
        lemma_df[lemma] += 1

# --- IDF ---
N = ARTICLES_COUNT
idf_terms = {term: math.log(N / df) for term, df in term_df.items()}
idf_lemmas = {lemma: math.log(N / df) for lemma, df in lemma_df.items()}

# --- Запись результатов ---
for i in range(1, ARTICLES_COUNT + 1):
    term_count = doc_term_counts[i - 1]
    lemma_count = doc_lemma_counts[i - 1]

    total_terms = sum(term_count.values())
    total_lemmas = sum(lemma_count.values())

    with open(f'{OUTPUT_TERMS_DIR}/article_{i}_tokens.txt', 'w', encoding='utf-8') as f:
        for term in sorted(term_count):
            tf = term_count[term] / total_terms if total_terms else 0
            tfidf = tf * idf_terms[term]
            f.write(f'{term} {idf_terms[term]:.6f} {tfidf:.6f}\n')

    with open(f'{OUTPUT_LEMMAS_DIR}/article_{i}_lemmas.txt', 'w', encoding='utf-8') as f:
        for lemma in sorted(lemma_count):
            tf = lemma_count[lemma] / total_lemmas if total_lemmas else 0
            tfidf = tf * idf_lemmas[lemma]
            f.write(f'{lemma} {idf_lemmas[lemma]:.6f} {tfidf:.6f}\n')
