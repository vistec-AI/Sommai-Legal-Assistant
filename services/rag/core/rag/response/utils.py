import textwrap

def to_markdown(text: str):
    # Transform and wrap the text as needed
    text = text.replace('•', '  *')
    text = textwrap.indent(text, '> ', predicate=lambda _: True)
    # Return a string of Markdown-formatted text
    return text