from typing import Optional
from llama_index.core.llms.llm import LLM

from ..prompting.template import EN_SYSTEM_PROMPT_STR, TH_SYSTEM_PROMPT_STR
from .const import PROMPT_TEMPLATE_SELECTION_DICT

def init_system_prompt(prompt_language: str = "en") -> str:
    """Initialize the system prompt based on the provided language."""
    prompt_language = prompt_language.lower()
    if prompt_language == "en":
        return EN_SYSTEM_PROMPT_STR
    elif prompt_language == "th":
        return TH_SYSTEM_PROMPT_STR
    else:
        raise ValueError(f"Invalid prompt language: {prompt_language}. We only support 'en' and 'th'.")

def completion_manager(base_llm: LLM,
                       prompt_language: str = "en") -> LLM:
    """
    Initializes an LLM with the specified model and system prompt.
    """
    
    assert base_llm in PROMPT_TEMPLATE_SELECTION_DICT, f"Base LLM {base_llm} prompt template not supported."
    completion_template = PROMPT_TEMPLATE_SELECTION_DICT.get(base_llm.lower().strip())
    base_system_prompt = init_system_prompt(prompt_language=prompt_language)
    def completion_to_prompt(completion: str, system_prompt: Optional[str] = None) -> str:
        system_prompt_str = system_prompt or base_system_prompt

        return (
            completion_template.format(
                system_prompt=system_prompt_str.strip(),
                question=completion.strip())
        )
        
    return completion_to_prompt