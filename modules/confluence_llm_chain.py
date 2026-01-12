from typing import Optional
from pydantic import ValidationError

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI

from modules.models import FigmaSummaryResult
from config.prompts import settings as prompt_settings


def build_confluence_chain(llm: ChatOpenAI):
    """
    Build LangChain chain for Confluence content summarization.
    Uses Confluence-specific prompts (without UI filtering).
    """
    parser = PydanticOutputParser(pydantic_object=FigmaSummaryResult)
    
    system_prompt = prompt_settings.confluence_system_prompt
    human_template = prompt_settings.confluence_human_template
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", human_template),
        ]
    )
    chain = prompt | llm | parser
    return chain, parser


def run_confluence_chain(
    url: str,
    content: str,
    llm: ChatOpenAI,
    config: Optional[RunnableConfig] = None,
) -> FigmaSummaryResult:
    """
    Run the Confluence summarization chain.
    
    Args:
        url: Source Confluence URL
        content: Extracted text content from Confluence
        llm: ChatOpenAI instance
        config: Optional runnable config
        
    Returns:
        FigmaSummaryResult with title, plan, summary, and qa
    """
    chain, parser = build_confluence_chain(llm)
    format_instructions = parser.get_format_instructions()
    try:
        result: FigmaSummaryResult = chain.invoke(
            {
                "url": url,
                "content": content,
                "format_instructions": format_instructions,
            },
            config=config or {},
        )
    except ValidationError as err:
        raise RuntimeError(f"LLM 輸出驗證失敗: {err}") from err
    return result
