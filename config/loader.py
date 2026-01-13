import json
import os
from pathlib import Path

def load_env_json():
    """
    Load configuration from env.json in the root directory and return as dict.
    This allows env.json values to be used directly without OS environment variables.
    """
    # Assuming env.json is in the project root, which is two levels up from config/
    # But we are running from root usually. Let's check root relative to CWD or file.
    # Safe bet: check CWD first, then relative to this file.
    
    paths_to_check = [
        Path("env.json"),
        Path(__file__).parent.parent / "env.json"
    ]
    
    config_dict = {}
    
    for env_path in paths_to_check:
        if env_path.exists():
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    config_dict = json.load(f)
                    break
            except Exception as e:
                print(f"Warning: Failed to load {env_path}: {e}")
    
    # Merge with os.environ: env.json (if present and not empty) takes precedence
    # Only use os.environ if the value in config_dict is empty or missing
    merged_config = os.environ.copy()
    
    for key, value in config_dict.items():
        if value: # If value is not empty string, None, etc.
            merged_config[key] = value
            
    return merged_config
