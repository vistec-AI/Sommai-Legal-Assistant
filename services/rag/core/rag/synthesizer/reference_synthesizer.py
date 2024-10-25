from llama_index.core.response_synthesizers.base import BaseSynthesizer
from llama_index.core.prompts.base import BasePromptTemplate
from llama_index.core.prompts.mixin import PromptDictType
from llama_index.core.service_context_elements.llm_predictor import (
    LLMPredictorType,
)
from llama_index.core.callbacks.base import CallbackManager
from llama_index.core.indices.prompt_helper import PromptHelper
from llama_index.core.bridge.pydantic import BaseModel
from llama_index.core.types import BasePydanticProgram
from llama_index.core.service_context import ServiceContext
from llama_index.core.schema import (
    TextNode,
    NodeWithScore,
    QueryBundle,
    QueryType,
)
from llama_index.core.base.response.schema import (
    RESPONSE_TYPE,
    Response,
    StreamingResponse,
)

from typing import Optional, Callable, List, Any, Generator, AsyncGenerator, Dict

from ..prompting.prompt_manager import init_prompts
from ..prompting.postprocess import clean_special_tokens

def empty_response_generator() -> Generator[str, None, None]:
    yield "Empty Response"

async def empty_response_agenerator() -> AsyncGenerator[str, None]:
    yield "Empty Response"

