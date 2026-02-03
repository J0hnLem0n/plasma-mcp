import os
from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import Schema, TEXT, ID, STORED
from whoosh.analysis import RegexTokenizer, LowercaseFilter, NgramFilter
from bs4 import BeautifulSoup
import markdown_it

def get_schema():
    # Кастомный анализатор: Токенизация -> Нижний регистр -> N-граммы
    # Это позволяет находить "кнопку" по слову "Кнопка" (общие n-граммы: "кноп", "нопк"...)
    analyzer = RegexTokenizer() | LowercaseFilter() | NgramFilter(minsize=3, maxsize=10)
    
    return Schema(
        path=ID(stored=True, unique=True),
        title=TEXT(stored=True),
        content=TEXT(analyzer=analyzer, stored=True),
        url=STORED,
    )

def create_index(index_dir):
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)
    return create_in(index_dir, get_schema())

def get_index(index_dir):
    if exists_in(index_dir):
        return open_dir(index_dir)
    return create_index(index_dir)

def parse_markdown(content):
    md = markdown_it.MarkdownIt()
    tokens = md.parse(content)
    # Простое извлечение: пока берем сырой текст из файла.
    # Можно использовать токены для более точного извлечения заголовков.
    # Для RAG часто достаточно сырого текста, если мы его разбиваем на части,
    # но здесь мы индексируем весь файл как один документ для MVP.
    # Для улучшения можно удалять HTML-теги, если они есть.
    html = md.render(content)
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    
    # Пытаемся извлечь заголовок из первого h1
    title = "Без названия"
    h1 = soup.find("h1")
    if h1:
        title = h1.get_text(strip=True)
    
    return title, text

def index_documentation(repo_path, index_dir):
    ix = get_index(index_dir)
    writer = ix.writer()
    
    # Путь к документации берем строго из .env
    docs_rel_path = os.getenv("PLASMA_DOCS_PATH")
    if not docs_rel_path:
        raise ValueError("Ошибка: Переменная окружения PLASMA_DOCS_PATH не установлена в .env")
        
    docs_path = os.path.join(repo_path, docs_rel_path)
    
    if not os.path.exists(docs_path):
        print(f"Предупреждение: Путь к документации не найден: {docs_path}")
        return

    for root, _, files in os.walk(docs_path):
        for file in files:
            if file.endswith((".md", ".mdx")):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    title, text_content = parse_markdown(content)
                    rel_path = os.path.relpath(file_path, repo_path)
                    
                    # Простая генерация URL (приближение, подходящее для контекста RAG)
                    # Предполагаем, что структура сайта зеркальна структуре документации
                    url = f"https://plasma.sberdevices.ru/web/docs/{os.path.relpath(file_path, docs_path)}"
                    
                    writer.update_document(
                        path=rel_path,
                        title=title,
                        content=text_content,
                        url=url
                    )
                    print(f"Проиндексировано: {rel_path}")
                except Exception as e:
                    print(f"Не удалось проиндексировать {file_path}: {e}")
    
    writer.commit()
    print("Индексация завершена.")
