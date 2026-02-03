import os
from .indexer import index_documentation, get_index
from .parsers import parse_tokens, list_components
from whoosh.qparser import QueryParser, OrGroup, MultifieldParser

class PlasmaRAG:
    def __init__(self, repo_path, index_dir):
        self.repo_path = repo_path
        self.index_dir = index_dir
        self.tokens = parse_tokens(repo_path)
        self.components = list_components(repo_path)
        
        # Убедимся, что индекс существует
        if not os.path.exists(index_dir) or not os.listdir(index_dir):
            print("Создание индекса...")
            index_documentation(repo_path, index_dir)
        
        self.ix = get_index(index_dir)

    def search_documentation(self, query_str, limit=3):
        results_list = []
        with self.ix.searcher() as searcher:
            # Ищем по заголовку и контенту с приоритетом заголовка (boost=10.0)
            # OrGroup обязателен для нечеткого поиска по многим словам
            query = MultifieldParser(
                ["title", "content"], 
                self.ix.schema, 
                group=OrGroup,
                fieldboosts={"title": 10.0, "content": 1.0}
            ).parse(query_str)
            
            results = searcher.search(query, limit=limit)
            for hit in results:
                results_list.append({
                    "title": hit["title"],
                    "path": hit["path"],
                    "url": hit["url"],
                    "content_snippet": hit["content"][:4000] + "..." # Увеличенный сниппет для кода
                })
        return results_list

    def get_token(self, token_name):
        # Точное или частичное совпадение
        matches = {}
        for key, data in self.tokens.items():
            if token_name.lower() in key.lower():
                matches[key] = data
        return matches

    def get_component_info(self, component_name):
        # Проверяем, существует ли компонент
        if component_name not in self.components:
             # Попробуем нечеткий поиск
             candidates = [c for c in self.components if component_name.lower() in c.lower()]
             if not candidates:
                 return None
             component_name = candidates[0]
        
        # Ищем специфично документацию компонента
        # Мы можем переиспользовать search_documentation, но это не гарантирует точного попадания в заголовок
        results = self.search_documentation(component_name, limit=1)
        return results[0] if results else None
    
    def list_components(self):
        return self.components
