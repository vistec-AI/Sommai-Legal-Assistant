import json
import os
from typing import Dict, List, Tuple

from pydantic import BaseModel

class EmbeddingQAFinetuneDataset(BaseModel):
    """Embedding QA Finetuning Dataset.

    Args:
        queries (Dict[str, str]): Dict id -> query.
        corpus (Dict[str, str]): Dict id -> string.
        relevant_docs (Dict[str, List[str]]): Dict query id -> list of doc ids.

    """

    queries: Dict[str, str]  # dict id -> query
    corpus: Dict[str, str]  # dict id -> string
    relevant_docs: Dict[str, List[str]]  # query id -> list of doc ids
    mode: str = "text"  # "mode": "text"

    @property
    def query_docid_pairs(self) -> List[Tuple[str, List[str]]]:
        """Get query, relevant doc ids."""
        return [
            (query, self.relevant_docs[query_id])
            for query_id, query in self.queries.items()
        ]

    def save_json(self, path: str) -> None:
        """Append new data to a JSON file, intelligently handling list appends."""
        if os.path.exists(path):
            # Load existing data
            with open(path, 'r', encoding='utf-8') as file:
                existing_data = json.load(file)
            
            existing_data["queries"].update(self.dict()["queries"])
            existing_data["corpus"].update(self.dict()["corpus"])
            existing_data["relevant_docs"].update(self.dict()["relevant_docs"])
            
            with open(path, 'w', encoding='utf-8') as file:
                json.dump(existing_data, file, indent=4, ensure_ascii=False)
        else:
            with open(path, 'w', encoding='utf-8') as file:
                json.dump(self.dict(), file, indent=4, ensure_ascii=False)

    @classmethod
    def from_json(cls, path: str) -> "EmbeddingQAFinetuneDataset":
        """Load json."""
        with open(path) as f:
            data = json.load(f)
        return cls(**data)