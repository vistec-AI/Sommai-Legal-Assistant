from llama_index.core.retrievers import BaseRetriever
from llama_index.core.schema import QueryBundle, NodeWithScore
from llama_index.core.response.notebook_utils import (display_source_node,
                                                      display_response)
from llama_index.core.llms.llm import LLM
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.retrievers.bm25 import BM25Retriever

from typing import List, Union
import logging

from .hybrid_retriever import (
    HybridRetriever
)

from ..prompting import (
    generate_queries
)


from typing import Union, List

class FusionRetriever(BaseRetriever):
    """Ensemble retriever with fusion."""

    def __init__(
        self,
        retrievers: Union[BaseRetriever, List[BaseRetriever]] = [],
        bm25_retriever: BM25Retriever = None,
        llm: LLM = None,
        reranker: BaseNodePostprocessor = None,
        reference_nodes: dict = None,
        top_k: int = 10,
        top_n: int = 10,
        num_queries: int = 1,
        verbose: bool = False,
    ) -> None:
        """Initialize FusionRetriever."""
        super().__init__()
        self.llm = llm
        self._top_k = top_k
        self._top_n = top_n
        self.bm25_retriever = bm25_retriever
        self.reference_nodes = reference_nodes
        self._initialize_retrievers(retrievers)
        self.reranker = reranker
        self._num_queries = num_queries
        self.verbose = verbose
        
    @property
    def top_k(self) -> int:
        return self._top_k

    @top_k.setter
    def top_k(self, value: int) -> None:
        if isinstance(value, int) and value >= 0:
            self._top_k = value
            self.retrievers = HybridRetriever(self.retrievers.retrievers, value)
        else:
            raise ValueError("top_k must be a non-negative integer")

    @property
    def top_n(self) -> int:
        return self._top_n

    @top_n.setter
    def top_n(self, value: int) -> None:
        if isinstance(value, int) and value >= 0:
            self._top_n = value
            if self.reranker:
                self.reranker.top_n = value
        else:
            raise ValueError("top_n must be a non-negative integer")
        
    @property
    def num_queries(self) -> int:
        return self._num_queries

    @num_queries.setter
    def num_queries(self, value: int) -> None:
        if isinstance(value, int) and value >= 0:
            self._num_queries = value
        else:
            raise ValueError("num_queries must be a non-negative integer")

    def _initialize_retrievers(self, retrievers: Union[BaseRetriever, List[BaseRetriever]]) -> None:
        """Initialize retrievers."""
        if isinstance(retrievers, BaseRetriever):
            self._initialize_single_retriever(retrievers)
        else:
            self._initialize_multiple_retrievers(retrievers)

    def _initialize_single_retriever(self, retriever: BaseRetriever) -> None:
        """Initialize with a single retriever."""
        self.reference_nodes = self.reference_nodes if self.reference_nodes else retriever._index.docstore.docs
        retrievers_list = [retriever]
        self._initialize_hybrid_retriever(retrievers_list)

    def _initialize_multiple_retrievers(self, retrievers: List[BaseRetriever]) -> None:
        """Initialize with multiple retrievers."""
        if not self.reference_nodes:
            for retriever in retrievers:
                self._check_reference_nodes(retriever)
        retrievers_list = retrievers.copy()
        if self.bm25_retriever:
            retrievers_list.append(self.bm25_retriever)
        self._initialize_hybrid_retriever(retrievers_list)

    def _initialize_hybrid_retriever(self, retrievers_list: List[BaseRetriever]) -> None:
        """Initialize hybrid retriever."""
        self.retrievers = HybridRetriever(retrievers_list, self._top_k)

    def _check_reference_nodes(self, retriever: BaseRetriever) -> None:
        """Check default nodes."""
        if self.reference_nodes:
            assert self.reference_nodes == retriever._index.docstore.docs, "Default nodes from all retrievers must be the same"
        else:
            self.reference_nodes = retriever._index.docstore.docs
        
    def update_config(self, **kwargs) -> None:
        """Update configuration of the FusionRetriever with a warning for invalid attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                if key == "retrievers":
                    self._initialize_retrievers(value)
                elif key == "top_k":
                    self._top_k = value
                    self.retrievers = HybridRetriever(self.retrievers.retrievers, value)
                elif key == "reranker":
                    self.reranker = value
                    if self.reranker:
                        self.reranker.top_n = self._top_n
                elif key == "top_n":
                    self._top_n = value
                    if self.reranker:
                        self.reranker.top_n = value
                else:
                    setattr(self, key, value)
            else:
                logging.warning(f"{key} is not a valid configuration attribute for FusionRetriever and will be ignored.")

    def _retrieve(self, query_str: str) -> List[NodeWithScore]:
        """Retrieve."""
        assert len(self.retrievers) > 0, "FusionRetriever must have at least one retriever"
        queries = generate_queries(self.llm, query_str, num_queries=self._num_queries)
        results = self.run_queries(queries, self.retrievers)
        
        if self.reranker:
            final_results = self.reranker.postprocess_nodes(results, query_str)
        else:
            final_results = results
        
        if self.verbose:
            for node in final_results:
                display_source_node(node)

        return final_results
    
    async def _aretrieve(self, query_str: str) -> List[NodeWithScore]:
        """Retrieve."""
        assert len(self.retrievers) < 1, "FusionRetriever must have at least one retriever"
        queries = generate_queries(self.llm, query_str, num_queries=self._num_queries)
        results = await self.arun_queries(queries, self.retrievers)
        
        if self.reranker:
            final_results = self.reranker.postprocess_nodes(results, query_str)
        else:
            final_results = results
        
        if self.verbose:
            for node in final_results:
                display_source_node(node)

        return final_results
    
    def run_queries(self, queries: list, hybrid_retriever: HybridRetriever) -> List[NodeWithScore]:
        """Run queries using hybrid retriever and rerank the results."""
        retrieved_results = [hybrid_retriever.retrieve(query) for query in queries]
        
        all_nodes = []
        node_ids = set()

        for nodes in retrieved_results:
            for n in nodes:
                if n.node.node_id not in node_ids:
                    all_nodes.append(n)
                    node_ids.add(n.node.node_id)
        return all_nodes
    
    async def arun_queries(self, queries: list, hybrid_retriever: HybridRetriever) -> List[NodeWithScore]:
        """Run queries using hybrid retriever and rerank the results."""
        retrieved_results = [await hybrid_retriever.aretrieve(query) for query in queries]
        
        all_nodes = []
        node_ids = set()

        for nodes in retrieved_results:
            for n in nodes:
                if n.node.node_id not in node_ids:
                    all_nodes.append(n)
                    node_ids.add(n.node.node_id)
        return retrieved_results