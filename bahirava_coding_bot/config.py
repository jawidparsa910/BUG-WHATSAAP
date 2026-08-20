import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OWNER_ID = int(os.getenv("OWNER_ID", "8204959327"))
OWNER_USERNAME = os.getenv("OWNER_USERNAME", "@PV_Parwani_4k")
REFERRAL_REQUIRED = 2

CHANNELS = [
    "@freenetking001",
    "@AFG_Hacking_1387",
    "@AFG_HACK_1387",
    "@AFG_Hacking_1387",
    "@AFG_HACK_1387",
]
GROUPS = ["@Dectator_Bug"]
REQUIRED_JOINS = CHANNELS + GROUPS
JOIN_LINKS = {
    "@freenetking001": "https://t.me/freenetking001",
    "@AFG_Hacking_1387": "https://t.me/AFG_Hacking_1387",
    "@AFG_HACK_1387": "https://t.me/AFG_HACK_1387",
    "@Dectator_Bug": "https://t.me/Dectator_Bug",
}
MENU_VIDEO_URL = "https://ar-hosting.pages.dev/1784466462055.mp4"
DB_FILE = os.getenv("DB_FILE", "bahirava_bot.db")
