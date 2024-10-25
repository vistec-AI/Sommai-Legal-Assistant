from llama_index.core.retrievers import BaseRetriever
from typing import List

class HybridRetriever(BaseRetriever):
    """get all retrievers and return all retrieved results"""
    def __init__(self, retrievers: List[BaseRetriever] = [], top_k: int = 10) -> None:
        self.retrievers = retrievers
        self.top_k = top_k
        super().__init__()
        
    def __len__(self) -> int:
        return len(self.retrievers)

    def _retrieve(self, query, **kwargs) -> List:
        all_nodes = []
        node_ids = set()

        # Synchronously gather results from all retrievers
        for retriever in self.retrievers:
            retriever._similarity_top_k = self.top_k
            nodes = retriever.retrieve(query, **kwargs)

            # Combine results while avoiding duplicates
            for n in nodes:
                if n.node.node_id not in node_ids:
                    all_nodes.append(n)
                    node_ids.add(n.node.node_id)
        return all_nodes
    
    async def _aretrieve(self, query, **kwargs) -> List:
        all_nodes = []
        node_ids = set()

        # Synchronously gather results from all retrievers
        for retriever in self.retrievers:
            retriever._similarity_top_k = self.top_k
            nodes = await retriever.aretrieve(query, **kwargs)

            # Combine results while avoiding duplicates
            for n in nodes:
                if n.node.node_id not in node_ids:
                    all_nodes.append(n)
                    node_ids.add(n.node.node_id)
        return all_nodes