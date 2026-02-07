import re
import asyncio
from pathlib import Path

from telegram import Message
from telegram.constants import ParseMode

from src.config import Config


def sanitize_filename(title: str) -> str:
    """Remove invalid characters and limit length"""
    return re.sub(r'[^\w\s.-]', '_', title).strip()[:100]


def human_size(size_bytes: int | float) -> str:
    """Convert bytes to human readable format"""
    for unit in ['B', 'KiB', 'MiB', 'GiB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TiB"


async def delete_later(message: Message, delay: int = 12):
    """Delete message after delay (best effort)"""
    try:
        await asyncio.sleep(delay)
        await message.delete()
    except:
        pass


async def reply_branded(
    message: Message,
    text: str,
    use_long_footer: bool = False,
    **kwargs
):
    footer = Config.FOOTER_LONG if use_long_footer else Config.FOOTER_SHORT
    full_text = text + footer

    return await message.reply_text(
        full_text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
        **kwargs
    )


async def edit_branded(
    message: Message,
    text: str,
    use_long_footer: bool = False,
    **kwargs
):
    footer = Config.FOOTER_LONG if use_long_footer else Config.FOOTER_SHORT
    full_text = text + footer

    try:
        await message.edit_text(
            full_text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            **kwargs
        )
    except Exception:
        await reply_branded(message, text, use_long_footer, **kwargs)
