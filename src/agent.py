import os
import sys
from gigachat import GigaChat
from dotenv import load_dotenv
from src.core.rag import PlasmaRAG

# Загрузка .env
load_dotenv()

# Конфигурация
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_PATH = os.environ.get("PLASMA_REPO_PATH")
INDEX_DIR = os.environ.get("PLASMA_INDEX_DIR")

if not REPO_PATH or not INDEX_DIR:
    print("Ошибка: Переменные PLASMA_REPO_PATH или PLASMA_INDEX_DIR не установлены в .env.")
    sys.exit(1)

# Преобразуем в абсолютные, если пути относительные (относительно корня сервера)
SERVER_ROOT = os.path.dirname(BASE_DIR)
if not os.path.isabs(REPO_PATH):
    REPO_PATH = os.path.abspath(os.path.join(SERVER_ROOT, REPO_PATH))
if not os.path.isabs(INDEX_DIR):
    INDEX_DIR = os.path.abspath(os.path.join(SERVER_ROOT, INDEX_DIR))
CREDENTIALS = os.environ.get("GIGACHAT_CREDENTIALS")
SCOPE = os.environ.get("GIGACHAT_SCOPE", "GIGACHAT_API_PERS") # или GIGACHAT_API_CORP

def main():
    if not CREDENTIALS:
        print("Ошибка: Переменная окружения GIGACHAT_CREDENTIALS не установлена.")
        print("Пожалуйста, экспортируйте её: export GIGACHAT_CREDENTIALS='ваши_данные_авторизации'")
        return

    print("Инициализация Plasma Agent...")
    rag = PlasmaRAG(REPO_PATH, INDEX_DIR)
    
    print("Подключение к GigaChat...")
    try:
        chat = GigaChat(credentials=CREDENTIALS, scope=SCOPE, verify_ssl_certs=False)
    except Exception as e:
        print(f"Не удалось подключиться к GigaChat: {e}")
        return

    print("\n--- Plasma AI Architect (GigaChat) ---")
    print("Спрашивайте меня о чем угодно про Plasma UI Kit (токены, компоненты, доки). Введите 'exit' для выхода.\n")

    conversation_history = [
        {"role": "system", "content": "Ты полезный AI помощник и эксперт по дизайн-системе Plasma UI Kit. "
                                      "Тебе будет предоставлен контекст из документации. "
                                      "Отвечай на вопросы пользователя, основываясь на предоставленном контексте. "
                                      "Если упоминаешь код, предоставляй его в Markdown."
                                      "Если контекст не содержит ответа, скажи об этом, но постарайся быть полезным."}
    ]

    while True:
        try:
            query = input("Вы: ")
        except EOFError:
            break
            
        if query.lower() in ["exit", "quit"]:
            break
        
        if not query.strip():
            continue

        # 1. Анализ запроса и перевод ключевых слов (Query Expansion)
        print("...Анализ запроса...")
        try:
            expansion_prompt = f"Ты помощник поисковой системы. Пользователь спрашивает: '{query}'. " \
                               f"Выдели названия компонентов UI Kit или технические термины. " \
                               f"Переведи их на английский язык, так как документация на английском. " \
                               f"Верни ТОЛЬКО список терминов через пробел. Если терминов нет, верни пустую строку."
            
            expansion_response = chat.chat(payload={"messages": [{"role": "user", "content": expansion_prompt}]})
            keywords = expansion_response.choices[0].message.content.strip()
            print(f"Ключевые слова: {keywords}")
        except Exception as e:
            print(f"Ошибка расширения запроса: {e}")
            keywords = ""

        # 2. Получение контекста (Поиск по оригиналу + ключевым словам)
        print("...Поиск контекста...")
        search_query = f"{query} {keywords}".strip()
        docs = rag.search_documentation(search_query, limit=5)
        
        # Эвристика: проверка токенов
        tokens_context = ""
        words = search_query.split()
        for word in words:
            # Если слово похоже на токен/camelCase или пользователь явно просит токен
             if "token" in query.lower() or (len(word) > 4 and word[0].islower() and any(c.isupper() for c in word)):
                found_tokens = rag.get_token(word)
                if found_tokens:
                    tokens_context += f"\nТокены, соответствующие '{word}':\n"
                    for k, v in list(found_tokens.items())[:5]:
                        tokens_context += f"- {k}: {v['value']} ({v['comment']})\n"
        
        context_str = "Контекст из документации:\n"
        for d in docs:
            context_str += f"Заголовок: {d['title']}\nСниппет: {d['content_snippet']}\n\n"
        
        if tokens_context:
            context_str += f"\n{tokens_context}"

        print(f"DEBUG: Retrieved {len(docs)} docs.")
        if docs:
            print(f"DEBUG Top Doc: {docs[0]['title']} - {docs[0]['path']}")
            # print(f"DEBUG Content: {docs[0]['content_snippet'][:200]}...")

        # 2. Формирование промпта
        prompt = f"Вопрос: {query}\n\n{context_str}"
        
        conversation_history.append({"role": "user", "content": prompt})
        
        # 3. Получение ответа
        try:
            response = chat.chat(payload={"messages": conversation_history})
            answer = response.choices[0].message.content
            print(f"\nAI: {answer}\n")
            
            # Держим историю короткой или просто добавляем ответ (GigaChat обычно обрабатывает контекстное окно, но будем аккуратны)
            conversation_history.append({"role": "assistant", "content": answer})
            
        except Exception as e:
            print(f"Ошибка вызова GigaChat: {e}")

if __name__ == "__main__":
    main()
