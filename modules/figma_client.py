import re
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests


FIGMA_FILE_URL_RE = re.compile(r"figma\.com/(?:file|design)/([A-Za-z0-9]+)")


def extract_file_key(url: str) -> Optional[str]:
    match = FIGMA_FILE_URL_RE.search(url)
    return match.group(1) if match else None


@dataclass
class FigmaMCPClient:
    """Minimal MCP-style client for Figma REST API interactions."""

    access_token: str
    base_url: str = "https://api.figma.com/v1"
    session: Optional[requests.Session] = None

    def __post_init__(self) -> None:
        if not self.access_token:
            raise ValueError("FIGMA_ACCESS_TOKEN 未提供，無法建立連線。")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-FIGMA-TOKEN": self.access_token,
                "Accept": "application/json",
            }
        )

    def fetch_file(self, file_key: str) -> Dict[str, Any]:
        url = f"{self.base_url}/files/{file_key}"
        response = self.session.get(url, timeout=30)
        if response.status_code != requests.codes.ok:
            raise RuntimeError(
                f"Figma API 回傳狀態碼 {response.status_code}: {response.text}"
            )
        return response.json()
