import os
import requests
from bs4 import BeautifulSoup
import time

# Настройки
START_URL = "https://organiclawn.ru/page"  # Ссылка на раздел новостей
BASE_URL = "https://organiclawn.ru/"
SAVE_DIR = "rt_articles"
TOTAL_PAGES = 100  # Количество страниц для скачивания
MAX_PAGES = 10  # Максимальное количество страниц для обхода (по 10 статей с каждой)

# Создаем папку для сохранения
os.makedirs(SAVE_DIR, exist_ok=True)

# Заголовки для эмуляции запроса браузера
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Глобальная переменная для хранения уже добавленных ссылок
added_links = set()

def get_article_links(page_url):
    """Получает ссылки на статьи с указанной страницы"""
    global added_links  # Используем глобальную переменную
    try:
        response = requests.get(page_url, headers=headers)  # Добавляем headers
        response.raise_for_status()  # Если ответ 4xx или 5xx, выбрасывается исключение

        soup = BeautifulSoup(response.text, "html.parser")
        links = []

        # Ищем все ссылки на статьи
        for article in soup.find_all("a", href=True):
            href = article.get("href")
            # Ищем ссылки на статьи, начинающиеся с "/news/"
            if "#href" not in href and "category" not in href and "%" not in href and BASE_URL in href and "page" not in href and href.count("/") == 4:
                full_url = f"{BASE_URL}{href}" if href.startswith("/") else href
                if full_url not in added_links:  # Проверяем, есть ли ссылка уже в added_links
                    links.append(full_url)
                    added_links.add(full_url)  # Добавляем ссылку в added_links
                if len(links) >= TOTAL_PAGES:
                    return links

        return links

    except requests.RequestException as e:
        print(f"Ошибка при получении страницы: {e}")
        return []


def download_article(url, index):
    """Скачивает статью и сохраняет её в формате .txt"""
    try:
        response = requests.get(url, headers=headers)  # Добавляем headers
        response.raise_for_status()

        # Разбираем HTML, чтобы удалить теги <link> и <script>
        soup = BeautifulSoup(response.text, "html.parser")

        # Удаляем все теги <link> и <script>
        for tag in soup.find_all(["link", "script"]):
            tag.decompose()

        # Сохраняем страницу как текстовый файл с HTML-разметкой
        filename = os.path.join(SAVE_DIR, f"article_{index}.txt")
        with open(filename, "w", encoding="utf-8") as file:
            file.write(str(soup))  # Сохраняем очищенный HTML

        print(f"Скачано: {url} -> {filename}")
        return url  # Возвращаем ссылку на статью
    except requests.RequestException as e:
        print(f"Ошибка при скачивании {url}: {e}")
        return None


def get_all_article_links():
    """Получает ссылки на все статьи, переходя по нескольким страницам"""
    all_links = []
    page_number = 1

    while len(all_links) < TOTAL_PAGES:
        page_url = f"{START_URL}/{page_number}"  # Добавляем номер страницы для пагинации
        print(f"Обрабатываю страницу {page_url}, уже получено ссылок: {len(all_links)}")
        article_links = get_article_links(page_url)
        all_links.extend(article_links)  # Используем extend вместо add
        page_number += 1
        time.sleep(1)  # Задержка между запросами

    return all_links[:TOTAL_PAGES]  # Возвращаем не более TOTAL_PAGES ссылок


def create_index_file(links):
    """Создает индексный файл index.txt"""
    index_filename = os.path.join(SAVE_DIR, "index.txt")
    with open(index_filename, "w", encoding="utf-8") as file:
        for idx, link in enumerate(links, start=1):
            file.write(f"{idx}. {link}\n")
    print(f"Индексный файл сохранен: {index_filename}")


def main():
    """Основная функция"""
    article_links = get_all_article_links()
    if not article_links:
        print("Не удалось найти статьи.")
        return

    print(f"Найдено {len(article_links)} ссылок на статьи.")

    # Скачиваем статьи и сохраняем ссылки
    downloaded_links = []
    for i, article_url in enumerate(article_links, start=1):
        url = download_article(article_url, i)
        if url:
            downloaded_links.append(url)

    # Создаем индексный файл с номерами и ссылками
    create_index_file(downloaded_links)


if __name__ == "__main__":
    main()