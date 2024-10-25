import random
from typing import List
from tqdm import tqdm
from collections import defaultdict

from ...hierarchical_parser.schema import LawTree

def law_sampling(law_sections: List[LawTree],
                 iterations: int = 1000,
                 sample_portion_size: int = 10,
                 show_progress: bool = True) -> List[List[LawTree]]:
    assert len(law_sections) > sample_portion_size, "sample_portion_size cannot exceed the number of law_sections"
    # create section counter
    selection_count = defaultdict(int)
    
    iterator = tqdm(range(iterations), desc="Sampling law sections...", unit="batch", leave=True, ncols=100, colour='blue') if show_progress else range(iterations)
    
    samples = []
    for _ in iterator:
        # Calculate weights inversely proportional to selection count (add 1 to avoid division by zero)
        weights = [1 / (selection_count[section.sectionNo] + 1) for section in law_sections]
        
        # Perform weighted sampling without replacement to select a portion
        selected_sections = random.choices(law_sections, weights=weights, k=sample_portion_size)

        # Update the counts for the selected values
        for selected_section in selected_sections:
            selection_count[selected_section.sectionNo] += 1
        
        # Append the selected values to the samples list
        samples.append(selected_sections)
        
    return samples