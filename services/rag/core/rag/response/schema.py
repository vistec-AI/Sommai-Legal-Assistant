from typing import List

from llama_index.core.schema import NodeWithScore

class LawResponse:
    def __init__(self, query: str, response: str, nodes: List[NodeWithScore], format_input: str, reference: List[List[str]]) -> None:
        self.query = query
        self.response = response
        self.nodes = nodes
        self.format_input = format_input
        self.reference = reference
        
    def __repr__(self):
        return f'LawResponse(query={self.query!r}, response={self.response!r}, nodes={self.nodes!r}, format_input={self.format_input!r}, reference={self.reference!r})'
    
    def __str__(self):
        return f'Query: {self.query}\nResponse: {self.response}\nNodes: {self.nodes}\nFormat Input: {self.format_input}\nReference: {self.reference}'
        
    def get_response(self) -> str:
        return self.response
    
    def get_query(self) -> str:
        return self.query
    
    def get_nodes(self) -> List[NodeWithScore]:
        return self.nodes
    
    def get_format_input(self) -> str:
        return self.format_input
    
    def get_reference(self) -> List[List[str]]:
        return self.reference