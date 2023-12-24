from src.core.config import PydanticSettings
from pathlib import Path

settings = PydanticSettings(
    _env_file=str(Path(__file__).parent.parent.parent / ".env"),
    _env_file_encoding="utf-8",
)
