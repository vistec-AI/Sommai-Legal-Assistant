from pydantic import BaseModel, PrivateAttr, Field
from typing import Any, Callable, Optional
from abc import abstractmethod

from ..rag.prompting.template import EN_SYSTEM_PROMPT_STR
from .utils import default_completion_to_prompt

class BaseLLM(BaseModel):
    model: str = Field(
        default="", description="The LLM to use."
    )
    
    temperature: float = Field(
        default=0.0,
        description="The temperature to use for sampling.",
        gte=0.0,
        lte=1.0,
    )
    
    max_tokens: int = Field(
        default=4096,
        description="The maximum number of tokens to generate.",
        gt=0,
    )
    
    system_prompt: Optional[str] = Field(
        default=EN_SYSTEM_PROMPT_STR, description="System prompt for LLM calls."
    )
    
    completion_to_prompt: Callable[[str], str] = Field(
        default=default_completion_to_prompt,
        description="Function to convert completion to prompt.",
    )
    
    _api_key: Optional[str] = PrivateAttr()
   
    _client: Any = PrivateAttr()
    
    @abstractmethod
    def complete(self, prompt: str) -> str:
        pass
    
    @abstractmethod
    def stream_complete(self, prompt: str) -> str:
        pass
    
    @abstractmethod
    def chat(self, prompt: str, chat_session = None):
        pass
    
    @abstractmethod
    def stream_chat(self, prompt: str, chat_session = None):
        pass