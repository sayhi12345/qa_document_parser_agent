from typing import List, Optional

from langchain_openai import ChatOpenAI

from modules.models import FigmaSummaryResult, QAItem
from modules.figma_client import FigmaMCPClient, extract_file_key
from modules.figma_parser import find_node_by_names, collapse_text_nodes, aggregate_figma_content
from modules.llm_chain import run_chain
from config.figma import settings as figma_settings
from config.openai import settings as openai_settings
from config.prompts import settings as prompt_settings
from utils.log import get_logger


# Initialize logger using factory function
logger = get_logger("figma_agent")


def format_output(result: FigmaSummaryResult) -> str:
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


def generate_figma_summary(
    url: str,
    *,
    access_token: Optional[str] = None,
    api_key: Optional[str] = None,
    llm_model: str = "gpt-4.1-mini",
    temperature: float = 0.0,
    search_activity_node: bool = True,
) -> FigmaSummaryResult:
    file_key = extract_file_key(url)
    if not file_key:
        raise ValueError("無法取得有效的Figma文件，請確認檔案連結或權限。")

    token = access_token or figma_settings.access_token
    if not token:
        logger.error(status="error", url=url, message="Figma金鑰未設定")
        raise ValueError("Figma金鑰未設定")

    try:
        client = FigmaMCPClient(access_token=token)
        figma_json = client.fetch_file(file_key)
    except Exception as exc:
        logger.error(status="error", url=url, message="無法取得有效的Figma文件，請確認檔案連結或權限。")
        raise RuntimeError(
            "無法取得有效的Figma文件，請確認檔案連結或權限。"
        ) from exc

    # 嘗試尋找 "活動說明" 節點
    document = figma_json.get("document", {})
    target_node = None
    if search_activity_node:
        target_node = find_node_by_names(document, prompt_settings.target_node_names)

    if target_node:
        logger.info(status="info", url=url, message="找到活動說明節點")
        text_fragments: List[str] = []
        collapse_text_nodes(target_node, text_fragments)
        figma_content = "\n".join(text_fragments) or "（活動說明區塊無文字節點）"
    else:
        logger.info(status="info", url=url, message="未找到活動說明節點")
        # 若找不到則使用完整內容
        figma_content = aggregate_figma_content(figma_json)

    # 使用提供的 API key 或從配置中讀取
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
        result = run_chain(url, figma_content, llm)
        logger.info(status="info", url=url, message="產生摘要與問答成功")
    except Exception as exc:
        logger.error(status="error", url=url, message=f"產生摘要與問答失敗: {exc}")
        raise RuntimeError(f"產生摘要與問答失敗: {exc}") from exc

    return result


def parse_figma(
    url: str,
    *,
    access_token: Optional[str] = None,
    api_key: Optional[str] = None,
    llm_model: str = "gpt-4.1-mini",
    temperature: float = 0.0,
    search_activity_node: bool = True,
) -> str:
    try:
        result = generate_figma_summary(
            url,
            access_token=access_token,
            api_key=api_key,
            llm_model=llm_model,
            temperature=temperature,
            search_activity_node=search_activity_node,
        )
    except Exception as exc:
        return str(exc)

    return format_output(result)


# Re-export models for backward compatibility
__all__ = [
    "generate_figma_summary",
    "parse_figma",
    "format_output",
    "FigmaSummaryResult",
    "QAItem",
]
