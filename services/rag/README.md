
# Sommai API

## Overview

Sommai API is a Retrieval-Augmented Generation (RAG) system designed for handling Thai legal data.

## Build

```sh
docker build -t sommai-api .
```

## RUN

```sh
docker run -p 9000:9000 -it --gpus all sommai-api
```

---

## Endpoints

The Sommai API provides three key endpoints for document retrieval, response generation, and system health checks:

1. **`/retrieval`** - Retrieves relevant documents based on a `RetrievalRequest`.
2. **`/generate`** - Generates a response based on a `QueryRequest`.
3. **`/healthz`** - Health check endpoint to verify the system's availability.

---

### 1. Retrieval Endpoint

This endpoint retrieves documents based on the query input, allowing for reranking and customizing the number of top results.

#### Request
```bash
curl --location 'http://0.0.0.0:9000/retrieval' --header 'Content-Type: application/json' --data '{
    "query": "การจัดซื้อจัดจ้างพัสดุของภาครัฐทำวิธีไหนได้บ้าง",
    "reranker": true,
    "top_k": 10,
    "top_n": 5
}'
```

#### Parameters:
- **`query`** (string): The search query.
- **`reranker`** (boolean): Whether to use a reranker for better results.
- **`top_k`** (integer): Maximum number of results to retrieve.
- **`top_n`** (integer): Number of results to return after reranking.

---

### 2. Generate Endpoint

This endpoint generates a response based on a query and allows customization of the model, language, and response generation parameters.

#### Request
```bash
curl --location 'http://0.0.0.0:9000/generate' --header 'Content-Type: application/json' --data '{
    "query": "การจัดซื้อจัดจ้างพัสดุของภาครัฐทำวิธีไหนได้บ้าง",
    "model": "WangchanX-Legal",
    "language": "th",
    "top_k": 10,
    "top_n": 5,
    "reranker": true,
    "temperature": 0.5
}'
```

#### Parameters:
- **`query`** (string): The question or request for generation.
- **`model`** (string): The model to use for generating responses (e.g., `WangchanX-Legal`, `Llama 3-70b`, `Llama 3.1-instruct-70b`, `Llama 3-typhoon-instruct-70b`, `Sea-Lion-8B`).
- **`language`** (string): The language for the response (e.g., `th`, `en`).
- **`top_k`** (integer): Maximum number of candidate responses.
- **`top_n`** (integer): Number of final responses to return.
- **`reranker`** (boolean): Whether to rerank the results.
- **`temperature`** (float): Controls the randomness of the generation. Lower values make the output more deterministic.

---

### 3. Healthz Endpoint

This endpoint checks the health and availability of the API.

#### Request
```bash
curl --location 'http://0.0.0.0:9000/healthz' --header 'Content-Type: application/json'
```

No parameters are required for this endpoint.

---

## Available Models

- **Llama 3-70b**
- **Llama 3.1-instruct-70b**
- **Llama 3-typhoon-instruct-70b**
- **Sea-Lion-8B**
- **WangchanX-Legal**

---

## License

This project is licensed under the **VISAI AI License**.

---
