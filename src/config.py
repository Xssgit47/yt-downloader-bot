from pathlib import Path
import os
from dotenv import load_dotenv
import random

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

    COOKIES_PATH        = BASE_DIR / "cookies.txt"

    # Your free proxies (from the table you shared)
    PROXIES = [
        "http://jgvppobhc:ulcjlzjnoyr@31.59.20.176:6754",
        "http://jgvppobhc:ulcjlzjnoyr@23.95.150.145:6114",
        "http://jgvppobhc:ulcjlzjnoyr@198.233.239.134:6540",
        "http://jgvppobhc:ulcjlzjnoyr@45.38.107.97:6014",
        "http://jgvppobhc:ulcjlzjnoyr@107.172.163.27:6543",
        "http://jgvppobhc:ulcjlzjnoyr@198.105.121.200:6462",
        "http://jgvppobhc:ulcjlzjnoyr@64.137.96.74:6641",
        "http://jgvppobhc:ulcjlzjnoyr@216.10.27.159:6837",
        "http://jgvppobhc:ulcjlzjnoyr@23.26.71.145:5628",
        "http://jgvppobhc:ulcjlzjnoyr@23.229.19.94:8689",
    ]

    # Randomly pick one proxy each time (or None if list empty)
    @classmethod
    def get_random_proxy(cls):
        if not cls.PROXIES:
            return None
        return random.choice(cls.PROXIES)

    YDL_COMMON_OPTS = {
        "quiet": True,
        "no_warnings": True,
        "continuedl": True,
        "retries": 10,
        "fragment_retries": 10,
        "http_chunk_size": 10 * 1024 * 1024,
        "outtmpl": str(TEMP_DIR / "%(title)s.%(ext)s"),
        "noplaylist": True,
        # Optional: force Android client (helps with bot detection)
        "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
        "user_agent": "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    }
