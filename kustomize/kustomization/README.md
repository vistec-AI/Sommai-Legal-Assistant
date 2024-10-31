# RAG Configuration

This document provides information on the essential configurations and settings for deploying various Large Language Models (LLMs) and services, as well as environment variables for integration with external services.

---

## Environment Variables

```
rag.env
```

### Langfuse Integration
- **LANGFUSE_PUBLIC_KEY**: Public key for accessing Langfuse services.
- **LANGFUSE_SECRET_KEY**: Secret key for secure communication with Langfuse.
- **LANGFUSE_HOST**: Host URL for Langfuse services.

### Re-Ranker Model
- **RERANKER_MODEL**: Specifies the re-ranking model used, currently set to `BAAI/bge-reranker-v2-m3`.


```
https://huggingface.co/BAAI/bge-reranker-v2-m3
```

### Embedding Service
- **EMBEDDING_URL**: Endpoint for accessing the embedding service, useful for various text analysis and retrieval tasks.

```
https://github.com/huggingface/text-embeddings-inference
```
---

## Language Model (LLM) Configuration

The following LLMs are available for selection, each with specific configurations such as IP address, port, and base model information:

| Model Name         | IP Address                                    | Port | Base Model | Max Tokens | vLLM |
|--------------------|-----------------------------------------------|------|------------|------------|------|
| Llama 3            | http://meta-llama-3.sommai.svc.cluster.local  | 8000 | llama3     | 8192       | True |
| Llama 3.1          | http://meta-llama-3-1.sommai.svc.cluster.local| 8000 | llama3     | 8192       | True |
| Typhoon-1.5        | http://scb-typhoon-1-5.sommai.svc.cluster.local| 8000 | llama3     | 8192       | True |
| sea-lion-8b        | http://sea-lion-2-1.sommai.svc.cluster.local  | 8000 | llama3     | 8192       | True |
| WangchanX-Legal    | https://infer-legal.wangchan.ai               | 443  | llama3     | 8192       | True |

- **LLM_SELECTION_DICT**: A dictionary defining the model configuration details, allowing for flexible model selection and deployment across environments.

```json
LLM_SELECTION_DICT={ "Llama 3": {"model_name": "Llama 3", "port": "8000", "ip_address": "http://meta-llama-3.sommai.svc.cluster.local", "base_llm": "llama3", "max_new_tokens": 8192, "is_vllm": True}}
```

- **To support the /generate endpoint via a vLLM server only**
```
docker run --gpus all --entrypoint sh vllm/vllm-openai:v0.5.5 python3 -m vllm.entrypoints.api_server --model /mnt/model --gpu_memory_utilization 0.30 --max_model_len 8192
```

---

## Usage

1. Configure the environment variables above in your deployment settings.
2. Use the `LLM_SELECTION_DICT` to dynamically select and connect to the desired model by referencing the model's name.
3. Integrate with Langfuse for tracking and re-ranking using the `RERANKER_MODEL` and relevant API keys.

---

## Additional Notes

- Ensure that all URLs and IPs are accessible within your deployment environment.
- Review token limits and base model compatibility before use.
  