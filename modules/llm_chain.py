from typing import Optional
from pydantic import ValidationError

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI

from modules.models import FigmaSummaryResult
from config.prompts import settings as prompt_settings


def build_chain(llm: ChatOpenAI):
    parser = PydanticOutputParser(pydantic_object=FigmaSummaryResult)
    
    system_prompt = prompt_settings.figma_system_prompt
    human_template = prompt_settings.figma_human_template
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", human_template),
        ]
    )
    chain = prompt | llm | parser
    return chain, parser


def run_chain(
    url: str,
    figma_content: str,
    llm: ChatOpenAI,
    config: Optional[RunnableConfig] = None,
) -> FigmaSummaryResult:
    chain, parser = build_chain(llm)
    format_instructions = parser.get_format_instructions()
    try:
        result: FigmaSummaryResult = chain.invoke(
            {
                "url": url,
                "figma_content": figma_content,
                "format_instructions": format_instructions,
            },
            config=config or {},
        )
    except ValidationError as err:
        raise RuntimeError(f"LLM 輸出驗證失敗: {err}") from err
    return result
