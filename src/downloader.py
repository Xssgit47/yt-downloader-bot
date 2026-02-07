import asyncio
import yt_dlp
from pathlib import Path

from .config import Config
from .utils import human_size


class DownloadError(Exception):
    pass


def get_ydl_opts(mode: str = "video", progress_callback=None):
    opts = Config.YDL_COMMON_OPTS.copy()

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

        # take the biggest / newest file
        file_path = max(files, key=lambda p: p.stat().st_size)
        size_mb = file_path.stat().st_size / (1024 * 1024)

        if size_mb > Config.MAX_FILE_SIZE_MB:
            file_path.unlink(missing_ok=True)
            raise DownloadError(f"File too large ({size_mb:.1f} MB)")

        return file_path, size_mb

    except Exception as e:
        raise DownloadError(str(e))
    finally:
        # cleanup old files (>5 min)
        now = asyncio.get_event_loop().time()
        for f in Config.TEMP_DIR.glob("*"):
            if (now - f.stat().st_mtime) > 300:
                f.unlink(missing_ok=True)
