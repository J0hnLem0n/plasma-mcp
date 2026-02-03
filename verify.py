import os
import shutil
from src.core.rag import PlasmaRAG

# Конфиг
# Конфиг (относительные пути для воспроизводимости)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_PATH = os.getenv("PLASMA_REPO_PATH", os.path.abspath(os.path.join(BASE_DIR, "../plasma_repo")))
INDEX_DIR = os.getenv("PLASMA_INDEX_DIR", os.path.join(BASE_DIR, "plasma_index"))

def cleanup():
    if os.path.exists(INDEX_DIR):
        shutil.rmtree(INDEX_DIR)
        print("Старый индекс очищен.")

def test():
    print("--- Запуск верификации ---")
    
    # 1. Тест индексации
    print("Инициализация RAG (запускает индексацию)...")
    rag = PlasmaRAG(REPO_PATH, INDEX_DIR)
    
    # 2. Тест парсинга токенов
    print("\n[Тест] Поиск токена:")
    token = rag.get_token("textPrimary")
    if token:
        print(f"✅ Найден токен 'textPrimary': {list(token.keys())[0]}")
    else:
        print("❌ Не отдать найти токен 'textPrimary'.")

    # 3. Тест списка компонентов
    print("\n[Тест] Список компонентов:")
    components = rag.list_components()
    if "Button" in components:
        print(f"✅ 'Button' найден в списке компонентов (всего {len(components)}).")
    else:
        print(f"❌ 'Button' не найден в компонентах. Найдено: {components[:5]}...")

    # 4. Тест поиска
    print("\n[Тест] Поиск в документации (English):")
    results = rag.search_documentation("Button")
    if results:
        print(f"✅ Найдено {len(results)} результатов для 'Button'. Топ результат: {results[0]['title']}")
    else:
        print("❌ Результатов для 'Button' не найдено.")

    print("\n[Тест] Поиск в документации (Russian 'кнопку'):")
    results = rag.search_documentation("кнопку", limit=10)
    if results:
        print(f"✅ Найдено {len(results)} результатов для 'кнопку'.")
        for res in results:
            print(f"- {res['title']}")
    else:
        print("❌ Результатов для 'кнопку' не найдено.")

    print("\n--- Верификация завершена ---")

if __name__ == "__main__":
    cleanup()
    test()
