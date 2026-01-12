from pydantic_settings import BaseSettings
from config.loader import load_env_json

# Load configuration from JSON
_config_data = load_env_json()

class MiscSettings(BaseSettings):
    log_dir: str = "./logs"
    
    class Config:
        # Allow extra fields to be ignored
        extra = "ignore"

# Initialize settings with values from env.json
settings = MiscSettings(
    log_dir=_config_data.get("LOG_DIR", "./logs")
)
