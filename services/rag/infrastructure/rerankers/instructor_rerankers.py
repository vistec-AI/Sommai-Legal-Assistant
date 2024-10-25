from llama_index.postprocessor.flag_embedding_reranker import FlagEmbeddingReranker

def get_instructor_reranker_model(model_name: str, use_fp16: bool, top_n: int):
    return FlagEmbeddingReranker(model=model_name, use_fp16=use_fp16, top_n=top_n)