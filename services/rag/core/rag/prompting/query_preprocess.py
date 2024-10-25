import re

from llama_index.core import PromptTemplate
from .template import (
    QUERY_GEN_PROMPT_STR
)

def preprocess_query(query_str: str) -> str:
    """rule based to adjust query"""
    preprocessed_query = re.sub(r"ตั้งใจ|ความตั้งใจ", "เจตนา", query_str)
    preprocessed_query = re.sub(r"ตาย", "เสียชีวิต", query_str)
    
    return preprocessed_query.strip()

def generate_queries(llm, query_str: str, num_queries: int = 4, verbose=False):
    """generate multiple query to enchance document retrieve process"""
    assert num_queries > 0
    # bypassing
    if num_queries == 1:
        return [query_str]
    
    def clean(text) -> str:
        text = re.sub(r"\d+\.", '', text)
        text = re.sub(r"-", '', text)
        return text.strip()
    
    fmt_prompt = QUERY_GEN_PROMPT_STR.format(
        num_queries=num_queries - 1, query=query_str
    )
    response = llm.complete(fmt_prompt)
    queries = response.text.split("\n")
    queries = [clean(query.strip()) for query in queries if query.strip()]
    # check if return as lines or not
    if len(queries) == 1:
        queries = re.sub(r'(\d+\.|\-)', '\n\1', queries[0])
    queries.append(query_str)
    if verbose:
        print(*queries, sep='\n')
    return queries

def generate_keypoint(llm, query_str: str, verbose=True):
    
    key_point_extraction_prompt_str = (
    "Summarize the given legal query into its most crucial component in Thai, condensing the query into a brief and precise statement. "
    "Focus on capturing the essence of the query's legal concern in the shortest form possible, using formal and accurate language. "
    "This summary should directly reflect the central legal issue or action described in the query, without including details about potential legal outcomes or specific laws. "
    "\nLegal Query: {query}\n"
    "Summary:\n"
    )

    # key_point_extraction_prompt_str = (
    #     "Summarize this query into one sentence in Thai. Only taking main ideas of the query. "
    #     "Query: {query}\n"
    #     "Summary:\n"
    # )


    query_gen_prompt = PromptTemplate(key_point_extraction_prompt_str)
    fmt_prompt = query_gen_prompt.format(
        query=query_str
    )
    response = llm.complete(fmt_prompt)
    
    if verbose:
        print(response.text)
    return response.text

def generate_keywords(llm, query_str: str, verbose=True):
    def clean(text) -> str:
        text = re.sub(r"\d+\.", '', text)
        text = re.sub(r"-", '', text)
        return text.strip()
    
    keywords_extraction_prompt_str = (
    "As an assistant specialized in information retrieval, your task is to analyze the given query and extract the most "
    "relevant keywords. These keywords should encapsulate the core topics, concepts, or terms that are crucial for conducting "
    "a focused and efficient search within the specified context. Ensure the keywords are identified in Thai, reflecting the original "
    "language of the query, and are broadly applicable across different databases or search engines. These should serve as effective "
    "search terms for retrieving relevant information on the subject. Present the extracted keywords in Thai, each must separated by a newline, "
    "to facilitate easy application in search queries. "
    "\nInput Query: {query}\n"
    "Keywords:\n"
)
    query_gen_prompt = PromptTemplate(keywords_extraction_prompt_str)
    
    fmt_prompt = query_gen_prompt.format(
        query=query_str
    )
    response = llm.complete(fmt_prompt)
    queries = response.text.split("\n")
    queries = [clean(query.strip()) for query in queries if query.strip()]
    if verbose:
        print(*queries, sep='\n')
    return queries