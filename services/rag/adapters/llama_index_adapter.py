import os
import json
from glob import glob
import pickle
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from llama_index.core import VectorStoreIndex, Settings, QueryBundle
from llama_index.core.schema import TextNode
from langfuse.llama_index import LlamaIndexCallbackHandler
from llama_index.core.callbacks import CallbackManager
from infrastructure.embeddings.instructor_embeddings import get_instructor_embedding_model
from infrastructure.rerankers.instructor_rerankers import get_instructor_reranker_model
from infrastructure.rag.llm import initialize_llm
from infrastructure.rag.query_engine import create_query_engine
from infrastructure.rag.retriever import visualize_retrieved_nodes
from ports.llama_service_port import LlamaServicePort

class LlamaIndexAdapter(LlamaServicePort):
    def __init__(self):
        self.callback_handler = self.initialize_callback_handler()
        self.vector_index = None
        self.law_url_mapper = self.load_law_url_mapper()
        self.embed_model = get_instructor_embedding_model(os.getenv("EMBEDDING_MODEL", "embedding"))
        if self.callback_handler:
            Settings.callback_manager = CallbackManager([self.callback_handler])

    @staticmethod
    def initialize_callback_handler():
        if os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY") and os.getenv("LANGFUSE_HOST"):
            return LlamaIndexCallbackHandler()
        return None

    @staticmethod
    def load_law_url_mapper():
        documents_dir = os.getenv("DOCUMENTS_DIR", "/app/data")
        try:
            with open(os.path.join(documents_dir, "wcx_law_url_mapper.json")) as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def initialize_retrievers(self):
        nodes = []
        documents_dir = os.getenv("DOCUMENTS_DIR", "/app/data")
        json_files = [f for f in glob(os.path.join(documents_dir, "*.json")) if os.path.basename(f) not in ["wcx_law_url_mapper.json", "vector_index.pkl"]]
        for path in json_files:
            law_code = os.path.basename(path).replace(".json", "")
            with open(path) as file:
                law_sections = json.load(file)
            nodes.extend(
                TextNode(
                    text=section["section_content"],
                    id_=f"{law_code}_{section['section_num']}",
                    extra_info={
                        "reference_nodes": [],
                        "law_name": section['law_name'],
                        "law_code": f"{law_code}_{section['section_num']}",
                        "url": self.law_url_mapper.get(law_code, "")
                    },
                )
                for section in law_sections
            )

        self.vector_index = VectorStoreIndex(nodes, embed_model=self.embed_model, show_progress=True, store_nodes_override=True)
        
    def load_vector_index(self):
        try:
            with open("/app/data/vector_index.pkl", "rb") as f:
                self.vector_index = pickle.load(f)
        except FileNotFoundError:
            raise HTTPException(status_code=500, detail="Vector index file not found. Please initialize retrievers first.")

    def get_vector_index(self):
        if self.vector_index is None:
            raise HTTPException(status_code=500, detail="Vector index not initialized.")
        return self.vector_index

    def retrieve_documents(self, request):
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query string cannot be empty.")
        Settings.llm = None
        vector_index = self.get_vector_index()
        retriever = vector_index.as_retriever(similarity_top_k=request.top_k)

        postprocessors = [
            get_instructor_reranker_model(model_name=os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-v2-m3"), use_fp16=True, top_n=request.top_n)
        ] if request.reranker else []
        query_engine = create_query_engine(
            retriever=retriever,
            node_postprocessors=postprocessors
        )
        retrieved_nodes = query_engine._nodes(QueryBundle(request.query))
        if self.callback_handler:
            self.callback_handler.flush()
        return visualize_retrieved_nodes(retrieved_nodes)

    def generate_response(self, request):
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query string cannot be empty.")

        vector_index = self.get_vector_index()
        if self.callback_handler:
            self.callback_handler.set_trace_params(tags=[request.model])
        Settings.llm = initialize_llm(
            model_id=request.model,
            prompt_language=request.language,
            temperature=request.temperature
        )

        retriever = vector_index.as_retriever(similarity_top_k=request.top_k)
        reranker = get_instructor_reranker_model(model_name=os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-v2-m3"), use_fp16=True, top_n=request.top_n)
        postprocessors = [
            reranker
        ] if request.reranker else []
        query_engine = create_query_engine(
            retriever=retriever,
            response_mode="default",
            prompt_language=request.language,
            node_postprocessors=postprocessors,
            streaming=True,
        )

        def fetch_stream(query_str, engine):
            response, _, _ = engine.query(QueryBundle(query_str))
            for chunk in response.get_response():
                yield f'{{"text": "{chunk}"}}\n\n'
            if self.callback_handler:
                self.callback_handler.flush()

        return StreamingResponse(fetch_stream(request.query, query_engine), media_type="text/event-stream")