class LawReferenceSynthesizer(BaseSynthesizer):
    """Augment referenced sections into prompt before completing response"""

    def __init__(
        self,
        llm: Optional[LLMPredictorType] = None,
        callback_manager: Optional[CallbackManager] = None,
        prompt_helper: Optional[PromptHelper] = None,
        reference_qa_template: Optional[BasePromptTemplate] = None,
        refine_template: Optional[BasePromptTemplate] = None,
        output_cls: Optional[BaseModel] = None,
        streaming: bool = False,
        verbose: bool = False,
        structured_answer_filtering: bool = False,
        program_factory: Optional[
            Callable[[BasePromptTemplate], BasePydanticProgram]
        ] = None,
        service_context: Optional[ServiceContext] = None,
        response_mode: str = "default",
        prompt_language: str = "en",
    ) -> None:
        if service_context is not None:
            prompt_helper = service_context.prompt_helper
        super().__init__(
            llm=llm,
            callback_manager=callback_manager,
            prompt_helper=prompt_helper,
            service_context=service_context,
            streaming=streaming,
        )
        prompt_template = init_prompts(prompt_language)
        self._reference_qa_template = reference_qa_template or prompt_template["REFERENCE_QA_TEMPLATE"]
        self._refine_template = refine_template or prompt_template["REFINE_TEMPLATE"]
        self._refine_reference_template = prompt_template["REFINE_REFERENCE_TEMPLATE"]
        self._default_reference_template = prompt_template["DEFAULT_REFERENCE_TEMPLATE"]
        self._verbose = verbose
        self._structured_answer_filtering = structured_answer_filtering
        self._output_cls = output_cls
        self._response_mode = response_mode

        if self._streaming and self._structured_answer_filtering:
            raise ValueError(
                "Streaming not supported with structured answer filtering."
            )
        if not self._structured_answer_filtering and program_factory is not None:
            raise ValueError(
                "Program factory not supported without structured answer filtering."
            )
        self._program_factory = program_factory
        
    def synthesize(
        self,
        query: QueryType,
        nodes: List[NodeWithScore],
        reference_nodes_dict: Dict[str, TextNode],
        **response_kwargs: Any,
    ) -> RESPONSE_TYPE:

        if len(nodes) == 0:
            if self._streaming:
                empty_response = StreamingResponse(
                    response_gen=empty_response_generator()
                )
                return empty_response
            else:
                empty_response = Response("Empty Response")
                return empty_response

        if isinstance(query, QueryBundle):
            query = query.query_str
            
        retrieved_nodes_content = [node.get_content() for node in nodes]
        retrieved_reference_id = [node.metadata["reference_nodes"] for node in nodes]
        reference_nodes_content = [[reference_nodes_dict[ref_id].sectionContent for ref_id in reference] for reference in retrieved_reference_id]
        response_str, format_input = self.get_response(
            query_str=query,
            retrieved_nodes_content = retrieved_nodes_content,
            reference_nodes_content = reference_nodes_content,
            **response_kwargs,
        )

        return response_str, format_input, reference_nodes_content
    
    def get_response(
        self,
        query_str: str,
        retrieved_nodes_content: List[str],
        reference_nodes_content: List[List[str]],
        prev_response: Optional[str] = None,
        **response_kwargs: Any,
    ) -> str:
        """Give response over chunks."""
        response: Optional[str] = None
        
        if self._response_mode.lower() == "refine":
            for reference_node, retrieve_node in zip(reference_nodes_content, retrieved_nodes_content):
                if reference_node:
                    reference_augment = self._refine_reference_template.format(context_str=retrieve_node, reference_str='\n\n'.join(reference_node))
                else:
                    reference_augment = self._refine_reference_template.format(context_str=retrieve_node, reference_str="no reference")
                    
                if prev_response is None:
                    # if this is the first chunk, and text chunk already
                    # is an answer, then return it
                    format_input = self._reference_qa_template.format(query_str = query_str, context_str = "\n".join(reference_augment))
                    response = self._llm.complete(format_input).text
                else:
                    # refine response if possible
                    format_input = self._refine_template.format(query_str = query_str, context_str = "\n".join(reference_augment), existing_answer=prev_response)
                    response = self._llm.complete(format_input).text
                prev_response = response
        
        elif self._response_mode.lower() == "default":
            reference_nodes_content = sorted(set([item for sublist in reference_nodes_content for item in sublist]))
            retrieve_augment = '\n\n'.join(retrieved_nodes_content)
            reference_augment = '\n\n'.join(reference_nodes_content)
            context = self._default_reference_template.format(context_str=retrieve_augment, reference_str=reference_augment)
            format_input = self._reference_qa_template.format(query_str = query_str, context_str = context)
            format_input = self._llm.completion_to_prompt(format_input)
            response = self._llm.complete(format_input)
            if not isinstance(response, str):
                response = response.text
            assert isinstance(response, str), f"Response must be a string, got {type(response)}"
            if format_input in response:
                response = response.replace(format_input, "")
            response = clean_special_tokens(response)
        else:
            raise ValueError(f"Unknown synthesize mode: {self._synthesize_mode}")
            
        assert isinstance(response, str), f"Response must be a string, got {type(response)}"
        return response, format_input
    
    def _get_prompts(self) -> dict:
        """Get prompts."""
        return {
            "reference_qa_template": self._reference_qa_template,
            "refine_template": self._refine_template,
            "refine_reference_template": self._refine_reference_template,
            "default_reference_template": self._default_reference_template
        }
    
    def _update_prompts(self, prompts: PromptDictType) -> None:
        """Update prompts."""
        if "reference_qa_template" in prompts:
            self._reference_qa_template = prompts["reference_qa_template"]
        if "refine_template" in prompts:
            self._refine_template = prompts["refine_template"]
        if "refine_reference_template" in prompts:
            self._refine_reference_template = prompts["refine_reference_template"]
        if "default_reference_template" in prompts:
            self._default_reference_template = prompts["default_reference_template"]
            
    async def aget_response(
        self) -> None:
        raise NotImplementedError("Async version not implemented")

    # async def asynthesize(
    #     self,
    #     query: QueryType,
    #     nodes: List[NodeWithScore],
    #     additional_source_nodes: Optional[Sequence[NodeWithScore]] = None,
    #     **response_kwargs: Any,
    # ) -> RESPONSE_TYPE:
    #     if len(nodes) == 0:
    #         if self._streaming:
    #             empty_response = AsyncStreamingResponse(
    #                 response_gen=empty_response_agenerator()
    #             )
    #             dispatcher.event(
    #                 SynthesizeEndEvent(query=query, response=empty_response)
    #             )
    #             return empty_response
    #         else:
    #             empty_response = Response("Empty Response")
    #             dispatcher.event(
    #                 SynthesizeEndEvent(query=query, response=empty_response)
    #             )
    #             return empty_response

    #     if isinstance(query, str):
    #         query = QueryBundle(query_str=query)

    #     with self._callback_manager.event(
    #         CBEventType.SYNTHESIZE, payload={EventPayload.QUERY_STR: query.query_str}
    #     ) as event:
    #         response_str = await self.aget_response(
    #             query_str=query.query_str,
    #             text_chunks=[
    #                 n.node.get_content(metadata_mode=MetadataMode.LLM) for n in nodes
    #             ],
    #             **response_kwargs,
    #         )

    #         additional_source_nodes = additional_source_nodes or []
    #         source_nodes = list(nodes) + list(additional_source_nodes)

    #         response = self._prepare_response_output(response_str, source_nodes)

    #         event.on_end(payload={EventPayload.RESPONSE: response})

    #     dispatcher.event(SynthesizeEndEvent(query=query, response=response))
    #     return response