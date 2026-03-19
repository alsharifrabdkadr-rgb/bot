"""
TEO Economy Bot
A full virtual economy bot for Telegram with multi-language support.

HOW TO INSTALL AND RUN:
1. Install Python 3.8+
2. Install requirements: pip install -r requirements.txt
3. Paste your BOT TOKEN below.
4. Run the bot: python bot.py
"""

import sqlite3
import random
import time
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
    ConversationHandler,
)

# --- CONFIGURATION ---
# PASTE YOUR BOT TOKEN HERE
BOT_TOKEN = "8626665643:AAEA70xUxw-7mbabFEsB34xtUqYVfiTOsGs"

# --- CONSTANTS ---
DB_PATH = "database.db"
TEO_TO_EUO = 1000
INITIAL_PRICE = 10.0
REFERRAL_REWARD = 300
DAILY_REWARD_AMOUNT = 200
GUESS_REWARD = 100
QUIZ_REWARD = 150
GROUP_REWARD = 5
LUCK_BOX_XP = 20
GAME_XP = 15
LEVEL_XP_BASE = 100
LEVEL_XP_STEP = 150
DAILY_LOGIN_REWARD = 150
GAME_DAILY_LIMIT = 2

# Conversation States
(
    SELECT_LANG,
    MAIN_MENU_STATE,
    SEND_USER,
    SEND_AMT,
    SEND_CURR,
    CONVERT_AMT,
    MARKET_BUY_AMT,
    MARKET_SELL_AMT,
    BANK_DEP_TEO,
    BANK_WITH_TEO,
    BANK_DEP_EUO,
    BANK_WITH_EUO,
    GUESS_NUM,
    SHOP_MENU,
    LOOT_BOX_MENU,
) = range(15)

