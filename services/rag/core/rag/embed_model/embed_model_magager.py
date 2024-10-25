from ...embeddings.custom_embedding.model import InstructorEmbeddings
from .const import CUSTOM_EMBED_MODEL_NAME

from llama_index.core.retrievers import BaseRetriever
from llama_index.core.schema import TextNode
from llama_index.core import VectorStoreIndex

from pydantic import BaseModel
from typing import Union, List, Dict
from collections import defaultdict

class EmbedModelManager(BaseModel):
    embed_model_name: Union[str, List[str]] = CUSTOM_EMBED_MODEL_NAME
    max_length: int = 514
    embed_batch_size: int = 10
    show_progress: bool = False
    
    def generate_retrievers(self, nodes: List[TextNode]) -> Dict[str, BaseRetriever]:
        vector_retrievers = defaultdict(dict)
        if isinstance(self.embed_model_name, list):
            for model_name in self.embed_model_name:
                embed_model = InstructorEmbeddings(model_name=model_name,
                                                   max_length=self.max_length,
                                                   embed_batch_size=self.embed_batch_size)
                
                # Create vector store index for each model
                index = VectorStoreIndex(nodes,
                                        embed_model=embed_model,
                                        show_progress=self.show_progress)

                # Create vector retriever for each model
                vector_retriever = index.as_retriever()

                # Store vector retriever in dictionary
                vector_retrievers[model_name] = vector_retriever
                
            return vector_retrievers
        
        else:
            embed_model = InstructorEmbeddings(model_name=self.model_name,
                                               max_length=self.max_length,
                                               embed_batch_size=self.embed_batch_size)
            
            index = VectorStoreIndex(nodes,
                                    embed_model=embed_model,
                                    show_progress=self.show_progress)
            
            vector_retriever = index.as_retriever()
            vector_retrievers[model_name] = vector_retriever
            
            return vector_retrievers