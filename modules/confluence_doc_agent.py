from typing import List, Optional

from langchain_openai import ChatOpenAI

from modules.models import FigmaSummaryResult, QAItem
from modules.confluence_client import ConfluenceAPIClient, extract_page_id, is_confluence_url
from modules.confluence_parser import aggregate_confluence_content
from modules.confluence_llm_chain import run_confluence_chain
from config.confluence import settings as confluence_settings
from config.openai import settings as openai_settings
from utils.log import get_logger


# Initialize logger using factory function
logger = get_logger("confluence_agent")


def format_output(result: FigmaSummaryResult) -> str:
    """Format the summary result as markdown output."""
    lines: List[str] = ["## 活動內容"]
    lines.extend(result.summary)
    lines.append("")
    lines.append("## 常見問答")
    for item in result.qa:
        lines.append(f"Q: {item.question}")
        lines.append(f"A: {item.answer}")
    lines.append("")
    lines.append("<questions>")
    for idx, item in enumerate(result.qa, start=1):
        lines.append(f"{idx} {item.question}")
    lines.append("</questions>\n")
    return "\n".join(lines)


def generate_confluence_summary(
    url: str,
    *,
    api_key: Optional[str] = None,
    llm_model: str = "gpt-4.1-mini",
    temperature: float = 0.0,
) -> FigmaSummaryResult:
    """
    Generate summary and Q&A from a Confluence page.
    
    Args:
        url: Confluence page URL
        api_key: Optional OpenAI API key override
        llm_model: LLM model to use
        temperature: LLM temperature
        
    Returns:
        FigmaSummaryResult with title, plan, summary, and qa
    """
    page_id = extract_page_id(url)
    if not page_id:
        raise ValueError("無法取得有效的Confluence頁面ID，請確認連結格式。")

    try:
        client = ConfluenceAPIClient()
        page_json = client.fetch_page(page_id)
    except Exception as exc:
        logger.error(status="error", url=url, message="無法取得Confluence頁面，請確認連結或權限。")
        raise RuntimeError(
            "無法取得Confluence頁面，請確認連結或權限。"
        ) from exc

    # Extract text content from the page
    confluence_content = aggregate_confluence_content(page_json)
    logger.info(status="info", url=url, message=f"成功取得Confluence內容，長度: {len(confluence_content)}")

    # Use provided API key or from configuration
    openai_api_key = api_key or openai_settings.api_key
    if not openai_api_key:
        logger.error(status="error", url=url, message="OpenAI API key 未設定")
        raise ValueError("OpenAI API key 未設定")
    
    llm = ChatOpenAI(
        model=llm_model,
        temperature=temperature,
        api_key=openai_api_key
    )
    try:
        result = run_confluence_chain(url, confluence_content, llm)
        logger.info(status="info", url=url, message="產生摘要與問答成功")
    except Exception as exc:
        logger.error(status="error", url=url, message=f"產生摘要與問答失敗: {exc}")
        raise RuntimeError(f"產生摘要與問答失敗: {exc}") from exc

    return result


def parse_confluence(
    url: str,
    *,
    api_key: Optional[str] = None,
    llm_model: str = "gpt-4.1-mini",
    temperature: float = 0.0,
) -> str:
    """
    Parse a Confluence page and return formatted markdown output.
    """
    try:
        result = generate_confluence_summary(
            url,
            api_key=api_key,
            llm_model=llm_model,
            temperature=temperature,
        )
    except Exception as exc:
        return str(exc)

    return format_output(result)


# Re-export for convenience
__all__ = [
    "generate_confluence_summary",
    "parse_confluence",
    "format_output",
    "is_confluence_url",
]
