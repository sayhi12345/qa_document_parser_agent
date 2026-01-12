from pydantic_settings import BaseSettings
from config.loader import load_env_json

# Load configuration from JSON
_config_data = load_env_json()

class ConfluenceSettings(BaseSettings):
    username: str = ""
    api_key: str = ""
    base_url: str = "https://lang.atlassian.net/wiki"
    space_key: str = "ACS"
    folder_id: str = "3412262946"
    
    class Config:
        # Allow extra fields to be ignored
        extra = "ignore"

# Initialize settings with values from env.json
settings = ConfluenceSettings(
    username=_config_data.get("CONFLUENCE_USERNAME", ""),
    api_key=_config_data.get("CONFLUENCE_API_KEY", ""),
    base_url=_config_data.get("CONFLUENCE_BASE_URL", "https://lang.atlassian.net/wiki"),
    space_key=_config_data.get("CONFLUENCE_SPACE_KEY", "ACS"),
    folder_id=_config_data.get("CONFLUENCE_FOLDER_ID", "3412262946")
)
