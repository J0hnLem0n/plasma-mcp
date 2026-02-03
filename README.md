# Руководство по запуску Plasma AI Assistant

Этот гид объясняет, как настроить и запустить проект после реорганизации структуры.

## Предварительные требования
- Python 3.10+
- Ключ GigaChat API

## Установка и настройка

1. **Клонируйте проект и репозиторий документации**:
   ```bash
   # Клонируйте основной проект (если еще не сделали)
   git clone git@github.com:J0hnLem0n/plasma-mcp.git
   cd plasma-mcp

   # Клонируйте репозиторий Plasma (для документации)
   git clone https://github.com/salute-developers/plasma.git plasma_repo
   ```

2. **Создайте виртуальное окружение**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # для macOS/Linux
   ```

2. **Установите зависимости**:
   ```bash
   pip install -e .
   ```

3. **Настройте `.env`**:
   Все пути должны быть указаны явно. Создайте файл `.env` в корне проекта:
   ```ini
   GIGACHAT_CREDENTIALS='ваш_авторизационный_ключ'
   GIGACHAT_SCOPE=GIGACHAT_API_CORP
   
   # Пути к данным (относительно корня проекта)
   PLASMA_REPO_PATH=plasma_repo
   PLASMA_INDEX_DIR=plasma_index
   PLASMA_DOCS_PATH=website/sdds-platform-ai-docs/docs
   ```

## Запуск компонентов

### 1. AI Агент (CLI)
Агент — это чат-бот в терминале, использующий локальный поиск в документации. 

> [!NOTE]
> При первом запуске агента или сервера будет автоматически создан поисковый индекс в папке `plasma_index`. Это может занять несколько секунд.

```bash
python -m src.agent
```

### 2. MCP Сервер (Streamable HTTP)
Сервер позволяет подключать знания Plasma к Cursor, Claude Desktop и другим IDE.
```bash
python -m src.server
```
При запуске сервер выведет: `🔗 URL для подключения: http://127.0.0.1:8000/mcp`

## Подключение к IDE

### Cursor
1. Перейдите в **Settings -> Cursor Settings -> General -> MCP**.
2. Нажмите **+ Add New MCP Server**.
3. Выберите тип **SSE** (или HTTP, если поддерживается).
4. Укажите URL: `http://127.0.0.1:8000/mcp`.

### Проверка (MCP Inspector)
Чтобы убедиться, что сервер работает корректно:
```bash
npx @modelcontextprotocol/inspector --transport http --server-url http://127.0.0.1:8000/mcp
```

## Тестирование ядра
Для проверки работы поиска вручную (без запуска серверов):
```bash
python verify.py
```
