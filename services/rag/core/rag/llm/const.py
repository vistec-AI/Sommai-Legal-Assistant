from ..prompting import LLAMA_3_PROMPT_TEMPLATE
import ast
import os

LLM_CONFIG = {"temperature": 0.5,
              "max_new_tokens": 8192,
              "top_k": 50,
              "top_p": 0.95
              }


default_llm_dict = {
    "Llama 3-70b": {"model_name": "Llama 3-70b",
                "port": "31100",
                "ip_address": "http://10.204.100.78",
                "base_llm": "llama3",
                "max_new_tokens": 8192,
                "is_vllm": True},
    "Llama 3.1-instruct-70b": {"model_name": "Llama 3.1-instruct-70b",
                  "port": "31200",
                  "ip_address": "http://10.204.100.78",
                  "base_llm": "llama3",
                  "max_new_tokens": 8192,
                  "is_vllm": True},
    "Llama 3-typhoon-instruct-70b": {"model_name": "Llama 3-typhoon-instruct-70b",
                    "port": "31300",
                    "ip_address": "http://10.204.100.78",
                    "base_llm": "llama3",
                    "max_new_tokens": 8192,
                    "is_vllm": True},
    "Sea-Lion-8B": {"model_name": "Sea-Lion-8B",
                    "port": "31400",
                    "ip_address": "http://10.204.100.78",
                    "base_llm": "llama3",
                    "max_new_tokens": 8192,
                    "is_vllm": True},
    "WangchanX-Legal": {"model_name": "WangchanX-Legal",
                        "port": "443",
                        "ip_address": "https://infer-legal.wangchan.ai",
                        "base_llm": "llama3",
                        "max_new_tokens": 8192,
                        "is_vllm": True}
}

if os.getenv("LLM_SELECTION_DICT"):
    LLM_SELECTION_DICT = ast.literal_eval(os.getenv("LLM_SELECTION_DICT"))
else:
    LLM_SELECTION_DICT = default_llm_dict

PROMPT_TEMPLATE_SELECTION_DICT = {
    "llama3": LLAMA_3_PROMPT_TEMPLATE
}
