from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from modules.confluence_doc_agent import (
    generate_confluence_summary,
    format_output,
)
from modules.confluence_agent import (
    resolve_confluence_title,
    build_confluence_adf,
    ConfluencePublisher
)
from modules.models import FigmaSummaryResult

router = APIRouter()


class ConfluenceParseRequest(BaseModel):
    url: str
    model: str = "gpt-4.1-mini"
    temperature: float = 0.0
    publish_confluence: bool = False
    confluence_title: Optional[str] = None
    confluence_folder_id: Optional[str] = None


class ConfluenceParseResponse(BaseModel):
    summary: str
    confluence_url: Optional[str] = None


@router.post("/parse", response_model=ConfluenceParseResponse)
async def parse_confluence_endpoint(request: ConfluenceParseRequest):
    """
    Parse a Confluence page and generate summary/Q&A.
    Optionally publish the result back to Confluence.
    """
    try:
        result: FigmaSummaryResult = generate_confluence_summary(
            request.url,
            llm_model=request.model,
            temperature=request.temperature,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    output_text = format_output(result)
    confluence_url = None

    if request.publish_confluence:
        title = request.confluence_title or resolve_confluence_title(result, request.url)
        try:
            publisher = ConfluencePublisher()
            confluence_url = publisher.create_page(
                title=title,
                adf_doc=build_confluence_adf(result, request.url),
                folder_id=request.confluence_folder_id
            )
        except Exception as e:
            # Log error but return summary
            print(f"Confluence publishing failed: {e}")
            pass

    return ConfluenceParseResponse(summary=output_text, confluence_url=confluence_url)
