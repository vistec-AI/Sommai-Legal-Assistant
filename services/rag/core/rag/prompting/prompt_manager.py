from ..prompting.template import (
    EN_DEFAULT_REFERENCE_TEMPLATE_STR,
    EN_REFERENCE_QA_TEMPLATE_STR,
    EN_REFINE_REFERENCE_TEMPLATE_STR,
    EN_REFINE_TEMPLATE_STR,
    TH_DEFAULT_REFERENCE_TEMPLATE_STR,
    TH_REFERENCE_QA_TEMPLATE_STR,
    TH_REFINE_REFERENCE_TEMPLATE_STR,
    TH_REFINE_TEMPLATE_STR,
    )

def init_prompts(prompt_language: str = "en") -> dict:
    """Initialize the prompts based on the provided language."""
    prompt_language = prompt_language.lower()
    if prompt_language == "en":
        return {
            "REFERENCE_QA_TEMPLATE": EN_REFERENCE_QA_TEMPLATE_STR,
            "REFINE_TEMPLATE": EN_REFINE_TEMPLATE_STR,
            "REFINE_REFERENCE_TEMPLATE": EN_REFINE_REFERENCE_TEMPLATE_STR,
            "DEFAULT_REFERENCE_TEMPLATE": EN_DEFAULT_REFERENCE_TEMPLATE_STR
        }
    elif prompt_language == "th":
        return {
            "REFERENCE_QA_TEMPLATE": TH_REFERENCE_QA_TEMPLATE_STR,
            "REFINE_TEMPLATE": TH_REFINE_TEMPLATE_STR,
            "REFINE_REFERENCE_TEMPLATE": TH_REFINE_REFERENCE_TEMPLATE_STR,
            "DEFAULT_REFERENCE_TEMPLATE": TH_DEFAULT_REFERENCE_TEMPLATE_STR
        }
    else:
        raise ValueError(f"Invalid prompt language: {prompt_language}. We only support 'en' and 'th'.")