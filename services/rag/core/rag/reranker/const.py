from llama_index.postprocessor.flag_embedding_reranker import FlagEmbeddingReranker

RERANKER_SELECTION_DICT = {
    "BAAI/bge-reranker-v2-m3": FlagEmbeddingReranker(model="BAAI/bge-reranker-v2-m3", use_fp16=True),
}
