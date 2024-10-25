from core.rag.query_engine import LawQueryEngine

def create_query_engine(*args, **kwargs):
    return LawQueryEngine.from_args(*args, **kwargs)