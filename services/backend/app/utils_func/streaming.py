from typing import AsyncGenerator
import json
import asyncio
import re

async def fetch_answer_stream(response_stream, delay) -> AsyncGenerator[str, None]:
    with response_stream as response:
        for chunk in response.iter_lines():
            if chunk:
                chunk_data = chunk.decode("utf-8")
                try:
                    chunk_json_obj = json.loads(chunk_data)
                    if "text" in chunk_json_obj:
                        yield chunk_json_obj["text"]
                    else:
                        yield "\n"
                except (ValueError, KeyError):
                    yield "\n"
            await asyncio.sleep(delay)

def filter_other_lang(text: str) -> str:
    pattern = r"[^A-Za-zก-๙0-9\s\.\,\;\:\?\!\"\'\(\)\[\]\{\}\-\_\+\=\&\%\$\#\@\^\*\/\\\|\<\>\`\~]+"
    # Filter the string using the regex pattern
    filtered_text = re.sub(pattern, "", text)
    return filtered_text

def escape_inner_quotes(text):
    # Find the position of the first and last double quotes
    first_quote_index = text.find('"', text.find(':') + 1)
    last_quote_index = text.rfind('"')

    # Extract the parts: before the first quote, the inner part, and after the last quote
    before = text[:first_quote_index + 1]  # Includes the first quote
    inner = text[first_quote_index + 1:last_quote_index]  # Content between first and last quotes
    after = text[last_quote_index:]  # Includes the last quote

    # Escape all inner quotes
    escaped_inner = inner.replace('"', '\\"')

    # Reassemble the string
    result_text = before + escaped_inner + after

    return result_text