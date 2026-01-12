import re
from typing import Any, Dict
from html.parser import HTMLParser


class HTMLTextExtractor(HTMLParser):
    """Simple HTML parser to extract text content."""
    
    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.skip_tags = {'script', 'style', 'head', 'meta', 'link'}
        self.current_skip = False
    
    def handle_starttag(self, tag, attrs):
        if tag.lower() in self.skip_tags:
            self.current_skip = True
        # Add newline for block elements
        if tag.lower() in {'p', 'div', 'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'tr'}:
            self.text_parts.append('\n')
    
    def handle_endtag(self, tag):
        if tag.lower() in self.skip_tags:
            self.current_skip = False
    
    def handle_data(self, data):
        if not self.current_skip:
            text = data.strip()
            if text:
                self.text_parts.append(text)
    
    def get_text(self) -> str:
        return ' '.join(self.text_parts)


def extract_text_from_html(html_content: str) -> str:
    """
    Extract text content from HTML.
    
    Args:
        html_content: HTML string from Confluence storage format
        
    Returns:
        Plain text content
    """
    if not html_content:
        return ""
    
    parser = HTMLTextExtractor()
    try:
        parser.feed(html_content)
        text = parser.get_text()
    except Exception:
        # Fallback: use regex to strip tags
        text = re.sub(r'<[^>]+>', ' ', html_content)
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def aggregate_confluence_content(page_json: Dict[str, Any]) -> str:
    """
    Aggregate all text content from a Confluence page JSON response.
    
    Args:
        page_json: The JSON response from Confluence API
        
    Returns:
        Aggregated text content as a single string
    """
    sections = []
    
    # Get page title
    title = page_json.get("title", "")
    if title:
        sections.append(f"=== 頁面標題 ===\n{title}")
    
    # Get space info
    space = page_json.get("space", {})
    space_name = space.get("name", "")
    if space_name:
        sections.append(f"=== 空間 ===\n{space_name}")
    
    # Get body content - try different formats
    body = page_json.get("body", {})
    
    # Try storage format first (Confluence's native XHTML)
    storage = body.get("storage", {})
    storage_value = storage.get("value", "")
    if storage_value:
        text_content = extract_text_from_html(storage_value)
        if text_content:
            sections.append(f"=== 文件內容 ===\n{text_content}")
    
    # Fallback to view format if storage is empty
    if not storage_value:
        view = body.get("view", {})
        view_value = view.get("value", "")
        if view_value:
            text_content = extract_text_from_html(view_value)
            if text_content:
                sections.append(f"=== 文件內容 ===\n{text_content}")
    
    if not sections:
        return "（無法取得文件內容）"
    
    return "\n\n".join(sections)
