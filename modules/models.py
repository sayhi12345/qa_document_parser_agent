from pydantic import BaseModel, Field, validator
from typing import List


class QAItem(BaseModel):
    question: str = Field(..., min_length=2, description="常見問題（繁體中文）")
    answer: str = Field(..., min_length=2, description="對應答案（繁體中文）")

    @validator("question", "answer")
    def ensure_traditional_chinese(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("內容不可為空白")
        return value


class FigmaSummaryResult(BaseModel):
    title: str = Field(
        ...,
        min_length=4,
        max_length=80,
        description="供 Confluence 使用的中文標題",
    )
    plan: List[str] = Field(..., min_items=3, max_items=7, description="執行前的概念步驟")
    summary: List[str] = Field(..., min_items=5, max_items=30, description="5-30個重點條列")
    qa: List[QAItem] = Field(..., min_items=3, max_items=20, description="3-20組常見問答")

    @validator("title")
    def validate_title(cls, value: str) -> str:
        sanitized = value.strip()
        if not sanitized:
            raise ValueError("標題不可為空白")
        return sanitized

    @validator("summary")
    def validate_summary_length(cls, value: List[str]) -> List[str]:
        sanitized = [item.strip() for item in value if item.strip()]
        if not 5 <= len(sanitized) <= 30:
            raise ValueError("Summary 條列需介於 5-30 項")
        if any(item.startswith(("-", "*")) for item in sanitized):
            raise ValueError("Summary 不可包含項目符號")
        return sanitized

    @validator("qa")
    def validate_qa_count(cls, value: List[QAItem]) -> List[QAItem]:
        if len(value) > 20:
            raise ValueError("Q&A 不可超過 20 組")
        return value
