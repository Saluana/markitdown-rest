
import os
from typing import Dict
from dotenv import load_dotenv

def load_environment() -> Dict[str, str]:
    """Load environment variables from .env file and system environment."""
    env_vars = {}
    
    # Try loading from .env file
    try:
        load_dotenv()
    except Exception as e:
        print(f"Warning: Could not load .env file: {e}")
    
    # Get all environment variables (both .env and system)
    env_vars = dict(os.environ)
    
    return env_vars
