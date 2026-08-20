#!/usr/bin/env python3
# ════════════════════════════════════════════════════════════════
#   ᗪIᑕTᗩTOᖇ Cᴏᴅɪɴɢ ʙᴏᴛ
#   Owner : @PV_Parwani_4k  |  ID : 8204959327
# ════════════════════════════════════════════════════════════════

import logging
import asyncio
from datetime import datetime

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    BotCommand
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)
from telegram.constants import ParseMode
import google.generativeai as genai

from config import (
    BOT_TOKEN, GEMINI_API_KEY, OWNER_ID, OWNER_USERNAME,
    REFERRAL_REQUIRED, MENU_VIDEO_URL
)
from database import (
    init_db, add_user, get_user, is_banned, ban_user, unban_user,
    get_all_users, get_user_count, add_referral, get_referral_count,
    is_verified, set_verified
)
from utils import to_sc, check_joined, join_buttons, progress_bar, btn

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ─── Gemini AI Setup ─────────────────────────
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

BOT_NAME   = "ᗪIᑕTᗩTOᖇ Cᴏᴅɪɴɢ ʙᴏᴛ"
BOT_FOOTER = f"\n\n━━━━━━━━━━━━━━━━━━\n🤖 {BOT_NAME}\n👑 {to_sc('Owner')} : {OWNER_USERNAME}"


# ════════════════════════════════════════════
#   KEYBOARDS  (all buttons use colored styles)
# ════════════════════════════════════════════

def main_menu_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            btn(f"💻 {to_sc('Generate Code')}",  callback_data="menu_code",     style="primary"),
            btn(f"🐛 {to_sc('Fix Bug')}",         callback_data="menu_fix",      style="danger"),
        ],
        [
            btn(f"📖 {to_sc('Explain Code')}",    callback_data="menu_explain",  style="success"),
            btn(f"⚡ {to_sc('Optimize Code')}",   callback_data="menu_optimize", style="warning"),
        ],
        [
            btn(f"🌐 {to_sc('Convert Language')}", callback_data="menu_convert",  style="info"),
            btn(f"📋 {to_sc('Code Review')}",      callback_data="menu_review",   style="primary"),
        ],
        [
            btn(f"👥 {to_sc('Referral')}",         callback_data="menu_referral", style="success"),
            btn(f"📊 {to_sc('My Stats')}",          callback_data="menu_stats",    style="info"),
        ],
        [
            btn(f"ℹ️ {to_sc('Help')}",              callback_data="menu_help",     style="warning"),
            btn(f"👑 {to_sc('Owner')}",
                url=f"https://t.me/{OWNER_USERNAME.lstrip('@')}",                 style="danger"),
        ],
    ])


def back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        btn(f"🔙 {to_sc('Back to Menu')}", callback_data="menu_back", style="primary")
    ]])


def share_keyboard(ref_link: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [btn(f"🔗 {to_sc('Share My Link')}", url=f"https://t.me/share/url?url={ref_link}", style="success")],
        [btn(f"🔙 {to_sc('Back')}",          callback_data="menu_back",                    style="primary")],
    ])


# ════════════════════════════════════════════
#   GATE CHECK
# ════════════════════════════════════════════

