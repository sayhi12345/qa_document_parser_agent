from pydantic_settings import BaseSettings
from config.loader import load_env_json

# Load configuration from JSON
_config_data = load_env_json()

class OpenAISettings(BaseSettings):
    api_key: str = ""
    model: str = "gpt-5.2"
    temperature: float = 0.0
    
    class Config:
        # Allow extra fields to be ignored
        extra = "ignore"

# Initialize settings with values from env.json
settings = OpenAISettings(
    api_key=_config_data.get("OPENAI_API_KEY", ""),
    model=_config_data.get("OPENAI_MODEL", "gpt-5.2"),
    temperature=_config_data.get("OPENAI_TEMPERATURE", 0.1)
)
