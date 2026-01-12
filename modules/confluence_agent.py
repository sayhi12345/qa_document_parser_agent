import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from urllib.parse import unquote

import requests

from config.confluence import settings
from modules.figma_agent import FigmaSummaryResult

@dataclass
class ConfluencePublisher:
    """Lightweight helper for publishing pages to Confluence Cloud."""

    base_url: str = settings.base_url
    space_key: str = settings.space_key
    username: Optional[str] = None
    api_token: Optional[str] = None
    folder_id: Optional[str] = None  # 新增: Confluence folder ID
    session: Optional[requests.Session] = None

    def __post_init__(self) -> None:
        self.username = self.username or settings.username
        self.api_token = self.api_token or settings.api_key
        self.folder_id = self.folder_id or settings.folder_id
        if not self.username or not self.api_token:
            raise ValueError(
                "Confluence 認證資訊不足，請確認 CONFLUENCE_USERNAME 與 CONFLUENCE_API_KEY。"
            )
        self.session = requests.Session()
        self.session.auth = (self.username, self.api_token)
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )
        
        # 驗證 folder_id 是否存在
        if self.folder_id:
            if not self._validate_folder(self.folder_id):
                print(f"Folder ID '{self.folder_id}' 不存在或無權限存取，將設為 None")
                self.folder_id = None


    def _validate_folder(self, folder_id: str) -> bool:
        """
        驗證 folder ID 是否存在且可存取
        
        Args:
            folder_id: Confluence folder ID
            
        Returns:
            True 如果 folder 存在且可存取，否則 False
        """
        try:
            endpoint = f"{self.base_url.rstrip('/')}/rest/api/content/{folder_id}"
            response = self.session.get(endpoint, timeout=30)
            return response.status_code == requests.codes.ok
        except Exception:
            # 捕獲所有異常（網路錯誤、timeout 等）
            return False

    def get_folder_info(self, folder_id: str) -> Dict[str, Any]:
        """取得 folder 資訊，用於驗證 folder 是否存在"""
        endpoint = f"{self.base_url.rstrip('/')}/rest/api/content/{folder_id}"
        response = self.session.get(endpoint, timeout=30)
        if response.status_code != requests.codes.ok:
            raise RuntimeError(
                f"無法取得 folder 資訊: {response.status_code} {response.text}"
            )
        return response.json()

    def create_page(
        self, 
        title: str, 
        adf_doc: Dict[str, Any], 
        folder_id: Optional[str] = None
    ) -> str:
        """
        建立 Confluence 頁面
        
        Args:
            title: 頁面標題
            adf_doc: ADF 格式的文件內容
            folder_id: (可選) Confluence folder ID，如果指定則頁面會建立在該 folder 下
                      範例: "3412262946" (從 URL 取得)
        
        Returns:
            建立成功的頁面 URL
        """
        if not title.strip():
            raise ValueError("Confluence 頁面標題不可為空。")
        
        # 優先使用參數傳入的 folder_id，否則使用實例的 folder_id
        target_folder_id = folder_id or self.folder_id
        
        endpoint = f"{self.base_url.rstrip('/')}/rest/api/content"
        payload = {
            "type": "page",
            "title": title.strip(),
            "space": {"key": self.space_key},
            "body": {
                "atlas_doc_format": {
                    "value": json.dumps(adf_doc),
                    "representation": "atlas_doc_format",
                }
            },
        }
        
        # 如果有指定 folder_id，將其設為父頁面
        if target_folder_id:
            payload["ancestors"] = [{"id": target_folder_id}]
        
        response = self.session.post(endpoint, json=payload, timeout=30)
        if response.status_code not in (requests.codes.ok, requests.codes.created):
            raise RuntimeError(
                f"Confluence 建立頁面失敗: {response.status_code} {response.text}"
            )
        data = response.json()
        links = data.get("_links", {})
        base_link = links.get("base") or self.base_url.rstrip("/")
        webui = links.get("webui") or ""
        return f"{base_link}{webui}"


def build_confluence_adf(result: FigmaSummaryResult, source_url: str) -> Dict[str, Any]:
    """Convert解析結果為 Confluence Atlas Document Format (ADF)。"""

    def text_node(text: str, marks: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        node: Dict[str, Any] = {"type": "text", "text": text}
        if marks:
            node["marks"] = marks
        return node

    def paragraph_node(children: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        return {"type": "paragraph", "content": children or [text_node("")]}

    def heading_node(text: str, level: int = 2) -> Dict[str, Any]:
        return {
            "type": "heading",
            "attrs": {"level": level},
            "content": [text_node(text)],
        }

    def bullet_list_nodes(items: List[str]) -> List[Dict[str, Any]]:
        if not items:
            return [paragraph_node([text_node("無資料")])]
        return [
            {
                "type": "bulletList",
                "content": [
                    {
                        "type": "listItem",
                        "content": [paragraph_node([text_node(item)])],
                    }
                    for item in items
                ],
            }
        ]

    qa_nodes: List[Dict[str, Any]] = []
    if result.qa:
        for idx, item in enumerate(result.qa, start=1):
            qa_nodes.append(paragraph_node([text_node(f"Q: {item.question}")]))
            qa_nodes.append(paragraph_node([text_node(f"A: {item.answer}")]))
    else:
        qa_nodes.append(paragraph_node([text_node("目前沒有常見問答。")]))

    doc_content: List[Dict[str, Any]] = []
    doc_content.append(heading_node("活動內容"))
    doc_content.extend(bullet_list_nodes(result.summary))
    doc_content.append(heading_node("常見問答"))
    doc_content.extend(qa_nodes)
    doc_content.append(paragraph_node([text_node("<questions>")]))
    for idx, item in enumerate(result.qa, start=1):
        doc_content.append(
            paragraph_node([text_node(f"{idx} {item.question}")])
        )
    doc_content.append(paragraph_node([text_node("</questions>")]))

    return {
        "version": 1,
        "type": "doc",
        "content": doc_content,
    }


def extract_title_from_url(url: str) -> Optional[str]:
    decoded = unquote(url or "")
    match = re.search(r"【([^】]+)】", decoded)
    if match:
        candidate = match.group(1).strip()
        if candidate:
            return candidate
    return None


def resolve_confluence_title(result: FigmaSummaryResult, url: str) -> str:
    parsed = extract_title_from_url(url)
    if parsed:
        return parsed
    candidate = (result.title or "").strip()
    return candidate
