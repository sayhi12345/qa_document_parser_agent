from pydantic_settings import BaseSettings
from config.loader import load_env_json

# Load configuration from JSON
_config_data = load_env_json()

class FigmaSettings(BaseSettings):
    access_token: str = ""
    base_url: str = "https://api.figma.com/v1"
    
    class Config:
        # Allow extra fields to be ignored
        extra = "ignore"

# Initialize settings with values from env.json
settings = FigmaSettings(
    access_token=_config_data.get("FIGMA_ACCESS_TOKEN", ""),
    base_url=_config_data.get("FIGMA_BASE_URL", "https://api.figma.com/v1")
)
