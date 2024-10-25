# WangchanX-Legal-ThaiCCL-Retriever

This guide details the process of fine-tuning [WangchanX-Legal-ThaiCCL-Retriever](https://huggingface.co/airesearch/WangchanX-Legal-ThaiCCL-Retriever) from `BGE-M3` embedding model to improve performance on a legal text retrieval task. BGE-M3, known for its versatility (multi-functionality, multi-linguality, multi-granularity), offers a powerful foundation for generating sentence embeddings. Fine-tuning tailors the pre-trained model to legal domain, leading to more meaningful representations.

For more details about `bge-m3` model, please refer to the [paper](https://arxiv.org/pdf/2402.03216.pdf) and [huggingface repo](https://huggingface.co/BAAI/bge-m3)

## Prerequisite
- **FlagEmbedding**
```
git clone https://github.com/FlagOpen/FlagEmbedding.git
cd FlagEmbedding
pip install -e .
```

## Dataset

A Legal dataset is [WangchanX-Legal-ThaiCCL-RAG](https://huggingface.co/datasets/airesearch/WangchanX-Legal-ThaiCCL-RAG) which supports the development of legal question-answering systems in Thai using Retrieval-Augmented Generation (RAG). It includes training and test sets specifically designed to enhance performance in the legal domain.

## Fine-tuning

You can follow `finetuning.ipynb` to fine-tune the embedding.

## License
MIT License