async def gate_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Returns True if user passes all gates. Sends block message & returns False otherwise."""
    user = update.effective_user
    msg  = update.effective_message

    # ── Banned ────────────────────────────────
    if is_banned(user.id):
        await msg.reply_text(
            f"🚫 *{to_sc('You are banned from using this bot.')}*\n"
            f"{to_sc('Contact')} {OWNER_USERNAME} {to_sc('to appeal.')}",
            parse_mode=ParseMode.MARKDOWN
        )
        return False

    # ── Force join ───────────────────────────
    not_joined = await check_joined(context.bot, user.id)
    if not_joined:
        text = (
            f"👋 *{to_sc('Welcome to')} {BOT_NAME}!*\n\n"
            f"⚠️ *{to_sc('You must join all channels & groups to use this bot')}:*\n\n"
            + "".join(f"  🔴 `{h}`\n" for h in not_joined)
            + f"\n✅ {to_sc('After joining, tap the button below.')}"
        )
        await msg.reply_text(text, parse_mode=ParseMode.MARKDOWN,
                             reply_markup=join_buttons(not_joined))
        return False

    # ── Referral lock ────────────────────────
    if not is_verified(user.id):
        ref_count = get_referral_count(user.id)
        if ref_count < REFERRAL_REQUIRED:
            bot_me   = await context.bot.get_me()
            ref_link = f"https://t.me/{bot_me.username}?start=ref_{user.id}"
            bar      = progress_bar(ref_count, REFERRAL_REQUIRED)
            text = (
                f"🔒 *{to_sc('Referral Lock')}*\n\n"
                f"{to_sc('You need')} *{REFERRAL_REQUIRED} {to_sc('referrals')}* "
                f"{to_sc('to unlock the bot')}.\n\n"
                f"📊 {to_sc('Progress')} : `{bar}`\n\n"
                f"🔗 *{to_sc('Your Referral Link')}:*\n`{ref_link}`\n\n"
                f"📣 {to_sc('Share this link. Each new user who starts via your link = 1 referral.')}"
                f"{BOT_FOOTER}"
            )
            kb = InlineKeyboardMarkup([[
                btn(f"🔗 {to_sc('Share My Link')}",
                    url=f"https://t.me/share/url?url={ref_link}", style="success")
            ]])
            await msg.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb)
            return False
        else:
            set_verified(user.id)

    return True


# ════════════════════════════════════════════
#   COMMAND HANDLERS
# ════════════════════════════════════════════

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username or "", user.full_name)

    # ── Referral tracking ─────────────────────
    args = context.args
    if args and args[0].startswith("ref_"):
        try:
            referrer_id = int(args[0].split("_")[1])
            if referrer_id != user.id:
                was_new = add_referral(referrer_id, user.id)
                if was_new:
                    ref_now = get_referral_count(referrer_id)
                    if ref_now >= REFERRAL_REQUIRED:
                        set_verified(referrer_id)
                    try:
                        await context.bot.send_message(
                            referrer_id,
                            f"🎉 *{to_sc('New Referral!')}*\n\n"
                            f"👤 *{user.full_name}* {to_sc('joined via your link!')}\n"
                            f"📊 {to_sc('Your referrals')} : *{ref_now}/{REFERRAL_REQUIRED}*\n\n"
                            + (f"✅ {to_sc('You are now fully unlocked! Use /start')}"
                               if ref_now >= REFERRAL_REQUIRED
                               else f"🔗 {to_sc('Keep sharing to unlock the bot!')}"),
                            parse_mode=ParseMode.MARKDOWN
                        )
                    except Exception:
                        pass
        except (ValueError, IndexError):
            pass

    if not await gate_check(update, context):
        return

    caption = (
        f"✨ *{to_sc('Welcome to')} {BOT_NAME}!* ✨\n\n"
        f"🤖 {to_sc('I generate, fix, explain, optimize & review code in any language!')}\n\n"
        f"👑 {to_sc('Owner')}     : {OWNER_USERNAME}\n"
        f"👤 {to_sc('Your Name')} : {user.full_name}\n"
        f"🆔 {to_sc('Your ID')}   : `{user.id}`\n\n"
        f"⬇️ {to_sc('Choose an option from the menu below')}:"
        f"{BOT_FOOTER}"
    )
    try:
        await update.message.reply_video(
            video=MENU_VIDEO_URL,
            caption=caption,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=main_menu_keyboard(user.id)
        )
    except Exception: 
        await update.message.reply_text(caption, parse_mode=ParseMode.MARKDOWN,
                                        reply_markup=main_menu_keyboard(user.id))


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await gate_check(update, context):
        return
    text = (
        f"📚 *{BOT_NAME} — {to_sc('Help')}*\n\n"
        f"• /start — {to_sc('Open main menu')}\n"
        f"• /help — {to_sc('Show this help')}\n"
        f"• /referral — {to_sc('Referral link & stats')}\n"
        f"• /stats — {to_sc('Your usage stats')}\n\n"
        f"💻 *{to_sc('Coding Features')}*\n"
        f"{to_sc('Send any coding question, code snippet or error message!')}\n\n"
        f"*{to_sc('Examples')}:*\n"
        f"• `{to_sc('Write a Python web scraper')}`\n"
        f"• `{to_sc('Fix this error: TypeError ...')}`\n"
        f"• `{to_sc('Explain this JavaScript code')}`\n"
        f"• `{to_sc('Convert this Python code to JavaScript')}`"
        f"{BOT_FOOTER}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN,
                                    reply_markup=main_menu_keyboard(update.effective_user.id))


async def cmd_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await gate_check(update, context):
        return
    user      = update.effective_user
    bot_me    = await context.bot.get_me()
    ref_link  = f"https://t.me/{bot_me.username}?start=ref_{user.id}"
    ref_count = get_referral_count(user.id)
    verified  = is_verified(user.id)
    bar       = progress_bar(ref_count, REFERRAL_REQUIRED)
    text = (
        f"👥 *{to_sc('Referral System')}*\n\n"
        f"🔗 *{to_sc('Your Link')}:*\n`{ref_link}`\n\n"
        f"📊 {to_sc('Referrals')}  : *{ref_count}*\n"
        f"🏆 {to_sc('Status')}     : {'✅ ' + to_sc('Unlocked') if verified else '🔒 ' + to_sc('Locked')}\n"
        + (f"📈 {to_sc('Progress')} : `{bar}`\n" if not verified else "")
        + f"\n📣 {to_sc('Share your link to earn referrals!')}"
        f"{BOT_FOOTER}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN,
                                    reply_markup=share_keyboard(ref_link))


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await gate_check(update, context):
        return
    user = update.effective_user
    u    = get_user(user.id)
    ref  = get_referral_count(user.id)
    text = (
        f"📊 *{to_sc('Your Stats')}*\n\n"
        f"👤 {to_sc('Name')}      : {user.full_name}\n"
        f"🆔 {to_sc('ID')}        : `{user.id}`\n"
        f"📅 {to_sc('Joined')}    : {(u['joined_at'] or '')[:10]}\n"
        f"👥 {to_sc('Referrals')} : *{ref}*\n"
        f"🔓 {to_sc('Status')}    : {'✅ ' + to_sc('Verified') if is_verified(user.id) else '🔒 ' + to_sc('Locked')}"
        f"{BOT_FOOTER}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN,
                                    reply_markup=back_keyboard())


# ─── Owner-only ᗪIᑕTᗩTOᖇ─────────────────────
def owner_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != OWNER_ID:
            await update.message.reply_text(
                f"🚫 *{to_sc('Owner Only Command')}*", parse_mode=ParseMode.MARKDOWN)
            return
        return await func(update, context)
    return wrapper


@owner_only
async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a text message or a replied-to message to every non-banned user."""
    source_message = update.message.reply_to_message
    msg_text = " ".join(context.args).strip()

    if not source_message and not msg_text:
        await update.message.reply_text(
            "ℹ️ روش استفاده:\n"
            "`/broadcast متن پیام`\n\n"
            "یا روی یک پیام ریپلای کنید و فقط `/broadcast` را بفرستید.",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    users = get_all_users()
    sent = 0
    failed = 0

    for user in users:
        try:
            if source_message:
                # Copies text, photo, video, document, voice, and other Telegram media.
                await context.bot.copy_message(
                    chat_id=user["user_id"],
                    from_chat_id=source_message.chat_id,
                    message_id=source_message.message_id
                )
            else:
                # Plain text avoids Markdown errors when the owner's message contains symbols.
                await context.bot.send_message(
                    chat_id=user["user_id"],
                    text=f"📢 {to_sc('Broadcast')}\n\n{msg_text}"
                )
            sent += 1
            await asyncio.sleep(0.05)
        except Exception as exc:
            failed += 1
            logger.warning("Broadcast failed for user %s: %s", user["user_id"], exc)

    await update.message.reply_text(
        f"✅ *{to_sc('Broadcast Complete')}*\n"
        f"📨 Sent: `{sent}/{len(users)}`\n"
        f"⚠️ Failed: `{failed}`",
        parse_mode=ParseMode.MARKDOWN
    )


@owner_only
async def cmd_ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("ℹ️ Usage: `/ban <user_id>`", parse_mode=ParseMode.MARKDOWN)
        return
    try:
        uid = int(context.args[0])
        ban_user(uid)
        await update.message.reply_text(f"✅ {to_sc('Banned user')} `{uid}`.",
                                        parse_mode=ParseMode.MARKDOWN)
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")


@owner_only
async def cmd_unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("ℹ️ Usage: `/unban <user_id>`", parse_mode=ParseMode.MARKDOWN)
        return
    try:
        uid = int(context.args[0])
        unban_user(uid)
        await update.message.reply_text(f"✅ {to_sc('Unbanned user')} `{uid}`.",
                                        parse_mode=ParseMode.MARKDOWN)
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")


@owner_only
async def cmd_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total = get_user_count()
    await update.message.reply_text(
        f"👥 *{to_sc('Users who started the bot')}* : `{total}`\n"
        f"✅ {to_sc('Each user needs 2 unique referrals before using the bot.')}",
        parse_mode=ParseMode.MARKDOWN)


@owner_only
async def cmd_addref(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("ℹ️ Usage: `/addref <user_id>`", parse_mode=ParseMode.MARKDOWN)
        return
    try:
        uid = int(context.args[0])
        set_verified(uid)
        await update.message.reply_text(f"✅ {to_sc('User')} `{uid}` {to_sc('verified.')}",
                                        parse_mode=ParseMode.MARKDOWN)
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")


# ════════════════════════════════════════════
#   CALLBACK QUERY HANDLER
# ════════════════════════════════════════════

# Pending action per user
user_pending: dict[int, str] = {}

MENU_ACTIONS = {
    "menu_code":     ("💻", "Generate Code",    "What code do you want me to generate? Describe it in detail."),
    "menu_fix":      ("🐛", "Fix Bug",           "Paste your buggy code or describe the error. I will fix it!"),
    "menu_explain":  ("📖", "Explain Code",      "Paste the code you want me to explain."),
    "menu_optimize": ("⚡", "Optimize Code",     "Paste the code you want me to optimize for performance."),
    "menu_convert":  ("🌐", "Convert Language",  "Paste your code and tell me which language to convert it to."),
    "menu_review":   ("📋", "Code Review",       "Paste your code for a full professional review."),
}

AI_PROMPTS = {
    "menu_code":     "You are an expert programmer. Generate clean, well-commented, production-ready code. Include brief explanations. Request: ",
    "menu_fix":      "You are an expert debugger. Analyze and fix the following buggy code or error. Show the fixed code and explain what was wrong. Input: ",
    "menu_explain":  "You are a programming teacher. Explain this code clearly step by step as if to someone learning. Code: ",
    "menu_optimize": "You are a performance expert. Optimize this code for speed and efficiency. Show the optimized version and explain improvements. Code: ",
    "menu_convert":  "You are a multilingual programmer. Convert the following code to the requested target language. Keep logic identical. Input: ",
    "menu_review":   "You are a senior software engineer doing a code review. Review this code for bugs, security issues, best practices, and improvements. Be thorough. Code: ",
}

MENU_STYLES = {
    "menu_code":     "primary",
    "menu_fix":      "danger",
    "menu_explain":  "success",
    "menu_optimize": "warning",
    "menu_convert":  "info",
    "menu_review":   "primary",
}


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    data = query.data

    # ── Check join status ─────────────────────
    if data == "check_joined":
        not_joined = await check_joined(context.bot, user.id)
        if not_joined:
            await query.edit_message_text(
                f"⚠️ *{to_sc('You still have not joined all channels!')}*\n\n"
                + "".join(f"  🔴 `{h}`\n" for h in not_joined)
                + f"\n{to_sc('Please join all and try again.')}",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=join_buttons(not_joined)
            )
        else:
            await query.edit_message_text(
                f"✅ *{to_sc('All channels joined! Use /start to open the menu.')}*",
                parse_mode=ParseMode.MARKDOWN
            )
        return

    if not await gate_check(update, context):
        return

    # ── Coding task menu items ────────────────
    if data in MENU_ACTIONS:
        emoji, title, prompt_text = MENU_ACTIONS[data]
        style = MENU_STYLES.get(data, "primary")
        user_pending[user.id] = data
        text = (
            f"{emoji} *{to_sc(title)}*\n\n"
            f"✏️ {to_sc(prompt_text)}\n\n"
            f"_{to_sc('Just type your message now...')}_"
            f"{BOT_FOOTER}"
        )
        await query.edit_message_text(
            text, parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                btn(f"🔙 {to_sc('Back to Menu')}", callback_data="menu_back", style=style)
            ]])
        )
        return

    if data == "menu_back":
        try:
            await query.edit_message_text(
                f"✨ *{BOT_NAME}* ✨\n\n"
                f"🤖 {to_sc('Select an option from the menu below')}:"
                f"{BOT_FOOTER}",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=main_menu_keyboard(user.id)
            )
        except Exception:
            pass
        return

    if data == "menu_referral":
        bot_me    = await context.bot.get_me()
        ref_link  = f"https://t.me/{bot_me.username}?start=ref_{user.id}"
        ref_count = get_referral_count(user.id)
        verified  = is_verified(user.id)
        bar       = progress_bar(ref_count, REFERRAL_REQUIRED)
        text = (
            f"👥 *{to_sc('Referral System')}*\n\n"
            f"🔗 *{to_sc('Your Link')}:*\n`{ref_link}`\n\n"
            f"📊 {to_sc('Referrals')}  : *{ref_count}*\n"
            f"🏆 {to_sc('Status')}     : {'✅ ' + to_sc('Unlocked') if verified else '🔒 ' + to_sc('Locked')}\n"
            + (f"📈 {to_sc('Progress')} : `{bar}`\n" if not verified else "")
            + f"\n📣 {to_sc('Share your link to earn referrals!')}"
            f"{BOT_FOOTER}"
        )
        await query.edit_message_text(
            text, parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [btn(f"🔗 {to_sc('Share Link')}",
                     url=f"https://t.me/share/url?url={ref_link}", style="success")],
                [btn(f"🔙 {to_sc('Back')}",
                     callback_data="menu_back",                    style="primary")],
            ])
        )
        return

    if data == "menu_stats":
        u   = get_user(user.id)
        ref = get_referral_count(user.id)
        text = (
            f"📊 *{to_sc('Your Stats')}*\n\n"
            f"👤 {to_sc('Name')}      : {user.full_name}\n"
            f"🆔 {to_sc('ID')}        : `{user.id}`\n"
            f"📅 {to_sc('Joined')}    : {(u['joined_at'] or '')[:10]}\n"
            f"👥 {to_sc('Referrals')} : *{ref}*\n"
            f"🔓 {to_sc('Status')}    : {'✅ ' + to_sc('Verified') if is_verified(user.id) else '🔒 ' + to_sc('Locked')}"
            f"{BOT_FOOTER}"
        )
        await query.edit_message_text(
            text, parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[
                btn(f"🔙 {to_sc('Back')}", callback_data="menu_back", style="primary")
            ]])
        )
        return

    if data == "menu_help":
        text = (
            f"📚 *{to_sc('How to use')} {BOT_NAME}*\n\n"
            f"1️⃣ {to_sc('Select a task from the menu')}\n"
            f"2️⃣ {to_sc('Type your coding question or paste code')}\n"
            f"3️⃣ {to_sc('Get AI-powered results instantly!')}\n\n"
            f"💡 *{to_sc('Supported Languages')}:*\n"
            f"Python • JavaScript • TypeScript • Java\n"
            f"C++ • C# • PHP • Go • Rust • Ruby\n"
            f"Swift • Kotlin • HTML/CSS • SQL • Bash\n\n"
            f"👑 {to_sc('Owner')} : {OWNER_USERNAME}"
            f"{BOT_FOOTER}"
        )
        await query.edit_message_text(
            text, parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [btn(f"👑 {to_sc('Contact Owner')}",
                     url=f"https://t.me/{OWNER_USERNAME.lstrip('@')}", style="danger")],
                [btn(f"🔙 {to_sc('Back')}",
                     callback_data="menu_back",                        style="primary")],
            ])
        )
        return


