# Project Overview: QA Document Parser Agent API

## Context & Goal
A FastAPI-based microservice designed to parse Figma design files and Confluence documents, generate structured summaries and Q&A using OpenAI's LLM, and optionally publish the results to Confluence as formatted pages.

## Architecture & Patterns
- **Entry Point:** `server.py` initializes the FastAPI app, mounts the web UI, and includes `routes.figma` and `routes.confluence` routers.
- **REST API:**
    - `POST /figma/parse`: Orchestrates Figma flow (Fetch → Summarize → Publish).
    - `POST /confluence/parse`: Orchestrates Confluence flow (Fetch → Summarize → Publish).
- **Core Logic (Modular Architecture):**
    - **Figma Pipeline:**
        - **Orchestration (`modules/figma_agent.py`):** Coordination for Figma parsing.
        - **Client (`modules/figma_client.py`):** Figma API interactions.
        - **Parser (`modules/figma_parser.py`):** Figma document tree traversal.
        - **Chain (`modules/llm_chain.py`):** Figma-specific LLM prompts.
    - **Confluence Pipeline:**
        - **Orchestration (`modules/confluence_doc_agent.py`):** Coordination for Confluence parsing.
        - **Client (`modules/confluence_client.py`):** Confluence API content fetching.
        - **Parser (`modules/confluence_parser.py`):** XHTML/Storage format parsing.
        - **Chain (`modules/llm_chain.py`):** Confluence-specific LLM prompts (no UI filtering).
    - **Shared Modules:**
        - **Models (`modules/models.py`):** Pydantic data models (`QAItem`, `FigmaSummaryResult`).
        - **Confluence Publisher (`modules/confluence_agent.py`):** Shared utility for publishing results to Confluence Cloud in ADF format.
- **Configuration:**
    - Custom loader `config/loader.py` reads from `env.json` (bypasses OS environment variables).
    - **Prompts (`config/prompts.py`):** Externalized prompts for both Figma and Confluence.

## Key Files
- `server.py`: App entry point
- `routes/figma.py` & `routes/confluence.py`: API endpoint handlers
- `modules/figma_agent.py` & `modules/confluence_doc_agent.py`: High-level orchestration
- `modules/confluence_client.py` & `modules/figma_client.py`: API clients
- `modules/confluence_parser.py` & `modules/figma_parser.py`: Content extraction logic
- `config/prompts.py`: LLM prompts configuration

## Data Structures
- **Figma Input (`FigmaParseRequest`):**
    - `url` (str): Figma file URL
    - `publish_confluence` (bool): Whether to sink result to Confluence
    - `search_activity_node` (bool): Search for specific nodes (defaults to true)
- **Confluence Input (`ConfluenceParseRequest`):**
    - `url` (str): Confluence page URL
    - `publish_confluence` (bool): Whether to publish back to Confluence
- **Output:** Both return a JSON response containing `summary` (markdown) and `confluence_url` (if published).

## Gotchas/Constraints
- **URL Detection:** The UI (`script.js`) detects URL type based on domain (`figma.com` vs `atlassian.net`) to route to the correct API.
- **Prompt Differences:** The Confluence parser uses a specific prompt that does **not** filter out UI design content, as Confluence is text-heavy.
- **Config Pattern:** Always use `env.json` for configuration updates.
- **Validation:** Both pipelines share `FigmaSummaryResult` validators (e.g., summary length, no bullets).
- **Hardcoded Logic:** Figma parsing still prioritizes "活動說明頁" or "活動說明" if enabled.
