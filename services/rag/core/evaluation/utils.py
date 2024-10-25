import json
import os
from typing import List, Any
from copy import deepcopy
import re

from llama_index.core.evaluation import (
    generate_question_context_pairs,
    EmbeddingQAFinetuneDataset,
)
from llama_index.core import Document


from .const import eval_data_path, eval_data_batch_path
from ..rag.prompting import QA_CRAFTING_TEMPLATE_STR


def batch_list(input_list, batch_size):
    # This function takes an input list and a batch size,
    # then yields batches of the given size.
    for i in range(0, len(input_list), batch_size):
        yield input_list[i:i + batch_size]
        
def merge_qa_pairs_batch(eval_data_path = eval_data_path,
                        eval_data_batch_path = eval_data_batch_path,
                        save_output: bool = True,
                        max_pairs: int = -1,
                    ) -> EmbeddingQAFinetuneDataset:
    
    merge: Any[None, dict] = None
    filenames = [os.path.join(eval_data_batch_path, f) for f in os.listdir(eval_data_batch_path)]
    for filename in filenames:
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
            # Iterate through queries and merge
            if merge:
                for key in ['queries', 'relevant_docs']:
                    pair_count = 0
                    for item_id, item_value in data.get(key, {}).items():
                        pair_count += 1
                        if max_pairs != -1 and pair_count >= max_pairs:
                            break
                        if isinstance(item_value, str):
                            pattern = r'^\"|\"$|^\'|\'$'
                            item_value = re.sub(pattern, '', item_value.strip())
                        merge[key][item_id] = item_value
                for key in ['corpus']:
                    for item_id, item_value in data.get(key, {}).items():
                        merge[key][item_id] = item_value
                    
            else:
                merge = deepcopy(data)
    print("merge complete")
                        
    if save_output:
        output_path = os.path.join(eval_data_path, 'criminal_code_qa_pairs_refine_merge.json')
        print(f"save file at {output_path}")
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(merge, file, ensure_ascii=False, indent=4)
    return merge

def generate_qa_pairs_batch(batches: List[Document], llm):
    """generate qa pairs from Documents"""
    for i, batch in enumerate(batches):
        while True:
            try:
                eval_dataset = generate_question_context_pairs(
                    batch,
                    llm,
                    qa_generate_prompt_tmpl=qa_crafting_tempalte_str
                )
                eval_dataset.save_json(os.path.join(eval_data_path, f"criminal_code_qa_pairs_refine_{i}.json"))
                break
            except:
                pass

    