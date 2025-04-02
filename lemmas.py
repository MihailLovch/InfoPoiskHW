import os
import re
import pymorphy2
from bs4 import BeautifulSoup

# Папки
INPUT_FOLDER = "rt_articles"   # Папка с HTML-статьями
OUTPUT_FOLDER = "lemmas_tokens"       # Папка для результатов

# Cписок стоп-слов (союзы, предлоги и т.д.)
STOPWORDS = {
    "и", "в", "во", "не", "что", "он", "на", "я", "с", "со", "как", "а", "то", "все", "она", "так",
    "его", "но", "да", "ты", "к", "у", "же", "вы", "за", "бы", "по", "только", "ее", "мне", "было",
    "вот", "от", "меня", "еще", "нет", "о", "из", "ему", "теперь", "когда", "даже", "ну", "вдруг",
    "ли", "если", "уже", "или", "ни", "быть", "был", "него", "до", "вас", "нибудь", "опять", "уж",
    "вам", "ведь", "там", "потом", "себя", "ничего", "ей", "может", "они", "тут", "где", "есть",
    "надо", "ней", "для", "мы", "тебя", "их", "чем", "была", "сам", "чтоб", "без", "будто", "чего",
    "раз", "тоже", "себе", "под", "будет", "ж", "тогда", "кто", "этот", "того", "потому", "этого",
    "какой", "совсем", "ним", "здесь", "этом", "один", "почти", "мой", "тем", "чтобы", "нее", "сейчас",
    "были", "куда", "зачем", "всех", "никогда", "можно", "при", "наконец", "два", "об", "другой", "хоть",
    "после", "над", "больше", "тот", "через", "эти", "нас", "про", "всего", "них", "какая", "много", "разве",
    "три", "эту", "моя", "впрочем", "свою", "этой", "перед", "иногда", "лучше", "чуть", "том", "нельзя",
    "такой", "им", "более", "всегда", "конечно", "всю", "между"
}

# Инициализируем лемматизатор
morph = pymorphy2.MorphAnalyzer()

# Функция очистки HTML и извлечения текста
def extract_text_from_html(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")
    text = soup.get_text()
    text = re.sub(r'\s+', ' ', text)  # Убираем лишние пробелы и переносы строк
    return text.strip()

# Функция токенизации с фильтрацией одиночных букв
def tokenize(text):
    words = re.findall(r'\b[а-яА-ЯёЁ]+\b', text.lower())  # Ищем только слова
    words = [word for word in words if len(word) > 1 and word not in STOPWORDS]  # Убираем односимвольные токены
    return list(set(words))  # Убираем дубликаты

# Функция лемматизации с фильтрацией односимвольных лемм
def lemmatize_tokens(tokens):
    lemma_dict = {}
    for token in tokens:
        lemma = morph.parse(token)[0].normal_form  # Получаем лемму
        if len(lemma) > 1:  # Фильтруем леммы, которые короче 2 символов
            if lemma not in lemma_dict:
                lemma_dict[lemma] = token  # Запоминаем одно слово для этой леммы
    return lemma_dict

# Основной процесс
def process_articles():
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)  # Создаем папку, если ее нет

    for i in range(1, 101):  # 100 файлов: article_1.txt - article_100.txt
        file_name = f"article_{i}.txt"
        input_path = os.path.join(INPUT_FOLDER, file_name)
        if not os.path.exists(input_path):
            print(f"Файл {file_name} не найден, пропускаем...")
            continue

        print(f"Обрабатываю {file_name}...")

        # 1. Извлекаем чистый текст
        text = extract_text_from_html(input_path)

        # 2. Токенизируем
        tokens = tokenize(text)

        # 3. Лемматизируем и убираем дубликаты
        lemma_dict = lemmatize_tokens(tokens)

        # 4. Записываем токены в файл
        tokens_file = os.path.join(OUTPUT_FOLDER, f"tokens_{i}.txt")
        with open(tokens_file, "w", encoding="utf-8") as f:
            f.write("\n".join(tokens))

        # 5. Записываем леммы в файл
        lemmas_file = os.path.join(OUTPUT_FOLDER, f"lemmas_{i}.txt")
        with open(lemmas_file, "w", encoding="utf-8") as f:
            for lemma, word in lemma_dict.items():
                f.write(f"{lemma} {word}\n")  # Только одна форма слова

    print("Обработка завершена! Все файлы сохранены в папке output/.")

# Запуск скрипта
if __name__ == "__main__":
    process_articles()
