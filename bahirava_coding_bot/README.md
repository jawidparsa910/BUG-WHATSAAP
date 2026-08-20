# ᗪIᑕTᗩTOᖇ Cᴏᴅɪɴɢ ʙᴏᴛ

**Owner:** @PV_Parwani_4k | **ID:** 8204959327

A full-featured Telegram coding bot powered by Google Gemini AI.

---

## 🚀 Features

- 💻 Generate code in any programming language
- 🐛 Fix bugs & errors automatically
- 📖 Explain code step by step
- ⚡ Optimize code for performance
- 🌐 Convert code between languages
- 📋 Professional code review
- 🔒 Force Join system (3 groups + 4 channels)
- ⏳ Referral system (2 referrals required)
- 👑 Owner panel (broadcast, ban, unban, stats)

---

## ⚙️ Setup Instructions
ل
### Step 1 — Install Python
Make sure Python 3.10+ is installed.

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Get API Keys

**Telegram Bot Token:**
1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow instructions
3. Copy the token

**Gemini AI API Key (FREE):**
1. Go to https://aistudio.google.com/
2. Click "Get API Key" → "Create API Key"
3. Copy the key

### Step 4 — Configure the bot

Open `config.py` and fill in:
```python
BOT_TOKEN      = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
```

### Step 5 — Make the bot admin in your channels/groups

The bot **must be admin** in all these channels/groups to check membership:
- @AFG_Hacking_1387
- @AFG_HACK_1387
-@Afganistan_Clan

### Step 6 — Run the bot
```bash
python bot.py
```

---

## 👑 Owner Commands

| Command | Description |
|---|---|
| `/broadcast <message>` | Send message to all users |
| `/ban <user_id>` | Ban a user |
| `/unban <user_id>` | Unban a user |
| `/users` | Total user count |
| `/addref <user_id>` | Manually verify a user |

---

## 📁 File Structure

```
bahirava_coding_bot/
├── bot.py          — Main bot file
├── config.py       — All configuration
├── database.py     — SQLite database functions
├── utils.py        — Font, force join, helpers
├── requirements.txt
└── README.md
```

---

## 🔒 Referral System

- New users must refer **2 friends** before using the bot
- Each user gets a unique referral link: `https://t.me/YourBot?start=ref_USERID`
- The referrer is notified instantly when someone joins via their link
- Owner can manually verify users with `/addref <user_id>`

---

## ⚠️ Notes

- The bot uses **SQLite** — no external database needed
- Database file `bahirava_bot.db` is created automatically on first run
- To run 24/7, host on a VPS (Ubuntu recommended) or use a free host like Railway/Render

---

*ᗪIᑕTᗩTOᖇ Cᴏᴅɪɴɢ ʙᴏᴛ — Powered by Gemini AI*
