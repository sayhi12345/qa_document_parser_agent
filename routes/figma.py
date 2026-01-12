from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional

from modules.figma_agent import (
    generate_figma_summary,
    format_output,
    FigmaSummaryResult
)
from modules.confluence_agent import (
    resolve_confluence_title,
    build_confluence_adf,
    ConfluencePublisher
)

router = APIRouter()

class FigmaParseRequest(BaseModel):
    url: str
    token: Optional[str] = None
    model: str = "gpt-4.1-mini"
    temperature: float = 0.0
    publish_confluence: bool = False
    confluence_title: Optional[str] = None
    confluence_folder_id: Optional[str] = None
    search_activity_node: bool = True

class FigmaParseResponse(BaseModel):
    summary: str
    confluence_url: Optional[str] = None

@router.post("/parse", response_model=FigmaParseResponse)
async def parse_figma_endpoint(request: FigmaParseRequest):
    try:
        result: FigmaSummaryResult = generate_figma_summary(
            request.url,
            access_token=request.token,
            llm_model=request.model,
            temperature=request.temperature,
            search_activity_node=request.search_activity_node,
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
            # We could also raise an error or return a warning, but for now let's just return the summary
            # and maybe include the error in the response if we change the response model.
            # For now, just leave confluence_url as None or we could append error to summary.
            pass

    return FigmaParseResponse(summary=output_text, confluence_url=confluence_url)
