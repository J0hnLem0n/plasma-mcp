from mcp.server.fastmcp import FastMCP
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from src.core.rag import PlasmaRAG
from dotenv import load_dotenv
import os

# Загрузка .env
load_dotenv()

# Конфигурация
REPO_PATH = os.environ.get("PLASMA_REPO_PATH")
INDEX_DIR = os.environ.get("PLASMA_INDEX_DIR")

if not REPO_PATH or not INDEX_DIR:
    raise ValueError("Ошибка: Переменные PLASMA_REPO_PATH или PLASMA_INDEX_DIR не установлены в .env.")

# Инициализация RAG
rag = PlasmaRAG(REPO_PATH, INDEX_DIR)

# Инициализация MCP Сервера
mcp = FastMCP(
    "Plasma Assistant",
    host="127.0.0.1",
    port=8000
)

@mcp.tool()
def ask_plasma(question: str) -> str:
    """
    Поиск ответов в документации Plasma UI Kit.
    Используйте этот инструмент, когда нужна общая информация о Plasma, использовании компонентов или гайдлайнах.
    """
    results = rag.search_documentation(question)
    if not results:
        return "Релевантная документация не найдена."
    
    response = "Найдена следующая документация:\n\n"
    for res in results:
        response += f"### {res['title']} ({res['url']})\n"
        response += f"{res['content_snippet']}\n\n"
    
    return response

@mcp.tool()
def get_token(name: str) -> str:
    """
    Получение информации о конкретном дизайн-токене.
    Используйте это для поиска значений цветов, стилей типографики или переменных отступов.
    Пример: get_token("textPrimary")
    """
    tokens = rag.get_token(name)
    if not tokens:
        return f"Токены, соответствующие '{name}', не найдены."
    
    response = f"Найдено {len(tokens)} токенов, соответствующих '{name}':\n"
    for key, data in list(tokens.items())[:20]: # Ограничиваем вывод
        response += f"- **{key}**: `{data['value']}`"
        if data['comment']:
            response += f" ({data['comment']})"
        response += "\n"
    
    if len(tokens) > 20:
        response += f"...и еще {len(tokens)-20}."
        
    return response

@mcp.tool()
def get_component_info(name: str) -> str:
    """
    Получение подробной информации о конкретном UI компоненте.
    Пример: get_component_info("Button")
    """
    info = rag.get_component_info(name)
    if not info:
        return f"Компонент '{name}' не найден или документация отсутствует."
    
    return f"### {info['title']}\nURL: {info['url']}\n\n{info['content_snippet']}\n\n(Полный текст доступен в документации)"

@mcp.tool()
def list_components() -> str:
    """
    Список всех доступных компонентов в Plasma UI Kit.
    """
    components = rag.list_components()
    return "Доступные компоненты:\n" + ", ".join(components)

if __name__ == "__main__":
    print(f"\n🚀 Plasma MCP Server запущен!")
    print(f"🔗 URL для подключения: http://127.0.0.1:8000/mcp\n")
    
    mcp.run(transport="streamable-http")
