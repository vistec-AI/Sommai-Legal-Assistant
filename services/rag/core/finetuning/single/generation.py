from llama_index.core.llms.utils import LLM
from llama_index.core.schema import TextNode

from ...rag.prompting import SINGLE_QA_CRAFTING_TEMPLATE_STR
from ..base import EmbeddingQAFinetuneDataset
from ..utils import postprocess_qa_pairs

import random
import sys
from tqdm import tqdm
import re
from typing import List, Dict

def generate_law_qa_embedding_pairs(
    nodes: List[TextNode],
    reference: Dict[str, str],
    llm: LLM,
    qa_generate_prompt_tmpl: str = SINGLE_QA_CRAFTING_TEMPLATE_STR,
    num_questions_per_chunk: int = 2,
    show_progress: bool = False,
    save_path: str = "",
    postprocess_chance: int = 70,
) -> EmbeddingQAFinetuneDataset:
    """Generate examples given a set of nodes."""
    
    def batch_list(input_list, batch_size):
        return [input_list[i:i+batch_size] for i in range(0, len(input_list), batch_size)]
    
    assert num_questions_per_chunk > 0, "Number of questions per chunk must be greater than 0"
    
    node_dict = {
        node.node_id: node.get_content()
        for node in nodes
    }

    queries = {}
    relevant_docs = {}
    
    iterator = tqdm(nodes, desc="Generating QA pairs...", unit="section", leave=True, ncols=100, colour='blue') if show_progress else nodes
    
    for node in iterator:
        while True:
            try:
                if node.metadata["reference_nodes"]:
                    try:
                        reference_str = "\n".join([reference[ref_id].sectionContent for ref_id in node.metadata["reference_nodes"]])
                    except Exception as e:
                        raise ValueError(f"An error occurred while processing reference for node {node.node_id}: {str(e)}")
                else:
                    reference_str = "No reference"
                    
                query = qa_generate_prompt_tmpl.format(
                    context_str=node.text,
                    reference_str=reference_str,
                    num_questions_per_chunk=num_questions_per_chunk
                )
                response = llm.complete(query)

                result = str(response).strip().split("\n")
                questions = [
                    re.sub(r"^\d+[\).\s]", "", question).strip() for question in result
                ]
                questions = [question for question in questions if len(question) > 0]
                questions = [postprocess_qa_pairs(question) if random.randint(1, 100) <= postprocess_chance else question for question in questions]

                for index, question in enumerate(questions):
                    question_id = f"{node.node_id}_{index+1}"
                    queries[question_id] = question
                    relevant_docs[question_id] = [node.node_id]
                if save_path:
                    EmbeddingQAFinetuneDataset(
                        queries=queries, corpus=node_dict, relevant_docs=relevant_docs
                    ).save_json(path=save_path)
                break

            except ValueError as e:
                print(f"Reference Failed. Error: {e}")
                sys.exit()
            except Exception as e:
                # Continue the outer loop if the exception is not a ValueError
                print(f"An error occurred: {str(e)}")
                pass

    # construct dataset
    return EmbeddingQAFinetuneDataset(
        queries=queries, corpus=node_dict, relevant_docs=relevant_docs
    )