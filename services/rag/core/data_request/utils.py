import re

from ..hierarchical_parser.const import (
    THAI_TO_ARABIC,
    THAI_TO_NUM,
)

def fix_newline_bug(text: str) -> str:
    """repalce newline with space to prevent bug (from source api)
    some newline will remain in the text by our custom logic"""
    pattern = [f"{p}$" for p in list(THAI_TO_NUM.keys())]
    pattern = re.compile("|".join(pattern))
    postprocess = []
    chunks = [chunk.strip() for chunk in text.split("\n")]
    for chunk in chunks:
        if postprocess:
            if chunk.startswith(("ถ้า", "ผู้ใด", "(", "ต้องระวาง")):
                if re.match(r"\d+$", postprocess[-1]) or pattern.search(postprocess[-1]):
                    postprocess.append(f" {chunk}")
                else:
                    postprocess.append(f"\n{chunk}")
            else:
                postprocess.append(f" {chunk}")
        else:
            postprocess.append(chunk)
    return "".join(postprocess)

def add_space_subsection(text: str) -> str:
    """add space in front of subsection to prevent bug (from source api)"""
    subsection_pattern = re.compile(r"(\S)(\(\d+/?\d*\))")
    
    return re.sub(subsection_pattern, r"\1\n\2", text)

def delete_newline_subsection(text: str) -> str:
    """delete newline after subsection to prevent bug (from source api)"""
    subsection_pattern = re.compile(r"(\(\d+/?\d*\)) *\n+")
    
    return re.sub(subsection_pattern, r"\1 ", text)
    
def clean_footnote(text):
    """remove footer from sections"""
    return re.sub(r"\[.+\]", " ", text)

def convert_thai_num(text):
    """convert Thai numbers to Arabic"""

    pattern = re.compile("|".join(THAI_TO_ARABIC.keys()))
    result = pattern.sub(lambda x: THAI_TO_ARABIC[x.group()], text)
    return result

def convert_thai_clause(text):
    """convert Thai number words to arabic number"""

    pattern = re.compile("|".join(THAI_TO_NUM.keys()))
    result = pattern.sub(lambda x: THAI_TO_NUM[x.group()], text)
    return result

def normalize_space(text) -> str:
    """replace multiple spaces with one space"""
    text = re.sub(r"&nbsp;", " ", text).strip()
    text = re.sub(r" +", " ", text)
    return text

def normalize_newlines(text: str) -> str:
    text = re.sub(r" *\n+ *", "\n", text)
    # prevent bug
    text = re.sub(r"(\n\(\d+\))\n", r"\1 ", text)
    return text

def replace_html_tags(text):
    """
    Replaces HTML tags in text with "" (for short tags) or "\n" (for complex tags).

    Args:
        text: The input text containing HTML tags.

    Returns:
        The text with HTML tags replaced.
    """
    def replace_tag(match):
        tag = match.group(0)
        if "MsoNormal" in tag:
            return "\n"
        else:  # Complex tags with attributes
            return ""

    pattern = r"<[^>]+>"  # Regex pattern to match any HTML tag
    return re.sub(pattern, replace_tag, text)