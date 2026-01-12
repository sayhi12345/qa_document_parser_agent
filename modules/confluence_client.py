import re
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

from config.confluence import settings


# Pattern to extract page ID from Confluence URLs
# Examples:
# - https://lang.atlassian.net/wiki/spaces/ACS/pages/123456789/Page+Title
# - https://lang.atlassian.net/wiki/spaces/ACS/pages/123456789
CONFLUENCE_PAGE_URL_RE = re.compile(r"atlassian\.net/wiki/spaces/[^/]+/pages/(\d+)")


def extract_page_id(url: str) -> Optional[str]:
    """Extract page ID from Confluence URL."""
    match = CONFLUENCE_PAGE_URL_RE.search(url)
    return match.group(1) if match else None


def is_confluence_url(url: str) -> bool:
    """Check if URL is a Confluence URL."""
    return "atlassian.net" in url


@dataclass
class ConfluenceAPIClient:
    """API client for fetching Confluence page content."""

    base_url: str = settings.base_url
    username: Optional[str] = None
    api_token: Optional[str] = None
    session: Optional[requests.Session] = None

    def __post_init__(self) -> None:
        self.username = self.username or settings.username
        self.api_token = self.api_token or settings.api_key
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

    def fetch_page(self, page_id: str) -> Dict[str, Any]:
        """
        Fetch Confluence page content by page ID.
        
        Args:
            page_id: The Confluence page ID
            
        Returns:
            Page content as JSON including body.storage or body.atlas_doc_format
        """
        # Use expand to get body content in storage format
        endpoint = f"{self.base_url.rstrip('/')}/rest/api/content/{page_id}"
        params = {
            "expand": "body.storage,body.view,version,space"
        }
        response = self.session.get(endpoint, params=params, timeout=30)
        if response.status_code != requests.codes.ok:
            raise RuntimeError(
                f"Confluence API 回傳狀態碼 {response.status_code}: {response.text}"
            )
        return response.json()
