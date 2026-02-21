from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings


def find_env_file(start: Path) -> Path | None:
    cur = start
    for _ in range(12):
        candidate = cur / ".env"
        if candidate.exists():
            return candidate
        if cur.parent == cur:
            break
        cur = cur.parent
    return None


HERE = Path(__file__).resolve()
ENV_PATH = find_env_file(HERE)

# Load .env into process env BEFORE Settings initializes
if ENV_PATH:
    load_dotenv(dotenv_path=ENV_PATH, override=False)


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"
    CORS_ORIGINS: str = "http://localhost:5173"

    OPENAQ_API_BASE: str = "https://api.openaq.org/v3"
    OPENAQ_API_KEY: str = ""
    OPENMETEO_BASE: str = "https://api.open-meteo.com/v1"


settings = Settings()