# --- MULTI-LANGUAGE SYSTEM ---
STRINGS = {
    "en": {
        "welcome": "Welcome to TEO Economy Bot! Choose your language / اختر لغتك",
        "main_menu": "Main Menu",
        "btn_balance": "💰 Balance",
        "btn_earn": "🎮 Earn EUO",
        "btn_convert": "💱 Convert",
        "btn_market": "📈 Market",
        "btn_bank": "🏦 Bank",
        "btn_invite": "👥 Invite Friends",
        "btn_leaderboard": "🏆 Leaderboard",
        "btn_shop": "🛒 Shop",
        "btn_about": "🤖 About Bot",
        "btn_settings": "⚙ Settings",
        "balance_text": "Your Profile\n\nUsername: @{username}\nTEO: {teo}\nEUO: {euo}\nLevel: {level} ({xp} XP)\nRank: {rank}\nVIP: {vip}\nBadge: {badge}",
        "btn_send_coins": "Send Coins",
        "btn_back": "Back",
        "send_ask_user": "Please enter the username of the person you want to send coins to (e.g. @username):",
        "send_ask_amount": "How much do you want to send?",
        "send_ask_currency": "Which currency? (TEO or EUO)",
        "send_success": "Successfully sent {amount} {currency} to @{username}!",
        "send_usage": "Use /send @username amount currency\nExample: /send @user1 100 EUO",
        "convert_usage": "Use /convert amount currency\nExample: /convert 5 TEO or /convert 2000 EUO",
        "earn_menu": "Earn EUO - Choose a game:",
        "btn_guess": "🎲 Guess Number",
        "btn_wheel": "🎡 Lucky Wheel",
        "btn_daily": "📅 Daily Reward",
        "btn_quiz": "🧠 Quiz",
        "btn_box": "🎁 Daily Box",
        "daily_success": "You've claimed your daily reward of {amount} EUO!",
        "daily_login_reward": "🎁 Daily Login Reward: {amount} EUO",
        "daily_cooldown": "You can claim your next reward in {hours}h {minutes}m.",
        "wheel_win": "You won {amount} EUO from the Lucky Wheel!",
        "game_limit_reached": "⛔ You reached today's limit for this game.",
        "guess_start": "I'm thinking of a number between 1 and 5. Can you guess it?",
        "guess_win": "Correct! You won {amount} EUO!",
        "guess_lose": "Wrong! The number was {number}.",
        "guess_cooldown": "You can play the Guess Number game once every 24 hours.",
        "box_result": "🎁 Daily Box\n\nYou opened the box...\n\nResult: {result}",
        "box_nothing": "You found nothing today.",
        "box_small": "You won {amount} EUO!",
        "box_large": "You won {amount} EUO!",
        "box_rare": "You found {amount} TEO!",
        "box_cooldown": "You can open one box per day.",
        "convert_ask": "How many EUO do you want to convert to TEO? (1000 EUO = 1 TEO)",
        "convert_restriction": "❌ Amount must be a multiple of 1000 EUO.",
        "convert_success": "Successfully converted {euo} EUO to {teo} TEO!",
        "market_menu": "📈 Market\n\nCurrent Price: 1 TEO = {price} EUO\nVolume: {volume} TEO\n\nPrice Chart (last 10 updates)\n{chart}",
        "btn_buy": "🟢 Buy TEO",
        "btn_sell": "🔴 Sell TEO",
        "btn_history": "📉 Market History",
        "market_buy_ask": "How many TEO do you want to buy? (Price: {price} EUO each)",
        "market_sell_ask": "How many TEO do you want to sell? (Price: {price} EUO each)",
        "market_success": "Transaction successful! New balance updated.",
        "bank_menu": "Bank - Secure your coins here.\nYour Bank Balance:\nTEO: {bank_teo}\nEUO: {bank_euo}",
        "btn_dep": "Deposit",
        "btn_with": "Withdraw",
        "bank_dep_ask": "Please type /deposit amount\nExample: /deposit 100",
        "bank_with_ask": "Please type /withdraw amount\nExample: /withdraw 100",
        "bank_success": "Bank transaction successful!",
        "invite_text": "Invite your friends and earn {reward} EUO!\nYour referral link:\n{link}",
        "leaderboard_title": "Global Leaderboard (Top 10 TEO holders)",
        "settings_menu": "Settings - Change your language:",
        "lang_en": "🇬🇧 English",
        "lang_ar": "🇸🇦 العربية",
        "shop_menu": "🛒 Shop\n\nSpend your TEO on exclusive items!",
        "item_vip": "💎 VIP Rank — 5 TEO",
        "item_badge": "Gold Badge — 3 TEO",
        "item_extra_box": "🎁 Extra Daily Box — 2 TEO",
        "item_extra_game": "🎮 Extra Game Attempts — 3 TEO",
        "item_double_reward": "⚡ Double Rewards (limited time) — 4 TEO",
        "item_loot_boxes": "📦 Loot Box Shop",
        "loot_box_menu": "📦 Loot Box Shop\n\nChoose a box to buy with TEO:",
        "box_basic": "🎁 Basic Box — 1 TEO",
        "box_rare": "🎁 Rare Box — 3 TEO",
        "box_epic": "🎁 Epic Box — 5 TEO",
        "shop_success": "Successfully purchased {item}!",
        "btn_euo_teo": "🔄 EUO → TEO",
        "btn_teo_euo": "🔄 TEO → EUO",
        "convert_menu": "Select conversion type:",
        "convert_type_ask": "Type the amount using:\n/convert NUMBER\n\nExample: /convert {example}",
        "market_table_header": "Time     Price",
        "about_text": "TEO Economy Bot is a Telegram economy game where users earn EUO, convert it to TEO, trade in the market, and compete with other users.\n\nFeatures:\n🎮 Games\n📈 Market\n🆙 Levels\n🛒 Shop\n🏦 Bank",
        "insufficient_balance": "Insufficient balance!",
        "user_not_found": "User not found!",
        "invalid_amount": "Invalid amount!",
        "group_active_reward": "You received {amount} EUO for being active in the group!",
        "quiz_q": "Quiz: What is the main currency of this bot?",
        "quiz_win": "Correct! You won {amount} EUO!",
        "quiz_lose": "Wrong answer!",
        "spam_wait": "Please wait a moment before trying again.",
        "level_up": "🆙 LEVEL UP! You reached Level {level} and won {reward}!",
    },
    "ar": {
        "welcome": "مرحبًا بك في بوت TEO Economy! اختر لغتك / Choose your language",
        "main_menu": "القائمة الرئيسية",
        "btn_balance": "💰 الرصيد",
        "btn_earn": "🎮 اربح EUO",
        "btn_convert": "💱 تحويل",
        "btn_market": "📈 السوق",
        "btn_bank": "🏦 البنك",
        "btn_invite": "👥 دعوة الأصدقاء",
        "btn_leaderboard": "🏆 المتصدرون",
        "btn_shop": "🛒 المتجر",
        "btn_about": "🤖 عن البوت",
        "btn_settings": "⚙ الإعدادات",
        "balance_text": "ملفك الشخصي\n\nاسم المستخدم: @{username}\nTEO: {teo}\nEUO: {euo}\nالمستوى: {level} ({xp} XP)\nالرتبة: {rank}\nVIP: {vip}\nشارة: {badge}",
        "btn_send_coins": "إرسال عملات",
        "btn_back": "رجوع",
        "send_ask_user": "يرجى إدخال اسم المستخدم للشخص الذي تريد إرسال العملات إليه (مثال: @username):",
        "send_ask_amount": "كم تريد أن ترسل؟",
        "send_ask_currency": "أي عملة؟ (TEO أو EUO)",
        "send_success": "تم إرسال {amount} {currency} بنجاح إلى @{username}!",
        "send_usage": "استخدم /send @username amount currency\nمثال: /send @user1 100 EUO",
        "convert_usage": "استخدم /convert والمبلغ والعملة\nمثال: /convert 5 TEO أو /convert 2000 EUO",
        "earn_menu": "اربح EUO - اختر لعبة:",
        "btn_guess": "🎲 خمن الرقم",
        "btn_wheel": "🎡 عجلة الحظ",
        "btn_daily": "📅 المكافأة اليومية",
        "btn_quiz": "🧠 اختبار",
        "btn_box": "🎁 صندوق الحظ",
        "daily_success": "لقد حصلت على مكافأتك اليومية البالغة {amount} EUO!",
        "daily_login_reward": "🎁 مكافأة تسجيل الدخول اليومية: {amount} EUO",
        "daily_cooldown": "يمكنك الحصول على مكافأتك التالية خلال {hours} ساعة و {minutes} دقيقة.",
        "wheel_win": "لقد فزت بـ {amount} EUO من عجلة الحظ!",
        "game_limit_reached": "⛔ لقد وصلت إلى الحد اليومي لهذه اللعبة.",
        "guess_start": "أنا أفكر في رقم بين 1 و 5. هل يمكنك تخمينه؟",
        "guess_win": "صحيح! لقد فزت بـ {amount} EUO!",
        "guess_lose": "خطأ! كان الرقم هو {number}.",
        "guess_cooldown": "يمكنك لعب لعبة تخمين الرقم مرة واحدة كل 24 ساعة.",
        "box_result": "🎁 صندوق الحظ اليومي\n\nلقد فتحت الصندوق...\n\nالنتيجة: {result}",
        "box_nothing": "لم تجد شيئاً اليوم.",
        "box_small": "لقد فزت بـ {amount} EUO!",
        "box_large": "لقد فزت بـ {amount} EUO!",
        "box_rare": "لقد وجدت {amount} TEO!",
        "box_cooldown": "يمكنك فتح صندوق واحد في اليوم.",
        "convert_ask": "كم EUO تريد تحويله إلى TEO؟ (1000 EUO = 1 TEO)",
        "convert_restriction": "❌ يجب أن يكون المبلغ من مضاعفات 1000 EUO.",
        "convert_success": "تم تحويل {euo} EUO إلى {teo} TEO بنجاح!",
        "market_menu": "📈 السوق\n\nالسعر الحالي: 1 TEO = {price} EUO\nالحجم: {volume} TEO\n\nمخطط السعر (آخر 10 تحديثات)\n{chart}",
        "btn_buy": "🟢 شراء TEO",
        "btn_sell": "🔴 بيع TEO",
        "btn_history": "📉 سجل السوق",
        "market_buy_ask": "كم TEO تريد شراءه؟ (السعر: {price} EUO للواحد)",
        "market_sell_ask": "كم TEO تريد بيعه؟ (السعر: {price} EUO للواحد)",
        "market_success": "تمت المعاملة بنجاح! تم تحديث الرصيد.",
        "bank_menu": "البنك - حافظ على عملاتك هنا.\nرصيدك في البنك:\nTEO: {bank_teo}\nEUO: {bank_euo}",
        "btn_dep": "إيداع",
        "btn_with": "سحب",
        "bank_dep_ask": "يرجى كتابة /deposit والمبلغ\nمثال: /deposit 100",
        "bank_with_ask": "يرجى كتابة /withdraw والمبلغ\nمثال: /withdraw 100",
        "bank_success": "تمت عملية البنك بنجاح!",
        "invite_text": "ادعُ أصدقاءك واربح {reward} EUO!\nرابط الإحالة الخاص بك:\n{link}",
        "leaderboard_title": "قائمة المتصدرين العالمية (أعلى 10 حاملين لـ TEO)",
        "settings_menu": "الإعدادات - تغيير لغتك:",
        "lang_en": "🇬🇧 English",
        "lang_ar": "🇸🇦 العربية",
        "shop_menu": "🛒 المتجر\n\nأنفق TEO الخاصة بك على عناصر حصرية!",
        "item_vip": "💎 رتبة VIP — 5 TEO",
        "item_badge": "شارة ذهبية — 3 TEO",
        "item_extra_box": "🎁 صندوق يومي إضافي — 2 TEO",
        "item_extra_game": "🎮 محاولات لعبة إضافية — 3 TEO",
        "item_double_reward": "⚡ مكافآت مضاعفة (وقت محدود) — 4 TEO",
        "item_loot_boxes": "📦 متجر صناديق الحظ",
        "loot_box_menu": "📦 متجر صناديق الحظ\n\nاختر صندوقًا لشرائه بـ TEO:",
        "box_basic": "🎁 صندوق أساسي — 1 TEO",
        "box_rare": "🎁 صندوق نادر — 3 TEO",
        "box_epic": "🎁 صندوق أسطوري — 5 TEO",
        "shop_success": "تم شراء {item} بنجاح!",
        "btn_euo_teo": "🔄 EUO → TEO",
        "btn_teo_euo": "🔄 TEO → EUO",
        "convert_menu": "اختر نوع التحويل:",
        "convert_type_ask": "اكتب المبلغ باستخدام:\n/convert NUMBER\n\nمثال: /convert {example}",
        "market_table_header": "الوقت     السعر",
        "about_text": "بوت TEO Economy هو لعبة اقتصادية على تيليجرام حيث يكسب المستخدمون EUO، ويحولونها إلى TEO، ويتداولون في السوق، ويتنافسون مع مستخدمين آخرين.\n\nالمميزات:\n🎮 ألعاب\n📈 سوق\n🆙 مستويات\n🛒 متجر\n🏦 بنك",
        "insufficient_balance": "رصيد غير كافٍ!",
        "user_not_found": "المستخدم غير موجود!",
        "invalid_amount": "مبلغ غير صحيح!",
        "group_active_reward": "لقد حصلت على {amount} EUO لكونك نشطاً في المجموعة!",
        "quiz_q": "اختبار: ما هي العملة الرئيسية لهذا البوت؟",
        "quiz_win": "صحيح! لقد فزت بـ {amount} EUO!",
        "quiz_lose": "إجابة خاطئة!",
        "spam_wait": "يرجى الانتظار لحظة قبل المحاولة مرة أخرى.",
        "level_up": "🆙 مستوى جديد! لقد وصلت إلى المستوى {level} وفزت بـ {reward}!",
    }
}

