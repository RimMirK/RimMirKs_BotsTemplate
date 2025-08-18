from functools import lru_cache

__all__ = [
    'escape', 'format_tag',
    'code', 'pre',
    'blockquote', 'bq',
    'b', 'i', 'a', 'u',
    's', 'spoiler'
]


def cache_with_signature(func):
    def wrapper(*args, **kwargs):
        return lru_cache()(func)(*args, **kwargs)
    return wrapper


@cache_with_signature
def escape(text: str) -> str:
    """
    Escapes special HTML characters in a string.

    Args:
        text (str): Text to escape.

    Returns:
        str: Escaped text.
    """
    text = str(text)
    chars = {"&": "&amp;", "<": "&lt;", ">": "&gt;"}
    if text is None:
        return ""
    for old, new in chars.items():
        text = text.replace(old, new)
    return text

@cache_with_signature
def format_tag(tag_name: str, content: str = "", escape_content=True, close_tag=True, **kwargs) -> str:
    """
    Generates an HTML tag.

    Args:
        tag_name (str): Tag name. For example, "a" or "div".
        content (str): Tag content. Optional. Default is "".
        escape_content (bool): Whether to escape the content. Optional. Default is True.
        close_tag (bool): Whether to include a closing tag. Optional. Default is True.
        **kwargs: Tag attributes. Attribute names can be written starts with "_".

    Returns:
        str: Generated HTML tag.

    """
    return (
        f"""<{escape(tag_name)}{''.join([f' {k.removeprefix("_")}="{escape(v)}"' for k,v in kwargs.items()])}>""" +
        ((escape(content) if escape_content else str(content)) if close_tag else "") +
        ((f"</{escape(tag_name)}>") if close_tag else "")
    )

@cache_with_signature
def code(text: str, escape_html=True) -> str:
    """
    Creates an HTML tag for code.

    Args:
        text (str): Code to be placed inside the tag.
        escape_html (bool): Whether to escape HTML inside the code. Optional. Default is True.

    Returns:
        str: Generated HTML tag for code.

    """
    return format_tag('code', text, escape_content=escape_html)

@cache_with_signature
def pre(text: str, lang: str = '', escape_html=True) -> str:
    """
    Generates an HTML tag for displaying a code block.

    Args:
        text (str): Code to display inside the tag.
        lang (str): Programming language. Optional. Default is ''.
        escape_html (bool): Whether to escape HTML. Optional. Default is True.

    Returns:
        str: Generated HTML tag for displaying a code block.

    """
    return format_tag('pre', text, language=lang, escape_content=escape_html)

# @cache_with_signature
def blockquote(text: str, expandable=False, escape_html=True) -> str:
    """
    Creates an HTML tag for a blockquote.

    Args:
        text (str): Text to be placed inside the tag.
        expandable (bool): Whether the quote can be expanded. Optional. Default is False.
        escape_html (bool): Whether to escape HTML. Optional. Default is True.

    Returns:
        str: Generated HTML tag for a blockquote.

    """
    if expandable:
        return format_tag('blockquote', text, escape_content=escape_html, expandable='')
    return format_tag('blockquote', text, escape_content=escape_html)



def bq(text: str, expandable=False, escape_html=True) -> str:
    """
    Same as blockquote.  
    Creates an HTML tag for a blockquote.

    Args:
        text (str): Text to be placed inside the tag.
        expandable (bool): Whether the quote can be expanded. Optional. Default is False.
        escape_html (bool): Whether to escape HTML. Optional. Default is True.

    Returns:
        str: Generated HTML tag for a blockquote.

    """
    if expandable:
        return format_tag('blockquote', text, escape_content=escape_html, expandable='')
    return format_tag('blockquote', text, escape_content=escape_html)


@cache_with_signature
def b(text: str, escape_html=True) -> str:
    """
    Creates an HTML tag for bold text.

    Args:
        text (str): Text to be placed inside the tag.
        escape_html (bool): Whether to escape HTML. Optional. Default is True.

    Returns:
        str: Generated HTML tag for bold text.

    """
    return format_tag('b', text, escape_content=escape_html)

@cache_with_signature
def i(text: str, escape_html=True) -> str:
    """
    Creates an HTML tag for italic text.

    Args:
        text (str): Text to be placed inside the tag.
        escape_html (bool): Whether to escape HTML. Optional. Default is True.

    Returns:
        str: Generated HTML tag for italic text.

    """
    return format_tag('i', text, escape_content=escape_html)

@cache_with_signature
def a(text: str, url: str, escape_html=True) -> str:
    """
    Creates an HTML tag for a hyperlink.

    Args:
        text (str): Link text.
        url (str): URL for the link.
        escape_html (bool): Whether to escape HTML. Optional. Default is True.

    Returns:
        str: Generated HTML tag for the hyperlink.

    """
    return format_tag('a', text, href=url, escape_content=escape_html)

@cache_with_signature
def u(text: str, escape_html=True) -> str:
    """
    Creates an HTML tag for underlined text.

    Args:
        text (str): Text to be placed inside the tag.
        escape_html (bool): Whether to escape HTML. Optional. Default is True.

    Returns:
        str: Generated HTML tag for underlined text.

    """
    return format_tag('u', text, escape_content=escape_html)

@cache_with_signature
def s(text: str, escape_html=True) -> str:
    """
    Creates an HTML tag for strikethrough text.

    Args:
        text (str): Text to be placed inside the tag.
        escape_html (bool): Whether to escape HTML. Optional. Default is True.

    Returns:
        str: Generated HTML tag for strikethrough text.

    """
    return format_tag('s', text, escape_content=escape_html)

@cache_with_signature
def spoiler(text: str, escape_html=True) -> str:
    """
    Creates an HTML tag for a spoiler.

    Args:
        text (str): Text to be placed inside the tag.
        escape_html (bool): Whether to escape HTML. Optional. Default is True.

    Returns:
        str: Generated HTML tag for a spoiler.
    """
    return format_tag('tg-spoiler', text, escape_content=escape_html)