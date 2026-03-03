import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from gigachat import GigaChat
from dotenv import load_dotenv
from src.core.rag import PlasmaRAG

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_ROOT = os.path.dirname(BASE_DIR)
REPO_PATH = os.environ.get("PLASMA_REPO_PATH", "plasma_repo")
INDEX_DIR = os.environ.get("PLASMA_INDEX_DIR", "plasma_index")
CREDENTIALS = os.environ.get("GIGACHAT_CREDENTIALS")
SCOPE = os.environ.get("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")

if not os.path.isabs(REPO_PATH):
    REPO_PATH = os.path.abspath(os.path.join(SERVER_ROOT, REPO_PATH))
if not os.path.isabs(INDEX_DIR):
    INDEX_DIR = os.path.abspath(os.path.join(SERVER_ROOT, INDEX_DIR))

app = FastAPI(title="Plasma AI Chat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

rag = PlasmaRAG(REPO_PATH, INDEX_DIR)
chat_client = None
if CREDENTIALS:
    chat_client = GigaChat(credentials=CREDENTIALS, scope=SCOPE, verify_ssl_certs=False)

SYSTEM_PROMPT = (
    "Ты полезный AI помощник и эксперт по дизайн-системе Plasma UI Kit. "
    "Тебе будет предоставлен контекст из документации. "
    "Отвечай на вопросы пользователя, основываясь на предоставленном контексте. "
    "Если упоминаешь код, предоставляй его в Markdown с указанием языка. "
    "Если упоминаешь дизайн-токены с цветовыми значениями, оформляй их так: "
    "`[token:имяТокена:#hex]` — это позволит UI отобразить цвет. "
    "Если контекст не содержит ответа, скажи об этом, но постарайся быть полезным."
)


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []


class TokenSearchRequest(BaseModel):
    query: str


def expand_query(query: str) -> str:
    if not chat_client:
        return ""
    try:
        prompt = (
            f"Ты помощник поисковой системы. Пользователь спрашивает: '{query}'. "
            f"Выдели названия компонентов UI Kit или технические термины. "
            f"Переведи их на английский язык, так как документация на английском. "
            f"Верни ТОЛЬКО список терминов через пробел."
        )
        resp = chat_client.chat(payload={"messages": [{"role": "user", "content": prompt}]})
        return resp.choices[0].message.content.strip()
    except Exception:
        return ""


def find_token_context(search_query: str, original_query: str) -> str:
    tokens_context = ""
    for word in search_query.split():
        if "token" in original_query.lower() or "токен" in original_query.lower() or "цвет" in original_query.lower() or (
            len(word) > 4 and word[0].islower() and any(c.isupper() for c in word)
        ):
            found = rag.get_token(word)
            if found:
                tokens_context += f"\nТокены '{word}':\n"
                for k, v in list(found.items())[:10]:
                    tokens_context += f"- {k}: {v['value']} ({v['comment']})\n"
    return tokens_context


@app.post("/api/chat")
def chat_endpoint(req: ChatRequest):
    if not chat_client:
        return {"error": "GigaChat не настроен. Проверьте GIGACHAT_CREDENTIALS в .env"}

    keywords = expand_query(req.message)
    search_query = f"{req.message} {keywords}".strip()

    docs = rag.search_documentation(search_query, limit=5)
    tokens_context = find_token_context(search_query, req.message)

    context_str = "Контекст из документации:\n"
    for d in docs:
        context_str += f"Заголовок: {d['title']}\nСниппет: {d['content_snippet']}\n\n"
    if tokens_context:
        context_str += tokens_context

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in req.history[-10:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": f"Вопрос: {req.message}\n\n{context_str}"})

    try:
        response = chat_client.chat(payload={"messages": messages})
        answer = response.choices[0].message.content
        return {"answer": answer}
    except Exception as e:
        return {"error": f"Ошибка GigaChat: {str(e)}"}


@app.get("/api/tokens")
def search_tokens(q: str = ""):
    if not q:
        return {"tokens": {}}
    matches = rag.get_token(q)
    result = {}
    for key, data in list(matches.items())[:30]:
        result[key] = {"value": data["value"], "comment": data.get("comment", "")}
    return {"tokens": result}


@app.get("/api/components")
def get_components():
    return {"components": rag.list_components()}


STATIC_DIR = os.path.join(SERVER_ROOT, "web", "dist")
if os.path.exists(STATIC_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")

    @app.get("/{path:path}")
    def serve_spa(path: str):
        file_path = os.path.join(STATIC_DIR, path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))


if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Plasma Chat UI запущен на http://127.0.0.1:8080\n")
    uvicorn.run(app, host="127.0.0.1", port=8080)