# ════════════════════════════════════════════
#   MESSAGE HANDLER  (AI code processing)
# ════════════════════════════════════════════

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not await gate_check(update, context):
        return

    text    = update.message.text or ""
    pending = user_pending.get(user.id, "menu_code")
    prefix  = AI_PROMPTS.get(pending, AI_PROMPTS["menu_code"])
    _, title, _ = MENU_ACTIONS.get(pending, ("💻", "Code", ""))

    typing_msg = await update.message.reply_text(
        f"⏳ *{to_sc('Processing your request...')}*\n_{to_sc('AI is thinking, please wait...')}_",
        parse_mode=ParseMode.MARKDOWN
    )

    try:
        full_prompt = (
            f"{prefix}{text}\n\n"
            "Format your response clearly. Use markdown code blocks (``` with language name) for all code."
        )
        response = await asyncio.to_thread(
            lambda: gemini_model.generate_content(full_prompt).text
        )
        user_pending.pop(user.id, None)
        await typing_msg.delete()

        header = f"✅ *{to_sc(title)} — {to_sc('Result')}*\n\n"
        footer = BOT_FOOTER
        MAX    = 4000

        if len(header + response + footer) <= MAX:
            await update.message.reply_text(
                header + response + footer,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=main_menu_keyboard(user.id)
            )
        else:
            await update.message.reply_text(
                header + response[: MAX - len(header)] + "…",
                parse_mode=ParseMode.MARKDOWN
            )
            rest = response[MAX - len(header):]
            while rest:
                chunk, rest = rest[:MAX], rest[MAX:]
                await asyncio.sleep(0.3)
                await update.message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN)
            await update.message.reply_text(
                f"↩️ {to_sc('Back to menu')}{footer}",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=main_menu_keyboard(user.id)
            )
    except Exception as e:
        await typing_msg.delete()
        logger.error(f"Gemini error: {e}")
        await update.message.reply_text(
            f"❌ *{to_sc('An error occurred')}*\n\n"
            f"`{str(e)[:200]}`\n\n"
            f"{to_sc('Please try again or contact')} {OWNER_USERNAME}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=main_menu_keyboard(user.id)
        )


# ════════════════════════════════════════════
#   MAIN
# ════════════════════════════════════════════

def main():
    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",     cmd_start))
    app.add_handler(CommandHandler("help",      cmd_help))
    app.add_handler(CommandHandler("referral",  cmd_referral))
    app.add_handler(CommandHandler("stats",     cmd_stats))
    app.add_handler(CommandHandler("broadcast", cmd_broadcast))
    app.add_handler(CommandHandler("ban",       cmd_ban))
    app.add_handler(CommandHandler("unban",     cmd_unban))
    app.add_handler(CommandHandler("users",     cmd_users))
    app.add_handler(CommandHandler("addref",    cmd_addref))

    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info(f"🤖 {BOT_NAME} is starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
