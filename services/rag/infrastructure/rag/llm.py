from core.rag.llm import initialize_llm as package_initialize_llm

def initialize_llm(model_id: str, prompt_language: str, temperature: float):
    return package_initialize_llm(model_id=model_id, prompt_language=prompt_language, temperature=temperature)