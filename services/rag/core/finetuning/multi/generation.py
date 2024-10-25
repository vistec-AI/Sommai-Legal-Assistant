from llama_index.core.llms.utils import LLM

from ...rag.prompting import MULTI_QA_CRAFTING_TEMPLATE_STR
from ..base import EmbeddingQAFinetuneDataset
from ..utils import postprocess_qa_pairs
from ...hierarchical_parser.parser import LawTree
from .query_random import law_sampling
from ...rag.prompting.template import EN_SYSTEM_PROMPT_STR

from tqdm import tqdm
import os
import uuid
import sys
import jsonlines
from typing import List, Dict
from pydantic import BaseModel
from openai import OpenAI

class MultiQueryAnswerGenerator(BaseModel):
    # llm: LLM
    filename: str
    save: bool = True
    save_path: str = ""
    save_filename: str = ""
    iterations: int = 1000
    sample_portion_size: int = 10
    max_retries: int = 3
    show_progress: bool = False
    
    @property
    def law_sections(self) -> List[LawTree]:
        law_sections = LawTree.from_filename(self.filename)
        law_sections = law_sections.get_leaf_nodes(return_as_list=True, as_reference=False)
        return law_sections
    
    @property
    def reference_sections(self) -> Dict[str, LawTree]:
        reference_sections = LawTree.from_filename(self.filename)
        reference_sections = reference_sections.get_leaf_nodes(return_as_list=False, as_reference=True)
        return reference_sections
    
    def openai_construct(self, query: str) -> str:
        client = OpenAI()

        response = client.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=[
            {"role": "system", "content": EN_SYSTEM_PROMPT_STR},
            {"role": "user", "content": query},
        ],
        response_format={"type": "json_object"},
        seed=3939
        )
        
        assert len(response.choices) == 1
        output_dict = eval(response.choices[0].message.content)
        assert isinstance(output_dict, dict)

        return output_dict
    
    def get_sampling(self):
        return law_sampling(self.law_sections, self.iterations, self.sample_portion_size, self.show_progress)
    
    def generate_multi_law_qa_embedding_pairs(self) -> EmbeddingQAFinetuneDataset:
        assert os.path.exists(self.save_path), f"Path not exist: {self.save_path}"
        node_dict = {node.sectionLabel: node.sectionContent for node in self.law_sections}
        
        jsonlines_output = []

        queries = {}
        relevant_docs = {}
        sampling = self.get_sampling()
        
        iterator = tqdm(sampling, desc="Generating multi law QA pairs...", unit="query", leave=True, ncols=100, colour='blue') if self.show_progress else sampling
        
        for query in iterator:
            while True:
                try:
                    sample_sections = [f"index {index}: {sample.sectionContent}" for index, sample in enumerate(query)]
                    reference_sections = [ref for reference in query for ref in reference.sectionReference]
                    reference_sections = list(set(reference_sections))
                    reference_sections = [self.reference_sections[reference].sectionContent for reference in reference_sections]
                    
                    section_construct = "\n".join(sample_sections)
                    reference_construct = "\n".join(reference_sections) if reference_sections else "No reference."
                    prompt = MULTI_QA_CRAFTING_TEMPLATE_STR.format(context_str=section_construct, reference_str=reference_construct)
                    response = self.openai_construct(query=prompt)
                    
                    # retrieved used section
                    used_section = [query[index] for index in response["context_index"]]
                    response["used_section"] = used_section
                    response["all_section"] = query
                    
                    # Need fix error
                    # Task aborted
                    jsonlines_output.append(response)
                    ###
                    
                    # construct EmbeddingQAFinetuneDataset
                    key = str(uuid.uuid4())
                    queries[key] = response["th_query"]
                    relevant_docs[key] = [node.sectionLabel for node in response["used_section"]]
                    if self.save:
                        save_head = self.save_path or os.path.split(self.filename)[0]
                        save_tail = self.save_filename or f"multi_qa_{os.path.split(self.filename)[1].split('.')[0]}.json"
                        save_tail = f"{save_tail}.json" if not save_tail.endswith(".json") else save_tail
                        save_path = os.path.join(save_head, save_tail)
                        EmbeddingQAFinetuneDataset(
                            queries=queries, corpus=node_dict, relevant_docs=relevant_docs
                        ).save_json(path=save_path)
                        
                        with jsonlines.open(f"{save_path}l", mode="a") as writer:
                            writer.write_all(jsonlines_output)
                    break
                except FileNotFoundError as file_error:
                    print(file_error)
                    sys.exit()
                    
                
            return response
        