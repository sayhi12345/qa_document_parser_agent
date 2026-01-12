from pydantic_settings import BaseSettings
from typing import List
from config.loader import load_env_json

# Load configuration from JSON
_config_data = load_env_json()

# Define defaults as module-level constants
DEFAULT_SYSTEM_PROMPT = (
    "你是一位熟悉 Figma 文件的產品設計分析師，會以繁體中文輸出結論。"
    "遵守以下規則：\n"
    "1. 先產出 4-80 字的中文標題，需能做為 Confluence 頁面標題。\n"
    "2. 忽略與 UI 設計相關的資訊。\n"
    "3. 列出 3-7 點的執行步驟，每點僅描述概念層級。\n"
    "4. 依據文件資訊整理至少 10 最多 30 條摘要，每條為一句完整語句，不可使用項目符號。\n"
    "5. 提供至少 5 最多 15 組常見問答。若無法滿足數量，提供找到的所有問題。\n"
    "6. 總結與問答需交叉檢查日期與金額，若來源疑慮請以自然語句標示推測。\n"
    "7. 請嚴格按照 parser 指定的 JSON schema 輸出內容。"
)

DEFAULT_HUMAN_TEMPLATE = (
    "Url: {url}\n"
    "Developer: 請先提供一個適合作為 Confluence 標題的中文摘要標題，"
    "接著以至少10個條列點中文總結此Figma文件，並提供至少5個常見Q&A（問題與答案）。\n"
    "<figma_content>\n{figma_content}\n</figma_content>\n"
    "{format_instructions}"
)

DEFAULT_TARGET_NODE_NAMES = ["活動說明頁", "活動說明"]

# Confluence-specific prompts (without UI design filtering)
CONFLUENCE_SYSTEM_PROMPT = (
    "你是一位熟悉企業文件的產品分析師，會以繁體中文輸出結論。"
    "遵守以下規則：\n"
    "1. 先產出 4-80 字的中文標題，需能做為 Confluence 頁面標題。\n"
    "2. 列出 3-7 點的執行步驟，每點僅描述概念層級。\n"
    "3. 依據文件資訊整理至少 10 最多 30 條摘要，每條為一句完整語句，不可使用項目符號。\n"
    "4. 提供至少 5 最多 15 組常見問答。若無法滿足數量，提供找到的所有問題。\n"
    "5. 總結與問答需交叉檢查日期與金額，若來源疑慮請以自然語句標示推測。\n"
    "6. 請嚴格按照 parser 指定的 JSON schema 輸出內容。"
)

CONFLUENCE_HUMAN_TEMPLATE = (
    "Url: {url}\n"
    "Developer: 請先提供一個適合作為 Confluence 標題的中文摘要標題，"
    "接著以至少10個條列點中文總結此Confluence文件，並提供至少5個常見Q&A（問題與答案）。\n"
    "<confluence_content>\n{content}\n</confluence_content>\n"
    "{format_instructions}"
)


class PromptSettings(BaseSettings):
    figma_system_prompt: str = DEFAULT_SYSTEM_PROMPT
    figma_human_template: str = DEFAULT_HUMAN_TEMPLATE
    target_node_names: List[str] = DEFAULT_TARGET_NODE_NAMES
    confluence_system_prompt: str = CONFLUENCE_SYSTEM_PROMPT
    confluence_human_template: str = CONFLUENCE_HUMAN_TEMPLATE
    
    class Config:
        # Allow extra fields to be ignored
        extra = "ignore"


# Initialize settings with values from env.json
settings = PromptSettings(
    figma_system_prompt=_config_data.get("FIGMA_SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT),
    figma_human_template=_config_data.get("FIGMA_HUMAN_TEMPLATE", DEFAULT_HUMAN_TEMPLATE),
    target_node_names=_config_data.get("TARGET_NODE_NAMES", DEFAULT_TARGET_NODE_NAMES),
    confluence_system_prompt=_config_data.get("CONFLUENCE_SYSTEM_PROMPT", CONFLUENCE_SYSTEM_PROMPT),
    confluence_human_template=_config_data.get("CONFLUENCE_HUMAN_TEMPLATE", CONFLUENCE_HUMAN_TEMPLATE)
)