# --- DATABASE MANAGEMENT ---
class Database:
    def __init__(self, path):
        self.path = path
        self.init_db()

    def get_conn(self):
        return sqlite3.connect(self.path)

    def init_db(self):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE,
                    username TEXT,
                    teo_balance REAL DEFAULT 0,
                    euo_balance REAL DEFAULT 0,
                    bank_teo REAL DEFAULT 0,
                    bank_euo REAL DEFAULT 0,
                    language TEXT DEFAULT 'en',
                    referral_id INTEGER,
                    last_daily_reward TEXT,
                    last_active TEXT,
                    xp REAL DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    last_box_open TEXT,
                    last_game_played TEXT,
                    vip_rank INTEGER DEFAULT 0,
                    gold_badge INTEGER DEFAULT 0,
                    last_login_reward TEXT,
                    daily_game_count INTEGER DEFAULT 0,
                    last_game_reset TEXT,
                    double_reward_until TEXT,
                    extra_box_count INTEGER DEFAULT 0,
                    extra_game_count INTEGER DEFAULT 0
                )
            ''')
            # Check if new columns exist, if not add them
            cursor.execute("PRAGMA table_info(users)")
            columns = [col[1] for col in cursor.fetchall()]
            new_cols = {
                'xp': 'REAL DEFAULT 0',
                'level': 'INTEGER DEFAULT 1',
                'last_box_open': 'TEXT',
                'last_game_played': 'TEXT',
                'vip_rank': 'INTEGER DEFAULT 0',
                'gold_badge': 'INTEGER DEFAULT 0',
                'last_login_reward': 'TEXT',
                'daily_game_count': 'INTEGER DEFAULT 0',
                'last_game_reset': 'TEXT',
                'double_reward_until': 'TEXT',
                'extra_box_count': 'INTEGER DEFAULT 0',
                'extra_game_count': 'INTEGER DEFAULT 0'
            }
            for col, spec in new_cols.items():
                if col not in columns:
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {spec}")

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender_id INTEGER,
                    receiver_id INTEGER,
                    amount REAL,
                    currency TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market (
                    price REAL,
                    volume REAL DEFAULT 0,
                    last_update DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    price REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute("SELECT COUNT(*) FROM market")
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO market (price, volume) VALUES (?, ?)", (INITIAL_PRICE, 0))
            conn.commit()

    def get_user(self, telegram_id):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
            return cursor.fetchone()

    def create_user(self, telegram_id, username, referral_id=None, language='en'):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO users (telegram_id, username, referral_id, language) VALUES (?, ?, ?, ?)",
                (telegram_id, username, referral_id, language)
            )
            conn.commit()

    def update_user(self, telegram_id, **kwargs):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            keys = list(kwargs.keys())
            query = "UPDATE users SET " + ", ".join([f"{k} = ?" for k in keys]) + " WHERE telegram_id = ?"
            cursor.execute(query, [kwargs[k] for k in keys] + [telegram_id])
            conn.commit()

    def get_user_by_username(self, username):
        if username.startswith('@'): username = username[1:]
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            return cursor.fetchone()

    def get_market(self):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM market")
            return cursor.fetchone()

    def update_market(self, price, volume_inc=0):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE market SET price = ?, volume = volume + ?, last_update = CURRENT_TIMESTAMP", (price, volume_inc))
            cursor.execute("INSERT INTO market_history (price) VALUES (?)", (price,))
            conn.commit()

    def get_market_history(self, limit=10):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT price, timestamp FROM market_history ORDER BY timestamp DESC LIMIT ?", (limit,))
            return cursor.fetchall()[::-1]

    def get_24h_change(self):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            now = datetime.now()
            day_ago = now - timedelta(hours=24)
            cursor.execute("SELECT price FROM market_history WHERE timestamp >= ? ORDER BY timestamp ASC LIMIT 1", (day_ago.isoformat(),))
            old_price = cursor.fetchone()
            cursor.execute("SELECT price FROM market_history ORDER BY timestamp DESC LIMIT 1")
            new_price = cursor.fetchone()
            
            if not old_price or not new_price: return 0.0
            if old_price[0] == 0: return 0.0
            return ((new_price[0] - old_price[0]) / old_price[0]) * 100

    def log_transaction(self, sender_id, receiver_id, amount, currency):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO transactions (sender_id, receiver_id, amount, currency) VALUES (?, ?, ?, ?)",
                         (sender_id, receiver_id, amount, currency))
            conn.commit()

    def get_leaderboard(self):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username, teo_balance FROM users ORDER BY teo_balance DESC LIMIT 10")
            return cursor.fetchall()

db = Database(DB_PATH)

# --- UTILS ---
def get_lang(user_id):
    u = db.get_user(user_id)
    return u[7] if u else 'en'

def ensure_user(update: Update):
    user = update.effective_user
    if not user: return None
    db_user = db.get_user(user.id)
    if not db_user:
        db.create_user(user.id, user.username)
        return db.get_user(user.id)
    return db_user

def get_main_keyboard(lang):
    return ReplyKeyboardMarkup([
        [KeyboardButton(STRINGS[lang]["btn_balance"]), KeyboardButton(STRINGS[lang]["btn_earn"])],
        [KeyboardButton(STRINGS[lang]["btn_convert"]), KeyboardButton(STRINGS[lang]["btn_market"])],
        [KeyboardButton(STRINGS[lang]["btn_bank"]), KeyboardButton(STRINGS[lang]["btn_invite"])],
        [KeyboardButton(STRINGS[lang]["btn_shop"]), KeyboardButton(STRINGS[lang]["btn_leaderboard"])],
        [KeyboardButton(STRINGS[lang]["btn_about"]), KeyboardButton(STRINGS[lang]["btn_settings"])]
    ], resize_keyboard=True)

async def add_xp(user_id, amount, context: ContextTypes.DEFAULT_TYPE):
    user = db.get_user(user_id)
    if not user: return
    
    current_xp = user[11] + amount
    current_level = user[12]
    lang = user[7]
    
    # Level up logic
    xp_needed = LEVEL_XP_BASE + (current_level - 1) * LEVEL_XP_STEP
    if current_xp >= xp_needed:
        current_xp -= xp_needed
        current_level += 1
        reward = 500 # Default reward
        db.update_user(user_id, xp=current_xp, level=current_level, euo_balance=user[4] + reward)
        
        # Notify user
        msg = STRINGS[lang]["level_up"].format(level=current_level, reward=f"{reward} EUO")
        await context.bot.send_message(chat_id=user_id, text=msg)
    else:
        db.update_user(user_id, xp=current_xp)

def generate_ascii_chart(history):
    if not history: return "No data yet."
    prices = [row[0] for row in history]
    if len(prices) < 2: return "▂"
    
    # Use ASCII blocks:  ▂▃▄▅▆▇█
    chars = " ▂▃▄▅▆▇█"
    min_p, max_p = min(prices), max(prices)
    range_p = max_p - min_p
    if range_p == 0: return "█" * len(prices)
    
    chart = ""
    for p in prices:
        idx = int(((p - min_p) / range_p) * (len(chars) - 1))
        chart += chars[idx]
    return chart

def get_trend_indicator(change):
    if change > 0.5: return "⬆"
    if change < -0.5: return "⬇"
    return "➡"

def get_user_rank(user_id):
    with db.get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT telegram_id FROM users ORDER BY teo_balance DESC")
        lb = [row[0] for row in cursor.fetchall()]
        try:
            rank = lb.index(user_id) + 1
            return rank
        except ValueError:
            return "N/A"

async def check_game_limit(user_id, lang, query):
    user = db.get_user(user_id)
    now = datetime.now()
    last_reset = user[19] # last_game_reset
    count = user[18] # daily_game_count
    extra_games = user[22] # extra_game_count
    
    if not last_reset or now.date() > datetime.fromisoformat(last_reset).date():
        db.update_user(user_id, daily_game_count=0, last_game_reset=now.isoformat())
        count = 0
    
    if count >= (GAME_DAILY_LIMIT + extra_games):
        await query.answer(STRINGS[lang]["game_limit_reached"], show_alert=True)
        return False
    
    db.update_user(user_id, daily_game_count=count + 1)
    return True

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user: return
    
    # Registration logic integrated into ensure_user
    db_user = ensure_user(update)
    lang = db_user[7]
    
    # Daily Login Reward logic
    now = datetime.now()
    last_login = db_user[17] # last_login_reward column
    can_claim = False
    if not last_login:
        can_claim = True
    else:
        last_date = datetime.fromisoformat(last_login)
        if now.date() > last_date.date():
            can_claim = True
            
    if can_claim:
        db.update_user(user.id, 
                       euo_balance=db_user[4] + DAILY_LOGIN_REWARD, 
                       last_login_reward=now.isoformat())
        await update.message.reply_text(STRINGS[lang]["daily_login_reward"].format(amount=DAILY_LOGIN_REWARD))

    args = context.args
    referral_id = args[0] if args else None
    if referral_id and referral_id.isdigit() and not db_user[8]: # Not already referred
        inviter = db.get_user(int(referral_id))
        if inviter:
            db.update_user(int(referral_id), euo_balance=inviter[4] + REFERRAL_REWARD)
            db.update_user(user.id, referral_id=int(referral_id))
    
    keyboard = [[InlineKeyboardButton("🇬🇧 English", callback_data="l_en")],
                [InlineKeyboardButton("🇸🇦 العربية", callback_data="l_ar")]]
    await update.message.reply_text(STRINGS['en']['welcome'], reply_markup=InlineKeyboardMarkup(keyboard))
    return SELECT_LANG

async def set_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = "en" if query.data == "l_en" else "ar"
    db.update_user(update.effective_user.id, language=lang)
    await query.message.reply_text(STRINGS[lang]["main_menu"], reply_markup=get_main_keyboard(lang))
    return MAIN_MENU_STATE

async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    user = ensure_user(update)
    if not user: return
    lang = user[7]
    
    if text == STRINGS[lang]["btn_balance"]:
        kb = [[InlineKeyboardButton(STRINGS[lang]["btn_send_coins"], callback_data="send")],
              [InlineKeyboardButton(STRINGS[lang]["btn_back"], callback_data="back")]]
        vip_status = "Yes" if user[15] else "No"
        badge_status = "Gold" if user[16] else "None"
        rank = get_user_rank(user_id)
        await update.message.reply_text(STRINGS[lang]["balance_text"].format(
            username=user[2], teo=user[3], euo=user[4], level=user[12], xp=int(user[11]), rank=rank, vip=vip_status, badge=badge_status
        ), reply_markup=InlineKeyboardMarkup(kb))
    elif text == STRINGS[lang]["btn_earn"]:
        kb = [[InlineKeyboardButton(STRINGS[lang]["btn_guess"], callback_data="e_guess"), InlineKeyboardButton(STRINGS[lang]["btn_wheel"], callback_data="e_wheel")],
              [InlineKeyboardButton(STRINGS[lang]["btn_daily"], callback_data="e_daily"), InlineKeyboardButton(STRINGS[lang]["btn_quiz"], callback_data="e_quiz")],
              [InlineKeyboardButton(STRINGS[lang]["btn_box"], callback_data="e_box")]]
        await update.message.reply_text(STRINGS[lang]["earn_menu"], reply_markup=InlineKeyboardMarkup(kb))
    elif text == STRINGS[lang]["btn_convert"]:
        kb = [[InlineKeyboardButton(STRINGS[lang]["btn_euo_teo"], callback_data="c_euo_teo")],
              [InlineKeyboardButton(STRINGS[lang]["btn_teo_euo"], callback_data="c_teo_euo")],
              [InlineKeyboardButton(STRINGS[lang]["btn_back"], callback_data="back")]]
        await update.message.reply_text(STRINGS[lang]["convert_menu"], reply_markup=InlineKeyboardMarkup(kb))
    elif text == STRINGS[lang]["btn_market"]:
        m = db.get_market()
        history = db.get_market_history(5) # Get last 5 for the table
        chart_history = db.get_market_history(10) # Get last 10 for the graph
        chart = generate_ascii_chart(chart_history)
        change = db.get_24h_change()
        trend = get_trend_indicator(change)
        
        # Build history table
        table = f"{STRINGS[lang]['market_table_header']}\n"
        for p, ts in history:
            time_str = datetime.fromisoformat(ts).strftime("%H:%M")
            table += f"{time_str}    {p} EUO\n"
            
        market_text = (
            f"📈 TEO Market\n\n"
            f"**Current Price**\n\n"
            f"1 TEO = {m[0]} EUO\n\n"
            f"--- \n\n"
            f"{table}\n"
            f"--- \n\n"
            f"**Price Trend**\n\n"
            f"{chart}\n\n"
            f"24h Change: {change:+.2f}% {trend}\n"
            f"Volume: {m[1]} TEO"
        )
        
        kb = [[InlineKeyboardButton(STRINGS[lang]["btn_buy"], callback_data="m_buy"), InlineKeyboardButton(STRINGS[lang]["btn_sell"], callback_data="m_sell")],
              [InlineKeyboardButton(STRINGS[lang]["btn_history"], callback_data="m_history")],
              [InlineKeyboardButton(STRINGS[lang]["btn_back"], callback_data="back")]]
        await update.message.reply_text(market_text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
    elif text == STRINGS[lang]["btn_bank"]:
        kb = [[InlineKeyboardButton(STRINGS[lang]["btn_dep"], callback_data="b_dep"), InlineKeyboardButton(STRINGS[lang]["btn_with"], callback_data="b_with")]]
        await update.message.reply_text(STRINGS[lang]["bank_menu"].format(bank_teo=user[5], bank_euo=user[6]), reply_markup=InlineKeyboardMarkup(kb))
    elif text == STRINGS[lang]["btn_invite"]:
        bot = await context.bot.get_me()
        link = f"https://t.me/{bot.username}?start={user_id}"
        await update.message.reply_text(STRINGS[lang]["invite_text"].format(reward=REFERRAL_REWARD, link=link))
    elif text == STRINGS[lang]["btn_leaderboard"]:
        lb = db.get_leaderboard()
        txt = f"🏆 {STRINGS[lang]['leaderboard_title']}\n\n"
        count = 1
        for u, t in lb:
            if u:
                txt += f"{count}. @{u} — {t} TEO\n"
                count += 1
        await update.message.reply_text(txt)
    elif text == STRINGS[lang]["btn_shop"]:
        kb = [[InlineKeyboardButton(STRINGS[lang]["item_vip"], callback_data="s_vip")],
              [InlineKeyboardButton(STRINGS[lang]["item_extra_game"], callback_data="s_game"), InlineKeyboardButton(STRINGS[lang]["item_extra_box"], callback_data="s_box")],
              [InlineKeyboardButton(STRINGS[lang]["item_double_reward"], callback_data="s_double")],
              [InlineKeyboardButton(STRINGS[lang]["item_loot_boxes"], callback_data="s_loot_boxes")],
              [InlineKeyboardButton(STRINGS[lang]["btn_back"], callback_data="back")]]
        await update.message.reply_text(STRINGS[lang]["shop_menu"], reply_markup=InlineKeyboardMarkup(kb))
    elif text == STRINGS[lang]["btn_about"]:
        await update.message.reply_text(STRINGS[lang]["about_text"])
    elif text == STRINGS[lang]["btn_settings"]:
        kb = [[InlineKeyboardButton("🇬🇧 English", callback_data="l_en")], [InlineKeyboardButton("🇸🇦 العربية", callback_data="l_ar")]]
        await update.message.reply_text(STRINGS[lang]["settings_menu"], reply_markup=InlineKeyboardMarkup(kb))
    
    # XP for using the bot
    await add_xp(user_id, 1, context)
    
    # Group Activity Reward
    if update.effective_chat.type in ['group', 'supergroup']:
        now = datetime.now()
        last_active = datetime.fromisoformat(user[10]) if user[10] else now - timedelta(minutes=10)
        if now > last_active + timedelta(minutes=5):
            db.update_user(user_id, euo_balance=user[4] + GROUP_REWARD, last_active=now.isoformat())
            # Optionally notify user
    
    return MAIN_MENU_STATE

# --- GAME CALLBACKS ---
async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = update.effective_user.id
    user = ensure_user(update)
    if not user: return
    lang = user[7]

    if data.startswith("l_"):
        new_lang = data.split("_")[1]
        db.update_user(user_id, language=new_lang)
        await query.message.reply_text(STRINGS[new_lang]["main_menu"], reply_markup=get_main_keyboard(new_lang))
        return MAIN_MENU_STATE
    elif data == "e_daily":
        last = user[9]
        now = datetime.now()
        if last and now < datetime.fromisoformat(last) + timedelta(hours=24):
            diff = (datetime.fromisoformat(last) + timedelta(hours=24)) - now
            h, r = divmod(int(diff.total_seconds()), 3600)
            m, _ = divmod(r, 60)
            await query.answer(STRINGS[lang]["daily_cooldown"].format(hours=h, minutes=m), show_alert=True)
        else:
            db.update_user(user_id, euo_balance=user[4] + DAILY_REWARD_AMOUNT, last_daily_reward=now.isoformat())
            await query.message.reply_text(STRINGS[lang]["daily_success"].format(amount=DAILY_REWARD_AMOUNT))
            await add_xp(user_id, 10, context)
    elif data == "e_wheel":
        if not await check_game_limit(user_id, lang, query): return
        
        res = random.random()
        if res < 0.50: # 50% Lose
            win = 0
            await query.message.reply_text("🎡 " + STRINGS[lang]["box_nothing"])
        elif res < 0.80: # 30% Small (50-150)
            win = random.randint(50, 150)
            result_key = "box_small"
        elif res < 0.95: # 15% Medium (200-500)
            win = random.randint(200, 500)
            result_key = "box_large"
        else: # 5% Big (1000-2000)
            win = random.randint(1000, 2000)
            result_key = "box_large"

        if win > 0:
            # Double reward check
            if user[20] and datetime.now() < datetime.fromisoformat(user[20]):
                win *= 2
            db.update_user(user_id, euo_balance=user[4] + win)
            await query.message.reply_text(STRINGS[lang]["wheel_win"].format(amount=win))
            await add_xp(user_id, 5, context)
            
    elif data == "e_guess":
        if not await check_game_limit(user_id, lang, query): return
        
        kb = [[InlineKeyboardButton(str(i), callback_data=f"g_{i}") for i in range(1, 6)]]
        await query.message.reply_text(STRINGS[lang]["guess_start"], reply_markup=InlineKeyboardMarkup(kb))
        context.user_data['guess_num'] = random.randint(1, 5)
    elif data.startswith("g_"):
        guess = int(data.split("_")[1])
        correct = context.user_data.get('guess_num')
        if not correct: return
        
        now = datetime.now()
        db.update_user(user_id, last_game_played=now.isoformat())
        
        if guess == correct:
            win = GUESS_REWARD
            if user[20] and datetime.now() < datetime.fromisoformat(user[20]):
                win *= 2
            db.update_user(user_id, euo_balance=user[4] + win)
            await query.message.edit_text(STRINGS[lang]["guess_win"].format(amount=win))
            await add_xp(user_id, GAME_XP, context)
        else:
            await query.message.edit_text(STRINGS[lang]["guess_lose"].format(number=correct))
        context.user_data['guess_num'] = None
    elif data == "e_box":
        last = user[13]
        now = datetime.now()
        extra_boxes = user[21] # extra_box_count
        
        # Check if they have an extra box they can use if the daily is on cooldown
        can_open = False
        if not last or now >= datetime.fromisoformat(last) + timedelta(hours=24):
            can_open = True
        elif extra_boxes > 0:
            can_open = True
            db.update_user(user_id, extra_box_count=extra_boxes - 1)
        
        if not can_open:
            await query.answer(STRINGS[lang]["box_cooldown"], show_alert=True)
            return
        
        res_val = random.random()
        # Adjusting to requested Luck System: Lose 50%, Small 30%, Medium 15%, Big 5%
        if res_val < 0.50: # 50% nothing
            result = STRINGS[lang]["box_nothing"]
        elif res_val < 0.80: # 30% small EUO
            amt = random.randint(50, 200)
            if user[20] and datetime.now() < datetime.fromisoformat(user[20]): amt *= 2
            db.update_user(user_id, euo_balance=user[4] + amt)
            result = STRINGS[lang]["box_small"].format(amount=amt)
        elif res_val < 0.95: # 15% medium EUO
            amt = random.randint(300, 1000)
            if user[20] and datetime.now() < datetime.fromisoformat(user[20]): amt *= 2
            db.update_user(user_id, euo_balance=user[4] + amt)
            result = STRINGS[lang]["box_large"].format(amount=amt)
        else: # 5% big (TEO)
            amt = random.randint(1, 3)
            db.update_user(user_id, teo_balance=user[3] + amt)
            result = STRINGS[lang]["box_rare"].format(amount=amt)
            
        db.update_user(user_id, last_box_open=now.isoformat())
        await query.message.reply_text(STRINGS[lang]["box_result"].format(result=result))
        await add_xp(user_id, LUCK_BOX_XP, context)
    elif data == "e_quiz":
        if not await check_game_limit(user_id, lang, query): return
        kb = [[InlineKeyboardButton("TEO", callback_data="q_win"), InlineKeyboardButton("EUO", callback_data="q_lose")]]
        await query.message.reply_text(STRINGS[lang]["quiz_q"], reply_markup=InlineKeyboardMarkup(kb))
    elif data == "q_win":
        win = QUIZ_REWARD
        if user[20] and datetime.now() < datetime.fromisoformat(user[20]):
            win *= 2
        db.update_user(user_id, euo_balance=user[4] + win)
        await query.message.edit_text(STRINGS[lang]["quiz_win"].format(amount=win))
        await add_xp(user_id, 10, context)
    elif data == "q_lose":
        await query.message.edit_text(STRINGS[lang]["quiz_lose"])
    elif data == "send":
        await query.message.reply_text(STRINGS[lang]["send_usage"])
    elif data == "m_buy":
        await query.message.reply_text(STRINGS[lang]["market_buy_ask"].format(price=db.get_market()[0]))
        return MARKET_BUY_AMT
    elif data == "m_sell":
        await query.message.reply_text(STRINGS[lang]["market_sell_ask"].format(price=db.get_market()[0]))
        return MARKET_SELL_AMT
    elif data == "m_history":
        history = db.get_market_history(15)
        txt = "📊 Market History\n\n"
        for p, ts in history:
            dt = datetime.fromisoformat(ts).strftime("%H:%M:%S")
            txt += f"• {dt} - {p} EUO\n"
        await query.message.reply_text(txt)
    elif data == "c_euo_teo":
        context.user_data['conv_mode'] = 'euo_teo'
        await query.message.reply_text(STRINGS[lang]["convert_type_ask"].format(example="2000"))
    elif data == "c_teo_euo":
        context.user_data['conv_mode'] = 'teo_euo'
        await query.message.reply_text(STRINGS[lang]["convert_type_ask"].format(example="2"))
    elif data == "b_dep":
        await query.message.reply_text(STRINGS[lang]["bank_dep_ask"])
    elif data == "b_with":
        await query.message.reply_text(STRINGS[lang]["bank_with_ask"])
    elif data == "s_loot_boxes":
        kb = [[InlineKeyboardButton(STRINGS[lang]["box_basic"], callback_data="lb_basic")],
              [InlineKeyboardButton(STRINGS[lang]["box_rare"], callback_data="lb_rare")],
              [InlineKeyboardButton(STRINGS[lang]["box_epic"], callback_data="lb_epic")],
              [InlineKeyboardButton(STRINGS[lang]["btn_back"], callback_data="back_shop")]]
        await query.message.edit_text(STRINGS[lang]["loot_box_menu"], reply_markup=InlineKeyboardMarkup(kb))
    elif data.startswith("lb_"):
        box_type = data.split("_")[1]
        costs = {"basic": 1, "rare": 3, "epic": 5}
        cost = costs[box_type]
        if user[3] >= cost:
            db.update_user(user_id, teo_balance=user[3] - cost)
            
            # Box rewards logic
            res = random.random()
            # Basic: nothing (60%), small EUO (30%), med EUO (10%)
            # Rare: nothing (30%), med EUO (50%), large EUO (15%), rare TEO (5%)
            # Epic: med EUO (40%), large EUO (40%), TEO (20%)
            
            reward_txt = ""
            if box_type == "basic":
                if res < 0.6: reward_txt = STRINGS[lang]["box_nothing"]
                elif res < 0.9: 
                    amt = random.randint(100, 500)
                    db.update_user(user_id, euo_balance=user[4] + amt)
                    reward_txt = STRINGS[lang]["box_small"].format(amount=amt)
                else:
                    amt = random.randint(600, 1500)
                    db.update_user(user_id, euo_balance=user[4] + amt)
                    reward_txt = STRINGS[lang]["box_large"].format(amount=amt)
            elif box_type == "rare":
                if res < 0.3: reward_txt = STRINGS[lang]["box_nothing"]
                elif res < 0.8:
                    amt = random.randint(1000, 3000)
                    db.update_user(user_id, euo_balance=user[4] + amt)
                    reward_txt = STRINGS[lang]["box_large"].format(amount=amt)
                elif res < 0.95:
                    amt = random.randint(4000, 8000)
                    db.update_user(user_id, euo_balance=user[4] + amt)
                    reward_txt = STRINGS[lang]["box_large"].format(amount=amt)
                else:
                    amt = random.randint(2, 5)
                    db.update_user(user_id, teo_balance=user[3] + amt)
                    reward_txt = STRINGS[lang]["box_rare"].format(amount=amt)
            elif box_type == "epic":
                if res < 0.4:
                    amt = random.randint(5000, 10000)
                    db.update_user(user_id, euo_balance=user[4] + amt)
                    reward_txt = STRINGS[lang]["box_large"].format(amount=amt)
                elif res < 0.8:
                    amt = random.randint(11000, 25000)
                    db.update_user(user_id, euo_balance=user[4] + amt)
                    reward_txt = STRINGS[lang]["box_large"].format(amount=amt)
                else:
                    amt = random.randint(6, 15)
                    db.update_user(user_id, teo_balance=user[3] + amt)
                    reward_txt = STRINGS[lang]["box_rare"].format(amount=amt)
            
            await query.message.reply_text(STRINGS[lang]["box_result"].format(result=reward_txt))
            await add_xp(user_id, 100, context)
        else:
            await query.answer(STRINGS[lang]["insufficient_balance"], show_alert=True)
            
    elif data.startswith("s_"):
        item = data.split("_")[1]
        cost = {"vip": 5, "badge": 3, "box": 2, "game": 3, "double": 4}[item]
        if user[3] >= cost:
            db.update_user(user_id, teo_balance=user[3] - cost)
            if item == "vip": db.update_user(user_id, vip_rank=1)
            elif item == "badge": db.update_user(user_id, gold_badge=1)
            elif item == "box": db.update_user(user_id, extra_box_count=user[21] + 1)
            elif item == "game": db.update_user(user_id, extra_game_count=user[22] + 1)
            elif item == "double":
                until = datetime.now() + timedelta(hours=2)
                db.update_user(user_id, double_reward_until=until.isoformat())
            
            await query.message.reply_text(STRINGS[lang]["shop_success"].format(item=STRINGS[lang][f"item_{item}"]))
            await add_xp(user_id, 50, context)
        else:
            await query.answer(STRINGS[lang]["insufficient_balance"], show_alert=True)
    elif data == "back_shop":
        # Return to shop menu
        kb = [[InlineKeyboardButton(STRINGS[lang]["item_vip"], callback_data="s_vip")],
              [InlineKeyboardButton(STRINGS[lang]["item_extra_game"], callback_data="s_game"), InlineKeyboardButton(STRINGS[lang]["item_extra_box"], callback_data="s_box")],
              [InlineKeyboardButton(STRINGS[lang]["item_double_reward"], callback_data="s_double")],
              [InlineKeyboardButton(STRINGS[lang]["item_loot_boxes"], callback_data="s_loot_boxes")],
              [InlineKeyboardButton(STRINGS[lang]["btn_back"], callback_data="back")]]
        await query.message.edit_text(STRINGS[lang]["shop_menu"], reply_markup=InlineKeyboardMarkup(kb))
    elif data == "back":
        await query.message.reply_text(STRINGS[lang]["main_menu"], reply_markup=get_main_keyboard(lang))
        return MAIN_MENU_STATE

async def send_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_lang(user_id)
    args = context.args
    if len(args) < 3:
        await update.message.reply_text(STRINGS[lang]["send_usage"])
        return

    target_username = args[0]
    try:
        amount = float(args[1])
        currency = args[2].upper()
    except ValueError:
        await update.message.reply_text(STRINGS[lang]["invalid_amount"])
        return

    if currency not in ["TEO", "EUO"]:
        await update.message.reply_text(STRINGS[lang]["send_usage"])
        return

    target = db.get_user_by_username(target_username)
    if not target:
        await update.message.reply_text(STRINGS[lang]["user_not_found"])
        return

    user = ensure_user(update)
    if not user: return
    
    bal_idx = 3 if currency == "TEO" else 4
    if user[bal_idx] >= amount:
        db.update_user(user_id, **{('teo_balance' if currency == "TEO" else 'euo_balance'): user[bal_idx] - amount})
        db.update_user(target[1], **{('teo_balance' if currency == "TEO" else 'euo_balance'): target[bal_idx] + amount})
        db.log_transaction(user_id, target[1], amount, currency)
        await update.message.reply_text(STRINGS[lang]["send_success"].format(amount=amount, currency=currency, username=target[2]))
        await add_xp(user_id, 5, context)
    else:
        await update.message.reply_text(STRINGS[lang]["insufficient_balance"])

async def convert_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_lang(user_id)
    if not context.args:
        await update.message.reply_text(STRINGS[lang]["convert_usage"])
        return
    
    try:
        amount = float(context.args[0])
    except (ValueError, IndexError):
        await update.message.reply_text(STRINGS[lang]["invalid_amount"])
        return

    user = ensure_user(update)
    if not user: return
    
    mode = context.user_data.get('conv_mode')
    
    # If no mode selected via buttons, try to detect based on second arg if present
    if not mode and len(context.args) > 1:
        curr = context.args[1].upper()
        if curr == "TEO": mode = "teo_euo"
        elif curr == "EUO": mode = "euo_teo"

    if mode == "teo_euo":
        if user[3] >= amount:
            euo_gain = amount * TEO_TO_EUO
            db.update_user(user_id, teo_balance=user[3] - amount, euo_balance=user[4] + euo_gain)
            await update.message.reply_text(STRINGS[lang]["convert_success"].format(euo=euo_gain, teo=amount))
            await add_xp(user_id, 5, context)
        else:
            await update.message.reply_text(STRINGS[lang]["insufficient_balance"])
    elif mode == "euo_teo":
        if amount % 1000 != 0:
            await update.message.reply_text(STRINGS[lang]["convert_restriction"])
            return
            
        if user[4] >= amount:
            teo_gain = amount / TEO_TO_EUO
            db.update_user(user_id, euo_balance=user[4] - amount, teo_balance=user[3] + teo_gain)
            await update.message.reply_text(STRINGS[lang]["convert_success"].format(euo=amount, teo=teo_gain))
            await add_xp(user_id, 5, context)
        else:
            await update.message.reply_text(STRINGS[lang]["insufficient_balance"])
    else:
        # Fallback to auto-detection if no mode and no currency arg
        if amount >= 100: # Assume EUO -> TEO
            if amount % 1000 != 0:
                await update.message.reply_text(STRINGS[lang]["convert_restriction"])
                return
                
            if user[4] >= amount:
                teo_gain = amount / TEO_TO_EUO
                db.update_user(user_id, euo_balance=user[4] - amount, teo_balance=user[3] + teo_gain)
                await update.message.reply_text(STRINGS[lang]["convert_success"].format(euo=amount, teo=teo_gain))
                await add_xp(user_id, 5, context)
            else: await update.message.reply_text(STRINGS[lang]["insufficient_balance"])
        else: # Assume TEO -> EUO
            if user[3] >= amount:
                euo_gain = amount * TEO_TO_EUO
                db.update_user(user_id, teo_balance=user[3] - amount, euo_balance=user[4] + euo_gain)
                await update.message.reply_text(STRINGS[lang]["convert_success"].format(euo=euo_gain, teo=amount))
                await add_xp(user_id, 5, context)
            else: await update.message.reply_text(STRINGS[lang]["insufficient_balance"])

async def deposit_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_lang(user_id)
    if not context.args:
        await update.message.reply_text(STRINGS[lang]["bank_dep_ask"])
        return
    
    try:
        amount = float(context.args[0])
    except ValueError:
        await update.message.reply_text(STRINGS[lang]["invalid_amount"])
        return

    user = ensure_user(update)
    if not user: return
    
    currency = "EUO"
    if len(context.args) > 1:
        currency = context.args[1].upper()
    
    bal_idx = 3 if currency == "TEO" else 4
    bank_idx = 5 if currency == "TEO" else 6
    
    if user[bal_idx] >= amount:
        db.update_user(user_id, **{
            ('teo_balance' if currency == "TEO" else 'euo_balance'): user[bal_idx] - amount,
            ('bank_teo' if currency == "TEO" else 'bank_euo'): user[bank_idx] + amount
        })
        await update.message.reply_text(STRINGS[lang]["bank_success"])
        await add_xp(user_id, 2, context)
    else:
        await update.message.reply_text(STRINGS[lang]["insufficient_balance"])

async def withdraw_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_lang(user_id)
    if not context.args:
        await update.message.reply_text(STRINGS[lang]["bank_with_ask"])
        return
    
    try:
        amount = float(context.args[0])
    except ValueError:
        await update.message.reply_text(STRINGS[lang]["invalid_amount"])
        return

    currency = "EUO"
    if len(context.args) > 1:
        currency = context.args[1].upper()
        
    user = ensure_user(update)
    if not user: return
    
    bal_idx = 3 if currency == "TEO" else 4
    bank_idx = 5 if currency == "TEO" else 6
    
    if user[bank_idx] >= amount:
        db.update_user(user_id, **{
            ('bank_teo' if currency == "TEO" else 'bank_euo'): user[bank_idx] - amount,
            ('teo_balance' if currency == "TEO" else 'euo_balance'): user[bal_idx] + amount
        })
        await update.message.reply_text(STRINGS[lang]["bank_success"])
        await add_xp(user_id, 2, context)
    else:
        await update.message.reply_text(STRINGS[lang]["insufficient_balance"])

# --- CONVERSATION STEPS ---
async def conv_convert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amt = float(update.message.text)
        user = db.get_user(update.effective_user.id)
        lang = user[7]
        if amt > 0 and user[4] >= amt:
            teo = amt / TEO_TO_EUO
            db.update_user(user[1], euo_balance=user[4] - amt, teo_balance=user[3] + teo)
            await update.message.reply_text(STRINGS[lang]["convert_success"].format(euo=amt, teo=teo))
        else: await update.message.reply_text(STRINGS[lang]["insufficient_balance"])
    except: pass
    return MAIN_MENU_STATE

async def conv_market(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amt = float(update.message.text)
        user = db.get_user(update.effective_user.id)
        lang = user[7]
        m = db.get_market()
        price = m[0]
        state = context.user_data.get('state') # We'll set this manually
        
        is_buy = context.user_data.get('market_mode') == 'buy'
        cost = amt * price if is_buy else amt
        
        if is_buy:
            if user[4] >= cost:
                db.update_user(user[1], euo_balance=user[4] - cost, teo_balance=user[3] + amt)
                new_price = price * (1 + (amt / 1000)) # Simple demand algorithm
                db.update_market(new_price, volume_inc=amt)
                await update.message.reply_text(STRINGS[lang]["market_success"])
            else: await update.message.reply_text(STRINGS[lang]["insufficient_balance"])
        else:
            if user[3] >= amt:
                gain = amt * price
                db.update_user(user[1], teo_balance=user[3] - amt, euo_balance=user[4] + gain)
                new_price = price * (1 - (amt / 1000))
                db.update_market(max(0.1, new_price), volume_inc=amt)
                await update.message.reply_text(STRINGS[lang]["market_success"])
            else: await update.message.reply_text(STRINGS[lang]["insufficient_balance"])
    except: pass
    return MAIN_MENU_STATE

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"Exception while handling an update: {context.error}")

def main():
    if BOT_TOKEN == "PASTE_YOUR_BOT_TOKEN_HERE":
        print("Please set your BOT_TOKEN in bot.py")
        return

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_error_handler(error_handler)

    # Command Handlers
    app.add_handler(CommandHandler("send", send_cmd))
    app.add_handler(CommandHandler("convert", convert_cmd))
    app.add_handler(CommandHandler("deposit", deposit_cmd))
    app.add_handler(CommandHandler("withdraw", withdraw_cmd))

    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu),
            CallbackQueryHandler(callbacks)
        ],
        states={
            SELECT_LANG: [CallbackQueryHandler(set_lang, pattern="^l_"), CallbackQueryHandler(callbacks)],
            MAIN_MENU_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu), CallbackQueryHandler(callbacks)],
            CONVERT_AMT: [MessageHandler(filters.TEXT & ~filters.COMMAND, conv_convert), CallbackQueryHandler(callbacks)],
            MARKET_BUY_AMT: [MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: (c.user_data.update({'market_mode': 'buy'}), conv_market(u, c))), CallbackQueryHandler(callbacks)],
            MARKET_SELL_AMT: [MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: (c.user_data.update({'market_mode': 'sell'}), conv_market(u, c))), CallbackQueryHandler(callbacks)],
        },
        fallbacks=[CommandHandler("start", start)],
        allow_reentry=True
    )

    app.add_handler(conv)
    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
