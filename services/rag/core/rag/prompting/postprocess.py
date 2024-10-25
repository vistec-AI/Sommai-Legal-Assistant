"""clean special tokens in response in case LLM return special tokens"""
import re

def clean_special_tokens(response: str) -> str:
    """clean special tokens in response in case LLM return special tokens"""
    response = response.strip()
    response = re.sub(r"\[/\w+\]", "", response)
    response = re.sub(r"\<\|\w+\|\>", "", response)
    response = re.sub(r"(^ตอบ\:?|^คำตอบ\:?)", "", response)
    return response.strip()