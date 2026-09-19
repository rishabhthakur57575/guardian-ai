import os
from pathlib import Path
from typing import List
from pydantic import BaseModel

# Base directory of the backend package
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB_PATH = BACKEND_DIR / "guardianai.db"

def get_allowed_origins() -> List[str]:
    env_origins = os.getenv("ALLOWED_ORIGINS") or os.getenv("CORS_ORIGINS")
    if env_origins:
        return [origin.strip() for origin in env_origins.split(",") if origin.strip()]
    return [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ]

class Settings(BaseModel):
    PROJECT_NAME: str = "GuardianAI Behavioral Threat Monitoring Engine"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH.as_posix()}")
    ALLOWED_ORIGINS: List[str] = get_allowed_origins()
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()


