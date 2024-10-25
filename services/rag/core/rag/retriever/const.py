from llama_index.retrievers.bm25 import BM25Retriever

HF_RETRIEVER_SELECTION_DICT = {
    "bge-m3": "BAAI/bge-m3",
    "me5-large": "intfloat/multilingual-e5-large",
    "me5-base": "intfloat/multilingual-e5-base",
    "wangchanberta": "airesearch/wangchanberta-base-att-spm-uncased",
}

BM25_RETRIEVER_SELECTION_DICT = {
    "bm25": BM25Retriever,
}