from llama_index.llms.vllm import VllmServer

import copy
from typing import Any

from ...llms.base import BaseLLM

from .completion import completion_manager, init_system_prompt
from .const import LLM_CONFIG, LLM_SELECTION_DICT

def init_vllm(port: str,
                base_llm: str,
                ip_address: str = "localhost",
                prompt_language: str = "en",
                **kwargs: Any) -> VllmServer:
    """
    Initializes a connection to the Nvidia vllm server.

    Args:
        port: The port number for the connection.
        ip_address: The IP address of the server (default is localhost).
        **kwargs: Additional keyword arguments for the VllmServer constructor.

    Returns:
        VllmServer: An instance of the VllmServer class.
    """
    completion_template = completion_manager(base_llm=base_llm, prompt_language=prompt_language)
    full_ip = ":".join([ip_address, port]) + "/generate"
    
    return VllmServer(api_url=full_ip,
                        completion_to_prompt=completion_template,
                        **kwargs,
                        )

def init_model(model_name: str,
               base_llm: str,
               ip_address: str = "localhost",
               port: str = None,
               is_vllm: bool = False,
               prompt_language: str = "en",
               **kwargs: Any) -> BaseLLM:
    """
    Initializes a model based on the provided model name, base language model, port (optional), and vllm flag.

    Parameters:
        model_name (str): The name of the model to be initialized.
        base_llm (str): The base language model to be used for initialization.
        ip_address (str, optional): The IP Address for vllm models. Defaults to None.
        port (str, optional): The port number for vllm models. Defaults to None.
        is_vllm (bool, optional): A flag indicating whether the model is a vllm model. Defaults to False.

    Returns:
        LLM: The initialized model based on the provided parameters.

    Raises:
        AssertionError: If the vllm flag is True and the port parameter is not provided.
        ValueError: If the base_llm parameter is not supported.
    """
    # overwrite base config
    config = copy.deepcopy(LLM_CONFIG)
    config.update(kwargs)
    
    if is_vllm:
        assert port, "Vllm models require a port number."
        return init_vllm(port=port,
                           ip_address=ip_address,
                           base_llm=base_llm,
                           prompt_language=prompt_language,
                           **config)
    else:
        del config["top_k"]
        del config["top_p"]
        del config["repetition_penalty"] 
    
def initialize_llm(model_id: str, prompt_language: str = "en", **kwargs: Any) -> BaseLLM:
    """Initialize an LLM with the given model identifier."""
    if model_id not in LLM_SELECTION_DICT:
        raise ValueError(f"Model ID {model_id} not supported.")

    model_kwargs = copy.deepcopy(LLM_SELECTION_DICT[model_id])
    model_kwargs.update(kwargs)
    model_init = init_model(prompt_language=prompt_language,
                            **model_kwargs)
    return model_init