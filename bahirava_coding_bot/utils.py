# ════════════════════════════════════════════
#   ᗪIᑕTᗩTOᖇ ᕼᗩᑕK Cᴏᴅɪɴɢ ʙᴏᴛ — Utilities
# ════════════════════════════════════════════

from telegram import Bot, ChatMember, InlineKeyboardButton, InlineKeyboardMarkup
from config import REQUIRED_JOINS, JOIN_LINKS


# ─── Small Caps Font (ꜰᴏɴᴛ style) ───────────
_NORMAL = 'abcdefghijklmnopqrstuvwxyz'
_SCAPS  = 'ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ'

def to_sc(text: str) -> str:
    """Convert ASCII letters to Unicode small caps (ꜰᴏɴᴛ style)."""
    out = []
    for ch in text:
        lo = ch.lower()
        if lo in _NORMAL:
            out.append(_SCAPS[_NORMAL.index(lo)])
        else:
            out.append(ch)
    return ''.join(out)


# ─── Colored Button Styles ───────────────────
# Telegram does not support native button colors via Bot API,
# so we prefix button text with a colored circle emoji.
BUTTON_STYLES = {
    'primary':  '🔵',   # Blue
    'success':  '🟢',   # Green
    'danger':   '🔴',   # Red
    'warning':  '🟡',   # Yellow
    'info':     '🔷',   # Light Blue
    'default':  '⬜',   # White / none
}

def btn(text: str, callback_data: str = None, url: str = None,
        style: str = 'default') -> InlineKeyboardButton:
    """
    Create a colored InlineKeyboardButton.
    style: 'primary' (🔵), 'success' (🟢), 'danger' (🔴), 'warning' (🟡), 'info' (🔷)
    """
    color = BUTTON_STYLES.get(style, '')
    label = f"{color} {text}" if color and color != '⬜' else text
    if url:
        return InlineKeyboardButton(label, url=url)
    return InlineKeyboardButton(label, callback_data=callback_data)


# ─── Force Join Checker ──────────────────────
async def check_joined(bot: Bot, user_id: int) -> list[str]:
    """Returns list of channels/groups the user has NOT joined yet."""
    not_joined = []
    for handle in REQUIRED_JOINS:
        try:
            member: ChatMember = await bot.get_chat_member(handle, user_id)
            if member.status in ("left", "kicked", "banned"):
                not_joined.append(handle)
        except Exception:
            pass
    return not_joined


def join_buttons(not_joined: list[str]) -> InlineKeyboardMarkup:
    """Build InlineKeyboardMarkup with colored join buttons."""
    buttons = []
    for i, handle in enumerate(not_joined):
        link  = JOIN_LINKS.get(handle, f"https://t.me/{handle.lstrip('@')}")
        style = 'primary' if i % 2 == 0 else 'success'
        buttons.append([btn(f"➕ {to_sc(handle.lstrip('@'))}", url=link, style=style)])

    buttons.append([btn(f"✅ {to_sc('I Have Joined All')}", callback_data="check_joined", style='success')])
    return InlineKeyboardMarkup(buttons)


# ─── Progress Bar ────────────────────────────
def progress_bar(current: int, total: int, length: int = 10) -> str:
    filled = int(length * current / total) if total else 0
    bar    = "█" * filled + "░" * (length - filled)
    return f"[{bar}] {current}/{total}"
