import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from src.downloader import get_video_info, download_media, DownloadError
from src.utils import reply_branded, edit_branded, human_size, sanitize_filename, delete_later
from src.config import Config


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🎥 <b>YouTube Downloader Bot</b>\n\n"
        "Send any YouTube / Shorts / Live link\n"
        "• Video: best ≤1080p + audio (mp4)\n"
        "• Audio: best quality (mp3 192kbps)\n"
        "• Max ~60 minutes / ~1.8 GB\n\n"
        "<b>Commands:</b>\n"
        "/start — this message\n"
        "/help — same\n"
        "/audio — switch to audio mode\n\n"
        "<i>For personal / educational use only. Respect YouTube TOS.</i>"
    )
    await reply_branded(update.message, text, use_long_footer=True)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)


async def audio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await reply_branded(
        update.message,
        "Audio mode activated ✅\n\nNow send a YouTube link – I'll download as MP3 (192 kbps).",
        use_long_footer=True
    )


async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE, mode: str = "video"):
    url = update.message.text.strip()
    if "youtube.com" not in url and "youtu.be" not in url:
        await reply_branded(
            update.message,
            "Please send a valid YouTube link.",
            use_long_footer=False
        )
        return

    status = await update.message.reply_text("🔍 Checking video...")

    try:
        info = await get_video_info(url)
        title = sanitize_filename(info.get("title", "video"))
        duration = info.get("duration", 0) or 0

        if duration > Config.MAX_DURATION_SEC:
            await edit_branded(
                status,
                "This video is too long (>60 min). Not supported.",
                use_long_footer=True
            )
            await delete_later(status)
            return

        await edit_branded(
            status,
            f"📥 Starting download: {title[:60]}...",
            use_long_footer=False
        )

        file_path, size_mb = await download_media(url, mode, status)

        await edit_branded(
            status,
            "📤 Uploading to Telegram...",
            use_long_footer=False
        )

        caption = (
            f"<b>{title}</b>\n"
            f"{human_size(file_path.stat().st_size)} • "
            f"{duration//60}:{duration%60:02d}"
        )

        if mode == "video" and file_path.suffix.lower() == ".mp4":
            await update.message.reply_video(
                video=file_path.open("rb"),
                caption=caption + Config.FOOTER_SHORT,
                supports_streaming=True,
                parse_mode=ParseMode.HTML
            )
        else:
            await update.message.reply_document(
                document=file_path.open("rb"),
                caption=caption + Config.FOOTER_SHORT,
                parse_mode=ParseMode.HTML
            )

        file_path.unlink(missing_ok=True)

    except DownloadError as e:
        await edit_branded(status, f"❌ {str(e)}", use_long_footer=True)
    except Exception:
        await edit_branded(status, "🚨 Something went wrong. Try again later.", use_long_footer=True)
    finally:
        await delete_later(status, 10)
