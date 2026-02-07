# Defensive path fix
import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import asyncio
import yt_dlp
from pathlib import Path
import logging

from src.config import Config
from src.utils import human_size

logger = logging.getLogger(__name__)


class DownloadError(Exception):
    pass


def get_ydl_opts(mode: str = "video", progress_callback=None):
    opts = Config.YDL_COMMON_OPTS.copy()

    # Cookies support
    if Config.COOKIES_PATH.exists():
        opts["cookies"] = str(Config.COOKIES_PATH)
        logger.info(f"Using cookies from: {Config.COOKIES_PATH}")
    else:
        logger.info("No cookies.txt found → running without authentication")

    if mode == "video":
        opts.update({
            "format": "bestvideo[height<=1080]+bestaudio/best",
            "merge_output_format": "mp4",
        })
    else:  # audio
        opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        })

    if progress_callback:
        opts["progress_hooks"] = [progress_callback]

    return opts


async def get_video_info(url: str) -> dict:
    with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
        try:
            return ydl.extract_info(url, download=False)
        except Exception as e:
            raise DownloadError(f"Info extraction failed: {str(e)}")


async def download_media(url: str, mode: str = "video", status_msg=None):
    def progress_hook(d):
        if d['status'] != 'downloading' or not status_msg:
            return
        percent = d.get('_percent_str', '?').strip()
        speed   = d.get('_speed_str',   '?').strip()
        eta     = d.get('_eta_str',     '?').strip()
        asyncio.create_task(
            status_msg.edit_text(f"↓ Downloading… {percent} • {speed} • ETA {eta}")
        )

    opts = get_ydl_opts(mode, progress_hook)

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

        files = list(Config.TEMP_DIR.glob("*"))
        if not files:
            raise DownloadError("No file downloaded")

        file_path = max(files, key=lambda p: p.stat().st_size)
        size_mb = file_path.stat().st_size / (1024 * 1024)

        if size_mb > Config.MAX_FILE_SIZE_MB:
            file_path.unlink(missing_ok=True)
            raise DownloadError(f"File too large ({size_mb:.1f} MB)")

        return file_path, size_mb

    except Exception as e:
        raise DownloadError(str(e))
    finally:
        now = asyncio.get_event_loop().time()
        for f in Config.TEMP_DIR.glob("*"):
            if (now - f.stat().st_mtime) > 300:
                f.unlink(missing_ok=True)
