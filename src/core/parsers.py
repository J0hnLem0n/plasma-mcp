import json
import os

def parse_tokens(repo_path):
    """
    Парсит токены из packages/plasma-tokens/data/themes/default.json
    Возвращает плоский словарь токенов.
    """
    tokens_path = os.path.join(repo_path, "packages/plasma-tokens/data/themes/default.json")
    if not os.path.exists(tokens_path):
        print(f"Ошибка: Файл токенов не найден по пути {tokens_path}")
        return {}

    try:
        with open(tokens_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Ошибка чтения файла токенов: {e}")
        return {}

    flattened_tokens = {}

    def recurse(node, prefix=""):
        if isinstance(node, dict):
            # Проверяем, является ли узел определением токена (имеет 'value' и 'comment')
            if "value" in node and isinstance(node["value"], (str, int, float)):
                # Это токен
                flattened_tokens[prefix] = {
                    "value": node["value"],
                    "comment": node.get("comment", "")
                }
            else:
                # Ключи верхнего уровня, такие как "dark", "text" и т.д.
                for key, value in node.items():
                    if key in ["config"]: # Пропускаем конфиг
                        continue
                    new_prefix = f"{prefix}.{key}" if prefix else key
                    recurse(value, new_prefix)

    recurse(data)
    return flattened_tokens

def list_components(repo_path):
    """
    Перчисляет компоненты из packages/plasma-web/src/components
    Возвращает список имен компонентов.
    """
    # Мы приоритизируем plasma-web как основной кит для веба
    components_path = os.path.join(repo_path, "packages/plasma-web/src/components")
    if not os.path.exists(components_path):
        return []
    
    components = []
    for item in os.listdir(components_path):
        full_path = os.path.join(components_path, item)
        if os.path.isdir(full_path) and not item.startswith("."):
            components.append(item)
    
    return sorted(components)
