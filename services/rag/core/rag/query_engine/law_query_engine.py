from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.schema import QueryBundle, QueryType
from llama_index.core.base.response.schema import RESPONSE_TYPE
from llama_index.core.base.base_retriever import BaseRetriever
from llama_index.core.prompts import BasePromptTemplate
from llama_index.core.llms.llm import LLM
from llama_index.core.callbacks.schema import CBEventType, EventPayload
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.bridge.pydantic import BaseModel
from llama_index.core.service_context import ServiceContext
from llama_index.core.response_synthesizers import (
    BaseSynthesizer,
)
from llama_index.core.settings import (
    Settings,
    callback_manager_from_settings_or_context,
)

from ..synthesizer.reference_synthesizer import (
    LawReferenceSynthesizer,
)
from ..response.schema import LawResponse

from typing import Optional, List, Any

from llama_index.core.instrumentation.events.query import (
    QueryEndEvent,
    QueryStartEvent,
)

import llama_index.core.instrumentation as instrument

dispatcher = instrument.get_dispatcher(__name__)

class LawQueryEngine(RetrieverQueryEngine):
    """xxx"""
    
    @classmethod
    def from_args(
        cls,
        retriever: BaseRetriever,
        llm: Optional[LLM] = None,
        response_synthesizer: Optional[BaseSynthesizer] = None,
        node_postprocessors: Optional[List[BaseNodePostprocessor]] = None,
        # response synthesizer args
        response_mode: str = "default",
        reference_qa_template: Optional[BasePromptTemplate] = None,
        refine_template: Optional[BasePromptTemplate] = None,
        output_cls: Optional[BaseModel] = None,
        use_async: bool = False,
        streaming: bool = False,
        prompt_language: str = "en",
        # deprecated
        service_context: Optional[ServiceContext] = None,
        **kwargs: Any,
    ) -> "RetrieverQueryEngine":
        """Initialize a RetrieverQueryEngine object.".

        Args:
            retriever (BaseRetriever): A retriever object.
            service_context (Optional[ServiceContext]): A ServiceContext object.
            node_postprocessors (Optional[List[BaseNodePostprocessor]]): A list of
                node postprocessors.
            verbose (bool): Whether to print out debug info.
            response_mode (ResponseMode): A ResponseMode object.
            reference_qa_template (Optional[BasePromptTemplate]): A BasePromptTemplate
                object.
            refine_template (Optional[BasePromptTemplate]): A BasePromptTemplate object.
            simple_template (Optional[BasePromptTemplate]): A BasePromptTemplate object.

            use_async (bool): Whether to use async.
            streaming (bool): Whether to use streaming.
            optimizer (Optional[BaseTokenUsageOptimizer]): A BaseTokenUsageOptimizer
                object.

        """
        response_synthesizer = response_synthesizer or LawReferenceSynthesizer(
            llm=llm,
            service_context=service_context,
            reference_qa_template=reference_qa_template,
            refine_template=refine_template,
            response_mode=response_mode,
            output_cls=output_cls,
            prompt_language=prompt_language,
            streaming=streaming,
        )

        callback_manager = callback_manager_from_settings_or_context(
            Settings, service_context
        )

        return cls(
            retriever=retriever,
            response_synthesizer=response_synthesizer,
            callback_manager=callback_manager,
            node_postprocessors=node_postprocessors,
        )
    
    @dispatcher.span
    def _query(self, query_bundle: QueryBundle) -> RESPONSE_TYPE:
        """Answer a query."""
        with self.callback_manager.event(
            CBEventType.QUERY, payload={EventPayload.QUERY_STR: query_bundle.query_str}
        ) as query_event:
            nodes = self.retrieve(query_bundle)
            reference_nodes_dict = self.retriever._index.docstore.docs
            response, format_input, reference_nodes_content = self._response_synthesizer.synthesize(
                query=query_bundle,
                nodes=nodes,
                reference_nodes_dict=reference_nodes_dict
            )
            
            response = LawResponse(
                query = query_bundle.query_str,
                response = response,
                nodes = nodes,
                format_input = format_input,
                reference = reference_nodes_content
            )
            
            query_event.on_end(payload={EventPayload.RESPONSE: response})

        return response, format_input, reference_nodes_content

    @dispatcher.span
    def query(self, str_or_query_bundle: QueryType) -> RESPONSE_TYPE:
        dispatcher.event(QueryStartEvent(query=str_or_query_bundle))
        with self.callback_manager.as_trace("query"):
            if isinstance(str_or_query_bundle, str):
                str_or_query_bundle = QueryBundle(str_or_query_bundle)
            response, format_input, reference_nodes_content = self._query(str_or_query_bundle)
        dispatcher.event(
            QueryEndEvent(query=str_or_query_bundle, response={EventPayload.RESPONSE: response.get_response()})
        )
        return response, format_input, reference_nodes_content

    def _nodes(self, query_bundle: QueryBundle) -> List[Any]:
        """Retrieve nodes."""
        return self.retrieve(query_bundle)
