from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TOKEN:
        raise ValueError("TELEGRAM_TOKEN is required in .env file")

    MAX_FILE_SIZE_MB    = float(os.getenv("MAX_FILE_SIZE_MB", 1800))
    MAX_DURATION_SEC    = int(os.getenv("MAX_DURATION_SECONDS", 3600))
    LOG_LEVEL           = os.getenv("LOG_LEVEL", "INFO")

    FOOTER_SHORT        = os.getenv("FOOTER_SHORT", "\n\nMade by @FNxDANGER")
    FOOTER_LONG         = os.getenv("FOOTER_LONG",  "\n\nDeveloper: @FNxDANGER\nMade with ❤️ by @FNxDANGER")

    TEMP_DIR            = BASE_DIR / "temp"
    TEMP_DIR.mkdir(exist_ok=True)

    COOKIES_PATH        = BASE_DIR / "cookies.txt"   # ← new

    YDL_COMMON_OPTS = {
        "quiet": True,
        "no_warnings": True,
        "continuedl": True,
        "retries": 10,
        "fragment_retries": 10,
        "http_chunk_size": 10 * 1024 * 1024,  # 10 MB
        "outtmpl": str(TEMP_DIR / "%(title)s.%(ext)s"),
        "noplaylist": True,
    }
