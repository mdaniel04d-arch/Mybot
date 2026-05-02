#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
𝐑𝐃𝐍𝐎 𝐌𝐗 Telegram Bot
Версия: 4.0 (Полностью исправленная)
"""

import os
import sys
import random
import sqlite3
import asyncio
import json
import time
import logging
import re
import hashlib
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple, Any, Union

# ============ Python 3.13 үчүн атайын оңдоолор ============
import struct

class imghdr:
    """imghdr модулун имитациялоо"""
    @staticmethod
    def what(file, h=None):
        """Файлдын сүрөт түрүн аныктоо"""
        return None

import urllib3

if not hasattr(urllib3, 'contrib'):
    urllib3.contrib = type('contrib', (), {})()

if not hasattr(urllib3.contrib, 'appengine'):
    class DummyAppEngine:
        def __getattr__(self, name):
            return None
        def __call__(self, *args, **kwargs):
            return None
    urllib3.contrib.appengine = DummyAppEngine()

sys.modules['imghdr'] = imghdr

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ChatMember, LabeledPrice
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, PreCheckoutQueryHandler
    from telegram.constants import ParseMode
    print("✅ telegram библиотекасы ийгиликтүү жүктөлдү!")
except ImportError as e:
    print("=" * 60)
    print("❌ КАТА: python-telegram-bot орнотулган эмес!")
    print("=" * 60)
    print("Орнотуу үчүн:")
    print("pip install python-telegram-bot==20.3")
    print("pip install aiohttp")
    print("=" * 60)
    print(f"Толук ката: {e}")
    sys.exit(1)

# ============ КОНФИГУРАЦИЯ ============
BOT_TOKEN = "8709879213:AAHVwPjYnmcFGONU3isl2dNnEI5Sp8QZ5qA"
ADMIN_ID = 8337481127  # Башкы админ
ADMIN_IDS = [8337481127, 7986506810, 7976776305]
ADMIN_USERNAME = "@MX_KASSA"
CHANNELS = []

def is_super_admin(user_id: int) -> bool:
    """Колдонуучу админ экенин текшер"""
    return user_id in ADMIN_IDS

DONATE_LINK = "https://t.me/MX_KASSA"
NEWS_CHANNEL = "https://t.me/MX_KASSA"
KASSA_CHANNEL = "https://t.me/MX_KASSA"

DATABASE_NAME = "rdno.db"
INITIAL_BALANCE = 5000
REFERRAL_BONUS = 1000
MIN_BET = 1
MIN_BANDIT_BET = 1
ROULETTE_LIMIT = 999999999
TRANSFER_COOLDOWN_HOURS = 6
TRANSFER_DAILY_LIMIT = 1000000

PROVIDER_TOKEN = ""

WEBAPP_URL = "https://t.me/VIPKGZ777"
API_SECRET_KEY = "squidgames_super_secret_key_2024"

GIF_URL = "https://islomav4.beget.tech/giphy.mp4"

CHANNEL_LINKS = [
    "https://t.me/MX_KASSA", "https://t.me/MX_KASSA", "https://t.me/MX_KASSA",
    "https://t.me/MX_KASSA", "https://t.me/MX_KASSA", "https://t.me/MX_KASSA",
    "https://t.me/MX_KASSA", "https://t.me/MX_KASSA", "https://t.me/MX_KASSA",
    "https://t.me/MX_KASSA", "https://t.me/MX_KASSA", "https://t.me/MX_KASSA",
    "https://t.me/MX_KASSA", "https://t.me/MX_KASSA", "https://t.me/MX_KASSA",
    "https://t.me/MX_KASSA", "https://t.me/MX_KASSA", "https://t.me/MX_KASSA",
    "https://t.me/MX_KASSA", "https://t.me/MX_KASSA", "https://t.me/MX_KASSA",
    "https://t.me/MX_KASSA", "https://t.me/MX_KASSA", "https://t.me/MX_KASSA",
    "https://t.me/MX_KASSA", "https://t.me/MX_KASSA", "https://t.me/MX_KASSA",
    "https://t.me/MX_KASSA", "https://t.me/MX_KASSA", "https://t.me/MX_KASSA"
]

CHANNEL_NAMES = [
    "Канал 1", "Канал 2", "Канал 3", "Канал 4", "Канал 5", "Канал 6", "Канал 7", "Канал 8", "Канал 9", "Канал 10",
    "Канал 11", "Канал 12", "Канал 13", "Канал 14", "Канал 15", "Канал 16", "Канал 17", "Канал 18", "Канал 19", "Канал 20",
    "Канал 21", "Канал 22", "Канал 23", "Канал 24", "Канал 25", "Канал 26", "Канал 27", "Канал 28", "Канал 29", "Канал 30"
]

SLOT_GAMES = {}

# ========================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class WebAppSync:
    def __init__(self):
        self.sync_url = "https://islomalievanvarbek6-hub.github.io/squidgames-bot/api/sync"
        self.pending_updates = defaultdict(list)

    async def send_balance_update(self, user_id: int, new_balance: int) -> bool:
        try:
            data = {
                "user_id": user_id,
                "balance": new_balance,
                "timestamp": datetime.now().isoformat(),
                "secret": hashlib.md5(f"{user_id}{new_balance}{API_SECRET_KEY}".encode()).hexdigest()
            }

            sync_dir = "sync_data"
            os.makedirs(sync_dir, exist_ok=True)

            filename = f"{sync_dir}/user_{user_id}.json"
            with open(filename, "w", encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info(f"Баланс синхронизирован: user {user_id} -> {new_balance}")
            return True
        except Exception as e:
            logger.error(f"Ошибка синхронизации: {e}")
            return False

    async def get_web_balance(self, user_id: int) -> Optional[int]:
        try:
            sync_dir = "sync_data"
            filename = f"{sync_dir}/web_user_{user_id}.json"

            if os.path.exists(filename):
                with open(filename, "r", encoding='utf-8') as f:
                    data = json.load(f)

                expected_secret = hashlib.md5(f"{user_id}{data['balance']}{API_SECRET_KEY}".encode()).hexdigest()
                if data.get("secret") == expected_secret:
                    return data.get("balance", 0)

            return None
        except Exception as e:
            logger.error(f"Ошибка получения веб баланса: {e}")
            return None

    async def sync_balances(self, user_id: int) -> bool:
        web_balance = await self.get_web_balance(user_id)

        if web_balance is not None:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()

            if result:
                bot_balance = result[0]

                if web_balance != bot_balance:
                    new_balance = max(web_balance, bot_balance)
                    cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
                    conn.commit()

                    await self.send_balance_update(user_id, new_balance)

                    logger.info(f"Балансы синхронизированы: user {user_id} -> {new_balance}")

            conn.close()
            return True

        return False

web_sync = WebAppSync()

class ChatManager:
    def __init__(self):
        self.roulette_bets = defaultdict(dict)
        self.roulette_spinning = defaultdict(bool)
        self.next_roulette_result = {}
        self.group_roulette_results = defaultdict(list)
        self.last_bet_amounts = defaultdict(dict)
        self.last_bet_types = defaultdict(dict)
        self.last_bets_details = defaultdict(dict)
        self.last_game_bets = defaultdict(dict)
        self.go_tasks = {}
        self.user_bets = defaultdict(list)
        self.chat_members_cache = defaultdict(dict)
        self.muted_users = defaultdict(dict)
        self.banned_users = defaultdict(dict)
        self.tournament_participants = {}
        self.tournament_questions = {}
        self.tournament_scores = {}
        self.tournament_active = False
        self.tournament_start_time = None
        self.last_activity = defaultdict(float)
        self.roulette_started = defaultdict(lambda: True)  # Рулетка дайыма иштеп турат
        self.last_spin_bets = defaultdict(dict)
        self.channel_subscriptions = defaultdict(dict)
        self.bonus_cooldown = defaultdict(float)
        self.bonus_day = defaultdict(str)
        self.bonus_index = defaultdict(int)
        self.premium_users = defaultdict(dict)
        self.blackjack_games = defaultdict(dict)

        self.user_current_bets = defaultdict(dict)
        self.user_range_bets = defaultdict(dict)

    def reset_chat_roulette(self, chat_id: int) -> None:
        if chat_id in self.roulette_bets:
            if chat_id in self.roulette_bets and self.roulette_bets[chat_id]:
                self.last_game_bets[chat_id] = {}
                for user_id, bets in self.roulette_bets[chat_id].items():
                    self.last_game_bets[chat_id][user_id] = bets.copy()

            del self.roulette_bets[chat_id]
        if chat_id in self.last_bet_amounts:
            del self.last_bet_amounts[chat_id]
        if chat_id in self.last_bet_types:
            del self.last_bet_types[chat_id]
        if chat_id in self.next_roulette_result:
            del self.next_roulette_result[chat_id]
        if chat_id in self.user_bets:
            del self.user_bets[chat_id]
        if chat_id in self.user_current_bets:
            del self.user_current_bets[chat_id]
        if chat_id in self.user_range_bets:
            del self.user_range_bets[chat_id]

    def add_tournament_participant(self, user_id: int, username: str) -> bool:
        if user_id not in self.tournament_participants:
            self.tournament_participants[user_id] = {
                'username': username,
                'score': 0,
                'joined_at': datetime.now()
            }
            return True
        return False

    def get_tournament_participants_count(self) -> int:
        return len(self.tournament_participants)

    def clear_tournament(self) -> None:
        self.tournament_participants = {}
        self.tournament_questions = {}
        self.tournament_scores = {}
        self.tournament_active = False
        self.tournament_start_time = None

chat_manager = ChatManager()

def init_db() -> None:
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                balance INTEGER DEFAULT 0,
                referrals INTEGER DEFAULT 0,
                last_transfer TIMESTAMP,
                referral_code TEXT,
                total_bet INTEGER DEFAULT 0,
                total_win INTEGER DEFAULT 0,
                max_bet INTEGER DEFAULT 0,
                max_win INTEGER DEFAULT 0,
                status TEXT DEFAULT 'Не женат',
                licenses INTEGER DEFAULT 0,
                vip_licenses INTEGER DEFAULT 0,
                roulette_limit INTEGER DEFAULT 2000000,
                display_name TEXT,
                daily_transfer_used INTEGER DEFAULT 0,
                last_daily_reset TIMESTAMP,
                married_to INTEGER DEFAULT NULL,
                marriage_date TIMESTAMP,
                marriage_partner_name TEXT,
                transfer_limit INTEGER DEFAULT 10000,
                added_users INTEGER DEFAULT 0,
                is_muted INTEGER DEFAULT 0,
                mute_until TIMESTAMP,
                mute_by INTEGER DEFAULT NULL,
                can_mute INTEGER DEFAULT 0,
                can_ban INTEGER DEFAULT 0,
                last_rodnoy_bonus_date DATE,
                daily_bonus_count INTEGER DEFAULT 0,
                premium_type INTEGER DEFAULT 0,
                premium_expires TIMESTAMP,
                tournament_wins INTEGER DEFAULT 0,
                last_sync TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_bonus_time TIMESTAMP,
                bonus_day TEXT,
                total_channels_subscribed INTEGER DEFAULT 0,
                last_bonus_timestamp TIMESTAMP,
                bonus_multiplier INTEGER DEFAULT 1,
                total_paid_bonus INTEGER DEFAULT 0
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount INTEGER,
                type TEXT,
                description TEXT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blocked_users (
                user_id INTEGER PRIMARY KEY,
                reason TEXT,
                blocked_by INTEGER,
                blocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roulette_bets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                bet_type TEXT,
                bet_value TEXT,
                amount INTEGER,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roulette_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                user_id INTEGER,
                result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                game_type TEXT,
                amount INTEGER,
                result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS global_roulette_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER,
                action TEXT,
                target_id INTEGER,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bank (
                user_id INTEGER PRIMARY KEY,
                balance INTEGER DEFAULT 0,
                last_deposit TIMESTAMP,
                last_withdraw TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_emojis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                emoji TEXT,
                bought_price INTEGER,
                bought_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emoji_auctions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                seller_id INTEGER,
                emoji TEXT,
                start_price INTEGER,
                current_price INTEGER,
                buyer_id INTEGER,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rodnoy_bonus_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount INTEGER,
                bonus_date DATE,
                channel_index INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tournament_registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tournament_id INTEGER DEFAULT 1
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tournament_winners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                position INTEGER,
                prize INTEGER,
                tournament_id INTEGER,
                awarded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS webapp_sync (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                balance INTEGER,
                action TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                synced INTEGER DEFAULT 0
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_roles (
                user_id INTEGER PRIMARY KEY,
                role TEXT DEFAULT NULL,
                role_expires TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS premium_purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                premium_type INTEGER,
                price INTEGER,
                purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS channel_subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                channel_index INTEGER,
                subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, channel_index)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blackjack_games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                bet_amount INTEGER,
                player_cards TEXT,
                dealer_cards TEXT,
                player_score INTEGER,
                dealer_score INTEGER,
                game_status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bonus_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount INTEGER,
                payment_date DATE,
                payment_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS promo_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE,
                amount INTEGER,
                uses_left INTEGER,
                expires_at TIMESTAMP,
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS promo_uses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                promo_id INTEGER,
                used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (promo_id) REFERENCES promo_codes(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weekly_bonus (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                week_start DATE,
                bonus_received INTEGER DEFAULT 0,
                UNIQUE(user_id, week_start)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS paid_premium (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                premium_type INTEGER,
                daily_amount INTEGER,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()
        logger.info("База данных инициализирована")
    except Exception as e:
        logger.error(f"Ошибка инициализации базы данных: {e}")

init_db()

class UserManager:
    @staticmethod
    def get_user(user_id: int) -> Optional[Tuple]:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            user = cursor.fetchone()
            conn.close()
            return user
        except Exception as e:
            logger.error(f"Ошибка получения пользователя: {e}")
            return None

    @staticmethod
    def create_user(user_id: int, username: str, first_name: str, referral_code: Optional[str] = None) -> None:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()

            referrer_id = None
            if referral_code:
                cursor.execute("SELECT user_id FROM users WHERE referral_code = ?", (referral_code,))
                result = cursor.fetchone()
                if result:
                    referrer_id = result[0]

            cursor.execute(
                """INSERT OR IGNORE INTO users
                (user_id, username, first_name, referral_code, balance, display_name,
                 roulette_limit, daily_transfer_used, last_daily_reset, transfer_limit, added_users,
                 is_muted, mute_until, mute_by, can_mute, can_ban, last_rodnoy_bonus_date, daily_bonus_count,
                 premium_type, premium_expires, tournament_wins, last_bonus_time, bonus_day, total_channels_subscribed,
                 last_bonus_timestamp, bonus_multiplier, total_paid_bonus)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, username, first_name, f"ref_{user_id}", INITIAL_BALANCE, first_name,
                 ROULETTE_LIMIT, 0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), TRANSFER_DAILY_LIMIT, 0,
                 0, None, None, 0, 0, None, 0,
                 0, None, 0, None, None, 0,
                 None, 1, 0)
            )

            if referrer_id:
                cursor.execute("UPDATE users SET balance = balance + ?, referrals = referrals + 1 WHERE user_id = ?",
                             (REFERRAL_BONUS, referrer_id))
                cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?",
                             (REFERRAL_BONUS, user_id))

                cursor.execute(
                    "INSERT INTO transactions (user_id, amount, type, description) VALUES (?, ?, ?, ?)",
                    (referrer_id, REFERRAL_BONUS, "ref_bonus", f"Реферальный бонус за {username}")
                )
                cursor.execute(
                    "INSERT INTO transactions (user_id, amount, type, description) VALUES (?, ?, ?, ?)",
                    (user_id, REFERRAL_BONUS, "ref_bonus", f"Реферальный бонус при регистрации")
                )

            conn.commit()
            conn.close()

            asyncio.create_task(web_sync.send_balance_update(user_id, INITIAL_BALANCE))
        except Exception as e:
            logger.error(f"Ошибка создания пользователя: {e}")

    @staticmethod
    async def update_balance(user_id: int, amount: int, description: str = "") -> int:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()

            cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))

            if amount < 0:
                cursor.execute("UPDATE users SET total_bet = total_bet + ? WHERE user_id = ?", (abs(amount), user_id))
                cursor.execute("UPDATE users SET max_bet = MAX(max_bet, ?) WHERE user_id = ?", (abs(amount), user_id))
                transaction_type = "bet"
            else:
                cursor.execute("UPDATE users SET total_win = total_win + ? WHERE user_id = ?", (amount, user_id))
                cursor.execute("UPDATE users SET max_win = MAX(max_win, ?) WHERE user_id = ?", (amount, user_id))
                transaction_type = "win"

            cursor.execute(
                "INSERT INTO transactions (user_id, amount, type, description) VALUES (?, ?, ?, ?)",
                (user_id, abs(amount), transaction_type, description)
            )

            cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
            new_balance = cursor.fetchone()[0]

            conn.commit()
            conn.close()

            await web_sync.send_balance_update(user_id, new_balance)

            return new_balance
        except Exception as e:
            logger.error(f"Ошибка обновления баланса: {e}")
            return 0

    @staticmethod
    def get_rodnoy_bonus_info(user_id: int) -> Optional[Tuple]:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT last_rodnoy_bonus_date, daily_bonus_count, last_bonus_time,
                       bonus_day, total_channels_subscribed, last_bonus_timestamp,
                       bonus_multiplier, total_paid_bonus
                FROM users WHERE user_id = ?
            """, (user_id,))
            result = cursor.fetchone()
            conn.close()
            return result
        except Exception as e:
            logger.error(f"Ошибка получения бонусной информации: {e}")
            return None

    @staticmethod
    async def update_rodnoy_bonus(user_id: int, amount: int, channel_index: Optional[int] = None) -> None:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            today = datetime.now().date()
            now = datetime.now()

            cursor.execute("""
                UPDATE users
                SET last_rodnoy_bonus_date = ?,
                    daily_bonus_count = daily_bonus_count + 1,
                    balance = balance + ?,
                    last_bonus_time = ?,
                    bonus_day = ?,
                    last_bonus_timestamp = ?
                WHERE user_id = ?""",
                (today.strftime("%Y-%m-%d"), amount, now.strftime("%Y-%m-%d %H:%M:%S"),
                 today.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d %H:%M:%S"), user_id))

            cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
            new_balance = cursor.fetchone()[0]

            cursor.execute(
                "INSERT INTO rodnoy_bonus_history (user_id, amount, bonus_date, channel_index) VALUES (?, ?, ?, ?)",
                (user_id, amount, today.strftime("%Y-%m-%d"), channel_index)
            )

            conn.commit()
            conn.close()

            await web_sync.send_balance_update(user_id, new_balance)
        except Exception as e:
            logger.error(f"Ошибка обновления бонуса: {e}")

    @staticmethod
    def add_channel_subscription(user_id: int, channel_index: int) -> bool:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()

            cursor.execute(
                "INSERT OR IGNORE INTO channel_subscriptions (user_id, channel_index) VALUES (?, ?)",
                (user_id, channel_index)
            )

            cursor.execute(
                "UPDATE users SET total_channels_subscribed = total_channels_subscribed + 1 WHERE user_id = ?",
                (user_id,)
            )

            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Ошибка добавления подписки: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def get_channel_subscriptions(user_id: int) -> List[int]:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT channel_index FROM channel_subscriptions WHERE user_id = ?",
                (user_id,)
            )

            result = [row[0] for row in cursor.fetchall()]
            conn.close()
            return result
        except Exception as e:
            logger.error(f"Ошибка получения подписок: {e}")
            return []

    @staticmethod
    def check_channel_subscribed(user_id: int, channel_index: int) -> bool:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT 1 FROM channel_subscriptions WHERE user_id = ? AND channel_index = ?",
                (user_id, channel_index)
            )

            result = cursor.fetchone() is not None
            conn.close()
            return result
        except Exception as e:
            logger.error(f"Ошибка проверки подписки: {e}")
            return False

    @staticmethod
    def get_premium_info(user_id: int) -> Optional[Tuple]:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT premium_type, premium_expires FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            conn.close()
            return result
        except Exception as e:
            logger.error(f"Ошибка получения premium информации: {e}")
            return None

    @staticmethod
    def get_paid_premium_info(user_id: int) -> Optional[Tuple]:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT premium_type, daily_amount, expires_at
                FROM paid_premium
                WHERE user_id = ? ORDER BY expires_at DESC LIMIT 1
            """, (user_id,))
            result = cursor.fetchone()
            conn.close()
            return result
        except Exception as e:
            logger.error(f"Ошибка получения paid premium информации: {e}")
            return None

    @staticmethod
    async def activate_paid_premium(user_id: int, premium_type: int, days: int, daily_amount: int) -> bool:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            expires = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                INSERT INTO paid_premium (user_id, premium_type, daily_amount, expires_at)
                VALUES (?, ?, ?, ?)
            """, (user_id, premium_type, daily_amount, expires))

            cursor.execute(
                "INSERT INTO transactions (user_id, amount, type, description) VALUES (?, ?, ?, ?)",
                (user_id, 0, "premium_activation", f"Активация Premium {premium_type} на {days} дней")
            )

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Ошибка активации premium: {e}")
            return False

    @staticmethod
    async def give_paid_bonus(user_id: int, amount: int) -> bool:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()

            cursor.execute("UPDATE users SET balance = balance + ?, total_paid_bonus = total_paid_bonus + ? WHERE user_id = ?",
                          (amount, amount, user_id))

            cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
            new_balance = cursor.fetchone()[0]

            cursor.execute(
                "INSERT INTO transactions (user_id, amount, type, description) VALUES (?, ?, ?, ?)",
                (user_id, amount, "paid_bonus", f"Платный бонус: +{amount}")
            )

            cursor.execute(
                "INSERT INTO bonus_payments (user_id, amount, payment_date, payment_type) VALUES (?, ?, ?, ?)",
                (user_id, amount, datetime.now().date().strftime("%Y-%m-%d"), "paid")
            )

            conn.commit()
            conn.close()

            await web_sync.send_balance_update(user_id, new_balance)
            return True
        except Exception as e:
            logger.error(f"Ошибка выдачи paid бонуса: {e}")
            return False

    @staticmethod
    def check_paid_premium_expiry() -> int:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("DELETE FROM paid_premium WHERE expires_at < ?", (now,))
            affected = cursor.rowcount
            conn.commit()
            conn.close()
            return affected
        except Exception as e:
            logger.error(f"Ошибка проверки premium expiry: {e}")
            return 0

    @staticmethod
    def get_all_paid_premium_users() -> List[Tuple]:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, premium_type, daily_amount, expires_at FROM paid_premium")
            result = cursor.fetchall()
            conn.close()
            return result
        except Exception as e:
            logger.error(f"Ошибка получения paid premium пользователей: {e}")
            return []

    @staticmethod
    def get_transaction_history(user_id: int, limit: int = 10) -> List[Tuple]:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT date, amount, type, description FROM transactions WHERE user_id = ? ORDER BY date DESC LIMIT ?",
                (user_id, limit)
            )
            result = cursor.fetchall()
            conn.close()
            return result
        except Exception as e:
            logger.error(f"Ошибка получения истории транзакций: {e}")
            return []

    @staticmethod
    def add_global_roulette_log(chat_id: int, result: str) -> None:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO global_roulette_logs (chat_id, result) VALUES (?, ?)",
                (chat_id, result)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Ошибка добавления глобального лога: {e}")

    @staticmethod
    def get_global_roulette_logs(chat_id: int, limit: int = 10) -> List[str]:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT result FROM global_roulette_logs WHERE chat_id = ? ORDER BY id DESC LIMIT ?",
                (chat_id, limit)
            )
            result = cursor.fetchall()
            conn.close()
            return [log[0] for log in result]
        except Exception as e:
            logger.error(f"Ошибка получения глобальных логов: {e}")
            return []

    @staticmethod
    def get_global_roulette_logs_all(chat_id: int, limit: int = 21) -> List[str]:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT result FROM global_roulette_logs WHERE chat_id = ? ORDER BY id DESC LIMIT ?",
                (chat_id, limit)
            )
            result = cursor.fetchall()
            conn.close()
            return [log[0] for log in result]
        except Exception as e:
            logger.error(f"Ошибка получения всех глобальных логов: {e}")
            return []

    @staticmethod
    def get_global_top_users(limit: int = 10) -> List[Tuple]:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT user_id, display_name, username, first_name, balance
                FROM users
                WHERE balance > 0
                ORDER BY balance DESC LIMIT ?
            """, (limit,))

            result = cursor.fetchall()
            conn.close()
            return result
        except Exception as e:
            logger.error(f"Ошибка получения топ пользователей: {e}")
            return []

    @staticmethod
    def get_user_position_by_balance(user_id: int) -> int:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(*) + 1 as position
                FROM users u1
                WHERE balance > (SELECT balance FROM users WHERE user_id = ?)
            """, (user_id,))

            result = cursor.fetchone()
            conn.close()

            return result[0] if result else 1
        except Exception as e:
            logger.error(f"Ошибка получения позиции пользователя: {e}")
            return 1

    @staticmethod
    def set_display_name(user_id: int, display_name: str) -> None:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET display_name = ? WHERE user_id = ?", (display_name, user_id))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Ошибка установки отображаемого имени: {e}")

    @staticmethod
    def update_user_from_tg(user_id: int, username: str, first_name: str) -> None:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()

            cursor.execute("SELECT username, first_name, display_name FROM users WHERE user_id = ?", (user_id,))
            user = cursor.fetchone()

            if user:
                current_username, current_first_name, display_name = user

                if current_username != username or current_first_name != first_name:
                    cursor.execute("UPDATE users SET username = ?, first_name = ? WHERE user_id = ?",
                                 (username, first_name, user_id))

                    if not display_name or display_name == current_first_name:
                        cursor.execute("UPDATE users SET display_name = ? WHERE user_id = ?", (first_name, user_id))

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Ошибка обновления пользователя из Telegram: {e}")

    @staticmethod
    async def add_coins_to_user(user_id: int, amount: int) -> bool:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()

            cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))

            cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
            new_balance = cursor.fetchone()[0]

            cursor.execute(
                "INSERT INTO transactions (user_id, amount, type, description) VALUES (?, ?, ?, ?)",
                (user_id, amount, "admin_add", f"Админ добавил {amount} монет")
            )

            cursor.execute(
                "INSERT INTO admin_logs (admin_id, action, target_id, details) VALUES (?, ?, ?, ?)",
                (ADMIN_ID, "add_coins", user_id, f"{amount} монет")
            )

            conn.commit()
            conn.close()

            await web_sync.send_balance_update(user_id, new_balance)

            return True
        except Exception as e:
            logger.error(f"Ошибка добавления монет: {e}")
            return False

    @staticmethod
    async def remove_coins_from_user(user_id: int, amount: int) -> Tuple[bool, Union[int, str]]:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()

            cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()

            if not result:
                conn.close()
                return False, "Пользователь не найден"

            current_balance = result[0]

            if amount > current_balance:
                cursor.execute("UPDATE users SET balance = 0 WHERE user_id = ?", (user_id,))
                removed_amount = current_balance
            else:
                cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, user_id))
                removed_amount = amount

            cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
            new_balance = cursor.fetchone()[0]

            cursor.execute(
                "INSERT INTO transactions (user_id, amount, type, description) VALUES (?, ?, ?, ?)",
                (user_id, -removed_amount, "admin_remove", f"Админ убрал {removed_amount} монет")
            )

            cursor.execute(
                "INSERT INTO admin_logs (admin_id, action, target_id, details) VALUES (?, ?, ?, ?)",
                (ADMIN_ID, "remove_coins", user_id, f"{removed_amount} монет")
            )

            conn.commit()
            conn.close()

            await web_sync.send_balance_update(user_id, new_balance)

            return True, removed_amount
        except Exception as e:
            logger.error(f"Ошибка удаления монет: {e}")
            return False, f"Ошибка: {e}"

    @staticmethod
    def add_roulette_log(chat_id: int, user_id: int, result: str) -> None:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO roulette_logs (chat_id, user_id, result) VALUES (?, ?, ?)",
                (chat_id, user_id, result)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Ошибка добавления лога рулетки: {e}")

    @staticmethod
    def is_muted(user_id: int) -> bool:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT is_muted, mute_until FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            conn.close()

            if not result:
                return False

            is_muted, mute_until = result
            if is_muted and mute_until:
                try:
                    mute_time = datetime.strptime(mute_until, "%Y-%m-%d %H:%M:%S")
                    if datetime.now() > mute_time:
                        conn = sqlite3.connect(DATABASE_NAME)
                        cursor = conn.cursor()
                        cursor.execute("UPDATE users SET is_muted = 0, mute_until = NULL WHERE user_id = ?", (user_id,))
                        conn.commit()
                        conn.close()
                        return False
                    return True
                except:
                    return False
            return False
        except Exception as e:
            logger.error(f"Ошибка проверки мута: {e}")
            return False

    @staticmethod
    def mute_user(user_id: int, hours: float, muted_by: Optional[int] = None) -> None:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            mute_until = (datetime.now() + timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("UPDATE users SET is_muted = 1, mute_until = ?, mute_by = ? WHERE user_id = ?",
                          (mute_until, muted_by, user_id))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Ошибка мута: {e}")

    @staticmethod
    def unmute_user(user_id: int) -> None:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET is_muted = 0, mute_until = NULL, mute_by = NULL WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Ошибка размута: {e}")

    @staticmethod
    def block_user(user_id: int, reason: str, blocked_by: int) -> None:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO blocked_users (user_id, reason, blocked_by) VALUES (?, ?, ?)",
                (user_id, reason, blocked_by)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Ошибка блокировки: {e}")

    @staticmethod
    def is_blocked(user_id: int) -> bool:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM blocked_users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            conn.close()
            return result is not None
        except Exception as e:
            logger.error(f"Ошибка проверки блокировки: {e}")
            return False

    @staticmethod
    def unblock_user(user_id: int) -> None:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM blocked_users WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Ошибка разблокировки: {e}")

    @staticmethod
    def can_make_transfer(user_id: int, amount: int) -> Tuple[bool, str]:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()

            cursor.execute("SELECT transfer_limit, last_transfer, daily_transfer_used FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()

            if not result:
                conn.close()
                return False, "Пользователь не найден"

            transfer_limit, last_transfer_str, daily_used = result
            now = datetime.now()

            if daily_used + amount > transfer_limit:
                remaining = transfer_limit - daily_used
                conn.close()
                return False, f"Лимит на передачу {transfer_limit} монет за {TRANSFER_COOLDOWN_HOURS} часов. Вы еще можете передать: {remaining}"

            if amount < 1:
                conn.close()
                return False, f"Минимальная сумма перевода: 1 монета"

            remaining = transfer_limit - daily_used

            conn.close()
            return True, f"Можно переводить. Доступно: {remaining}"
        except Exception as e:
            logger.error(f"Ошибка проверки трансфера: {e}")
            return False, f"Ошибка: {e}"

    @staticmethod
    def update_transfer_usage(user_id: int, amount: int) -> None:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("UPDATE users SET last_transfer = ?, daily_transfer_used = daily_transfer_used + ? WHERE user_id = ?",
                          (now, amount, user_id))

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Ошибка обновления трансфера: {e}")

    @staticmethod
    def reset_daily_limits() -> None:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()

            cursor.execute("UPDATE users SET daily_transfer_used = 0, last_daily_reset = ?, daily_bonus_count = 0",
                          (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))

            conn.commit()
            conn.close()
            logger.info("Күнүмдүк лимиттер баштапкы абалга келтирилди")
        except Exception as e:
            logger.error(f"Ошибка сброса лимитов: {e}")

    @staticmethod
    def grant_permission(chat_id: int, user_id: int, permission_type: str, granted_by: int) -> None:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()

            if permission_type == "mute":
                cursor.execute("UPDATE users SET can_mute = 1 WHERE user_id = ?", (user_id,))
            elif permission_type == "ban":
                cursor.execute("UPDATE users SET can_ban = 1 WHERE user_id = ?", (user_id,))
            elif permission_type == "all":
                cursor.execute("UPDATE users SET can_mute = 1, can_ban = 1 WHERE user_id = ?", (user_id,))

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Ошибка выдачи разрешения: {e}")

    @staticmethod
    def revoke_permission(user_id: int, permission_type: str) -> None:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()

            if permission_type == "mute":
                cursor.execute("UPDATE users SET can_mute = 0 WHERE user_id = ?", (user_id,))
            elif permission_type == "ban":
                cursor.execute("UPDATE users SET can_ban = 0 WHERE user_id = ?", (user_id,))
            elif permission_type == "all":
                cursor.execute("UPDATE users SET can_mute = 0, can_ban = 0 WHERE user_id = ?", (user_id,))

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Ошибка отзыва разрешения: {e}")

    @staticmethod
    def has_permission(user_id: int, permission_type: str) -> bool:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()

            if permission_type == "mute":
                cursor.execute("SELECT can_mute FROM users WHERE user_id = ?", (user_id,))
            elif permission_type == "ban":
                cursor.execute("SELECT can_ban FROM users WHERE user_id = ?", (user_id,))
            else:
                conn.close()
                return False

            result = cursor.fetchone()
            conn.close()

            if result and result[0] == 1:
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка проверки разрешения: {e}")
            return False

    @staticmethod
    def set_roulette_limit(user_id: int, limit: int) -> None:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET roulette_limit = ? WHERE user_id = ?", (limit, user_id))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Ошибка установки лимита рулетки: {e}")

    @staticmethod
    def set_transfer_limit(user_id: int, limit: int) -> None:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET transfer_limit = ? WHERE user_id = ?", (limit, user_id))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Ошибка установки лимита перевода: {e}")

    @staticmethod
    def get_transfer_limit(user_id: int) -> int:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT transfer_limit FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            conn.close()

            if result and result[0]:
                return result[0]
            return TRANSFER_DAILY_LIMIT
        except Exception as e:
            logger.error(f"Ошибка получения лимита перевода: {e}")
            return TRANSFER_DAILY_LIMIT

    @staticmethod
    def reduce_all_balances_above_limit(limit: int = 100000) -> int:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()

            cursor.execute("SELECT user_id, balance FROM users WHERE balance > ?", (limit,))
            users = cursor.fetchall()

            affected_users = 0

            for user_id, current_balance in users:
                if current_balance > limit:
                    reduction_amount = current_balance - limit
                    cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (limit, user_id))

                    cursor.execute(
                        "INSERT INTO transactions (user_id, amount, type, description) VALUES (?, ?, ?, ?)",
                        (user_id, -reduction_amount, "system_reduction", f"Система: баланс {limit:,}га түшүрүлдү")
                    )

                    affected_users += 1

            conn.commit()
            logger.info(f"Баланстары {limit:,}га түшүрүлдү: {affected_users} колдонуучу")

            return affected_users

        except Exception as e:
            conn.rollback()
            logger.error(f"Балансты түшүрүүдө ката: {e}")
            return 0
        finally:
            conn.close()

    @staticmethod
    def register_for_tournament(user_id: int, username: str) -> None:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR IGNORE INTO tournament_registrations (user_id, username, tournament_id)
                VALUES (?, ?, 1)
            """, (user_id, username))

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Ошибка регистрации на турнир: {e}")

    @staticmethod
    def get_tournament_registrations() -> List[Tuple]:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()

            cursor.execute("SELECT user_id, username FROM tournament_registrations WHERE tournament_id = 1")
            result = cursor.fetchall()

            conn.close()
            return result
        except Exception as e:
            logger.error(f"Ошибка получения регистраций: {e}")
            return []

    @staticmethod
    def clear_tournament_registrations() -> int:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM tournament_registrations WHERE tournament_id = 1")
            deleted = cursor.rowcount

            conn.commit()
            conn.close()
            return deleted
        except Exception as e:
            logger.error(f"Ошибка очистки регистраций: {e}")
            return 0

    @staticmethod
    async def add_tournament_winner(user_id: int, username: str, position: int, prize: int) -> None:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO tournament_winners (user_id, username, position, prize, tournament_id)
                VALUES (?, ?, ?, ?, 1)
            """, (user_id, username, position, prize))

            cursor.execute("UPDATE users SET balance = balance + ?, tournament_wins = tournament_wins + 1 WHERE user_id = ?",
                          (prize, user_id))

            cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
            new_balance = cursor.fetchone()[0]

            cursor.execute(
                "INSERT INTO transactions (user_id, amount, type, description) VALUES (?, ?, ?, ?)",
                (user_id, prize, "tournament_prize", f"Приз турнира: {position} место")
            )

            conn.commit()
            conn.close()

            await web_sync.send_balance_update(user_id, new_balance)
        except Exception as e:
            logger.error(f"Ошибка добавления победителя: {e}")

    @staticmethod
    async def add_stars_purchase(user_id: int, stars_amount: int, coins_amount: int) -> bool:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()

            cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (coins_amount, user_id))

            cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
            new_balance = cursor.fetchone()[0]

            cursor.execute(
                "INSERT INTO transactions (user_id, amount, type, description) VALUES (?, ?, ?, ?)",
                (user_id, coins_amount, "stars_purchase", f"Покупка через Stars: {stars_amount} ⭐ = {coins_amount} 🪙")
            )

            conn.commit()
            conn.close()

            await web_sync.send_balance_update(user_id, new_balance)

            return True
        except Exception as e:
            logger.error(f"Ошибка покупки через Stars: {e}")
            return False

    @staticmethod
    def get_user_role(user_id: int) -> Optional[Tuple]:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT role, role_expires FROM user_roles WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            conn.close()
            return result
        except Exception as e:
            logger.error(f"Ошибка получения роли: {e}")
            return None

    @staticmethod
    def set_user_role(user_id: int, role: str, days: int = 30) -> None:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            expires = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT OR REPLACE INTO user_roles (user_id, role, role_expires) VALUES (?, ?, ?)",
                          (user_id, role, expires))

            cursor.execute(
                "INSERT INTO admin_logs (admin_id, action, target_id, details) VALUES (?, ?, ?, ?)",
                (ADMIN_ID, f"give_role_{role}", user_id, f"{role} на {days} дней")
            )

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Ошибка установки роли: {e}")

    @staticmethod
    def remove_user_role(user_id: int) -> None:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_roles WHERE user_id = ?", (user_id,))

            cursor.execute(
                "INSERT INTO admin_logs (admin_id, action, target_id, details) VALUES (?, ?, ?, ?)",
                (ADMIN_ID, "remove_role", user_id, "Роль удалена")
            )

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Ошибка удаления роли: {e}")

    @staticmethod
    def check_role_expiry() -> int:
        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("DELETE FROM user_roles WHERE role_expires < ?", (now,))
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            return deleted_count
        except Exception as e:
            logger.error(f"Ошибка проверки срока ролей: {e}")
            return 0

def calculate_next_result(logs: List[str], chat_id: Optional[int] = None) -> str:
    if not logs:
        return "7🔴"

    if chat_id and chat_id in chat_manager.next_roulette_result:
        result = chat_manager.next_roulette_result[chat_id]
        if result and len(result) >= 2 and re.match(r'^\d+', result):
            return result
        else:
            del chat_manager.next_roulette_result[chat_id]

    last_results = logs[:10]
    red_count = 0
    black_count = 0
    green_count = 0

    for result in last_results:
        if result:
            if "🔴" in result:
                red_count += 1
            elif "⚫️" in result:
                black_count += 1
            elif "💚" in result:
                green_count += 1

    last_result = logs[0] if logs else "0💚"

    if red_count >= black_count and red_count >= green_count:
        black_numbers = ["2⚫️", "4⚫️", "6⚫️", "8⚫️", "10⚫️", "12⚫️"]
        filtered = [num for num in black_numbers if num != last_result]
        if filtered:
            result = random.choice(filtered)
        else:
            result = random.choice(black_numbers)
    elif black_count >= red_count and black_count >= green_count:
        red_numbers = ["1🔴", "3🔴", "5🔴", "7🔴", "9🔴", "11🔴"]
        filtered = [num for num in red_numbers if num != last_result]
        if filtered:
            result = random.choice(filtered)
        else:
            result = random.choice(red_numbers)
    else:
        if green_count > 0 and random.random() < 0.1:
            result = "0💚"
        else:
            all_numbers = [
                "0💚", "1🔴", "2⚫️", "3🔴", "4⚫️", "5🔴", "6⚫️",
                "7🔴", "8⚫️", "9🔴", "10⚫️", "11🔴", "12⚫️"
            ]
            possible_numbers = [num for num in all_numbers if num != last_result]
            if possible_numbers:
                result = random.choice(possible_numbers)
            else:
                result = "7🔴"

    if not result or not re.match(r'^\d+', result):
        result = "7🔴"

    if chat_id:
        chat_manager.next_roulette_result[chat_id] = result

    return result

def get_main_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton("🏠 𝐑𝐃𝐍𝐎 𝐌𝐗")],
        [KeyboardButton("🎁 Бонус"), KeyboardButton("💳 Донат")],
        [KeyboardButton("❓ Помощь"), KeyboardButton("🔗 Ссылки")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def handle_id_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target_user_id = target_user.id
        target_name = target_user.first_name
        if target_user.username:
            target_name = target_user.username

        await update.effective_chat.send_message(f"🆔 ID пользователя {target_name}: {target_user_id}")
    else:
        user = UserManager.get_user(user_id)
        if user and user[15]:
            display_name = user[15]
        elif user and user[1]:
            display_name = user[1]
        else:
            display_name = update.effective_user.first_name

        await update.effective_chat.send_message(f"🆔 Ваш ID ({display_name}): {user_id}")

async def handle_refs_command(update, context):
    user_id = update.effective_user.id
    user = UserManager.get_user(user_id)
    if not user:
        await update.effective_chat.send_message("❌ Колдонуучу табылган жок!")
        return

    ref_code = f"ref_{user_id}"
    bot_info = await context.bot.get_me()
    bot_username = bot_info.username
    ref_link = f"https://t.me/{bot_username}?start={ref_code}"

    referrals_count = user[4] if user[4] else 0
    total_earned = referrals_count * REFERRAL_BONUS

    text = (
        f"🔗 *Реферальная программа*\n\n"
        f"Твоя реферальная ссылка:\n"
        f"`{ref_link}`\n\n"
        f"📊 *Статистика:*\n"
        f"👥 Приглашено друзей: *{referrals_count}*\n"
        f"💰 Заработано бонусов: *{total_earned:,}* 🪙\n\n"
        f"🎁 *Условия:*\n"
        f"• Ты получаешь: *{REFERRAL_BONUS:,}* 🪙 за каждого друга\n"
        f"• Друг получает: *{REFERRAL_BONUS:,}* 🪙 при регистрации\n\n"
        f"👆 Скопируй ссылку и отправь друзьям!"
    )

    await update.effective_chat.send_message(text, parse_mode=ParseMode.MARKDOWN)


async def show_rodnoy_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat.type in ['group', 'supergroup']:
        return

    user_id = update.effective_user.id
    user = UserManager.get_user(user_id)

    if not user:
        username = update.effective_user.username
        first_name = update.effective_user.first_name
        UserManager.create_user(user_id, username, first_name, None)
        user = UserManager.get_user(user_id)

    await web_sync.sync_balances(user_id)
    user = UserManager.get_user(user_id)

    keyboard = [
        [InlineKeyboardButton("🏠 ГЛАВНАЯ", callback_data="rodnoy_home")],
        [InlineKeyboardButton("💰 БАЛАНС", callback_data="rodnoy_balance_page")],
        [InlineKeyboardButton("🎰 ИГРЫ", callback_data="rodnoy_games")],
        [InlineKeyboardButton("🎭 РОЛИ", callback_data="rodnoy_roles")],
        [InlineKeyboardButton("🎁 БОНУС", callback_data="rodnoy_bonus_page")],
        [InlineKeyboardButton("🏆 РЕЙТИНГ", callback_data="rodnoy_rating")],
        [InlineKeyboardButton("⚙️ НАСТРОЙКИ", callback_data="rodnoy_settings")],
        [InlineKeyboardButton("🔗 ССЫЛКИ", callback_data="rodnoy_links")],
        [InlineKeyboardButton("🌐 ВЕБ ПРИЛОЖЕНИЕ", url=WEBAPP_URL)],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if user[15]:
        display_name = user[15]
    elif user[1]:
        display_name = user[1]
    else:
        display_name = user[2]

    menu_text = (
        f"#𝐑𝐃𝐍𝐎 𝐌𝐗\n\n"
        f"👤 {display_name}\n"
        f"🆔 ID: {user_id}\n"
        f"💰 Баланс: {user[3]} 🪙\n\n"
        f"📅 {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        f"👇 Нажмите кнопку для управления:"
    )

    if update.message:
        await update.message.reply_text(menu_text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.edit_text(menu_text, reply_markup=reply_markup)

async def show_rodnoy_balance_page(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    user = UserManager.get_user(user_id)

    if not user:
        return

    await web_sync.sync_balances(user_id)
    user = UserManager.get_user(user_id)

    keyboard = [
        [InlineKeyboardButton("💳 Донат", url="https://t.me/MX_KASSA")],
        [InlineKeyboardButton("📊 Статистика", callback_data="rodnoy_stats")],
        [InlineKeyboardButton("🌐 ВЕБ ПРИЛОЖЕНИЕ", url=WEBAPP_URL)],
        [InlineKeyboardButton("◀️ Назад", callback_data="rodnoy_main_menu")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    balance_text = (
        f"#𝐑𝐃𝐍𝐎 𝐌𝐗\n\n"
        f"## БАЛАНС\n\n"
        f"1. **𝐑𝐃𝐍𝐎 𝐌𝐗 Coins**\n"
        f"   {user[3]} 🪙\n\n"
        f"2. 💳 Донат\n"
        f"3. Подписки\n\n"
        f"💰 Доступно: {user[3]} 🪙\n"
        f"💳 Для пополнения нажмите кнопку ниже:\n\n"
        f"🌐 Веб приложение: играйте в Крэш и Дурак!\n\n"
        f"💳 Донат (рубль):\n"
        f"• 200.000 - 100₽\n"
        f"• 500.000 - 230₽\n"
        f"• 1.000.000 - 450₽\n"
        f"• 2.000.000 - 845₽\n"
        f"• 5.000.000 - 2.000₽\n"
        f"• 10.000.000 - 4.000₽\n"
        f"• 50.000.000 - 20000₽\n"
        f"• 100.000.000 - 40000₽\n\n"
        f"По вопросам доната: https://t.me/MX_KASSA"
    )

    await query.message.edit_text(balance_text, reply_markup=reply_markup)

async def show_stars_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    keyboard = [
        [InlineKeyboardButton("200.000 монет - 100 ⭐", callback_data="stars_200000")],
        [InlineKeyboardButton("500.000 монет - 230 ⭐", callback_data="stars_500000")],
        [InlineKeyboardButton("1.000.000 монет - 450 ⭐", callback_data="stars_1000000")],
        [InlineKeyboardButton("2.000.000 монет - 845 ⭐", callback_data="stars_2000000")],
        [InlineKeyboardButton("5.000.000 монет - 2.000 ⭐", callback_data="stars_5000000")],
        [InlineKeyboardButton("10.000.000 монет - 4.000 ⭐", callback_data="stars_10000000")],
        [InlineKeyboardButton("50.000.000 монет - 20.000 ⭐", callback_data="stars_50000000")],
        [InlineKeyboardButton("100.000.000 монет - 40.000 ⭐", callback_data="stars_100000000")],
        [InlineKeyboardButton("◀️ Назад", callback_data="rodnoy_balance_page")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        f"#𝐑𝐃𝐍𝐎 𝐌𝐗\n\n"
        f"## ПОКУПКА ЗА TELEGRAM STARS\n\n"
        f"💰 Выберите количество монет:\n\n"
        f"• 200.000 монет - 100 ⭐\n"
        f"• 500.000 монет - 230 ⭐\n"
        f"• 1.000.000 монет - 450 ⭐\n"
        f"• 2.000.000 монет - 845 ⭐\n"
        f"• 5.000.000 монет - 2.000 ⭐\n"
        f"• 10.000.000 монет - 4.000 ⭐\n"
        f"• 50.000.000 монет - 20.000 ⭐\n"
        f"• 100.000.000 монет - 40.000 ⭐\n\n"
        f"⭐ Telegram Stars - это внутренняя валюта Telegram.\n"
        f"Купить Stars можно в настройках Telegram."
    )

    await query.message.edit_text(text, reply_markup=reply_markup)

def get_stars_price(coins: int) -> int:
    prices = {
        200000: 100,
        500000: 230,
        1000000: 450,
        2000000: 845,
        5000000: 2000,
        10000000: 4000,
        50000000: 20000,
        100000000: 40000
    }
    return prices.get(coins, 100)

async def handle_stars_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id

    data = query.data
    coins_amount = int(data.replace("stars_", ""))

    context.user_data['pending_purchase'] = {
        'coins': coins_amount,
        'stars': get_stars_price(coins_amount)
    }

    stars_price = get_stars_price(coins_amount)

    title = f"Покупка {coins_amount} монет"
    description = f"Купить {coins_amount} 🪙 за {stars_price} ⭐"
    payload = f"buy_coins_{coins_amount}_{int(time.time())}"
    currency = "XTR"
    prices = [LabeledPrice("Монеты", stars_price)]

    await context.bot.send_invoice(
        chat_id=user_id,
        title=title,
        description=description,
        payload=payload,
        provider_token=PROVIDER_TOKEN,
        currency=currency,
        prices=prices,
        start_parameter="buy_coins"
    )

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.pre_checkout_query
    if query.invoice_payload.startswith("buy_coins_"):
        await query.answer(ok=True)
    else:
        await query.answer(ok=False, error_message="Что-то пошло не так")

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    payment = update.message.successful_payment
    payload = payment.invoice_payload

    match = re.search(r'buy_coins_(\d+)_', payload)
    if match:
        coins_amount = int(match.group(1))
        await UserManager.add_stars_purchase(user_id, payment.total_amount, coins_amount)

        await update.message.reply_text(
            f"✅ Оплата прошла успешно!\n\n"
            f"💰 Вам начислено: {coins_amount} 🪙\n"
            f"⭐ Потрачено Stars: {payment.total_amount}\n\n"
            f"Спасибо за покупку!"
        )

async def show_rodnoy_bonus_page(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    user = UserManager.get_user(user_id)

    if not user:
        return

    today = datetime.now().date()

    bonus_data = UserManager.get_rodnoy_bonus_info(user_id)
    daily_bonus_taken = False
    last_bonus_time = None
    total_subscribed = 0

    if bonus_data:
        if bonus_data[0]:
            last_date = datetime.strptime(bonus_data[0], "%Y-%m-%d").date()
            if last_date == today:
                daily_bonus_taken = True
        if bonus_data[2]:
            last_bonus_time = datetime.strptime(bonus_data[2], "%Y-%m-%d %H:%M:%S")
        if bonus_data[4]:
            total_subscribed = bonus_data[4]

    can_take_bonus = False
    if not daily_bonus_taken:
        can_take_bonus = True
    elif last_bonus_time and (datetime.now() - last_bonus_time).total_seconds() > 12 * 3600:
        can_take_bonus = True

    subscriptions = UserManager.get_channel_subscriptions(user_id)
    subscribed_count = len(subscriptions)

    keyboard = [
        [InlineKeyboardButton("🎁 Бесплатный бонус (подписка на каналы)", callback_data="show_channel_bonus")],
        [InlineKeyboardButton("💰 Премиум 1 (200 руб/мес - 40.000 монет/день)", callback_data="premium_1_info")],
        [InlineKeyboardButton("💎 Премиум 2 (300 руб/мес - 60.000 монет/день)", callback_data="premium_2_info")],
        [InlineKeyboardButton("🌐 ВЕБ ПРИЛОЖЕНИЕ", url=WEBAPP_URL)],
        [InlineKeyboardButton("◀️ Назад", callback_data="rodnoy_main_menu")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    bonus_text = (
        f"#𝐑𝐃𝐍𝐎 𝐌𝐗\n\n"
        f"## БОНУСНАЯ СИСТЕМА\n\n"
        f"🎁 **Бесплатный бонус**\n"
        f"   • Подпишитесь на каналы (30 каналов)\n"
        f"   • Получите 20.000 монет за каждый канал\n"
        f"   • Доступно раз в 12 часов\n"
        f"   • Вы подписались на: {subscribed_count}/30 каналов\n\n"
        f"💰 **Премиум 1**\n"
        f"   • 40.000 монет ежедневно\n"
        f"   • Срок: 30 дней\n"
        f"   • Цена: 200 руб\n\n"
        f"💎 **Премиум 2**\n"
        f"   • 60.000 монет ежедневно\n"
        f"   • Срок: 30 дней\n"
        f"   • Цена: 300 руб\n\n"
        f"👇 Выберите бонус:"
    )

    await query.message.edit_text(bonus_text, reply_markup=reply_markup)

async def show_channel_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id

    if update.effective_chat.type in ['group', 'supergroup']:
        await query.answer("❌ Бонус можно получить только в личных сообщениях с ботом!", show_alert=True)
        return

    user = UserManager.get_user(user_id)

    if not user:
        return

    bonus_data = UserManager.get_rodnoy_bonus_info(user_id)
    last_bonus_time = None

    if bonus_data and bonus_data[5]:
        last_bonus_time = datetime.strptime(bonus_data[5], "%Y-%m-%d %H:%M:%S")

    if last_bonus_time and (datetime.now() - last_bonus_time).total_seconds() < 12 * 3600:
        hours_left = 12 - (datetime.now() - last_bonus_time).total_seconds() / 3600
        await query.answer(
            f"❌ Бонус можно получить раз в 12 часов! Осталось {hours_left:.1f} ч.",
            show_alert=True
        )
        return

    subscriptions = UserManager.get_channel_subscriptions(user_id)
    subscribed_count = len(subscriptions)

    if subscribed_count >= 30:
        await query.answer(
            "❌ Вы уже подписались на все 30 каналов!",
            show_alert=True
        )
        return

    remaining_channels = []
    for i in range(30):
        if i not in subscriptions:
            remaining_channels.append(i)

    if not remaining_channels:
        await query.answer(
            "❌ Нет доступных каналов для подписки!",
            show_alert=True
        )
        return

    channel_index = remaining_channels[0]

    channel_link = CHANNEL_LINKS[channel_index]
    channel_name = CHANNEL_NAMES[channel_index]

    keyboard = [
        [InlineKeyboardButton("📢 Подписаться", url=channel_link)],
        [InlineKeyboardButton("✅ Я подписался", callback_data=f"check_sub_{channel_index}")],
        [InlineKeyboardButton("◀️ Отмена", callback_data="rodnoy_bonus_page")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(
        f"#𝐑𝐃𝐍𝐎 𝐌𝐗\n\n"
        f"## ПОДПИШИТЕСЬ НА КАНАЛ\n\n"
        f"📢 Канал: {channel_name}\n"
        f"🔗 Ссылка: {channel_link}\n\n"
        f"После подписки нажмите кнопку 'Я подписался',\n"
        f"чтобы получить 20.000 монет!",
        reply_markup=reply_markup
    )

async def check_channel_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id

    channel_index = int(query.data.replace("check_sub_", ""))

    UserManager.add_channel_subscription(user_id, channel_index)

    bonus_amount = 20000
    await UserManager.update_rodnoy_bonus(user_id, bonus_amount, channel_index)

    keyboard = [
        [InlineKeyboardButton("🎁 Следующий канал", callback_data="show_channel_bonus")],
        [InlineKeyboardButton("◀️ Назад", callback_data="rodnoy_bonus_page")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    subscriptions = UserManager.get_channel_subscriptions(user_id)
    subscribed_count = len(subscriptions)

    await query.message.edit_text(
        f"#𝐑𝐃𝐍𝐎 𝐌𝐗\n\n"
        f"## 🎁 БОНУС ПОЛУЧЕН!\n\n"
        f"💰 +20.000 🪙\n\n"
        f"✅ Спасибо за подписку!\n"
        f"📊 Каналов подписано: {subscribed_count}/30\n\n"
        f"Следующий бонус через 12 часов.",
        reply_markup=reply_markup
    )
    await query.answer(f"🎁 +20.000 монет получено!")

async def handle_premium_1_info(update, context):
    query = update.callback_query
    user_id = query.from_user.id

    keyboard = [
        [InlineKeyboardButton("💳 Купить Premium 1 (200 руб)", url=f"https://t.me/{ADMIN_USERNAME[1:]}")],
        [InlineKeyboardButton("🌐 ВЕБ ПРИЛОЖЕНИЕ", url=WEBAPP_URL)],
        [InlineKeyboardButton("◀️ Назад", callback_data="rodnoy_bonus_page")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    premium_text = (
        f"#𝐑𝐃𝐍𝐎 𝐌𝐗\n\n"
        f"## 💰 PREMIUM 1\n\n"
        f"💰 Цена: 200 руб\n"
        f"⏰ Срок: 30 дней\n\n"
        f"**Преимущества:**\n"
        f"• 40.000 монет ежедневно\n"
        f"• Не нужно подписываться на каналы\n"
        f"• Приоритетная поддержка\n"
        f"• Доступ к турнирам\n\n"
        f"**Для покупки:**\n"
        f"1. Нажмите кнопку 'Купить Premium 1'\n"
        f"2. Отправьте 200 руб администратору\n"
        f"3. Отправьте скриншот оплаты\n"
        f"4. Ваш ID: {user_id}\n\n"
        f"💡 После оплаты Premium активируется в течение 5 минут"
    )

    await query.message.edit_text(premium_text, reply_markup=reply_markup)

async def handle_premium_2_info(update, context):
    query = update.callback_query
    user_id = query.from_user.id

    keyboard = [
        [InlineKeyboardButton("💳 Купить Premium 2 (300 руб)", url=f"https://t.me/{ADMIN_USERNAME[1:]}")],
        [InlineKeyboardButton("🌐 ВЕБ ПРИЛОЖЕНИЕ", url=WEBAPP_URL)],
        [InlineKeyboardButton("◀️ Назад", callback_data="rodnoy_bonus_page")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    premium_text = (
        f"#𝐑𝐃𝐍𝐎 𝐌𝐗\n\n"
        f"## 💎 PREMIUM 2\n\n"
        f"💰 Цена: 300 руб\n"
        f"⏰ Срок: 30 дней\n\n"
        f"**Преимущества:**\n"
        f"• 60.000 монет ежедневно\n"
        f"• Не нужно подписываться на каналы\n"
        f"• Приоритетная поддержка\n"
        f"• Участие в турнирах\n"
        f"• Доступ к эксклюзивным играм\n\n"
        f"**Для покупки:**\n"
        f"1. Нажмите кнопку 'Купить Premium 2'\n"
        f"2. Отправьте 300 руб администратору\n"
        f"3. Отправьте скриншот оплаты\n"
        f"4. Ваш ID: {user_id}\n\n"
        f"💡 После оплаты Premium активируется в течение 5 минут"
    )

    await query.message.edit_text(premium_text, reply_markup=reply_markup)

async def show_rodnoy_roles_menu(update, context):
    query = update.callback_query
    user_id = query.from_user.id

    role_data = UserManager.get_user_role(user_id)

    current_role = "Нет"
    role_expires = ""

    if role_data:
        current_role = role_data[0]
        if role_data[1]:
            expire_date = datetime.strptime(role_data[1], "%Y-%m-%d %H:%M:%S")
            role_expires = expire_date.strftime("%d.%m.%Y %H:%M")

    keyboard = [
        [InlineKeyboardButton("👑 Вор в законе", callback_data="rodnoy_buy_thief")],
        [InlineKeyboardButton("👮 Полицейский", callback_data="rodnoy_buy_police")],
        [InlineKeyboardButton("ℹ️ Информация", callback_data="rodnoy_roles_info")],
        [InlineKeyboardButton("🌐 ВЕБ ПРИЛОЖЕНИЕ", url=WEBAPP_URL)],
        [InlineKeyboardButton("◀️ Назад", callback_data="rodnoy_main_menu")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    roles_text = (
        f"#𝐑𝐃𝐍𝐎 𝐌𝐗\n\n"
        f"## 🎭 РОЛИ\n\n"
        f"📊 Текущая роль: {current_role}\n"
        f"⏰ Действует: {role_expires if role_expires else 'Нет'}\n\n"
        f"🛒 **Доступные роли:**\n\n"
        f"👑 **Вор в законе** - 4,000₽ / 30 дней\n"
        f"   • Возможность красть монеты у других игроков\n"
        f"   • Защищен от некоторых ограничений\n\n"
        f"👮 **Полицейский** - 2,000₽ / 30 дней\n"
        f"   • Защищен от Вора в законе\n"
        f"   • Возможность ловить воров\n\n"
        f"👇 Выберите роль для покупки:"
    )

    await query.message.edit_text(roles_text, reply_markup=reply_markup)

async def handle_rodnoy_buy_thief(update, context):
    query = update.callback_query
    user_id = query.from_user.id

    keyboard = [
        [InlineKeyboardButton("💳 Купить за 4,000₽", url=f"https://t.me/{ADMIN_USERNAME[1:]}")],
        [InlineKeyboardButton("🌐 ВЕБ ПРИЛОЖЕНИЕ", url=WEBAPP_URL)],
        [InlineKeyboardButton("◀️ Назад", callback_data="rodnoy_roles")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    thief_text = (
        f"#𝐑𝐃𝐍𝐎 𝐌𝐗\n\n"
        f"## 👑 ВОР В ЗАКОНЕ\n\n"
        f"💰 Цена: 4,000₽\n"
        f"⏰ Срок: 30 дней\n\n"
        f"**Преимущества:**\n"
        f"• Возможность красть монеты у других игроков\n"
        f"• Команда: ответьте на сообщение игрока и напишите 'вор -9000'\n"
        f"• Защищен от некоторых ограничений\n"
        f"• Автоматически снимается через 30 дней\n\n"
        f"**Для покупки:**\n"
        f"1. Нажмите кнопку 'Купить за 4,000₽'\n"
        f"2. Отправьте 4,000₽ администратору\n"
        f"3. Отправьте скриншот оплаты\n"
        f"4. Ваш ID: {user_id}\n\n"
        f"💡 После оплаты роль активируется в течение 5 минут"
    )

    await query.message.edit_text(thief_text, reply_markup=reply_markup)

async def handle_rodnoy_buy_police(update, context):
    query = update.callback_query
    user_id = query.from_user.id

    keyboard = [
        [InlineKeyboardButton("💳 Купить за 2,000₽", url=f"https://t.me/{ADMIN_USERNAME[1:]}")],
        [InlineKeyboardButton("🌐 ВЕБ ПРИЛОЖЕНИЕ", url=WEBAPP_URL)],
        [InlineKeyboardButton("◀️ Назад", callback_data="rodnoy_roles")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    police_text = (
        f"#𝐑𝐃𝐍𝐎 𝐌𝐗\n\n"
        f"## 👮 ПОЛИЦЕЙСКИЙ\n\n"
        f"💰 Цена: 2,000₽\n"
        f"⏰ Срок: 30 дней\n\n"
        f"**Преимущества:**\n"
        f"• Защищен от Вора в законе\n"
        f"• Возможность ловить воров\n"
        f"• Команда: 'полиция' для защиты\n"
        f"• Автоматически снимается через 30 дней\n\n"
        f"**Для покупки:**\n"
        f"1. Нажмите кнопку 'Купить за 2,000₽'\n"
        f"2. Отправьте 2,000₽ администратору\n"
        f"3. Отправьте скриншот оплаты\n"
        f"4. Ваш ID: {user_id}\n\n"
        f"💡 После оплаты роль активируется в течение 5 минут"
    )

    await query.message.edit_text(police_text, reply_markup=reply_markup)

async def show_rodnoy_rating_page(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    user = UserManager.get_user(user_id)

    top_users = UserManager.get_global_top_users(10)

    user_position = UserManager.get_user_position_by_balance(user_id)

    rating_text = f"#𝐑𝐃𝐍𝐎 𝐌𝐗\n\n## РЕЙТИНГ\n\n"
    rating_text += "| Игрок | Баланс |\n"
    rating_text += "|-------|--------|\n"

    for i, (top_user_id, display_name, username, first_name, balance) in enumerate(top_users, 1):
        if display_name:
            name = display_name
        elif username:
            name = username
        else:
            name = first_name

        if len(name) > 15:
            name = name[:12] + "..."

        rating_text += f"| **{i}. {name}** | {balance:,} |\n"

    if user[15]:
        display_name = user[15]
    elif user[1]:
        display_name = user[1]
    else:
        display_name = user[2]

    rating_text += f"\n📊 **Ваша позиция:** {user_position}\n"
    rating_text += f"👤 **Вы:** {display_name}\n"
    rating_text += f"💰 **Ваш баланс:** {user[3]:,} 🪙"

    keyboard = [
        [InlineKeyboardButton("🔄 Обновить", callback_data="rodnoy_rating")],
        [InlineKeyboardButton("🌐 ВЕБ ПРИЛОЖЕНИЕ", url=WEBAPP_URL)],
        [InlineKeyboardButton("◀️ Назад", callback_data="rodnoy_main_menu")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(rating_text, reply_markup=reply_markup)

async def show_rodnoy_settings(update, context):
    query = update.callback_query

    keyboard = [
        [InlineKeyboardButton("👤 Профиль", callback_data="rodnoy_profile_settings")],
        [InlineKeyboardButton("🔔 Уведомления", callback_data="rodnoy_notifications")],
        [InlineKeyboardButton("🌙 Внешний вид", callback_data="rodnoy_appearance")],
        [InlineKeyboardButton("🔒 Конфиденциальность", callback_data="rodnoy_privacy")],
        [InlineKeyboardButton("🌐 ВЕБ ПРИЛОЖЕНИЕ", url=WEBAPP_URL)],
        [InlineKeyboardButton("◀️ Назад", callback_data="rodnoy_main_menu")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    settings_text = (
        f"#𝐑𝐃𝐍𝐎 𝐌𝐗\n\n"
        f"## ⚙️ НАСТРОЙКИ\n\n"
        f"👇 Настройте приложение под себя:\n\n"
        f"👤 **Профиль** - настройки профиля и отображение\n"
        f"🔔 **Уведомления** - управление уведомлений\n"
        f"🌙 **Внешний вид** - тема и дизайн\n"
        f"🔒 **Конфиденциальность** - настройки конфиденциальности\n\n"
        f"С любовью создано 𝐑𝐃𝐍𝐎 𝐌𝐗 Technologies, 1.0.2"
    )

    await query.message.edit_text(settings_text, reply_markup=reply_markup)

async def show_rodnoy_games_menu(update, context):
    query = update.callback_query

    keyboard = [
        [InlineKeyboardButton("🎰 Рулетка", callback_data="rodnoy_roulette_game")],
        [InlineKeyboardButton("🎴 Бандит", callback_data="rodnoy_bandit_game")],
        [InlineKeyboardButton("🃏 BlackJack", callback_data="rodnoy_blackjack")],
        [InlineKeyboardButton("✈️ Крэш", callback_data="rodnoy_crash_game")],
        [InlineKeyboardButton("🃏 Дурак (веб)", url=f"{WEBAPP_URL}")],
    ]

    keyboard.append([InlineKeyboardButton("🌐 ВЕБ ПРИЛОЖЕНИЕ", url=WEBAPP_URL)])
    keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="rodnoy_main_menu")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    games_text = (
        f"#𝐑𝐃𝐍𝐎 𝐌𝐗\n\n"
        f"## 🎮 ИГРЫ\n\n"
        f"👇 Играть в игры:\n\n"
        f"🎰 **Рулетка** - угадайте число или цвет\n"
        f"🎴 **Бандит** - соберите одинаковые символы\n"
        f"🃏 **BlackJack** - играйте в блэкджек\n"
        f"🌐 **Веб приложение:**\n"
        f"• 💥 Крэш - самолет летит, забери выигрыш вовремя!\n"
        f"• 🃏 Дурак - карточная игра с друзьями\n\n"
        f"🏆 Участвуйте и выигрывайте призы!"
    )

    await query.message.edit_text(games_text, reply_markup=reply_markup)

async def show_rodnoy_links(update, context):
    query = update.callback_query

    links_text = (
        f"\u203c\ufe0fВсе свежие новости и обновления нашего бота вы сможете найти на нашем канале - \U0001f4b0https://t.me/MX_KASSA\U0001f4b0\n\n"
        f"Актуальная информация о донате: https://t.me/MX_KASSA\n\n"
        f"Основные игровые чаты для вас:\n\n"
        f"1. \U0001f607 Райская РУЛЕТКА \U0001f4b8 https://t.me/RAY_Roulette - чат для спокойных игроков со стандартным набором правил.\n"
        f"6. \U0001f381 Розыгрыш монет \U0001f381 - https://t.me/FREEMONETA1 - чат, где проводятся розыгрыши от администраторов официальных чатов.\n"
        f"9. \U0001f1f7\U0001f1fa Russia \U0001f1f7\U0001f1fa - https://t.me/VIPKGZ777 - \u203c\ufe0fNEW\u203c\ufe0f Чат для русскоязычных игроков\n"
        f"10. \U0001f1fa\U0001f1f8 English \U0001f1fa\U0001f1f8 - https://t.me/AMERICA_MX - \u203c\ufe0fNEW\u203c\ufe0f Чат для англоязычных игроков\n"
        f"11. \U0001f1fa\U0001f1ff Uzbekistan \U0001f1fa\U0001f1ff - https://t.me/Uzbekston3 - Чат для игроков Узбекистана\n"
        f"12. \U0001f1f0\U0001f1ff Kazakhstan \U0001f1f0\U0001f1ff - https://t.me/KAZAKHSTAN_MX - Чат для игроков Казахстана\n"
        f"13. \U0001f1fa\U0001f1e6 Ukraine \U0001f1fa\U0001f1e6 - https://t.me/UKRAINE_MX - Чат для игроков Украины\n"
        f"14. \U0001f1f0\U0001f1ec Kyrgyzstan \U0001f1f0\U0001f1ec - https://t.me/tanyshuu_kg1 - Чат для игроков Кыргызстана\n"
        f"15. \U0001f3c6 Tournaments \U0001f3c6 - https://t.me/VIPKGZ777 - Чат для проведения турниров"
    )

    keyboard = [
        [InlineKeyboardButton("◀️ Назад", callback_data="rodnoy_main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(links_text, reply_markup=reply_markup)

async def show_rodnoy_stickers(update, context):
    query = update.callback_query

    await query.message.reply_sticker(
        sticker="CAACAgIAAxkBAAEMRfRnfD1GgFqFqFqFqFqFqFqFqFqFqFqFqFqFqFqFqA"
    )

    keyboard = [
        [InlineKeyboardButton("◀️ Назад", callback_data="rodnoy_main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text("🎭 Вот наши стикеры!", reply_markup=reply_markup)

async def handle_thief_steal(update, context):
    user_id = update.effective_user.id

    role_data = UserManager.get_user_role(user_id)

    if not role_data or role_data[0] != "вор_в_законе":
        return

    if role_data[1]:
        expire_date = datetime.strptime(role_data[1], "%Y-%m-%d %H:%M:%S")
        if datetime.now() > expire_date:
            UserManager.remove_user_role(user_id)
            return

    if not update.message.reply_to_message:
        return

    target_user = update.message.reply_to_message.from_user
    target_id = target_user.id

    target_role = UserManager.get_user_role(target_id)

    if target_role and target_role[0] == "полицейский":
        await update.effective_chat.send_message(
            f"⚠️ <a href='tg://user?id={user_id}'>Вор</a> пытался украсть у <a href='tg://user?id={target_id}'>полицейского</a>, но был остановлен!",
            parse_mode='HTML'
        )
        return

    target_user_data = UserManager.get_user(target_id)
    if not target_user_data or target_user_data[3] < 1000:
        return

    text = update.message.text.lower()
    steal_amount = 0

    match = re.search(r'вор\s*(-?\s*\d+)', text)
    if match:
        try:
            steal_amount = int(match.group(1).replace(' ', '').replace('-', ''))
            if steal_amount < 0:
                steal_amount = abs(steal_amount)
        except:
            steal_amount = 0

    if steal_amount <= 0:
        target_balance = target_user_data[3]
        steal_amount = int(target_balance * random.uniform(0.1, 0.9))

        if steal_amount < 100:
            steal_amount = min(100, target_balance)

    max_steal = int(target_user_data[3] * 0.9)
    if steal_amount > max_steal:
        steal_amount = max_steal

    if steal_amount < 10:
        return

    await UserManager.update_balance(target_id, -steal_amount, f"Кража вором в законе: -{steal_amount}")
    await UserManager.update_balance(user_id, steal_amount, f"Кража как вор в законе: +{steal_amount}")

    target_name = target_user.first_name
    if target_user.username:
        target_name = target_user.username

    thief_name = update.effective_user.first_name
    if update.effective_user.username:
        thief_name = update.effective_user.username

    await update.effective_chat.send_message(
        f"💰 Вор в законе <a href='tg://user?id={user_id}'>{thief_name}</a>\n"
        f"👤 Украл у <a href='tg://user?id={target_id}'>{target_name}</a>: {steal_amount} монет!\n"
        f"💸 Новый баланс жертвы: {target_user_data[3] - steal_amount} 🪙",
        parse_mode='HTML'
    )

async def handle_police_protect(update, context):
    user_id = update.effective_user.id

    role_data = UserManager.get_user_role(user_id)

    if not role_data or role_data[0] != "полицейский":
        return

    if role_data[1]:
        expire_date = datetime.strptime(role_data[1], "%Y-%m-%d %H:%M:%S")
        if datetime.now() > expire_date:
            UserManager.remove_user_role(user_id)
            return

    police_name = update.effective_user.first_name
    if update.effective_user.username:
        police_name = update.effective_user.username

    await update.effective_chat.send_message(
        f"👮 Полицейский <a href='tg://user?id={user_id}'>{police_name}</a>\n"
        f"✅ Вы защищены от воров в законе на 24 часа!",
        parse_mode='HTML'
    )

async def handle_text_mute(update, context):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if not update.message.reply_to_message:
        await update.effective_chat.send_message("❌ Команда должна быть ответом на сообщение пользователя!")
        return

    is_admin = await is_group_admin(context, chat_id, user_id)

    if not (is_super_admin(user_id) or UserManager.has_permission(user_id, "mute") or is_admin):
        await update.effective_chat.send_message("❌ У вас нет прав на мутирование!")
        return

    target_user = update.message.reply_to_message.from_user
    target_id = target_user.id

    if target_id == user_id:
        await update.effective_chat.send_message("❌ Нельзя замутить самого себя!")
        return

    target_is_admin = await is_group_admin(context, chat_id, target_id)
    if target_is_admin and not is_super_admin(user_id):
        await update.effective_chat.send_message("❌ Нельзя замутить другого администратора!")
        return

    UserManager.mute_user(target_id, 24, user_id)

    target_name = target_user.first_name
    if target_user.username:
        target_name = target_user.username

    admin_name = update.effective_user.first_name
    if update.effective_user.username:
        admin_name = update.effective_user.username

    await update.effective_chat.send_message(
        f"🔇 Пользователь <a href='tg://user?id={target_id}'>{target_name}</a> замьючен на 24 часа!\n"
        f"👮 Администратор: <a href='tg://user?id={user_id}'>{admin_name}</a>",
        parse_mode='HTML'
    )

async def handle_text_unmute(update, context):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if not update.message.reply_to_message:
        await update.effective_chat.send_message("❌ Команда должна быть ответом на сообщение пользователя!")
        return

    is_admin = await is_group_admin(context, chat_id, user_id)

    if not (is_super_admin(user_id) or UserManager.has_permission(user_id, "mute") or is_admin):
        await update.effective_chat.send_message("❌ У вас нет прав на размучивание!")
        return

    target_user = update.message.reply_to_message.from_user
    target_id = target_user.id

    UserManager.unmute_user(target_id)

    target_name = target_user.first_name
    if target_user.username:
        target_name = target_user.username

    admin_name = update.effective_user.first_name
    if update.effective_user.username:
        admin_name = update.effective_user.username

    await update.effective_chat.send_message(
        f"🔊 Пользователь <a href='tg://user?id={target_id}'>{target_name}</a> размьючен!\n"
        f"👮 Администратор: <a href='tg://user?id={user_id}'>{admin_name}</a>",
        parse_mode='HTML'
    )

async def handle_text_ban(update, context):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if not update.message.reply_to_message:
        await update.effective_chat.send_message("❌ Команда должна быть ответом на сообщение пользователя!")
        return

    is_admin = await is_group_admin(context, chat_id, user_id)

    if not (is_super_admin(user_id) or UserManager.has_permission(user_id, "ban") or is_admin):
        await update.effective_chat.send_message("❌ У вас нет прав на бан!")
        return

    target_user = update.message.reply_to_message.from_user
    target_id = target_user.id

    if target_id == user_id:
        await update.effective_chat.send_message("❌ Нельзя забанить самого себя!")
        return

    target_is_admin = await is_group_admin(context, chat_id, target_id)
    if target_is_admin and not is_super_admin(user_id):
        await update.effective_chat.send_message("❌ Нельзя забанить другого администратора!")
        return

    UserManager.block_user(target_id, "Нарушение правил", user_id)

    target_name = target_user.first_name
    if target_user.username:
        target_name = target_user.username

    admin_name = update.effective_user.first_name
    if update.effective_user.username:
        admin_name = update.effective_user.username

    try:
        await context.bot.ban_chat_member(
            chat_id=update.effective_chat.id,
            user_id=target_id
        )
    except Exception as e:
        logger.error(f"Ошибка при бане в чате: {e}")

    await update.effective_chat.send_message(
        f"🚫 Пользователь <a href='tg://user?id={target_id}'>{target_name}</a> забанен!\n"
        f"📝 Причина: Нарушение правил\n"
        f"👮 Администратор: <a href='tg://user?id={user_id}'>{admin_name}</a>",
        parse_mode='HTML'
    )

async def handle_text_unban(update, context):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if not update.message.reply_to_message:
        await update.effective_chat.send_message("❌ Команда должна быть ответом на сообщение пользователя!")
        return

    is_admin = await is_group_admin(context, chat_id, user_id)

    if not (is_super_admin(user_id) or UserManager.has_permission(user_id, "ban") or is_admin):
        await update.effective_chat.send_message("❌ У вас нет прав на разбан!")
        return

    target_user = update.message.reply_to_message.from_user
    target_id = target_user.id

    UserManager.unblock_user(target_id)

    try:
        await context.bot.unban_chat_member(
            chat_id=update.effective_chat.id,
            user_id=target_id
        )
    except Exception as e:
        logger.error(f"Ошибка при разбане в чате: {e}")

    target_name = target_user.first_name
    if target_user.username:
        target_name = target_user.username

    admin_name = update.effective_user.first_name
    if update.effective_user.username:
        admin_name = update.effective_user.username

    await update.effective_chat.send_message(
        f"✅ Пользователь <a href='tg://user?id={target_id}'>{target_name}</a> разбанен!\n"
        f"👮 Администратор: <a href='tg://user?id={user_id}'>{admin_name}</a>",
        parse_mode='HTML'
    )

async def handle_mute_list_text(update, context):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    is_admin = await is_group_admin(context, chat_id, user_id)

    if not (is_super_admin(user_id) or UserManager.has_permission(user_id, "mute") or is_admin):
        await update.effective_chat.send_message("❌ У вас нет прав на просмотр мутов!")
        return

    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, mute_until, mute_by FROM users WHERE is_muted = 1")
        muted_users = cursor.fetchall()
        conn.close()
    except Exception as e:
        logger.error(f"Ошибка получения списка мутов: {e}")
        muted_users = []

    if not muted_users:
        await update.effective_chat.send_message("✅ Список мутов пуст!")
        return

    mute_list_text = "🔇 **СПИСОК ЗАМУЧЕННЫХ ПОЛЬЗОВАТЕЛЕЙ:**\n\n"

    for user_id, mute_until, mute_by in muted_users:
        user = UserManager.get_user(user_id)
        if user:
            if user[15]:
                name = user[15]
            elif user[1]:
                name = user[1]
            else:
                name = user[2]
        else:
            name = f"ID: {user_id}"

        admin = UserManager.get_user(mute_by) if mute_by else None
        if admin:
            if admin[15]:
                admin_name = admin[15]
            elif admin[1]:
                admin_name = admin[1]
            else:
                admin_name = admin[2]
        else:
            admin_name = f"ID: {mute_by}"

        mute_list_text += f"👤 <a href='tg://user?id={user_id}'>{name}</a> (ID: {user_id})\n"
        mute_list_text += f"⏰ До: {mute_until}\n"
        mute_list_text += f"👮 Замутил: {admin_name}\n"
        mute_list_text += "─" * 30 + "\n"

    await update.effective_chat.send_message(mute_list_text, parse_mode='HTML')

async def handle_ban_list_text(update, context):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    is_admin = await is_group_admin(context, chat_id, user_id)

    if not (is_super_admin(user_id) or UserManager.has_permission(user_id, "ban") or is_admin):
        await update.effective_chat.send_message("❌ У вас нет прав на просмотр банов!")
        return

    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, reason, blocked_by, blocked_at FROM blocked_users")
        banned_users = cursor.fetchall()
        conn.close()
    except Exception as e:
        logger.error(f"Ошибка получения списка банов: {e}")
        banned_users = []

    if not banned_users:
        await update.effective_chat.send_message("✅ Список банов пуст!")
        return

    ban_list_text = "🚫 **СПИСОК ЗАБАНЕННЫХ ПОЛЬЗОВАТЕЛЕЙ:**\n\n"

    for user_id, reason, blocked_by, blocked_at in banned_users:
        user = UserManager.get_user(user_id)
        if user:
            if user[15]:
                name = user[15]
            elif user[1]:
                name = user[1]
            else:
                name = user[2]
        else:
            name = f"ID: {user_id}"

        admin = UserManager.get_user(blocked_by)
        if admin:
            if admin[15]:
                admin_name = admin[15]
            elif admin[1]:
                admin_name = admin[1]
            else:
                admin_name = admin[2]
        else:
            admin_name = f"ID: {blocked_by}"

        ban_list_text += f"👤 <a href='tg://user?id={user_id}'>{name}</a> (ID: {user_id})\n"
        ban_list_text += f"📝 Причина: {reason}\n"
        ban_list_text += f"👮 Забанил: {admin_name}\n"
        ban_list_text += f"🕐 Дата: {blocked_at}\n"
        ban_list_text += "─" * 30 + "\n"

    await update.effective_chat.send_message(ban_list_text, parse_mode='HTML')

async def handle_mutdan_command(update, context):
    await handle_mute_list_text(update, context)

async def handle_bandan_command(update, context):
    await handle_ban_list_text(update, context)

async def handle_razmut_username(update, context):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    is_admin = await is_group_admin(context, chat_id, user_id)

    if not (is_super_admin(user_id) or UserManager.has_permission(user_id, "mute") or is_admin):
        await update.effective_chat.send_message("❌ У вас нет прав на размучивание!")
        return

    text = update.message.text.strip()
    words = text.split()

    if len(words) < 2:
        await update.effective_chat.send_message("❌ Формат: размут @username\nИли: размут <user_id>")
        return

    target_identifier = words[1]

    if target_identifier.startswith('@'):
        username = target_identifier[1:].lower()

        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users WHERE username LIKE ?", (f'%{username}%',))
            result = cursor.fetchone()
            conn.close()
        except Exception as e:
            logger.error(f"Ошибка поиска пользователя: {e}")
            result = None

        if not result:
            await update.effective_chat.send_message(f"❌ Пользователь @{username} не найден!")
            return

        target_id = result[0]

    elif target_identifier.isdigit():
        target_id = int(target_identifier)

    else:
        await update.effective_chat.send_message("❌ Неверный формат! Используйте: размут @username или размут <id>")
        return

    user = UserManager.get_user(target_id)
    if not user:
        await update.effective_chat.send_message("❌ Пользователь не найден!")
        return

    UserManager.unmute_user(target_id)

    target_name = user[15] if user[15] else (user[1] if user[1] else user[2])
    admin_name = update.effective_user.first_name
    if update.effective_user.username:
        admin_name = update.effective_user.username

    await update.effective_chat.send_message(
        f"🔊 Пользователь <a href='tg://user?id={target_id}'>{target_name}</a> размьючен!\n"
        f"👮 Администратор: <a href='tg://user?id={user_id}'>{admin_name}</a>",
        parse_mode='HTML'
    )

async def handle_razban_username(update, context):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    is_admin = await is_group_admin(context, chat_id, user_id)

    if not (is_super_admin(user_id) or UserManager.has_permission(user_id, "ban") or is_admin):
        await update.effective_chat.send_message("❌ У вас нет прав на разбан!")
        return

    text = update.message.text.strip()
    words = text.split()

    if len(words) < 2:
        await update.effective_chat.send_message("❌ Формат: разбан @username\nИли: разбан <user_id>")
        return

    target_identifier = words[1]

    if target_identifier.startswith('@'):
        username = target_identifier[1:].lower()

        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users WHERE username LIKE ?", (f'%{username}%',))
            result = cursor.fetchone()
            conn.close()
        except Exception as e:
            logger.error(f"Ошибка поиска пользователя: {e}")
            result = None

        if not result:
            await update.effective_chat.send_message(f"❌ Пользователь @{username} не найден!")
            return

        target_id = result[0]

    elif target_identifier.isdigit():
        target_id = int(target_identifier)

    else:
        await update.effective_chat.send_message("❌ Неверный формат! Используйте: разбан @username или разбан <id>")
        return

    user = UserManager.get_user(target_id)
    if not user:
        await update.effective_chat.send_message("❌ Пользователь не найден!")
        return

    UserManager.unblock_user(target_id)

    try:
        await context.bot.unban_chat_member(
            chat_id=update.effective_chat.id,
            user_id=target_id
        )
    except Exception as e:
        logger.error(f"Ошибка при разбане в чате: {e}")

    target_name = user[15] if user[15] else (user[1] if user[1] else user[2])
    admin_name = update.effective_user.first_name
    if update.effective_user.username:
        admin_name = update.effective_user.username

    await update.effective_chat.send_message(
        f"✅ Пользователь <a href='tg://user?id={target_id}'>{target_name}</a> разбанен!\n"
        f"👮 Администратор: <a href='tg://user?id={user_id}'>{admin_name}</a>",
        parse_mode='HTML'
    )

async def handle_dai_admin_command(update, context):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if not is_super_admin(user_id):
        await update.effective_chat.send_message("❌ Эта команда только для главного администратора!")
        return

    if not update.message.reply_to_message:
        await update.effective_chat.send_message("❌ Команда должна быть ответом на сообщение пользователя!")
        return

    target_user = update.message.reply_to_message.from_user
    target_id = target_user.id

    text = update.message.text.strip()
    words = text.split()

    if len(words) < 2:
        await update.effective_chat.send_message(
            "❌ Формат команды: дай админ <тип>\n\n"
            "📋 Примеры:\n"
            "• дай админ мут - дать право на мут\n"
            "• дай админ бан - дать право на бан\n"
            "• дай админ все - дать все права\n\n"
            "💡 Пользователь сможет использовать:\n"
            "• мут/размут\n"
            "• бан/разбан\n"
            "• мут список/бан список"
        )
        return

    permission_type = words[2].lower()

    if permission_type == "мут":
        UserManager.grant_permission(chat_id, target_id, "mute", user_id)
        message = f"✅ Пользователю дано право на мут!"
    elif permission_type == "бан":
        UserManager.grant_permission(chat_id, target_id, "ban", user_id)
        message = f"✅ Пользователю дано право на бан!"
    elif permission_type == "все":
        UserManager.grant_permission(chat_id, target_id, "all", user_id)
        message = f"✅ Пользователю даны все права (мут и бан)!"
    else:
        await update.effective_chat.send_message("❌ Неверный тип прав! Используйте: мут, бан или все")
        return

    target_name = target_user.first_name
    if target_user.username:
        target_name = target_user.username

    await update.effective_chat.send_message(
        f"{message}\n\n"
        f"👤 Пользователь: <a href='tg://user?id={target_id}'>{target_name}</a>\n"
        f"🆔 ID: {target_id}\n"
        f"🎯 Права: {permission_type}",
        parse_mode='HTML'
    )

async def handle_uberi_admin_command(update, context):
    user_id = update.effective_user.id

    if not is_super_admin(user_id):
        await update.effective_chat.send_message("❌ Эта команда только для главного администратора!")
        return

    if not update.message.reply_to_message:
        await update.effective_chat.send_message("❌ Команда должна быть ответом на сообщение пользователя!")
        return

    target_user = update.message.reply_to_message.from_user
    target_id = target_user.id

    text = update.message.text.strip()
    words = text.split()

    if len(words) < 2:
        await update.effective_chat.send_message(
            "❌ Формат команды: убери админ <тип>\n\n"
            "📋 Примеры:\n"
            "• убери админ мут - убрать право на мут\n"
            "• убери админ бан - убрать право на бан\n"
            "• убери админ все - убрать все права"
        )
        return

    permission_type = words[2].lower()

    if permission_type == "мут":
        UserManager.revoke_permission(target_id, "mute")
        message = f"✅ У пользователя убрано право на мут!"
    elif permission_type == "бан":
        UserManager.revoke_permission(target_id, "ban")
        message = f"✅ У пользователя убрано право на бан!"
    elif permission_type == "все":
        UserManager.revoke_permission(target_id, "all")
        message = f"✅ У пользователя убраны все права!"
    else:
        await update.effective_chat.send_message("❌ Неверный тип прав! Используйте: мут, бан или все")
        return

    target_name = target_user.first_name
    if target_user.username:
        target_name = target_user.username

    await update.effective_chat.send_message(
        f"{message}\n\n"
        f"👤 Пользователь: <a href='tg://user?id={target_id}'>{target_name}</a>\n"
        f"🆔 ID: {target_id}\n"
        f"🎯 Убраны права: {permission_type}",
        parse_mode='HTML'
    )

async def handle_tournament_register(update, context):
    user_id = update.effective_user.id
    user = UserManager.get_user(user_id)

    if not user:
        return

    username = update.effective_user.username or update.effective_user.first_name

    paid_premium = UserManager.get_paid_premium_info(user_id)
    if not paid_premium:
        await update.effective_chat.send_message(
            "❌ Для участия в турнире нужен платный Premium!\n\n"
            "💰 Premium 1: 200 руб/мес - 40.000 монет/день\n"
            "💎 Premium 2: 300 руб/мес - 60.000 монет/день"
        )
        return

    UserManager.register_for_tournament(user_id, username)
    chat_manager.add_tournament_participant(user_id, username)

    await update.effective_chat.send_message(
        f"✅ Вы зарегистрированы на турнир!\n\n"
        f"👤 Участник: {username}\n"
        f"🆔 ID: {user_id}\n\n"
        f"📊 Зарегистрировано: {chat_manager.get_tournament_participants_count()}/150\n"
        f"💰 Призовой фонд: 650.000.000 🪙"
    )

async def handle_tournament_start(update, context):
    user_id = update.effective_user.id

    if not is_super_admin(user_id):
        await update.effective_chat.send_message("❌ Эта команда только для администратора!")
        return

    if chat_manager.tournament_active:
        await update.effective_chat.send_message("❌ Турнир уже запущен!")
        return

    participants = UserManager.get_tournament_registrations()
    if len(participants) < 10:
        await update.effective_chat.send_message(f"❌ Недостаточно участников! Нужно минимум 10, сейчас: {len(participants)}")
        return

    chat_manager.tournament_active = True
    chat_manager.tournament_start_time = datetime.now()

    for participant_id, username in participants:
        await UserManager.update_balance(participant_id, 1000000, f"Стартовый бонус турнира")

    await update.effective_chat.send_message(
        f"🎮 **ТУРНИР НАЧАТ!**\n\n"
        f"📊 Участников: {len(participants)}\n"
        f"💰 Стартовый бонус: 1.000.000 🪙 каждому\n"
        f"⏰ Начало: {datetime.now().strftime('%H:%M:%S')}\n\n"
        f"🔔 Внимание! Турнир продлится 24 часа.\n"
        f"🏆 Победители будут определены автоматически."
    )

    asyncio.create_task(finish_tournament_after_delay(context))

async def finish_tournament_after_delay(context):
    await asyncio.sleep(86400)
    await finish_tournament(context)

async def finish_tournament(context):
    if not chat_manager.tournament_active:
        return

    participants = UserManager.get_tournament_registrations()

    if not participants:
        return

    participants_with_balance = []
    for user_id, username in participants:
        user = UserManager.get_user(user_id)
        if user:
            participants_with_balance.append((user_id, username, user[3]))

    participants_with_balance.sort(key=lambda x: x[2], reverse=True)

    winners = participants_with_balance[:10]

    prizes = [
        (1, "3 месяца Premium"),
        (2, 100000000),
        (3, 90000000),
        (4, 80000000),
        (5, 70000000),
        (6, 50000000),
        (7, 50000000),
        (8, 50000000),
        (9, 50000000),
        (10, 50000000),
    ]

    results_text = "🏆 **РЕЗУЛЬТАТЫ ТУРНИРА** 🏆\n\n"

    for i, (position, prize) in enumerate(prizes):
        if i < len(winners):
            user_id, username, balance = winners[i]

            if position == 1:
                results_text += f"🥇 1. <a href='tg://user?id={user_id}'>{username}</a>\n"
                results_text += f"   🎁 Приз: {prize}\n"
            else:
                results_text += f"#{position}. <a href='tg://user?id={user_id}'>{username}</a>\n"
                results_text += f"   💰 Приз: {prize:,} 🪙\n"
                await UserManager.add_tournament_winner(user_id, username, position, prize)

            results_text += f"   📊 Баланс: {balance:,} 🪙\n\n"

    results_text += f"\n🎯 Всего участников: {len(participants)}\n"
    results_text += f"💰 Общий призовой фонд: 650.000.000 🪙\n"
    results_text += f"⏰ Турнир завершен: {datetime.now().strftime('%d.%m.%Y %H:%M')}"

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=results_text,
        parse_mode='HTML'
    )

    UserManager.clear_tournament_registrations()
    chat_manager.clear_tournament()

    chat_manager.tournament_active = False

async def handle_tournament_status(update, context):
    participants = UserManager.get_tournament_registrations()

    status_text = "🏆 **СТАТУС ТУРНИРА**\n\n"

    if chat_manager.tournament_active:
        status_text += "🔵 **Турнир активен**\n"
        if chat_manager.tournament_start_time:
            elapsed = datetime.now() - chat_manager.tournament_start_time
            hours_left = 24 - (elapsed.total_seconds() / 3600)
            status_text += f"⏰ Осталось: {hours_left:.1f} часов\n"
    else:
        status_text += "🔴 **Турнир не активен**\n"

    status_text += f"📊 Зарегистрировано: {len(participants)}/150\n\n"

    if participants:
        status_text += "📋 **Зарегистрированные участники:**\n"
        for i, (user_id, username) in enumerate(participants[:10], 1):
            status_text += f"{i}. {username}\n"

        if len(participants) > 10:
            status_text += f"... и еще {len(participants) - 10} участников\n"

    status_text += "\n💰 **Призовые места:**\n"
    status_text += "1️⃣ 3 месяца Premium\n"
    status_text += "2️⃣ 100.000.000 🪙\n"
    status_text += "3️⃣ 90.000.000 🪙\n"
    status_text += "4️⃣ 80.000.000 🪙\n"
    status_text += "5️⃣ 70.000.000 🪙\n"
    status_text += "6️⃣-🔟 50.000.000 🪙"

    await update.effective_chat.send_message(status_text)

async def handle_give_role_command(update, context):
    user_id = update.effective_user.id

    if not is_super_admin(user_id):
        await update.effective_chat.send_message("❌ Эта команда только для администратора!")
        return

    text = update.message.text.strip()
    words = text.split()

    if len(words) < 4:
        await update.effective_chat.send_message(
            "❌ Формат: /giverole <user_id> <role> <days>\n\n"
            "📋 Примеры:\n"
            "• /giverole 123456789 вор 30 - вор в законе на 30 дней\n"
            "• /giverole 123456789 полиция 30 - полицейский на 30 дней\n"
            "• /giverole 123456789 вор 7 - вор в законе на 7 дней"
        )
        return

    try:
        target_user_id = int(words[1])
        role_type = words[2].lower()
        days = int(words[3])

        if days <= 0:
            await update.effective_chat.send_message("❌ Количество дней должно быть положительным!")
            return

        target_user = UserManager.get_user(target_user_id)
        if not target_user:
            await update.effective_chat.send_message("❌ Пользователь не найден!")
            return

        if role_type in ["вор", "thief", "вор_в_законе"]:
            role_name = "вор_в_законе"
            role_display = "👑 Вор в законе"
            price = "4,000₽"
        elif role_type in ["полиция", "police", "полицейский"]:
            role_name = "полицейский"
            role_display = "👮 Полицейский"
            price = "2,000₽"
        else:
            await update.effective_chat.send_message("❌ Неизвестная роль! Доступные: 'вор' или 'полиция'")
            return

        UserManager.set_user_role(target_user_id, role_name, days)

        target_name = target_user[15] if target_user[15] else (target_user[1] if target_user[1] else target_user[2])

        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text=f"🎭 Вам выдана роль!\n\n"
                     f"📛 Роль: {role_display}\n"
                     f"⏰ Срок: {days} дней\n"
                     f"💰 Цена: {price}\n\n"
                     f"✅ Роль активирована!\n\n"
                     f"💡 Команды:\n"
                     f"• Вор в законе: ответьте на сообщение 'вор -9000'\n"
                     f"• Полицейский: 'полиция'\n"
                     f"📅 Роль автоматически снимет: через {days} дней"
            )
        except:
            pass

        await update.effective_chat.send_message(
            f"✅ Роль выдана!\n\n"
            f"👤 Пользователь: {target_name}\n"
            f"🆔 ID: {target_user_id}\n"
            f"🎭 Роль: {role_display}\n"
            f"⏰ Срок: {days} дней\n"
            f"💰 Цена: {price}\n\n"
            f"📊 Роль активирована!"
        )

    except ValueError:
        await update.effective_chat.send_message("❌ Неверный формат! Введите числа правильно.")

async def handle_remove_role_command(update, context):
    user_id = update.effective_user.id

    if not is_super_admin(user_id):
        await update.effective_chat.send_message("❌ Эта команда только для администратора!")
        return

    text = update.message.text.strip()
    words = text.split()

    if len(words) < 2:
        await update.effective_chat.send_message("❌ Формат: /removerole <user_id>")
        return

    try:
        target_user_id = int(words[1])

        target_user = UserManager.get_user(target_user_id)
        if not target_user:
            await update.effective_chat.send_message("❌ Пользователь не найден!")
            return

        role_data = UserManager.get_user_role(target_user_id)

        if not role_data:
            await update.effective_chat.send_message("❌ У этого пользователя нет роли!")
            return

        UserManager.remove_user_role(target_user_id)

        target_name = target_user[15] if target_user[15] else (target_user[1] if target_user[1] else target_user[2])

        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text=f"🎭 Ваша роль снята!\n\n"
                     f"📛 Роль: {role_data[0]}\n"
                     f"⚠️ Ваша роль снята администратором\n\n"
                     f"💡 Для покупки новой роли зайдите в магазин."
            )
        except:
            pass

        await update.effective_chat.send_message(
            f"✅ Роль снята!\n\n"
            f"👤 Пользователь: {target_name}\n"
            f"🆔 ID: {target_user_id}\n"
            f"🎭 Роль: {role_data[0]}\n\n"
            f"📊 Роль деактивирована!"
        )

    except ValueError:
        await update.effective_chat.send_message("❌ Неверный формат!")

async def handle_addcoins_command(update, context):
    user_id = update.effective_user.id

    if not is_super_admin(user_id):
        await update.effective_chat.send_message("❌ Эта команда только для администратора!")
        return

    text = update.message.text.strip()
    words = text.split()

    if len(words) < 3:
        await update.effective_chat.send_message("❌ Формат команды: /addcoins <user_id> <amount>")
        return

    try:
        target_user_id = int(words[1])
        amount = int(words[2])

        if amount <= 0:
            await update.effective_chat.send_message("❌ Сумма должна быть положительной!")
            return

        user = UserManager.get_user(target_user_id)
        if not user:
            await update.effective_chat.send_message("❌ Пользователь не найден!")
            return

        await UserManager.add_coins_to_user(target_user_id, amount)

        target_name = user[15] if user[15] else (user[1] if user[1] else user[2])
        await update.effective_chat.send_message(f"✅ Пользователю {target_name} добавлено {amount} монет!\nНовый баланс: {user[3] + amount} 🪙")

    except ValueError:
        await update.effective_chat.send_message("❌ Неверный формат! Используйте: /addcoins <user_id> <amount>")

async def handle_removecoins_command(update, context):
    user_id = update.effective_user.id

    if not is_super_admin(user_id):
        await update.effective_chat.send_message("❌ Эта команда только для администратора!")
        return

    text = update.message.text.strip()
    words = text.split()

    if len(words) < 3:
        await update.effective_chat.send_message("❌ Формат команды: /removecoins <user_id> <amount>")
        return

    try:
        target_user_id = int(words[1])
        amount = int(words[2])

        if amount <= 0:
            await update.effective_chat.send_message("❌ Сумма должна быть положительной!")
            return

        user = UserManager.get_user(target_user_id)
        if not user:
            await update.effective_chat.send_message("❌ Пользователь не найден!")
            return

        success, removed_amount = await UserManager.remove_coins_from_user(target_user_id, amount)

        if success:
            target_name = user[15] if user[15] else (user[1] if user[1] else user[2])
            await update.effective_chat.send_message(f"✅ У пользователя {target_name} убрано {removed_amount} монет!\nНовый баланс: {max(0, user[3] - removed_amount)} 🪙")
        else:
            await update.effective_chat.send_message("❌ Ошибка при удалении монет!")

    except ValueError:
        await update.effective_chat.send_message("❌ Неверный формат! Используйте: /removecoins <user_id> <amount>")

async def handle_setlimit_command(update, context):
    user_id = update.effective_user.id

    if not is_super_admin(user_id):
        await update.effective_chat.send_message("❌ Эта команда только для администратора!")
        return

    text = update.message.text.strip()
    words = text.split()

    if len(words) < 4:
        await update.effective_chat.send_message(
            "❌ Формат команды: /setlimit <user_id> <тип> <лимит>\n\n"
            "📋 Примеры:\n"
            "• /setlimit 123456789 transfer 50000 - установить лимит перевода 50000 монет\n"
            "• /setlimit 123456789 roulette 5000000 - установить лимит рулетки 5 млн\n\n"
            "💡 Можно установить очень большие значения:\n"
            "• /setlimit 123456789 transfer 999999999\n"
            "• /setlimit 123456789 roulette 999999999"
        )
        return

    try:
        target_user_id = int(words[1])
        limit_type = words[2].lower()
        limit = int(words[3])

        if limit <= 0:
            await update.effective_chat.send_message("❌ Лимит должен быть положительным!")
            return

        user = UserManager.get_user(target_user_id)
        if not user:
            await update.effective_chat.send_message("❌ Пользователь не найден!")
            return

        if limit_type == "roulette":
            UserManager.set_roulette_limit(target_user_id, limit)
            target_name = user[15] if user[15] else (user[1] if user[1] else user[2])
            await update.effective_chat.send_message(
                f"✅ Лимит рулетки для пользователя {target_name} (ID: {target_user_id})\n"
                f"Установлен: {limit:,} монет 🪙\n\n"
                f"Теперь он может ставить до {limit:,} монет в рулетке!"
            )
        elif limit_type == "transfer":
            UserManager.set_transfer_limit(target_user_id, limit)
            target_name = user[15] if user[15] else (user[1] if user[1] else user[2])
            await update.effective_chat.send_message(
                f"✅ Лимит перевода для пользователя {target_name} (ID: {target_user_id})\n"
                f"Установлен: {limit:,} монет 🪙 за {TRANSFER_COOLDOWN_HOURS} часов\n\n"
                f"Теперь он может переводить до {limit:,} монет каждые {TRANSFER_COOLDOWN_HOURS} часов!"
            )
        else:
            await update.effective_chat.send_message("❌ Неверный тип лимита! Используйте: roulette или transfer")

    except ValueError:
        await update.effective_chat.send_message("❌ Неверный формат! Используйте числа для ID и лимита")

async def handle_limits_command(update, context):
    user_id = update.effective_user.id

    if not is_super_admin(user_id):
        await update.effective_chat.send_message("❌ Эта команда только для администратора!")
        return

    text = update.message.text.strip()
    words = text.split()

    if len(words) < 2:
        await update.effective_chat.send_message("❌ Формат: /limits <user_id>")
        return

    try:
        target_user_id = int(words[1])
        user = UserManager.get_user(target_user_id)

        if not user:
            await update.effective_chat.send_message("❌ Пользователь не найден!")
            return

        roulette_limit = user[14] if len(user) > 14 and user[14] else ROULETTE_LIMIT
        transfer_limit = user[21] if len(user) > 21 and user[21] else TRANSFER_DAILY_LIMIT

        target_name = user[15] if user[15] else (user[1] if user[1] else user[2])

        await update.effective_chat.send_message(
            f"📊 Лимиты пользователя {target_name} (ID: {target_user_id}):\n\n"
            f"🎰 Лимит рулетки: {roulette_limit:,} монет 🪙\n"
            f"🔄 Лимит перевода: {transfer_limit:,} монет 🪙 за {TRANSFER_COOLDOWN_HOURS} ч.\n\n"
            f"💰 Баланс: {user[3]:,} 🪙"
        )

    except ValueError:
        await update.effective_chat.send_message("❌ Неверный формат ID!")

async def handle_resetbalances_command(update, context):
    user_id = update.effective_user.id

    if not is_super_admin(user_id):
        await update.effective_chat.send_message("❌ Эта команда только для администратора!")
        return

    await update.effective_chat.send_message("ℹ️ Функция временно недоступна")

async def handle_reducebalances_command(update, context):
    user_id = update.effective_user.id

    if not is_super_admin(user_id):
        await update.effective_chat.send_message("❌ Эта команда только для администратора!")
        return

    text = update.message.text.strip()
    words = text.split()

    if len(words) < 2:
        await update.effective_chat.send_message(
            "❌ Формат: /reducebalances <лимит>\n\n"
            "📋 Примеры:\n"
            "• /reducebalances 100000 - уменьшить до 100к\n"
            "• /reducebalances 50000 - уменьшить до 50к\n"
            "• /reducebalances 5000 - уменьшить до 5к\n\n"
            "💡 Внимание: Пользователи с балансом ниже лимита не изменятся!"
        )
        return

    try:
        limit = int(words[1])

        if limit < 0:
            await update.effective_chat.send_message("❌ Лимит не может быть отрицательным!")
            return

        affected_users = UserManager.reduce_all_balances_above_limit(limit)

        if affected_users > 0:
            await update.effective_chat.send_message(
                f"✅ Балансы уменьшены!\n\n"
                f"📊 Результаты:\n"
                f"• Затронуто пользователей: {affected_users}\n"
                f"• Новый баланс: {limit:,} 🪙 (или меньше)\n\n"
                f"💎 Балансы пользователей выше {limit:,} уменьшены.\n"
                f"📈 Пользователи с балансом ниже {limit:,} не изменены."
            )
        else:
            await update.effective_chat.send_message(f"✅ Нет пользователей с балансом выше {limit:,}!")

    except ValueError:
        await update.effective_chat.send_message("❌ Неверный формат! Введите число.")
    except Exception as e:
        logger.error(f"Ошибка в команде уменьшения балансов: {e}")
        await update.effective_chat.send_message(f"❌ Ошибка: {e}")

async def handle_activate_premium(update, context):
    user_id = update.effective_user.id

    if not is_super_admin(user_id):
        await update.effective_chat.send_message("❌ Эта команда только для администратора!")
        return

    text = update.message.text.strip()
    words = text.split()

    if len(words) < 3:
        await update.effective_chat.send_message(
            "❌ Формат: /activatepremium <user_id> <type>\n\n"
            "📋 Примеры:\n"
            "• /activatepremium 123456789 1 - активировать Premium 1 (200 руб)\n"
            "• /activatepremium 123456789 2 - активировать Premium 2 (300 руб)\n\n"
            "💡 Premium 1: 40.000 монет ежедневно\n"
            "💎 Premium 2: 60.000 монет ежедневно"
        )
        return

    try:
        target_user_id = int(words[1])
        premium_type = int(words[2])

        if premium_type not in [1, 2]:
            await update.effective_chat.send_message("❌ Неверный тип Premium! Используйте 1 или 2")
            return

        user = UserManager.get_user(target_user_id)
        if not user:
            await update.effective_chat.send_message("❌ Пользователь не найден!")
            return

        daily_amount = 40000 if premium_type == 1 else 60000
        await UserManager.activate_paid_premium(target_user_id, premium_type, 30, daily_amount)

        target_name = user[15] if user[15] else (user[1] if user[1] else user[2])
        premium_name = "Premium 1" if premium_type == 1 else "Premium 2"

        await update.effective_chat.send_message(
            f"✅ Premium активирован!\n\n"
            f"👤 Пользователь: {target_name}\n"
            f"🆔 ID: {target_user_id}\n"
            f"💰 Тип: {premium_name}\n"
            f"🎁 Ежедневно: {daily_amount} монет\n"
            f"⏰ Срок: 30 дней\n\n"
            f"📊 Premium успешно активирован!"
        )

    except ValueError:
        await update.effective_chat.send_message("❌ Неверный формат! Используйте числа.")

async def handle_give_daily_bonus(context):
    premium_users = UserManager.get_all_paid_premium_users()

    for user_id, premium_type, daily_amount, expires_at in premium_users:
        try:
            expire_date = datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
            if datetime.now() < expire_date:
                await UserManager.give_paid_bonus(user_id, daily_amount)

                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"🎁 **ЕЖЕДНЕВНЫЙ БОНУС!**\n\n"
                         f"💰 Вам начислено: {daily_amount} 🪙\n\n"
                         f"Спасибо за использование Premium!"
                )
        except Exception as e:
            logger.error(f"Ошибка при выдаче бонуса пользователю {user_id}: {e}")

async def handle_rodnoy_callbacks(update, context):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "rodnoy_main_menu":
        await show_rodnoy_main_menu(update, context)

    elif data == "rodnoy_balance_page":
        await show_rodnoy_balance_page(update, context)

    elif data == "stars_payment":
        await show_stars_payment(update, context)

    elif data.startswith("stars_"):
        await handle_stars_purchase(update, context)

    elif data == "rodnoy_bonus_page":
        await show_rodnoy_bonus_page(update, context)

    elif data == "show_channel_bonus":
        await show_channel_bonus(update, context)

    elif data.startswith("check_sub_"):
        await check_channel_subscription(update, context)

    elif data == "premium_1_info":
        await handle_premium_1_info(update, context)

    elif data == "premium_2_info":
        await handle_premium_2_info(update, context)

    elif data == "rodnoy_games":
        await show_rodnoy_games_menu(update, context)

    elif data == "rodnoy_roles":
        await show_rodnoy_roles_menu(update, context)

    elif data == "rodnoy_rating":
        await show_rodnoy_rating_page(update, context)

    elif data == "rodnoy_settings":
        await show_rodnoy_settings(update, context)

    elif data == "rodnoy_buy_thief":
        await handle_rodnoy_buy_thief(update, context)

    elif data == "rodnoy_buy_police":
        await handle_rodnoy_buy_police(update, context)

    elif data == "rodnoy_links":
        await show_rodnoy_links(update, context)

    elif data == "rodnoy_stickers":
        await show_rodnoy_stickers(update, context)

    elif data == "rodnoy_home":
        await show_rodnoy_main_menu(update, context)

    elif data == "rodnoy_blackjack":
        await Games.start_blackjack(update, context)

    elif data == "rodnoy_crash_game":
        await Games.crash_start(update, context)

    elif data == "rodnoy_roulette_game":
        if update.callback_query:
            await update.callback_query.message.reply_text("Рулетка доступна в групповых чатах! Напишите 'Рулетка' в чате.")
        return

    elif data == "rodnoy_bandit_game":
        await Games.banditka(update, context)

    elif data in ["rodnoy_stats", "rodnoy_roles_info", "rodnoy_profile_settings",
                  "rodnoy_notifications", "rodnoy_appearance", "rodnoy_privacy"]:
        query = update.callback_query
        keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="rodnoy_main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.edit_text("🚧 Бул функция иштеп жатат...\n\n⏳ Жакында жеткиликтүү болот!", reply_markup=reply_markup)

    elif data.startswith("slot_"):
        game_key = data.replace("slot_", "")
        await handle_slot_game(update, context, game_key)

async def handle_rodnoy_button(update, context):
    if update.effective_chat.type in ['group', 'supergroup']:
        return
    await show_rodnoy_main_menu(update, context)

async def handle_bonus_button(update, context):
    if update.effective_chat.type in ['group', 'supergroup']:
        await update.effective_chat.send_message("❌ Бонус можно получить только в личных сообщениях с ботом! Перейдите в @RST_ks_bot")
        return

    user_id = update.effective_user.id
    user = UserManager.get_user(user_id)

    if not user:
        username = update.effective_user.username
        first_name = update.effective_user.first_name
        UserManager.create_user(user_id, username, first_name, None)
        user = UserManager.get_user(user_id)

    keyboard = [
        [InlineKeyboardButton("🎁 Бесплатный бонус (подписка на каналы)", callback_data="show_channel_bonus")],
        [InlineKeyboardButton("💰 Premium 1 (200 руб)", callback_data="premium_1_info")],
        [InlineKeyboardButton("💎 Premium 2 (300 руб)", callback_data="premium_2_info")],
        [InlineKeyboardButton("🌐 ВЕБ ПРИЛОЖЕНИЕ", url=WEBAPP_URL)],
        [InlineKeyboardButton("◀️ Назад", callback_data="rodnoy_main_menu")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    subscriptions = UserManager.get_channel_subscriptions(user_id)
    subscribed_count = len(subscriptions)

    bonus_text = (
        f"#𝐑𝐃𝐍𝐎 𝐌𝐗\n\n"
        f"## БОНУСНАЯ СИСТЕМА\n\n"
        f"🎁 **Бесплатный бонус**\n"
        f"   • Подпишитесь на каналы (30 каналов)\n"
        f"   • Получите 20.000 монет за каждый канал\n"
        f"   • Доступно раз в 12 часов\n"
        f"   • Вы подписались на: {subscribed_count}/30 каналов\n\n"
        f"💰 **Premium 1**\n"
        f"   • 40.000 монет ежедневно\n"
        f"   • Срок: 30 дней\n"
        f"   • Цена: 200 руб\n\n"
        f"💎 **Premium 2**\n"
        f"   • 60.000 монет ежедневно\n"
        f"   • Срок: 30 дней\n"
        f"   • Цена: 300 руб\n\n"
        f"👇 Выберите бонус:"
    )

    await update.effective_chat.send_message(bonus_text, reply_markup=reply_markup)

async def handle_donate_button(update, context):
    if update.effective_chat.type in ['group', 'supergroup']:
        return

    user_id = update.effective_user.id
    user = UserManager.get_user(user_id)

    if not user:
        username = update.effective_user.username
        first_name = update.effective_user.first_name
        UserManager.create_user(user_id, username, first_name, None)
        user = UserManager.get_user(user_id)

    donate_text = (
        f"Монеты🪙\n"
        f"200.000 - 100₽\n"
        f"500.000 - 230₽\n"
        f"1.000.000 - 450₽\n"
        f"2.000.000 - 845₽\n"
        f"5.000.000 - 2.000₽\n"
        f"10.000.000 - 4.000₽\n"
        f"50.000.000 - 20000₽\n"
        f"100.000.000 - 40000₽\n\n"
        f"Telegram не сможет помочь с покупками, сделанными через нашего бота,\n"
        f"Если возникнут вопросы, Вы можете обратиться к: https://t.me/MX_KASSA"
    )

    keyboard = [
        [InlineKeyboardButton("💳 Донат", url="https://t.me/MX_KASSA")],
        [InlineKeyboardButton("Получить бонус", url="https://t.me/mani_app_bot/app")],
        [InlineKeyboardButton("Связаться с тех. поддержкой", url="https://t.me/MX_KASSA")],
        [InlineKeyboardButton("🌐 ВЕБ ПРИЛОЖЕНИЕ", url=WEBAPP_URL)]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.effective_chat.send_message(donate_text, reply_markup=reply_markup)

async def handle_links_button(update, context):
    if update.effective_chat.type in ['group', 'supergroup']:
        return

    links_text = (
        f"‼️Все свежие новости и обновления нашего бота вы сможете найти на нашем канале - 💰{NEWS_CHANNEL}💰\n\n"
        f"Актуальная информация о донате: {KASSA_CHANNEL}\n\n"
        f"Основные игровые чаты для вас:\n\n"
        f"1. 😇 Райская РУЛЕТКА 💸 https://t.me/RAY_Roulette - чат для спокойных игроков со стандартным набором правил.\n"
        f"2. 😈 Адская РУЛЕТКА 🔥 - https://t.me/RAY_Roulette - чат для всех игроков с меньшим количеством правил.\n"
        f"3. 🌿 Monaco 🇮🇩 - @CasinoMonacoI - VIP чат для продвинутых игроков (минимальный баланс для входа: 500к)\n"
        f"4. 👰 Weddings 🤵- @MX_KASSA - чат для заключения браков\n"
        f"5. ⛓ ТЮРЬМА ⛓ - @MX_KASSA - это тюрьма для забаненых игроков\n"
        f"6. 🎁 Розыгрыш монет 🎁 - https://t.me/FREEMONETA1 - чат, где проводятся розыгрыши от администраторов официальных чатов.\n"
        f"7. 🃏BlackJack ♠️ - https://t.me/+yZo_DRkI1QcyOTg6 - чат для игры в одну из самых популярных карточных игр казино\n"
        f"8. 📜 LETTERS 🔍 - https://t.me/+M1ziJECcdcZmMGI6 - чат для игры в «Буквы». Составляй слова на скорость и развивай свой интеллект\n"
        f"9. 🇷🇺 Russia 🇷🇺 - https://t.me/VIPKGZ777 -  ‼️NEW‼️ Чат для русскоязычных игроков\n"
        f"10. 🇺🇸 English 🇺🇸 - https://t.me/AMERICA_MX - ‼️NEW‼️ Чат для англоязычных игроков\n"
        f"11. 🇺🇿 Uzbekistan 🇺🇿 -https://t.me/Uzbekston3 - Чат для игроков Узбекистана\n"
        f"12. 🇰🇿 Kazakhstan 🇰🇿 - https://t.me/KAZAKHSTAN_MX- Чат для игроков Казахстана\n"
        f"13. 🇺🇦 Ukraine 🇺🇦 - https://t.me/UKRAINE_MX - Чат для игроков Украины\n"
        f"14. 🇰🇬 Kyrgyzstan 🇰🇬 - https://t.me/tanyshuu_kg1 - Чат для игроков Кыргызстана\n"
        f"15. 🏆 Tournaments 🏆 - https://t.me/VIPKGZ777 - Чат для проведения турниров\n\n"
        f"💳 Донат / Касса: https://t.me/MX_KASSA"
    )

    keyboard = [
        [InlineKeyboardButton("◀️ Назад", callback_data="rodnoy_main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.effective_chat.send_message(links_text, reply_markup=reply_markup)

async def handle_stickers_button(update, context):
    if update.effective_chat.type in ['group', 'supergroup']:
        return

    try:
        await update.effective_chat.send_sticker(
            sticker="CAACAgIAAxkBAAEMRfRnfD1GgFqFqFqFqFqFqFqFqFqFqFqFqFqFqFqFqA"
        )
    except:
        await update.effective_chat.send_animation(
            animation=GIF_URL,
            caption="🎭 Вот наши стикеры!"
        )

    keyboard = [
        [InlineKeyboardButton("◀️ Назад", callback_data="rodnoy_main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.effective_chat.send_message("🎭 Вот наши стикеры!", reply_markup=reply_markup)

async def handle_help_button(update, context):
    if update.effective_chat.type in ['group', 'supergroup']:
        return

    help_text = (
        "❓ ** 𝐑𝐃𝐍𝐎 𝐌𝐗 ПОМОЩЬ**\n\n"
        "📖 **Основные команды:**\n"
        "• /start - запустить бота\n"
        "• /RDNO_MX - главное меню\n"
        "• /bonus - бонус система\n"
        "• /id - узнать свой ID\n"
        "• /setname - изменить отображаемое имя\n\n"
        "🎮 **Игры:**\n"
        "• Рулетка - угадайте число или цвет\n"
        "• Бандит - соберите одинаковые символы\n"
        "• BlackJack - играйте в блэкджек\n"
        "• Крэш - игра в веб приложении\n"
        "• Дурак - карточная игра в веб приложении\n"
        "• 20 разных слотов (футбол, баскетбол, боулинг и др.)\n\n"
        "👥 **Групповые команды:**\n"
        "• Б - баланс\n"
        "• ТОП - топ игроков\n"
        "• ГО - запустить рулетку\n"
        "• !лог - история рулетки (21 результат)\n"
        "• лог - история рулетки (10 результатов)\n"
        "• Ва-банк - все на одно число или диапазон\n"
        "• ставки - показать все ваши текущие ставки\n"
        "• повторить - повторить последние ставки\n"
        "• удвоить - удвоить последние ставки\n\n"
        "🎭 **Роли:**\n"
        "• Вор в законе - кража монет (4000₽)\n"
        "• Полицейский - защита от воров (2000₽)\n\n"
        "🎁 **Бонусы:**\n"
        "• Бесплатный бонус: 20.000 монет за подписку (раз в 12 часов)\n"
        "• Premium 1: 40.000 монет/день (200 руб)\n"
        "• Premium 2: 60.000 монет/день (300 руб)\n"
        "• Веб бонусы: 6,000 - 1,000,000 монет\n\n"
        "🏆 **Турниры:**\n"
        "• /tournament_register - регистрация\n"
        "• /tournament_status - статус\n"
        "• (Только Premium)\n\n"
        "💡 **Полезное:**\n"
        "• '!бот иши' - информация о боте\n"
        "• 'вор -9000' - украсть монеты\n"
        "• 'полиция' - защититься\n"
        "• '1000 1-6' - ставка на диапазон\n"
        "• 'Ва-банк 1-6' - все на диапазон\n\n"
        "🛡️ **Модерация (для админов):**\n"
        "• мут - замутить на 24 часа (ответом на сообщение)\n"
        "• размут - размутить (ответом на сообщение)\n"
        "• бан - забанить (ответом на сообщение)\n"
        "• разбан - разбанить (ответом на сообщение)\n"
        "• мут список - список мутов\n"
        "• бан список - список банов\n"
        "• мутдан - мулга түшкөндөрдүн тизмеси\n"
        "• бандан - банга түшкөндөрдүн тизмеси\n"
        "• размут @username - username боюнча размут\n"
        "• разбан @username - username боюнча разбан\n\n"
        "💰 **Telegram Stars:**\n"
        "• Покупайте монеты за Stars\n"
        "• Автоматическое зачисление\n"
        "• Без участия администратора\n\n"
        "🌐 **Веб приложение:**\n"
        "• Крэш - самолет летит, забери выигрыш вовремя!\n"
        "• Дурак - играй с друзьями\n"
        "• Бонусы - получай бонусы каждый день\n\n"
        "📞 **Поддержка:** https://t.me/MX_KASSA"
    )

    await update.effective_chat.send_message(help_text)

async def rodnoy_start(update, context):
    if update.effective_chat.type in ['group', 'supergroup']:
        return

    user_id = update.effective_user.id

    if UserManager.is_blocked(user_id):
        return

    username = update.effective_user.username
    first_name = update.effective_user.first_name

    UserManager.create_user(user_id, username, first_name, None)

    await web_sync.sync_balances(user_id)

    welcome_text = (
        f"Приветствуем! {first_name}\n\n"
        f"🔥 **RDNO MX** - Твоя атмосфера!\n"
        f"🎮 Твой вайб! Твоя игра!\n\n"
        f"Начав использование нашего бота, вы подтверждаете свое согласие на соблюдение правил бота! "
        f"Комфорт пользователя, это наша цель! @RST_ks_bot"
    )

    keyboard = [
        [KeyboardButton("🏠 𝐑𝐃𝐍𝐎 𝐌𝐗")],
        [KeyboardButton("🎁 Бонус"), KeyboardButton("💳 Донат")],
        [KeyboardButton("❓ Помощь"), KeyboardButton("🔗 Ссылки")]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.effective_chat.send_message(welcome_text, reply_markup=reply_markup)

async def check_expiry_job(context):
    deleted_roles = UserManager.check_role_expiry()
    deleted_premium = UserManager.check_paid_premium_expiry()

    if deleted_roles > 0:
        logger.info(f"Истекшие роли удалены: {deleted_roles}")
    if deleted_premium > 0:
        logger.info(f"Истекшие Premium удалены: {deleted_premium}")

async def send_weekend_bonus_ad(context):
    today = datetime.now().strftime("%d.%m.%Y")

    text = (
        f"⚡️Дорогие друзья, пользователи @RST_ks_bot⚡️\n"
        f"Сегодня ночью в 23:59 начинается акция «День х2 доната»🌟\n"
        f"Любой донат сделаный с пятницы 23:59 по Мск до субботы 23:59 по Мск будет удваиваться.\n"
        f"(АКЦИЯ РАБОТАЕТ В ЛЮБОМ ВИДЕ ДОНАТА, ДАЖЕ В ЛС БОТА)\n"
        f"С ув. администрация бота @RST_ks_bot ⚡️"
    )

    keyboard = [
        [InlineKeyboardButton("💳 Донат", url="https://t.me/MX_KASSA")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT chat_id FROM global_roulette_logs WHERE chat_id < 0")
        chats = cursor.fetchall()
        conn.close()

        sent_chats = set()
        for (chat_id,) in chats:
            if chat_id in sent_chats:
                continue
            try:
                await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
                sent_chats.add(chat_id)
                await asyncio.sleep(0.1)
            except:
                pass
    except Exception as e:
        logger.error(f"Ошибка отправки бонусной рекламы: {e}")

async def is_group_admin(context, chat_id, user_id):
    try:
        if is_super_admin(user_id):
            return True
        chat_member = await context.bot.get_chat_member(chat_id, user_id)
        if chat_member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
            return True
        return False
    except Exception as e:
        logger.error(f"Ошибка проверки админа: {e}")
        return False

URL_PATTERNS = [
    r'https?://\S+',
    r't\.me/\S+',
    r'@\w+',
    r'telegram\.me/\S+',
    r'bit\.ly/\S+',
    r'tinyurl\.com/\S+'
]

def contains_url(text: str) -> bool:
    if not text:
        return False
    text_lower = text.lower()
    for pattern in URL_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False

class Games:
    @staticmethod
    async def ruleka(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat_id = update.effective_chat.id

        chat_manager.roulette_started[chat_id] = True
        chat_manager.last_activity[chat_id] = datetime.now().timestamp()

        user_id = update.effective_user.id

        keyboard = [
            [
                InlineKeyboardButton("1-3", callback_data="bet_1_3"),
                InlineKeyboardButton("4-6", callback_data="bet_4_6"),
                InlineKeyboardButton("7-9", callback_data="bet_7_9"),
                InlineKeyboardButton("10-12", callback_data="bet_10_12")
            ],
            [
                InlineKeyboardButton("1к🔴", callback_data="bet_red"),
                InlineKeyboardButton("1к⚫️", callback_data="bet_black"),
                InlineKeyboardButton("1к💚", callback_data="bet_zero")
            ],
            [
                InlineKeyboardButton("Повторить", callback_data="repeat_bet"),
                InlineKeyboardButton("Удвоить", callback_data="double_bet"),
                InlineKeyboardButton("Крутить", callback_data="spin_roulette")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        user = UserManager.get_user(user_id)
        if not user:
            return

        roulette_layout = (
            "РУЛЕТКА\n"
            "Угадайте число из:\n"
            "0💚\n"
            "1🔴 2⚫️ 3🔴 4⚫️ 5🔴 6⚫️\n"
            "7🔴 8⚫️ 9🔴 10⚫️ 11🔴 12⚫️\n"
            "Ставки можно текстом:\n"
            "1000 на красное | 5000 на 12 | 1000 1-6 на диапазон\n"
            "Минимальная ставка: 1 монета!\n"
        )

        if update.message:
            await update.message.reply_text(roulette_layout, reply_markup=reply_markup)
        elif update.callback_query:
            await update.callback_query.message.reply_text(roulette_layout, reply_markup=reply_markup)

    @staticmethod
    async def handle_roulette_bet(update: Update, context: ContextTypes.DEFAULT_TYPE, bet_type: str, bet_value: str, amount: int) -> bool:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        user = UserManager.get_user(user_id)

        chat_manager.last_activity[chat_id] = datetime.now().timestamp()

        if chat_id not in chat_manager.roulette_started or not chat_manager.roulette_started[chat_id]:
            if update.callback_query:
                await update.callback_query.answer("Рулетка не запущена, наберите Рулетка", show_alert=True)
            else:
                await update.effective_chat.send_message("Рулетка не запущена, наберите Рулетка")
            return False

        if not user:
            return False

        if amount <= 0:
            return False

        if bet_type == 'number':
            try:
                num = int(bet_value)
                if num < 0 or num > 12:
                    return False
            except:
                return False

        if bet_type == 'color':
            if bet_value not in ['red', 'black', 'zero']:
                return False

        if bet_type == 'range':
            if bet_value not in ['1_3', '4_6', '7_9', '10_12']:
                return False

        if user[3] < amount:
            if user[15]:
                display_name = user[15]
            elif user[1]:
                display_name = user[1]
            else:
                display_name = user[2]

            keyboard = [
                [InlineKeyboardButton("💳 Донат", url="https://t.me/MX_KASSA")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            if update.callback_query:
                await update.callback_query.message.reply_text(
                    f"{display_name}, недостаточно монет!\n\n",
                    reply_markup=reply_markup
                )
            else:
                await update.effective_chat.send_message(
                    f"{display_name}, недостаточно монет!\n\n",
                    reply_markup=reply_markup
                )
            return False

        if chat_id not in chat_manager.roulette_bets:
            chat_manager.roulette_bets[chat_id] = {}
        if user_id not in chat_manager.roulette_bets[chat_id]:
            chat_manager.roulette_bets[chat_id][user_id] = []

        if user[15]:
            username = user[15]
        elif user[1]:
            username = user[1]
        else:
            username = user[2]

        existing_bet = None
        for bet in chat_manager.roulette_bets[chat_id][user_id]:
            if bet['type'] == bet_type and bet['value'] == bet_value:
                existing_bet = bet
                break

        bet_description = ""
        if bet_type == 'number':
            bet_description = f"{bet_value}"
        elif bet_type == 'color':
            color_names = {'red': 'красное', 'black': 'чёрное', 'zero': 'зеленое'}
            bet_description = color_names.get(bet_value, bet_value)
        elif bet_type == 'range':
            range_names = {'1_3': '1-3', '4_6': '4-6', '7_9': '7-9', '10_12': '10-12'}
            bet_description = range_names.get(bet_value, bet_value)

        if existing_bet:
            existing_bet['amount'] += amount
        else:
            chat_manager.roulette_bets[chat_id][user_id].append({
                'type': bet_type,
                'value': bet_value,
                'amount': amount,
                'username': username,
                'description': bet_description
            })

        if chat_id not in chat_manager.user_current_bets:
            chat_manager.user_current_bets[chat_id] = {}
        if user_id not in chat_manager.user_current_bets[chat_id]:
            chat_manager.user_current_bets[chat_id][user_id] = []

        if existing_bet:
            for bet in chat_manager.user_current_bets[chat_id][user_id]:
                if bet['type'] == bet_type and bet['value'] == bet_value:
                    bet['amount'] += amount
                    break
        else:
            chat_manager.user_current_bets[chat_id][user_id].append({
                'type': bet_type,
                'value': bet_value,
                'amount': amount,
                'description': bet_description
            })

        await UserManager.update_balance(user_id, -amount, f"Ставка в рулетку: {bet_description}")

        try:
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO roulette_bets (user_id, bet_type, bet_value, amount) VALUES (?, ?, ?, ?)",
                (user_id, bet_type, bet_value, amount)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Ошибка сохранения ставки: {e}")

        chat_manager.last_bet_amounts[chat_id][user_id] = amount
        chat_manager.last_bet_types[chat_id][user_id] = (bet_type, bet_value, bet_description)

        return True

    @staticmethod
    async def handle_range_bet(update: Update, context: ContextTypes.DEFAULT_TYPE, total_amount: int, start_num: int, end_num: int) -> bool:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        user = UserManager.get_user(user_id)

        if not user:
            return False

        if user[3] < total_amount:
            keyboard = [[InlineKeyboardButton("💳 Донат", url="https://t.me/MX_KASSA")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.effective_chat.send_message("❌ Недостаточно монет!\n\n", reply_markup=reply_markup)
            return False

        range_count = end_num - start_num + 1
        bet_per_number = total_amount // range_count

        if bet_per_number < 1:
            await update.effective_chat.send_message("❌ Слишком маленькая ставка для этого диапазона!")
            return False

        if chat_id not in chat_manager.roulette_started or not chat_manager.roulette_started[chat_id]:
            await update.effective_chat.send_message("Рулетка не запущена, наберите Рулетка")
            return False

        desc = f"{start_num}-{end_num}"

        # Диапазон ставкасын бир бүтүн катары сактайбыз (бөлбөйбүз)
        if chat_id not in chat_manager.roulette_bets:
            chat_manager.roulette_bets[chat_id] = {}
        if user_id not in chat_manager.roulette_bets[chat_id]:
            chat_manager.roulette_bets[chat_id][user_id] = []

        # Эгер ушул эле диапазон мурун коюлган болсо — кошот
        existing = None
        for bet in chat_manager.roulette_bets[chat_id][user_id]:
            if bet['type'] == 'range_custom' and bet['value'] == desc:
                existing = bet
                break

        if existing:
            existing['amount'] += total_amount
            existing['bet_per_number'] = existing['amount'] // range_count
        else:
            chat_manager.roulette_bets[chat_id][user_id].append({
                'type': 'range_custom',
                'value': desc,
                'amount': total_amount,
                'start': start_num,
                'end': end_num,
                'bet_per_number': bet_per_number,
                'description': desc
            })

        # user_current_bets да бир жол катары
        if chat_id not in chat_manager.user_current_bets:
            chat_manager.user_current_bets[chat_id] = {}
        if user_id not in chat_manager.user_current_bets[chat_id]:
            chat_manager.user_current_bets[chat_id][user_id] = []

        existing_cur = None
        for bet in chat_manager.user_current_bets[chat_id][user_id]:
            if bet.get('type') == 'range_custom' and bet.get('value') == desc:
                existing_cur = bet
                break
        if existing_cur:
            existing_cur['amount'] += total_amount
        else:
            chat_manager.user_current_bets[chat_id][user_id].append({
                'type': 'range_custom',
                'value': desc,
                'amount': total_amount,
                'description': desc
            })

        chat_manager.last_activity[chat_id] = datetime.now().timestamp()

        # Баланстан алып салабыз
        await UserManager.update_balance(user_id, -total_amount, f"Ставка в рулетку: {desc}")

        if user[15]:
            username = user[15]
        elif user[1]:
            username = user[1]
        else:
            username = user[2]

        await update.effective_chat.send_message(
            f"<a href='tg://user?id={user_id}'>{username}</a> {total_amount} на {desc}",
            parse_mode='HTML'
        )

        return True

    @staticmethod
    async def spin_roulette_logic(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> None:
        if chat_id in chat_manager.roulette_spinning and chat_manager.roulette_spinning[chat_id]:
            if update.callback_query:
                await update.callback_query.answer("Рулетка уже крутится!", show_alert=True)
            return

        if chat_id not in chat_manager.roulette_bets or not chat_manager.roulette_bets[chat_id]:
            if update.callback_query:
                await update.callback_query.answer("Никто не сделал ставок! Сначала сделайте ставку.", show_alert=True)
            return

        chat_manager.roulette_spinning[chat_id] = True

        if chat_id in chat_manager.roulette_bets:
            chat_manager.last_spin_bets[chat_id] = {}
            for uid, bets in chat_manager.roulette_bets[chat_id].items():
                chat_manager.last_spin_bets[chat_id][uid] = bets.copy()

        try:
            winning_number = 0
            winning_color = "💚"
            color_name = "зеленое"

            if chat_id in chat_manager.next_roulette_result and chat_manager.next_roulette_result[chat_id]:
                winning_result = chat_manager.next_roulette_result[chat_id]
                try:
                    if winning_result:
                        match = re.match(r'^(\d+)', winning_result)
                        if match:
                            winning_number = int(match.group(1))
                        else:
                            winning_number = random.randint(0, 12)

                        if "💚" in winning_result:
                            winning_color = "💚"
                            color_name = "зеленое"
                        elif "🔴" in winning_result:
                            winning_color = "🔴"
                            color_name = "красное"
                        elif "⚫️" in winning_result:
                            winning_color = "⚫️"
                            color_name = "чёрное"
                        else:
                            if winning_number == 0:
                                winning_color = "💚"
                                color_name = "зеленое"
                            elif winning_number % 2 == 1:
                                winning_color = "🔴"
                                color_name = "красное"
                            else:
                                winning_color = "⚫️"
                                color_name = "чёрное"
                    else:
                        winning_number = random.randint(0, 12)
                        if winning_number == 0:
                            winning_color = "💚"
                            color_name = "зеленое"
                        elif winning_number % 2 == 1:
                            winning_color = "🔴"
                            color_name = "красное"
                        else:
                            winning_color = "⚫️"
                            color_name = "чёрное"
                except (ValueError, AttributeError) as e:
                    logger.error(f"Ошибка обработки next_roulette_result: {e}")
                    winning_number = random.randint(0, 12)
                    if winning_number == 0:
                        winning_color = "💚"
                        color_name = "зеленое"
                    elif winning_number % 2 == 1:
                        winning_color = "🔴"
                        color_name = "красное"
                    else:
                        winning_color = "⚫️"
                        color_name = "чёрное"
            else:
                winning_number = random.randint(0, 12)
                if winning_number == 0:
                    winning_color = "💚"
                    color_name = "зеленое"
                elif winning_number % 2 == 1:
                    winning_color = "🔴"
                    color_name = "красное"
                else:
                    winning_color = "⚫️"
                    color_name = "чёрное"

            result_text = f"{winning_number}{winning_color}"

            UserManager.add_global_roulette_log(chat_id, result_text)

            if chat_id not in chat_manager.group_roulette_results:
                chat_manager.group_roulette_results[chat_id] = []

            chat_manager.group_roulette_results[chat_id].insert(0, result_text)
            if len(chat_manager.group_roulette_results[chat_id]) > 21:
                chat_manager.group_roulette_results[chat_id] = chat_manager.group_roulette_results[chat_id][:21]

            try:
                gif_message = await context.bot.send_animation(
                    chat_id=chat_id,
                    animation=GIF_URL,
                    caption="🎰 Рулетка вращается..."
                )

                await asyncio.sleep(3)

                try:
                    await context.bot.delete_message(
                        chat_id=chat_id,
                        message_id=gif_message.message_id
                    )
                except:
                    pass

            except Exception as e:
                logger.error(f"Ошибка отправки GIF: {e}")

            if chat_manager.roulette_bets[chat_id]:
                for user_id in chat_manager.roulette_bets[chat_id]:
                    UserManager.add_roulette_log(chat_id, user_id, result_text)

            result_message = f"Рулетка: {winning_number}{winning_color}\n"

            user_results = {}
            user_bets_map = {}

            if chat_manager.roulette_bets[chat_id]:
                for user_id, bet_info in chat_manager.roulette_bets[chat_id].items():
                    user = UserManager.get_user(user_id)
                    if not user:
                        continue

                    if user[15]:
                        username = user[15]
                    else:
                        username = user[2] or f"ID{user_id}"

                    user_bets_map[user_id] = username

                    if user_id not in user_results:
                        user_results[user_id] = {'bets': [], 'total_win': 0, 'username': username}

                    for bet in bet_info:
                        bet_won = False
                        win_amount = 0
                        return_amount = 0
                        total_win = 0
                        display_value = bet.get('description', '')

                        if bet['type'] == 'number':
                            if int(bet['value']) == winning_number:
                                bet_won = True
                                win_amount = bet['amount'] * 12
                                if winning_number == 0:
                                    return_amount = int(bet['amount'] * 0.5)
                                total_win = win_amount + return_amount

                        elif bet['type'] == 'color':
                            color_map = {'red': '🔴', 'black': '⚫️', 'zero': '💚'}
                            if bet['value'] in color_map and color_map[bet['value']] == winning_color:
                                bet_won = True
                                win_amount = bet['amount'] * 2
                                if winning_number == 0:
                                    return_amount = int(bet['amount'] * 0.5)
                                total_win = win_amount + return_amount

                        elif bet['type'] == 'range':
                            ranges = {'1_3': (1, 3), '4_6': (4, 6), '7_9': (7, 9), '10_12': (10, 12)}
                            if bet['value'] in ranges:
                                start, end = ranges[bet['value']]
                                if start <= winning_number <= end:
                                    bet_won = True
                                    win_amount = bet['amount'] * 3
                                    if winning_number == 0:
                                        return_amount = int(bet['amount'] * 0.5)
                                    total_win = win_amount + return_amount

                        elif bet['type'] == 'range_custom':
                            b_start = bet.get('start', 0)
                            b_end = bet.get('end', 0)
                            b_per = bet.get('bet_per_number', 0)
                            if b_start <= winning_number <= b_end:
                                bet_won = True
                                win_amount = b_per * 12
                                total_win = win_amount

                        if bet_won:
                            await UserManager.update_balance(user_id, total_win, f"Выигрыш в рулетку: +{total_win}")
                            user_results[user_id]['total_win'] += total_win
                            user_results[user_id]['bets'].append((bet['amount'], display_value, True, win_amount, return_amount))
                        else:
                            if winning_number == 0:
                                return_amount = int(bet['amount'] * 0.5)
                                await UserManager.update_balance(user_id, return_amount, f"Возврат при 0💚: +{return_amount}")
                            user_results[user_id]['bets'].append((bet['amount'], display_value, False, 0, return_amount))



            if user_results:
                for user_id, data in user_results.items():
                    username = data['username']
                    uid_link = f"<a href='tg://user?id={user_id}'>{username}</a>"
                    for amount, desc, won, win_amt, ret_amt in data['bets']:
                        result_message += f"{username} {amount} на {desc}\n"
                    for amount, desc, won, win_amt, ret_amt in data['bets']:
                        if won and win_amt > 0:
                            result_message += f"{uid_link} выиграл {win_amt} на {desc}\n"
                        elif ret_amt > 0 and not won:
                            result_message += f"{username} возврат {ret_amt}\n"
            else:
                result_message += "Никто не сделал ставок\n"

            keyboard = [
                [
                    InlineKeyboardButton("1-3", callback_data="bet_1_3"),
                    InlineKeyboardButton("4-6", callback_data="bet_4_6"),
                    InlineKeyboardButton("7-9", callback_data="bet_7_9"),
                    InlineKeyboardButton("10-12", callback_data="bet_10_12")
                ],
                [
                    InlineKeyboardButton("1к🔴", callback_data="bet_red"),
                    InlineKeyboardButton("1к⚫️", callback_data="bet_black"),
                    InlineKeyboardButton("1к💚", callback_data="bet_zero")
                ],
                [
                    InlineKeyboardButton("Повторить", callback_data="repeat_bet"),
                    InlineKeyboardButton("Удвоить", callback_data="double_bet"),
                    InlineKeyboardButton("Крутить", callback_data="spin_roulette")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            if chat_id in chat_manager.roulette_bets:
                chat_manager.last_game_bets[chat_id] = {}
                for uid, bets in chat_manager.roulette_bets[chat_id].items():
                    chat_manager.last_game_bets[chat_id][uid] = bets.copy()

            if update.callback_query:
                try:
                    await update.callback_query.message.edit_text(result_message, parse_mode='HTML')
                except:
                    pass
                roulette_layout = (
                    "РУЛЕТКА\n"
                    "Угадайте число из:\n"
                    "0💚\n"
                    "1🔴 2⚫️ 3🔴 4⚫️ 5🔴 6⚫️\n"
                    "7🔴 8⚫️ 9🔴 10⚫️ 11🔴 12⚫️\n"
                    "Ставки можно текстом:\n"
                    "1000 на красное | 5000 на 12 | 1000 1-6 на диапазон\n"
                    "Минимальная ставка: 1 монета!\n"
                )
                await context.bot.send_message(chat_id=chat_id, text=roulette_layout, reply_markup=reply_markup)
            else:
                await context.bot.send_message(chat_id=chat_id, text=result_message, parse_mode='HTML')
                roulette_layout = (
                    "РУЛЕТКА\n"
                    "Угадайте число из:\n"
                    "0💚\n"
                    "1🔴 2⚫️ 3🔴 4⚫️ 5🔴 6⚫️\n"
                    "7🔴 8⚫️ 9🔴 10⚫️ 11🔴 12⚫️\n"
                    "Ставки можно текстом:\n"
                    "1000 на красное | 5000 на 12 | 1000 1-6 на диапазон\n"
                    "Минимальная ставка: 1 монета!\n"
                )
                await context.bot.send_message(chat_id=chat_id, text=roulette_layout, reply_markup=reply_markup)

        finally:
            if chat_id in chat_manager.roulette_bets:
                chat_manager.roulette_bets[chat_id] = {}
            if chat_id in chat_manager.user_current_bets:
                chat_manager.user_current_bets[chat_id] = {}
            if chat_id in chat_manager.user_range_bets:
                chat_manager.user_range_bets[chat_id] = {}
            chat_manager.roulette_spinning[chat_id] = False
            if chat_id in chat_manager.next_roulette_result:
                del chat_manager.next_roulette_result[chat_id]

    @staticmethod
    async def handle_bandit_bet(update: Update, context: ContextTypes.DEFAULT_TYPE, amount: int) -> bool:
        user_id = update.effective_user.id
        user = UserManager.get_user(user_id)

        if not user:
            return False

        if amount < 1:
            await update.effective_chat.send_message("Сумма должна быть больше 0!")
            return False

        if user[3] < amount:
            if user[15]:
                display_name = user[15]
            elif user[1]:
                display_name = user[1]
            else:
                display_name = user[2]

            keyboard = [[InlineKeyboardButton("💳 Донат", url="https://t.me/MX_KASSA")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.effective_chat.send_message(
                f"{display_name}, недостаточно монет!\n\n",
                reply_markup=reply_markup
            )
            return False

        await UserManager.update_balance(user_id, -amount, f"Ставка в бандитку: -{amount}")

        asyncio.create_task(Games._banditka_logic_with_amount(update, context, amount))
        return True

    @staticmethod
    async def banditka(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        user = UserManager.get_user(user_id)
        amount = 1000

        if not user or user[3] < amount:
            keyboard = [[InlineKeyboardButton("💳 Донат", url="https://t.me/MX_KASSA")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.effective_chat.send_message(f"Недостаточно монет!\n\n", reply_markup=reply_markup)
            return

        await UserManager.update_balance(user_id, -amount, f"Ставка в бандитку: -{amount}")

        asyncio.create_task(Games._banditka_logic_with_amount(update, context, amount))

    @staticmethod
    async def _banditka_logic_with_amount(update: Update, context: ContextTypes.DEFAULT_TYPE, amount: int) -> None:
        user_id = update.effective_user.id
        user = UserManager.get_user(user_id)

        username = update.effective_user.username
        first_name = update.effective_user.first_name
        UserManager.update_user_from_tg(user_id, username, first_name)

        user = UserManager.get_user(user_id)
        if user[15]:
            display_name = user[15]
        elif user[1]:
            display_name = user[1]
        else:
            display_name = user[2]

        symbols = ["♦️", "♣️", "♥️", "♠️", "🧧", "🎴", "🀄"]
        result = [random.choice(symbols) for _ in range(5)]

        message = await update.effective_chat.send_message(f"RDNO:\n{display_name}\n\n{result[0]}\U0001f532\U0001f532\U0001f532\U0001f532")
        await asyncio.sleep(1.0)

        await message.edit_text(f"RDNO:\n{display_name}\n\n{result[0]}{result[1]}\U0001f532\U0001f532\U0001f532")
        await asyncio.sleep(1.0)

        await message.edit_text(f"RDNO:\n{display_name}\n\n{result[0]}{result[1]}{result[2]}\U0001f532\U0001f532")
        await asyncio.sleep(1.0)

        await message.edit_text(f"RDNO:\n{display_name}\n\n{result[0]}{result[1]}{result[2]}{result[3]}\U0001f532")
        await asyncio.sleep(1.0)

        final_result = "".join(result)
        from collections import Counter
        counts = Counter(result)
        max_same = max(counts.values())  # эң көп кайталанган символдун саны

        if max_same == 5:
            # 5 бирдей — джекпот
            win = random.randint(amount * 7, amount * 8)
        elif max_same == 4:
            # 4 бирдей
            win = random.randint(amount * 4, amount * 5)
        else:
            # 3, 2 же эч окшош жок — утпайт
            win = 0

        if win > 0:
            await UserManager.update_balance(user_id, win, f"Выигрыш в бандитку: +{win}")
            final_message = f"RDNO:\n{display_name}\n\n{final_result}\n\nВыигрыш: {win} \U0001fa99"
        else:
            final_message = f"RDNO:\n{display_name}\n\n{final_result}\n\nПроигрыш: {amount} \U0001fa99"

        await message.edit_text(final_message)


    @staticmethod
    async def crash_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        user = UserManager.get_user(user_id)
        if not user:
            return
        keyboard = [
            [InlineKeyboardButton("100 \U0001fa99", callback_data="crash_bet_100"),
             InlineKeyboardButton("500 \U0001fa99", callback_data="crash_bet_500")],
            [InlineKeyboardButton("1,000 \U0001fa99", callback_data="crash_bet_1000"),
             InlineKeyboardButton("5,000 \U0001fa99", callback_data="crash_bet_5000")],
            [InlineKeyboardButton("10,000 \U0001fa99", callback_data="crash_bet_10000"),
             InlineKeyboardButton("50,000 \U0001fa99", callback_data="crash_bet_50000")],
            [InlineKeyboardButton("\u25c0\ufe0f \u041d\u0430\u0437\u0430\u0434", callback_data="rodnoy_games")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = (
            "\u2708\ufe0f RDNO \u041a\u0420\u042d\u0428\n\n"
            "\u0421\u0430\u043c\u043e\u043b\u0435\u0442 \u0432\u0437\u043b\u0435\u0442\u0430\u0435\u0442 \u0438 \u043c\u043d\u043e\u0436\u0438\u0442\u0435\u043b\u044c \u0440\u0430\u0441\u0442\u0451\u0442. "
            "\u041d\u0430\u0436\u043c\u0438 \u0417\u0410\u0411\u0420\u0410\u0422\u042c \u0434\u043e \u0432\u0437\u0440\u044b\u0432\u0430!\n\n"
            "\u0427\u0435\u043c \u0434\u043e\u043b\u044c\u0448\u0435 \u043b\u0435\u0442\u0438\u0442 \u2014 \u0442\u0435\u043c \u0431\u043e\u043b\u044c\u0448\u0435 \u0432\u044b\u0438\u0433\u0440\u044b\u0448.\n"
            "\u0415\u0441\u043b\u0438 \u043d\u0435 \u0443\u0441\u043f\u0435\u0435\u0448\u044c \u2014 \u043f\u043e\u0442\u0435\u0440\u044f\u0435\u0448\u044c \u0432\u0441\u0451!\n\n"
            "\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u0441\u0442\u0430\u0432\u043a\u0443:"
        )
        if update.callback_query:
            await update.callback_query.message.edit_text(text, reply_markup=reply_markup)
        else:
            await update.effective_chat.send_message(text, reply_markup=reply_markup)

    @staticmethod
    async def crash_play(update: Update, context: ContextTypes.DEFAULT_TYPE, bet: int) -> None:
        query = update.callback_query
        user_id = query.from_user.id
        user = UserManager.get_user(user_id)
        if not user or user[3] < bet:
            await query.answer("\u274c \u0416\u0435\u0442\u0438\u0448\u043f\u0435\u0435\u0442 \u043c\u043e\u043d\u0435\u0442\u0430!", show_alert=True)
            return
        await UserManager.update_balance(user_id, -bet, f"\u041a\u0440\u044d\u0448 \u0441\u0442\u0430\u0432\u043a\u0430: -{bet}")
        username = query.from_user.username
        first_name = query.from_user.first_name
        UserManager.update_user_from_tg(user_id, username, first_name)
        user = UserManager.get_user(user_id)
        if user[15]:
            display_name = user[15]
        elif user[1]:
            display_name = user[1]
        else:
            display_name = user[2]

        rand = random.random()
        if rand < 0.38:
            crash_at = round(random.uniform(1.01, 1.49), 2)
        elif rand < 0.62:
            crash_at = round(random.uniform(1.50, 1.99), 2)
        elif rand < 0.80:
            crash_at = round(random.uniform(2.00, 3.49), 2)
        elif rand < 0.91:
            crash_at = round(random.uniform(3.50, 6.99), 2)
        elif rand < 0.97:
            crash_at = round(random.uniform(7.00, 14.99), 2)
        else:
            crash_at = round(random.uniform(15.00, 25.00), 2)

        steps = []
        m = 1.00
        while m < crash_at:
            steps.append(round(m, 2))
            if m < 2.0:
                m += random.uniform(0.10, 0.18)
            elif m < 5.0:
                m += random.uniform(0.18, 0.35)
            else:
                m += random.uniform(0.35, 0.70)
        steps.append(crash_at)

        def plane_bar(mult):
            filled = min(int((mult / max(crash_at, 3.0)) * 10), 10)
            return "\U0001f7e9" * filled + "\u2b1c" * (10 - filled)

        def build_msg(mult, bet, display_name, cashed=False):
            winnings = int(bet * mult)
            bar = plane_bar(mult)
            if cashed:
                return (
                    f"RDNO:\n{display_name}\n\n"
                    f"\u2705 \u0417\u0430\u0431\u0440\u0430\u043b!\n\n"
                    f"{bar}\n\n"
                    f"\U0001f4c8 \u041c\u043d\u043e\u0436\u0438\u0442\u0435\u043b\u044c: {mult:.2f}x\n"
                    f"\U0001f4b0 \u0421\u0442\u0430\u0432\u043a\u0430: {bet:,} \U0001fa99\n"
                    f"\U0001f3c6 \u0412\u044b\u0438\u0433\u0440\u044b\u0448: {winnings:,} \U0001fa99\n\n"
                    f"\U0001f4a5 \u0421\u0430\u043c\u043e\u043b\u0435\u0442 \u0432\u0437\u043e\u0440\u0432\u0430\u043b\u0441\u044f \u043d\u0430 {crash_at:.2f}x"
                )
            return (
                f"RDNO:\n{display_name}\n\n"
                f"\u2708\ufe0f \u0421\u0430\u043c\u043e\u043b\u0435\u0442 \u043b\u0435\u0442\u0438\u0442!\n\n"
                f"{bar}\n\n"
                f"\U0001f4c8 \u041c\u043d\u043e\u0436\u0438\u0442\u0435\u043b\u044c: {mult:.2f}x\n"
                f"\U0001f4b0 \u0421\u0442\u0430\u0432\u043a\u0430: {bet:,} \U0001fa99\n"
                f"\U0001f4b5 \u0415\u0441\u043b\u0438 \u0437\u0430\u0431\u0435\u0440\u0451\u0448\u044c: {winnings:,} \U0001fa99\n\n"
                f"\u26a1 \u041d\u0430\u0436\u043c\u0438 \u0417\u0410\u0411\u0420\u0410\u0422\u042c \u0447\u0442\u043e\u0431\u044b \u0432\u044b\u0439\u0442\u0438!"
            )

        cashout_kb = InlineKeyboardMarkup([[InlineKeyboardButton(
            f"\u2705 \u0417\u0410\u0411\u0420\u0410\u0422\u042c {bet:,} \U0001fa99",
            callback_data=f"crash_cashout_{user_id}"
        )]])

        msg = await query.message.edit_text(
            build_msg(1.00, bet, display_name),
            reply_markup=cashout_kb
        )

        context.bot_data[f"crash_{user_id}"] = {
            "cashed_out": False,
            "bet": bet,
            "display_name": display_name,
            "chat_id": query.message.chat_id,
            "message_id": msg.message_id,
            "current_mult": 1.00
        }

        cashed_out_mult = None

        for mult in steps[1:]:
            await asyncio.sleep(0.9)
            game_state = context.bot_data.get(f"crash_{user_id}", {})
            if game_state.get("cashed_out"):
                cashed_out_mult = game_state.get("cashout_mult", mult)
                break
            context.bot_data[f"crash_{user_id}"]["current_mult"] = mult
            try:
                await context.bot.edit_message_text(
                    chat_id=query.message.chat_id,
                    message_id=msg.message_id,
                    text=build_msg(mult, bet, display_name),
                    reply_markup=cashout_kb
                )
            except Exception:
                pass

        game_state = context.bot_data.pop(f"crash_{user_id}", {})
        end_kb = InlineKeyboardMarkup([[InlineKeyboardButton("\U0001f504 \u0418\u0433\u0440\u0430\u0442\u044c \u0441\u043d\u043e\u0432\u0430", callback_data="rodnoy_crash_game")]])

        if cashed_out_mult or game_state.get("cashed_out"):
            m_used = cashed_out_mult or game_state.get("cashout_mult", 1.0)
            win = int(bet * m_used)
            await UserManager.update_balance(user_id, win, f"\u041a\u0440\u044d\u0448 \u0432\u044b\u0438\u0433\u0440\u044b\u0448: +{win}")
            try:
                await context.bot.edit_message_text(
                    chat_id=query.message.chat_id,
                    message_id=msg.message_id,
                    text=build_msg(m_used, bet, display_name, cashed=True),
                    reply_markup=end_kb
                )
            except Exception:
                pass
        else:
            bar_crashed = "\U0001f7e5" * 10
            result_text = (
                f"RDNO:\n{display_name}\n\n"
                f"\U0001f4a5 \u0412\u0417\u0420\u042b\u0412!\n\n"
                f"{bar_crashed}\n\n"
                f"\U0001f4c8 \u0412\u0437\u043e\u0440\u0432\u0430\u043b\u0441\u044f \u043d\u0430: {crash_at:.2f}x\n"
                f"\U0001f4b0 \u0421\u0442\u0430\u0432\u043a\u0430: {bet:,} \U0001fa99\n"
                f"\u274c \u041f\u0440\u043e\u0438\u0433\u0440\u044b\u0448: {bet:,} \U0001fa99\n\n"
                f"\U0001f614 \u041d\u0435 \u0443\u0441\u043f\u0435\u043b \u0437\u0430\u0431\u0440\u0430\u0442\u044c..."
            )
            try:
                await context.bot.edit_message_text(
                    chat_id=query.message.chat_id,
                    message_id=msg.message_id,
                    text=result_text,
                    reply_markup=end_kb
                )
            except Exception:
                pass

    @staticmethod
    async def start_blackjack(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id

        user = UserManager.get_user(user_id)
        if not user:
            return

        keyboard = [
            [InlineKeyboardButton("💰 Сделать ставку", callback_data="bj_bet_1000")],
            [InlineKeyboardButton("💰 Ставка 5000", callback_data="bj_bet_5000")],
            [InlineKeyboardButton("💰 Ставка 10000", callback_data="bj_bet_10000")],
            [InlineKeyboardButton("💰 Ставка 50000", callback_data="bj_bet_50000")],
            [InlineKeyboardButton("◀️ Назад", callback_data="rodnoy_games")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        rules_text = (
            "🃏 **BLACKJACK**\n\n"
            "Правила игры:\n"
            "• Игрок и дилер получают по 2 карты\n"
            "• Цель: набрать 21 очко или больше, чем дилер\n"
            "• Карты: 2-10 по номиналу, J/Q/K = 10, Туз = 1 или 11\n"
            "• Выигрыш: 2x от ставки\n"
            "• Блэкджек (21 с двух карт): 3x от ставки\n\n"
            "Выберите ставку:"
        )

        if update.callback_query:
            await update.callback_query.message.reply_text(rules_text, reply_markup=reply_markup)
        else:
            await update.effective_chat.send_message(rules_text, reply_markup=reply_markup)

    @staticmethod
    async def handle_blackjack_bet(update, context, bet_amount):
        query = update.callback_query
        user_id = query.from_user.id
        chat_id = query.message.chat_id

        user = UserManager.get_user(user_id)
        if not user:
            return

        if user[3] < bet_amount:
            await query.answer("❌ Недостаточно монет!", show_alert=True)
            return

        await UserManager.update_balance(user_id, -bet_amount, f"Ставка в BlackJack: -{bet_amount}")

        def get_card():
            cards = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11]
            return random.choice(cards)

        player_cards = [get_card(), get_card()]
        dealer_cards = [get_card(), get_card()]

        player_score = Games.calculate_blackjack_score(player_cards)
        dealer_score = Games.calculate_blackjack_score(dealer_cards)

        game_id = f"{user_id}_{int(time.time())}"
        chat_manager.blackjack_games[game_id] = {
            'user_id': user_id,
            'bet': bet_amount,
            'player_cards': player_cards,
            'dealer_cards': dealer_cards,
            'player_score': player_score,
            'dealer_score': dealer_score,
            'status': 'playing',
            'game_id': game_id
        }

        player_cards_display = Games.format_cards(player_cards)
        dealer_cards_display = f"{Games.card_to_symbol(dealer_cards[0])} | ?"

        game_text = (
            f"🃏 **BLACKJACK**\n\n"
            f"💰 Ставка: {bet_amount} 🪙\n\n"
            f"👤 Ваши карты: {player_cards_display}\n"
            f"📊 Ваши очки: {player_score}\n\n"
            f"🤵 Карты дилера: {dealer_cards_display}\n\n"
            f"Выберите действие:"
        )

        keyboard = [
            [
                InlineKeyboardButton("🎯 Ещё", callback_data=f"bj_hit_{game_id}"),
                InlineKeyboardButton("⏹ Хватит", callback_data=f"bj_stand_{game_id}")
            ],
            [InlineKeyboardButton("🔄 Новая игра", callback_data="rodnoy_blackjack")],
            [InlineKeyboardButton("◀️ Выход", callback_data="rodnoy_games")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.edit_text(game_text, reply_markup=reply_markup)

    @staticmethod
    def calculate_blackjack_score(cards: List[int]) -> int:
        score = sum(cards)
        aces = cards.count(11)

        while score > 21 and aces > 0:
            score -= 10
            aces -= 1

        return score

    @staticmethod
    def card_to_symbol(card: int) -> str:
        if card == 11:
            return "Т♥"
        elif card == 10:
            return "10♦"
        else:
            return f"{card}♠"

    @staticmethod
    def format_cards(cards: List[int]) -> str:
        return " | ".join([Games.card_to_symbol(c) for c in cards])

    @staticmethod
    async def handle_blackjack_hit(update, context, game_id):
        query = update.callback_query
        user_id = query.from_user.id

        if game_id not in chat_manager.blackjack_games:
            await query.answer("❌ Игра не найдена!", show_alert=True)
            return

        game = chat_manager.blackjack_games[game_id]

        if game['user_id'] != user_id:
            await query.answer("❌ Это не ваша игра!", show_alert=True)
            return

        if game['status'] != 'playing':
            await query.answer("❌ Игра уже завершена!", show_alert=True)
            return

        new_card = random.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11])
        game['player_cards'].append(new_card)
        game['player_score'] = Games.calculate_blackjack_score(game['player_cards'])

        if game['player_score'] > 21:
            game['status'] = 'lost'

            player_cards_display = Games.format_cards(game['player_cards'])
            dealer_cards_display = Games.format_cards(game['dealer_cards'])

            result_text = (
                f"🃏 **BLACKJACK - ПРОИГРЫШ**\n\n"
                f"💰 Ставка: {game['bet']} 🪙\n"
                f"💸 Проигрыш: {game['bet']} 🪙\n\n"
                f"👤 Ваши карты: {player_cards_display}\n"
                f"📊 Ваши очки: {game['player_score']}\n\n"
                f"🤵 Карты дилера: {dealer_cards_display}\n"
                f"📊 Очки дилера: {game['dealer_score']}\n\n"
                f"❌ Перебор!"
            )

            del chat_manager.blackjack_games[game_id]

            keyboard = [
                [InlineKeyboardButton("🔄 Новая игра", callback_data="rodnoy_blackjack")],
                [InlineKeyboardButton("◀️ Выход", callback_data="rodnoy_games")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.message.edit_text(result_text, reply_markup=reply_markup)
            return

        player_cards_display = Games.format_cards(game['player_cards'])
        dealer_cards_display = f"{Games.card_to_symbol(game['dealer_cards'][0])} | ?"

        game_text = (
            f"🃏 **BLACKJACK**\n\n"
            f"💰 Ставка: {game['bet']} 🪙\n\n"
            f"👤 Ваши карты: {player_cards_display}\n"
            f"📊 Ваши очки: {game['player_score']}\n\n"
            f"🤵 Карты дилера: {dealer_cards_display}\n\n"
            f"Выберите действие:"
        )

        keyboard = [
            [
                InlineKeyboardButton("🎯 Ещё", callback_data=f"bj_hit_{game_id}"),
                InlineKeyboardButton("⏹ Хватит", callback_data=f"bj_stand_{game_id}")
            ],
            [InlineKeyboardButton("🔄 Новая игра", callback_data="rodnoy_blackjack")],
            [InlineKeyboardButton("◀️ Выход", callback_data="rodnoy_games")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.edit_text(game_text, reply_markup=reply_markup)

    @staticmethod
    async def handle_blackjack_stand(update, context, game_id):
        query = update.callback_query
        user_id = query.from_user.id

        if game_id not in chat_manager.blackjack_games:
            await query.answer("❌ Игра не найдена!", show_alert=True)
            return

        game = chat_manager.blackjack_games[game_id]

        if game['user_id'] != user_id:
            await query.answer("❌ Это не ваша игра!", show_alert=True)
            return

        if game['status'] != 'playing':
            await query.answer("❌ Игра уже завершена!", show_alert=True)
            return

        game['status'] = 'finished'

        while game['dealer_score'] < 17:
            new_card = random.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11])
            game['dealer_cards'].append(new_card)
            game['dealer_score'] = Games.calculate_blackjack_score(game['dealer_cards'])

        win_amount = 0
        result_status = ""

        if game['dealer_score'] > 21:
            win_amount = game['bet'] * 2
            result_status = "ВЫИГРЫШ"
        elif game['player_score'] > game['dealer_score']:
            win_amount = game['bet'] * 2
            result_status = "ВЫИГРЫШ"
        elif game['player_score'] == game['dealer_score']:
            win_amount = game['bet']
            result_status = "НИЧЬЯ"
        else:
            win_amount = 0
            result_status = "ПРОИГРЫШ"

        if win_amount > 0:
            await UserManager.update_balance(user_id, win_amount, f"Выигрыш в BlackJack: +{win_amount}")

        player_cards_display = Games.format_cards(game['player_cards'])
        dealer_cards_display = Games.format_cards(game['dealer_cards'])

        result_text = (
            f"🃏 **BLACKJACK - {result_status}**\n\n"
            f"💰 Ставка: {game['bet']} 🪙\n"
        )

        if win_amount > 0 and result_status != "НИЧЬЯ":
            result_text += f"🎁 Выигрыш: {win_amount} 🪙\n"
        elif result_status == "НИЧЬЯ":
            result_text += f"🔄 Возврат: {win_amount} 🪙\n"
        else:
            result_text += f"💸 Проигрыш: {game['bet']} 🪙\n"

        result_text += (
            f"\n👤 Ваши карты: {player_cards_display}\n"
            f"📊 Ваши очки: {game['player_score']}\n\n"
            f"🤵 Карты дилера: {dealer_cards_display}\n"
            f"📊 Очки дилера: {game['dealer_score']}"
        )

        del chat_manager.blackjack_games[game_id]

        keyboard = [
            [InlineKeyboardButton("🔄 Новая игра", callback_data="rodnoy_blackjack")],
            [InlineKeyboardButton("◀️ Выход", callback_data="rodnoy_games")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.edit_text(result_text, reply_markup=reply_markup)

async def handle_slot_game(update, context, game_key):
    query = update.callback_query
    user_id = query.from_user.id

    if game_key not in SLOT_GAMES:
        await query.answer("❌ Игра не найдена!", show_alert=True)
        return

    game = SLOT_GAMES[game_key]

    context.user_data['current_slot'] = {
        'game_key': game_key,
        'game_name': game['name'],
        'emoji': game['emoji']
    }

    text = (
        f"{game['emoji']} **{game['name']}**\n\n"
        f"💰 Мин. ставка: {game['min_bet']} 🪙\n"
        f"💰 Макс. ставка: {game['max_bet']} 🪙\n"
        f"🎰 Множители: x1.5, x2, x3, x5, x10\n\n"
        f"Введите сумму ставки:"
    )

    keyboard = [
        [InlineKeyboardButton("100 🪙", callback_data=f"slot_bet_100")],
        [InlineKeyboardButton("500 🪙", callback_data=f"slot_bet_500")],
        [InlineKeyboardButton("1000 🪙", callback_data=f"slot_bet_1000")],
        [InlineKeyboardButton("5000 🪙", callback_data=f"slot_bet_5000")],
        [InlineKeyboardButton("10000 🪙", callback_data=f"slot_bet_10000")],
        [InlineKeyboardButton("◀️ Назад", callback_data="rodnoy_games")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(text, reply_markup=reply_markup)

async def handle_slot_bet(update, context, amount):
    query = update.callback_query
    user_id = query.from_user.id

    if 'current_slot' not in context.user_data:
        await query.answer("❌ Выберите игру сначала!", show_alert=True)
        return

    slot_data = context.user_data['current_slot']
    game_key = slot_data['game_key']
    game = SLOT_GAMES[game_key]

    if amount < game['min_bet'] or amount > game['max_bet']:
        await query.answer(f"❌ Ставка должна быть от {game['min_bet']} до {game['max_bet']}!", show_alert=True)
        return

    user = UserManager.get_user(user_id)
    if not user or user[3] < amount:
        await query.answer("❌ Недостаточно монет!", show_alert=True)
        return

    await UserManager.update_balance(user_id, -amount, f"Ставка в {game['name']}: -{amount}")

    symbols = ["🍒", "🍋", "🍊", "🍇", "💎", "7️⃣", "⭐", "🎰"]
    result = [random.choice(symbols) for _ in range(3)]

    multiplier = 1
    if result[0] == result[1] == result[2]:
        multiplier = random.choice([5, 10])
    elif result[0] == result[1] or result[1] == result[2] or result[0] == result[2]:
        multiplier = random.choice([1.5, 2, 3])
    else:
        multiplier = 0

    win_amount = int(amount * multiplier)

    if win_amount > 0:
        await UserManager.update_balance(user_id, win_amount, f"Выигрыш в {game['name']}: +{win_amount}")

    result_text = (
        f"{game['emoji']} **{game['name']}**\n\n"
        f"{result[0]} | {result[1]} | {result[2]}\n\n"
    )

    if win_amount > 0:
        result_text += f"🎉 Выигрыш: {win_amount} 🪙 (x{multiplier})"
    else:
        result_text += f"😞 Проигрыш: {amount} 🪙"

    keyboard = [
        [InlineKeyboardButton("🎰 Играть еще", callback_data=f"slot_{game_key}")],
        [InlineKeyboardButton("◀️ Назад к играм", callback_data="rodnoy_games")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(result_text, reply_markup=reply_markup)

async def handle_go_command(update, context):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if chat_id not in chat_manager.roulette_started or not chat_manager.roulette_started[chat_id]:
        await update.effective_chat.send_message("Рулетка не запущена, наберите Рулетка")
        return

    if chat_id in chat_manager.go_tasks and not chat_manager.go_tasks[chat_id].done():
        await update.effective_chat.send_message("⏳ ГО уже запущен! Подождите завершения.")
        return

    task = asyncio.create_task(run_go_command(update, context, chat_id, user_id))
    chat_manager.go_tasks[chat_id] = task

    def cleanup(_):
        if chat_id in chat_manager.go_tasks:
            del chat_manager.go_tasks[chat_id]

    task.add_done_callback(cleanup)

async def run_go_command(update, context, chat_id, user_id):
    user = UserManager.get_user(user_id)
    if not user:
        return

    if chat_id not in chat_manager.roulette_bets or not chat_manager.roulette_bets[chat_id]:
        await update.effective_chat.send_message("Никто не сделал ставок! Сначала сделайте ставку.")
        return

    if user[15]:
        display_name = user[15]
    elif user[1]:
        display_name = user[1]
    else:
        display_name = user[2]

    random_wait = random.choice([3, 5, 10, 12, 15])

    time_message = await update.effective_chat.send_message(f"{display_name} крутит (через {random_wait} сек)..")

    await asyncio.sleep(random_wait)

    try:
        await context.bot.delete_message(
            chat_id=chat_id,
            message_id=time_message.message_id
        )
    except Exception as e:
        logger.error(f"Ошибка удаления сообщения: {e}")

    try:
        gif_message = await update.effective_chat.send_animation(
            animation=GIF_URL,
            caption="🎰"
        )

        await asyncio.sleep(3)

        try:
            await context.bot.delete_message(
                chat_id=chat_id,
                message_id=gif_message.message_id
            )
        except:
            pass

    except Exception as e:
        logger.error(f"Ошибка отправки GIF: {e}")

    winning_number = 0
    winning_color = "💚"
    color_name = "зеленое"

    if chat_id in chat_manager.next_roulette_result and chat_manager.next_roulette_result[chat_id]:
        winning_result = chat_manager.next_roulette_result[chat_id]
        try:
            if winning_result:
                match = re.match(r'^(\d+)', winning_result)
                if match:
                    winning_number = int(match.group(1))
                else:
                    winning_number = random.randint(0, 12)

                if "💚" in winning_result:
                    winning_color = "💚"
                    color_name = "зеленое"
                elif "🔴" in winning_result:
                    winning_color = "🔴"
                    color_name = "красное"
                elif "⚫️" in winning_result:
                    winning_color = "⚫️"
                    color_name = "чёрное"
                else:
                    if winning_number == 0:
                        winning_color = "💚"
                        color_name = "зеленое"
                    elif winning_number % 2 == 1:
                        winning_color = "🔴"
                        color_name = "красное"
                    else:
                        winning_color = "⚫️"
                        color_name = "чёрное"
            else:
                winning_number = random.randint(0, 12)
                if winning_number == 0:
                    winning_color = "💚"
                    color_name = "зеленое"
                elif winning_number % 2 == 1:
                    winning_color = "🔴"
                    color_name = "красное"
                else:
                    winning_color = "⚫️"
                    color_name = "чёрное"
        except (ValueError, AttributeError) as e:
            logger.error(f"Ошибка обработки next_roulette_result: {e}")
            winning_number = random.randint(0, 12)
            if winning_number == 0:
                winning_color = "💚"
                color_name = "зеленое"
            elif winning_number % 2 == 1:
                winning_color = "🔴"
                color_name = "красное"
            else:
                winning_color = "⚫️"
                color_name = "чёрное"
    else:
        winning_number = random.randint(0, 12)
        if winning_number == 0:
            winning_color = "💚"
            color_name = "зеленое"
        elif winning_number % 2 == 1:
            winning_color = "🔴"
            color_name = "красное"
        else:
            winning_color = "⚫️"
            color_name = "чёрное"

    result_text = f"{winning_number}{winning_color}"

    UserManager.add_global_roulette_log(chat_id, result_text)

    if chat_id not in chat_manager.group_roulette_results:
        chat_manager.group_roulette_results[chat_id] = []

    chat_manager.group_roulette_results[chat_id].insert(0, result_text)
    if len(chat_manager.group_roulette_results[chat_id]) > 21:
        chat_manager.group_roulette_results[chat_id] = chat_manager.group_roulette_results[chat_id][:21]

    if chat_manager.roulette_bets[chat_id]:
        for user_id in chat_manager.roulette_bets[chat_id]:
            UserManager.add_roulette_log(chat_id, user_id, result_text)

    result_message = f"Рулетка: {winning_number}{winning_color}\n"

    # user_id -> {bets: [(amount, desc, won, win_amount, return_amount)], total_win: int}
    user_results = {}
    user_bets_map = {}

    if chat_manager.roulette_bets[chat_id]:
        for user_id, bet_info in chat_manager.roulette_bets[chat_id].items():
            user = UserManager.get_user(user_id)
            if not user:
                continue

            if user[15]:
                username = user[15]
            else:
                username = user[2] or f"ID{user_id}"

            user_bets_map[user_id] = username

            if user_id not in user_results:
                user_results[user_id] = {'bets': [], 'total_win': 0, 'username': username}

            for bet in bet_info:
                bet_won = False
                win_amount = 0
                return_amount = 0
                total_win = 0
                display_value = bet.get('description', '')

                if bet['type'] == 'number':
                    if int(bet['value']) == winning_number:
                        bet_won = True
                        win_amount = bet['amount'] * 12
                        if winning_number == 0:
                            return_amount = int(bet['amount'] * 0.5)
                        total_win = win_amount + return_amount

                elif bet['type'] == 'color':
                    color_map = {'red': '🔴', 'black': '⚫️', 'zero': '💚'}
                    if bet['value'] in color_map and color_map[bet['value']] == winning_color:
                        bet_won = True
                        win_amount = bet['amount'] * 2
                        if winning_number == 0:
                            return_amount = int(bet['amount'] * 0.5)
                        total_win = win_amount + return_amount

                elif bet['type'] == 'range':
                    ranges = {'1_3': (1, 3), '4_6': (4, 6), '7_9': (7, 9), '10_12': (10, 12)}
                    if bet['value'] in ranges:
                        start, end = ranges[bet['value']]
                        if start <= winning_number <= end:
                            bet_won = True
                            win_amount = bet['amount'] * 3
                            if winning_number == 0:
                                return_amount = int(bet['amount'] * 0.5)
                            total_win = win_amount + return_amount

                elif bet['type'] == 'range_custom':
                    b_start = bet.get('start', 0)
                    b_end = bet.get('end', 0)
                    b_per = bet.get('bet_per_number', 0)
                    if b_start <= winning_number <= b_end:
                        bet_won = True
                        win_amount = b_per * 12
                        total_win = win_amount

                if bet_won:
                    await UserManager.update_balance(user_id, total_win, f"Выигрыш в рулетку: +{total_win}")
                    user_results[user_id]['total_win'] += total_win
                    user_results[user_id]['bets'].append((bet['amount'], display_value, True, win_amount, return_amount))
                else:
                    if winning_number == 0:
                        return_amount = int(bet['amount'] * 0.5)
                        await UserManager.update_balance(user_id, return_amount, f"Возврат при 0💚: +{return_amount}")
                    user_results[user_id]['bets'].append((bet['amount'], display_value, False, 0, return_amount))



    # Натыйжаны бир адам боюнча топтоп чыгаруу
    if user_results:
        for user_id, data in user_results.items():
            username = data['username']
            uid_link = f"<a href='tg://user?id={user_id}'>{username}</a>"
            # Бардык ставкалары
            for amount, desc, won, win_amt, ret_amt in data['bets']:
                result_message += f"{username} {amount} на {desc}\n"
            # Жеңүүлөрү
            for amount, desc, won, win_amt, ret_amt in data['bets']:
                if won and win_amt > 0:
                    result_message += f"{uid_link} выиграл {win_amt} на {desc}\n"
                elif ret_amt > 0 and not won:
                    result_message += f"{username} возврат {ret_amt}\n"
    else:
        result_message += "Никто не сделал ставок\n"

    if chat_id in chat_manager.roulette_bets:
        chat_manager.last_game_bets[chat_id] = {}
        for uid, bets in chat_manager.roulette_bets[chat_id].items():
            chat_manager.last_game_bets[chat_id][uid] = bets.copy()

    await update.effective_chat.send_message(result_message, parse_mode='HTML')

    keyboard = [
        [
            InlineKeyboardButton("1-3", callback_data="bet_1_3"),
            InlineKeyboardButton("4-6", callback_data="bet_4_6"),
            InlineKeyboardButton("7-9", callback_data="bet_7_9"),
            InlineKeyboardButton("10-12", callback_data="bet_10_12")
        ],
        [
            InlineKeyboardButton("1к🔴", callback_data="bet_red"),
            InlineKeyboardButton("1к⚫️", callback_data="bet_black"),
            InlineKeyboardButton("1к💚", callback_data="bet_zero")
        ],
        [
            InlineKeyboardButton("Повторить", callback_data="repeat_bet"),
            InlineKeyboardButton("Удвоить", callback_data="double_bet"),
            InlineKeyboardButton("Крутить", callback_data="spin_roulette")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    roulette_layout = (
        "РУЛЕТКА\n"
        "Угадайте число из:\n"
        "0💚\n"
        "1🔴 2⚫️ 3🔴 4⚫️ 5🔴 6⚫️\n"
        "7🔴 8⚫️ 9🔴 10⚫️ 11🔴 12⚫️\n"
        "Ставки можно текстом:\n"
        "1000 на красное | 5000 на 12 | 1000 1-6 на диапазон\n"
        "Минимальная ставка: 1 монета!\n"
    )
    await update.effective_chat.send_message(roulette_layout, reply_markup=reply_markup)

    # Рулетка айлангандан кийин DB ставкаларын тазала
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        # Ошол чат мүчөлөрүнүн ставкаларын гана өчүр
        if chat_id in chat_manager.roulette_bets:
            user_ids = list(chat_manager.roulette_bets.get(chat_id, {}).keys())
            if user_ids:
                placeholders = ','.join('?' * len(user_ids))
                cursor.execute(f"DELETE FROM roulette_bets WHERE user_id IN ({placeholders})", user_ids)
                conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Ставкаларды тазалоодо ката: {e}")

    chat_manager.reset_chat_roulette(chat_id)



# ============ РОЗЫГРЫШ СИСТЕМАСЫ ============

active_giveaways = {}


def _giveaway_text(giveaway):
    prize = giveaway['prize']
    max_p = giveaway['max']
    participants = giveaway['participants']
    each = prize // max_p if max_p > 0 else prize
    count = len(participants)
    names = ', '.join([n for _, n in participants]) if participants else 'пока никого'
    lines = [
        "\U0001f381 *\U0001d411\U0001d403\U0001d0de\U0001d438 \U0001d40c\U0001d417* "
        + "предлагает принять участие в розыгрыше *" + "{prize}" + "* монет, "
        + "максимальное число участников - *" + "{max_p}" + "*",
        "\U0001f4b0 Ар бирине: *" + "{each}" + "* монета",
        "\U0001f464 Уюштурду: " + giveaway['admin_name'],
        "",
        "Участники: " + names,
        "",
        "Всего: " + str(count) + "/" + str(max_p),
    ]
    # Replace placeholders
    result = "\n".join(lines)
    result = result.replace("{prize}", f"{prize:,}")
    result = result.replace("{max_p}", str(max_p))
    result = result.replace("{each}", f"{each:,}")
    return result


def _giveaway_keyboard(chat_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("\u2705 Присоединиться", callback_data="gw_join_" + str(chat_id)),
            InlineKeyboardButton("\u25b6\ufe0f Начать", callback_data="gw_start_" + str(chat_id))
        ],
        [InlineKeyboardButton("\u274c Отмена", callback_data="gw_cancel_" + str(chat_id))]
    ])


async def handle_giveaway_command(update, context):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    if not is_super_admin(user_id):
        await update.message.reply_text("\u274c Бул команда жалаң гана администраторлор үчүн!")
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("\u274c Туура формат: /giveaway <сумма> <катышуучулар>\nМисалы: /giveaway 500000 20")
        return
    try:
        prize_amount = int(args[0])
        max_participants = int(args[1])
    except ValueError:
        await update.message.reply_text("\u274c Сумма жана катышуучулар саны бүтүн сан болуш керек!")
        return
    if prize_amount < 100:
        await update.message.reply_text("\u274c Минималдуу сумма: 100 монета!")
        return
    if max_participants < 1 or max_participants > 500:
        await update.message.reply_text("\u274c Катышуучулар саны 1-500 арасында болуш керек!")
        return
    admin_user = UserManager.get_user(user_id)
    if not admin_user or admin_user[3] < prize_amount:
        bal = admin_user[3] if admin_user else 0
        await update.message.reply_text(
            "\u274c Жетишсиз монета! Сениндеги: " + str(bal) + "\U0001fab9\n" + "Керек: " + str(prize_amount) + "\U0001fab9"
        )
        return
    await UserManager.update_balance(user_id, -prize_amount)
    admin_name = admin_user[15] or admin_user[1] or admin_user[2] or "Админ"
    active_giveaways[chat_id] = {
        'prize': prize_amount,
        'max': max_participants,
        'participants': [],
        'admin_id': user_id,
        'admin_name': admin_name,
        'message_id': None
    }
    text = _giveaway_text(active_giveaways[chat_id])
    keyboard = _giveaway_keyboard(chat_id)
    sent = await update.effective_chat.send_message(text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)
    active_giveaways[chat_id]['message_id'] = sent.message_id


async def handle_giveaway_callback(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    parts = data.split('_')
    try:
        chat_id = int(parts[-1])
    except Exception:
        await query.answer("\u274c Ката!")
        return

    if data.startswith('gw_join_'):
        if chat_id not in active_giveaways:
            await query.answer("\u274c Розыгрыш жок!", show_alert=True)
            return
        giveaway = active_giveaways[chat_id]
        if any(p[0] == user_id for p in giveaway['participants']):
            await query.answer("\u26a0\ufe0f Сен буга чейин катышып жатасың!", show_alert=True)
            return
        user = UserManager.get_user(user_id)
        if not user:
            UserManager.create_user(user_id, query.from_user.username, query.from_user.first_name, None)
            user = UserManager.get_user(user_id)
        display_name = (user[15] or user[1] or user[2] or query.from_user.first_name) if user else query.from_user.first_name
        giveaway['participants'].append((user_id, display_name))
        count = len(giveaway['participants'])
        max_p = giveaway['max']
        await query.answer("\u2705 Катышып жатасың! [" + str(count) + "/" + str(max_p) + "]")
        try:
            await query.edit_message_text(
                text=_giveaway_text(giveaway),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=_giveaway_keyboard(chat_id)
            )
        except Exception:
            pass
        if count >= max_p:
            await _finish_giveaway(context, chat_id, query.message)

    elif data.startswith('gw_start_'):
        if not is_super_admin(user_id):
            await query.answer("\u274c Жалаң гана администраторлор!", show_alert=True)
            return
        if chat_id not in active_giveaways:
            await query.answer("\u274c Розыгрыш жок!", show_alert=True)
            return
        if len(active_giveaways[chat_id]['participants']) == 0:
            await query.answer("\u274c Катышуучу жок!", show_alert=True)
            return
        await query.answer("\u25b6\ufe0f Розыгрыш башталды!")
        await _finish_giveaway(context, chat_id, query.message)

    elif data.startswith('gw_cancel_'):
        if not is_super_admin(user_id):
            await query.answer("\u274c Жалаң гана администраторлор!", show_alert=True)
            return
        if chat_id not in active_giveaways:
            await query.answer("\u274c Розыгрыш жок!", show_alert=True)
            return
        giveaway = active_giveaways.pop(chat_id)
        await UserManager.update_balance(giveaway["admin_id"], giveaway["prize"])
        await query.answer("\u274c Жокко чыгарылды!")
        try:
            await query.edit_message_text(
                "\u274c *Розыгрыш жокко чыгарылды.*\nМонеталар кайтарылды.",
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception:
            pass


async def _finish_giveaway(context, chat_id, message):
    if chat_id not in active_giveaways:
        return
    giveaway = active_giveaways.pop(chat_id)
    participants = giveaway['participants']
    if not participants:
        await UserManager.update_balance(giveaway['admin_id'], giveaway['prize'])
        try:
            await message.edit_text("\u274c Катышуучу жок — розыгрыш жокко чыгарылды.")
        except Exception:
            pass
        return

    total_prize = giveaway['prize']
    count = len(participants)

    # Рандом бөлүштүрүү: ар бирине башка-башка сумма
    if count == 1:
        prizes = [total_prize]
    else:
        # Ар бирине минималдуу 1% гарантия, калганы рандом
        min_share = max(1, total_prize // (count * 10))  # минималдуу 10%дан аз болбосун
        # Рандом "кесүү чекиттери" менен бөлүштүр
        cuts = sorted(random.sample(range(min_share, total_prize - min_share * (count - 1)), count - 1))
        prizes = []
        prev = 0
        for cut in cuts:
            prizes.append(cut - prev)
            prev = cut
        prizes.append(total_prize - prev)
        # Минималдуу чекти камсыз кыл
        prizes = [max(min_share, p) for p in prizes]
        # Жалпы суммага дал келтир
        diff = total_prize - sum(prizes)
        prizes[0] += diff
        random.shuffle(prizes)

    # Монеталарды бер жана натыйжа тизмесин түз
    winner_lines = []
    for i, (pid, pname) in enumerate(participants):
        amount = prizes[i]
        await UserManager.update_balance(pid, amount)
        winner_lines.append(f"{pname} выиграл {amount:,} монет")

    winners_text = "\n".join(winner_lines)
    result_text = (
        "\U0001f389 *Розыгрыш аяктады!* \U0001f389\n\n"
        + f"\U0001f4b0 Жалпы фонд: *{total_prize:,}* монета\n"
        + f"\U0001f465 Катышуучулар: *{count}*\n\n"
        + f"{winners_text}\n\n"
        + "\U0001f38a Баарыңарды куттуктайм!"
    )
    try:
        await message.edit_text(result_text, parse_mode=ParseMode.MARKDOWN)
    except Exception:
        await context.bot.send_message(chat_id=chat_id, text=result_text, parse_mode=ParseMode.MARKDOWN)


async def handle_stop_giveaway(update, context):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    if not is_super_admin(user_id):
        await update.message.reply_text("\u274c Бул команда жалаң гана администраторлор үчүн!")
        return
    if chat_id not in active_giveaways:
        await update.message.reply_text("\u274c Учурда активдүү розыгрыш жок!")
        return
    if len(active_giveaways[chat_id]['participants']) == 0:
        await update.message.reply_text("\u274c Катышуучу жок!")
        return
    giveaway = active_giveaways[chat_id]
    await update.message.reply_text("\u25b6\ufe0f Розыгрыш аяктатылууда...")
    try:
        fake_msg = await context.bot.send_message(chat_id=chat_id, text="...")
        await _finish_giveaway(context, chat_id, fake_msg)
    except Exception:
        await _finish_giveaway(context, chat_id, update.message)


# =============================================

async def handle_text_messages(update, context):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    username = update.effective_user.username
    first_name = update.effective_user.first_name
    UserManager.update_user_from_tg(user_id, username, first_name)

    if update.effective_chat.type in ['group', 'supergroup']:
        if UserManager.is_muted(user_id):
            try:
                await update.message.delete()
                return
            except Exception as e:
                logger.error(f"Ошибка при проверке мута: {e}")

        text = update.message.text or ""
        if contains_url(text):
            try:
                await update.message.delete()
                return
            except Exception as e:
                logger.error(f"Ошибка при удалении ссылки: {e}")

    user = UserManager.get_user(user_id)
    if not user:
        UserManager.create_user(user_id, username, first_name, None)
        user = UserManager.get_user(user_id)

    if not user:
        return

    text = update.message.text.strip()
    text_lower = text.lower()

    # Группада "Монеты🪙" же "монеты" — донат маалыматы
    # ===== БАНК СИСТЕМАСЫ =====
    # "банк" — банктагы балансты көрсөт
    if text_lower == "банк":
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM bank WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        bank_bal = row[0] if row else 0
        wallet_bal = user[3] if user else 0
        await update.effective_chat.send_message(
            f"🏦 *Твой банк*\n\n"
            f"💰 На счету: *{bank_bal:,}* 🪙\n"
            f"👛 В кошельке: *{wallet_bal:,}* 🪙\n\n"
            f"📥 Пополнить: *банк +10000*\n"
            f"📤 Снять: *банк -10000*",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # "банк +СУММА" — депозит
    if text_lower.startswith("банк +"):
        parts = text.split()
        if len(parts) == 2:
            try:
                amount = int(parts[1].replace("+", "").replace(",", "").replace(".", "").strip())
            except ValueError:
                await update.effective_chat.send_message("❌ Неверный формат! Используйте: банк +10000")
                return
            if amount <= 0:
                await update.effective_chat.send_message("❌ Сумма должна быть больше нуля!")
                return
            wallet_bal = user[3] if user else 0
            if wallet_bal < amount:
                await update.effective_chat.send_message(
                    f"❌ Недостаточно монет! В кошельке: *{wallet_bal:,}* 🪙",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO bank (user_id, balance, last_deposit) VALUES (?, ?, ?) "
                "ON CONFLICT(user_id) DO UPDATE SET balance = balance + ?, last_deposit = ?",
                (user_id, amount, datetime.now(), amount, datetime.now())
            )
            conn.commit()
            cursor.execute("SELECT balance FROM bank WHERE user_id = ?", (user_id,))
            new_bank = cursor.fetchone()[0]
            conn.close()
            await UserManager.update_balance(user_id, -amount)
            new_wallet = wallet_bal - amount
            display = user[15] or user[1] or user[2] or "Пользователь"
            await update.effective_chat.send_message(
                f"🏦 *Пополнение банка!*\n\n"
                f"👤 {display}\n"
                f"📥 Внесено: *+{amount:,}* 🪙\n\n"
                f"💰 На счету: *{new_bank:,}* 🪙\n"
                f"👛 В кошельке: *{new_wallet:,}* 🪙",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.effective_chat.send_message("❌ Неверный формат! Используйте: банк +10000")
        return

    # "банк -СУММА" — алып чыгуу
    if text_lower.startswith("банк -"):
        parts = text.split()
        if len(parts) == 2:
            try:
                amount = int(parts[1].replace("-", "").replace(",", "").replace(".", "").strip())
            except ValueError:
                await update.effective_chat.send_message("❌ Неверный формат! Используйте: банк -10000")
                return
            if amount <= 0:
                await update.effective_chat.send_message("❌ Сумма должна быть больше нуля!")
                return
            conn = sqlite3.connect(DATABASE_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT balance FROM bank WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            bank_bal = row[0] if row else 0
            if bank_bal < amount:
                conn.close()
                await update.effective_chat.send_message(
                    f"❌ Недостаточно средств! На счету: *{bank_bal:,}* 🪙",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            cursor.execute(
                "UPDATE bank SET balance = balance - ?, last_withdraw = ? WHERE user_id = ?",
                (amount, datetime.now(), user_id)
            )
            conn.commit()
            cursor.execute("SELECT balance FROM bank WHERE user_id = ?", (user_id,))
            new_bank = cursor.fetchone()[0]
            conn.close()
            await UserManager.update_balance(user_id, amount)
            new_wallet = (user[3] if user else 0) + amount
            display = user[15] or user[1] or user[2] or "Пользователь"
            await update.effective_chat.send_message(
                f"🏦 *Снятие с банка!*\n\n"
                f"👤 {display}\n"
                f"📤 Снято: *-{amount:,}* 🪙\n\n"
                f"💰 На счету: *{new_bank:,}* 🪙\n"
                f"👛 В кошельке: *{new_wallet:,}* 🪙",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.effective_chat.send_message("❌ Неверный формат! Используйте: банк -10000")
        return
    # ===== БАНК АЯКТАДЫ =====

    # ===== МАГАЗИН ТЕКСТ БУЙРУКТАРЫ =====
    shop_handled = await handle_shop_text(update, context, user, text, text_lower)
    if shop_handled:
        return
    # ===== МАГАЗИН АЯКТАДЫ =====

    if text_lower in ["монеты🪙", "монеты", "монета", "донат"]:
        donate_group_text = (
            "Монеты🪙\n"
            "200.000 - 100₽\n"
            "500.000 - 230₽\n"
            "1.000.000 - 450₽\n"
            "2.000.000 - 845₽\n"
            "5.000.000 - 2.000₽\n"
            "10.000.000 - 4.000₽\n"
            "50.000.000 - 20000₽\n"
            "100.000.000 - 40000₽\n\n"
            "Telegram не сможет помочь с покупками, сделанными через нашего бота,\n"
            "Если возникнут вопросы, Вы можете обратиться к: https://t.me/MX_KASSA"
        )
        keyboard = [[InlineKeyboardButton("💳 Донат", url="https://t.me/MX_KASSA")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.effective_chat.send_message(donate_group_text, reply_markup=reply_markup)
        return

    # Группада "ссылки" — чаттардын ссылкалары
    if text_lower in ["ссылки", "ссылка"]:
        links_group_text = (
            "‼️ Основные игровые чаты:\n\n"
            "1. 😇 Райская РУЛЕТКА 💸 https://t.me/RAY_Roulette\n"
            "2. 😈 Адская РУЛЕТКА 🔥 https://t.me/RAY_Roulette\n"
            "3. 🌿 Monaco 🇮🇩 @CasinoMonacoI\n"
            "4. 👰 Weddings 🤵 @MX_KASSA\n"
            "5. ⛓ ТЮРЬМА ⛓ @MX_KASSA\n"
            "6. 🎁 Розыгрыш монет 🎁 https://t.me/FREEMONETA1\n"
            "7. 🃏 BlackJack ♠️ https://t.me/+yZo_DRkI1QcyOTg6\n"
            "8. 📜 LETTERS 🔍 https://t.me/+M1ziJECcdcZmMGI6\n"
            "9. 🇷🇺 Russia 🇷🇺 https://t.me/VIPKGZ777\n"
            "10. 🇺🇸 English 🇺🇸 https://t.me/AMERICA_MX\n"
            "11. 🇺🇿 Uzbekistan 🇺🇿 https://t.me/Uzbekston3\n"
            "12. 🇰🇿 Kazakhstan 🇰🇿 https://t.me/KAZAKHSTAN_MX\n"
            "13. 🇺🇦 Ukraine 🇺🇦 https://t.me/UKRAINE_MX\n"
            "14. 🇰🇬 Kyrgyzstan 🇰🇬 https://t.me/tanyshuu_kg1\n"
            "15. 🏆 Tournaments 🏆 https://t.me/VIPKGZ777\n\n"
            "💳 Донат / Касса: https://t.me/MX_KASSA"
        )
        await update.effective_chat.send_message(links_group_text)
        return

    if text == "🏠 𝐑𝐃𝐍𝐎 𝐌𝐗":
        await show_rodnoy_main_menu(update, context)
        return

    if text == "🎁 Бонус":
        await handle_bonus_button(update, context)
        return

    if text == "💳 Донат":
        await handle_donate_button(update, context)
        return

    if text == "❓ Помощь":
        await handle_help_button(update, context)
        return

    if text == "🔗 Ссылки":
        await handle_links_button(update, context)
        return

    if text_lower.startswith("вор"):
        await handle_thief_steal(update, context)
        return

    if text_lower == "полиция" or text_lower == "полицейский":
        await handle_police_protect(update, context)
        return

    if text_lower == "мут":
        await handle_text_mute(update, context)
        return

    if text_lower == "размут":
        await handle_text_unmute(update, context)
        return

    if text_lower == "бан":
        await handle_text_ban(update, context)
        return

    if text_lower == "разбан":
        await handle_text_unban(update, context)
        return

    if text_lower == "мут список":
        await handle_mute_list_text(update, context)
        return

    if text_lower == "бан список":
        await handle_ban_list_text(update, context)
        return

    if text_lower == "мутдан":
        await handle_mutdan_command(update, context)
        return

    if text_lower == "бандан":
        await handle_bandan_command(update, context)
        return

    if text_lower.startswith("размут"):
        await handle_razmut_username(update, context)
        return

    if text_lower.startswith("разбан"):
        await handle_razban_username(update, context)
        return

    if text_lower.startswith("дай админ"):
        await handle_dai_admin_command(update, context)
        return

    if text_lower.startswith("убери админ"):
        await handle_uberi_admin_command(update, context)
        return

    if text_lower == "ставки" or text_lower == "ставка" or text_lower == "мои ставки":
        await show_user_current_bets(update, context)
        return

    if text_lower == "повторить" or text_lower == "повтор" or text_lower == "repeat":
        await repeat_user_last_bets(update, context)
        return

    if text_lower == "удвоить" or text_lower == "удвой" or text_lower == "double":
        await double_user_last_bets(update, context)
        return

    if text.upper() == "Б":
        if user[15]:
            display_name = user[15]
        elif user[1]:
            display_name = user[1]
        else:
            display_name = user[2]

        # Учурдагы ставкаларды эсептөө
        total_bets = 0
        if chat_id in chat_manager.user_current_bets and user_id in chat_manager.user_current_bets[chat_id]:
            for bet in chat_manager.user_current_bets[chat_id][user_id]:
                total_bets += bet['amount']
        if chat_id in chat_manager.user_range_bets and user_id in chat_manager.user_range_bets[chat_id]:
            total_bets += chat_manager.user_range_bets[chat_id][user_id].get('total_amount', 0)

        if total_bets > 0:
            balance_text = f"{display_name}\nМонеты: {user[3]} +{total_bets}🪙"
        else:
            balance_text = f"{display_name}\nМонеты: {user[3]}🪙"

        if user[3] == 0 and total_bets == 0:
            keyboard = [[InlineKeyboardButton("🎁 Получить бонус", callback_data="show_channel_bonus")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.effective_chat.send_message(balance_text, reply_markup=reply_markup)
        else:
            await update.effective_chat.send_message(balance_text)
        return

    if text.upper() == "ГО":
        if chat_id not in chat_manager.roulette_started or not chat_manager.roulette_started[chat_id]:
            await update.effective_chat.send_message("Рулетка не запущена, наберите Рулетка")
            return
        await handle_go_command(update, context)
        return

    if text.upper() == "КРУТИТЬ":
        if chat_id not in chat_manager.roulette_started or not chat_manager.roulette_started[chat_id]:
            await update.effective_chat.send_message("Рулетка не запущена, наберите Рулетка")
            return
        await handle_go_command(update, context)
        return

    if text.upper() == "!ЛОГ":
        await show_big_log(update, context)
        return

    if text.upper() == "ЛОГ":
        await show_small_log(update, context)
        return

    if text.upper() == "ТОП":
        current_user_id = update.effective_user.id
        current_user = UserManager.get_user(current_user_id)
        user_position = UserManager.get_user_position_by_balance(current_user_id)

        top_users = UserManager.get_global_top_users(10)

        if not top_users:
            top_text = "[ТОП 10 БОГАТЫХ]\n\nТоп пуст!\n\n"
            telegram_name = current_user[2] if current_user and current_user[2] else update.effective_user.first_name
            top_text += f"{telegram_name}: {user_position} место"
            await update.effective_chat.send_message(top_text)
            return

        top_text = "[ТОП 10 БОГАТЫХ]\n\n"

        for i, (top_user_id, display_name, username, first_name, balance) in enumerate(top_users, 1):
            if display_name:
                name = display_name
            elif username:
                name = username
            else:
                name = first_name

            top_text += f"{i}. {name} [{balance}]\n"

        top_text += "¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯\n"
        if current_user:
            display_name_me = current_user[15] if current_user[15] else (current_user[1] if current_user[1] else current_user[2])
        else:
            display_name_me = update.effective_user.first_name
        top_text += f"Топ {user_position}: {display_name_me} [{current_user[3] if current_user else 0}]"

        await update.effective_chat.send_message(top_text)
        return

    if text.upper() in ["ДОНАТ", "ДОНАЦ", "DONATE", "ПОПОЛНИТЬ"]:
        user = UserManager.get_user(user_id)

        if not user:
            return

        display_name = user[15] if len(user) > 15 and user[15] else (user[1] if user[1] else user[2])

        donate_text = (
            f"Монеты🪙\n"
            f"200.000 - 100₽\n"
            f"500.000 - 230₽\n"
            f"1.000.000 - 450₽\n"
            f"2.000.000 - 845₽\n"
            f"5.000.000 - 2.000₽\n"
            f"10.000.000 - 4.000₽\n"
            f"50.000.000 - 20000₽\n"
            f"100.000.000 - 40000₽\n\n"
            f"Telegram не сможет помочь с покупками, сделанными через нашего бота,\n"
            f"Если возникнут вопросы, Вы можете обратиться к: https://t.me/MX_KASSA"
        )

        keyboard = [
            [InlineKeyboardButton("💳 Донат", url="https://t.me/MX_KASSA")],
            [InlineKeyboardButton("Получить бонус", url="https://t.me/mani_app_bot/app")],
            [InlineKeyboardButton("Связаться с тех. поддержкой", url="https://t.me/MX_KASSA")],
            [InlineKeyboardButton("🌐 ВЕБ ПРИЛОЖЕНИЕ", url=WEBAPP_URL)]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.effective_chat.send_message(donate_text, reply_markup=reply_markup)
        return

    if text.upper() in ["ПРОФИЛЬ", "ПРОФ", "PROFILE", "PROF"]:
        user_id = update.effective_user.id
        user = UserManager.get_user(user_id)

        if not user:
            return

        if user[15]:
            display_name = user[15]
        elif user[1]:
            display_name = user[1]
        else:
            display_name = user[2]

        profile_text = (
            f"{display_name}: ♠️♥️\n"
            f"ID: {user_id}\n"
            f"Монеты: {user[3]}🪙\n"
            f"Выиграно: {user[8]}\n"
            f"Проиграно: {user[7]}\n"
            f"Макс. выигрыш: {user[10]}\n"
            f"Макс. ставка: {user[9]}"
        )

        await update.effective_chat.send_message(profile_text)
        return

    if text_lower == "история":
        user_id = update.effective_user.id
        transactions = UserManager.get_transaction_history(user_id, 10)

        if not transactions:
            await update.effective_chat.send_message("История пуста")
            return

        history_text = ""
        for date_str, amount, ttype, description in transactions:
            try:
                time_str = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").strftime("[%H:%M:%S]")
                if amount > 0:
                    history_text += f"{time_str} выигрыш в {description.lower()}: +{amount}\n"
                else:
                    history_text += f"{time_str} проигрыш в {description.lower()}: {amount}\n"
            except:
                continue

        await update.effective_chat.send_message(history_text)
        return

    if text_lower == "отмена":
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id

        user = UserManager.get_user(user_id)
        if not user:
            return

        if user[15]:
            username = user[15]
        elif user[1]:
            username = user[1]
        else:
            username = user[2]

        if chat_id in chat_manager.roulette_bets and user_id in chat_manager.roulette_bets[chat_id]:
            bets = chat_manager.roulette_bets[chat_id][user_id]
            total_return = 0

            for bet in bets:
                total_return += bet['amount']
                await UserManager.update_balance(user_id, bet['amount'], f"Возврат ставки: +{bet['amount']}")

            del chat_manager.roulette_bets[chat_id][user_id]
            if chat_id in chat_manager.user_current_bets and user_id in chat_manager.user_current_bets[chat_id]:
                del chat_manager.user_current_bets[chat_id][user_id]
            if chat_id in chat_manager.user_range_bets and user_id in chat_manager.user_range_bets[chat_id]:
                del chat_manager.user_range_bets[chat_id][user_id]

            await update.effective_chat.send_message(f"Ставки {username} отменены\n💰 Возврат: {total_return} 🪙")
        else:
            await update.effective_chat.send_message(f"{username}, у вас нет ставок для отмены")
        return

    if text.upper() in ["РУЛЕТКА", "RULE", "ROULETTE"]:
        await Games.ruleka(update, context)
        return

    if text.upper() in ["БАНДИТ", "BANDIT"]:
        await Games.banditka(update, context)
        return

    if text.upper() == "БЛЭКДЖЕК" or text.upper() == "BLACKJACK" or text.upper() == "БД":
        await Games.start_blackjack(update, context)
        return

    for game_key in SLOT_GAMES.keys():
        if text_lower == game_key:
            if user[3] < SLOT_GAMES[game_key]['min_bet']:
                await update.effective_chat.send_message(f"❌ Недостаточно монет! Минимум {SLOT_GAMES[game_key]['min_bet']} 🪙")
                return

            context.user_data['current_slot'] = {
                'game_key': game_key,
                'game_name': SLOT_GAMES[game_key]['name'],
                'emoji': SLOT_GAMES[game_key]['emoji']
            }

            await update.effective_chat.send_message(
                f"{SLOT_GAMES[game_key]['emoji']} **{SLOT_GAMES[game_key]['name']}**\n\n"
                f"Введите сумму ставки:"
            )
            return

    if text.upper().startswith("ВА-БАНК"):
        if chat_id not in chat_manager.roulette_started or not chat_manager.roulette_started[chat_id]:
            await update.effective_chat.send_message("Рулетка не запущена, наберите Рулетка")
            return

        user_id = update.effective_user.id
        user = UserManager.get_user(user_id)

        if not user:
            return

        amount = user[3]

        if amount < 1:
            keyboard = [
                [InlineKeyboardButton("💳 Донат", url="https://t.me/MX_KASSA")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.effective_chat.send_message(
                f"❌ Недостаточно монет для ставки!\n\n",
                reply_markup=reply_markup
            )
            return

        text_upper = text.upper()

        range_match = re.search(r'ВА-БАНК\s+(\d+)-(\d+)', text_upper)
        if range_match:
            start_num = int(range_match.group(1))
            end_num = int(range_match.group(2))

            if start_num < 0 or end_num > 12 or start_num >= end_num:
                await update.effective_chat.send_message("❌ Неверный диапазон! Используйте числа от 0 до 12.")
                return

            await Games.handle_range_bet(update, context, amount, start_num, end_num)
            return

        for num in range(0, 13):
            num_str = str(num)
            if text_upper == f"ВА-БАНК {num_str}" or text_upper == f"ВА-БАНК{num_str}" or text_upper.startswith(f"ВА-БАНК {num_str} ") or text_upper.startswith(f"ВА-БАНК {num_str}\n"):
                success = await Games.handle_roulette_bet(update, context, "number", num_str, amount)
                if success:
                    if user[15]:
                        username = user[15]
                    elif user[1]:
                        username = user[1]
                    else:
                        username = user[2]
                    await update.effective_chat.send_message(
                        f"<a href='tg://user?id={user_id}'>{username}</a> поставил все {amount} на {num_str}",
                        parse_mode='HTML'
                    )
                return

        if "ВА-БАНК К" in text_upper or "ВА-БАНК КРАС" in text_upper:
            success = await Games.handle_roulette_bet(update, context, "color", "red", amount)
            bet_desc = "красное"
        elif "ВА-БАНК Ч" in text_upper or "ВА-БАНК ЧЕР" in text_upper or "ВА-БАНК ЧЁР" in text_upper:
            success = await Games.handle_roulette_bet(update, context, "color", "black", amount)
            bet_desc = "чёрное"
        elif "ВА-БАНК З" in text_upper or "ВА-БАНК ЗЕЛ" in text_upper or "ВА-БАНК 0" in text_upper:
            success = await Games.handle_roulette_bet(update, context, "number", "0", amount)
            bet_desc = "зеленое"
        elif "ВА-БАНК 1-3" in text_upper:
            success = await Games.handle_roulette_bet(update, context, "range", "1_3", amount)
            bet_desc = "1-3"
        elif "ВА-БАНК 4-6" in text_upper:
            success = await Games.handle_roulette_bet(update, context, "range", "4_6", amount)
            bet_desc = "4-6"
        elif "ВА-БАНК 7-9" in text_upper:
            success = await Games.handle_roulette_bet(update, context, "range", "7_9", amount)
            bet_desc = "7-9"
        elif "ВА-БАНК 10-12" in text_upper:
            success = await Games.handle_roulette_bet(update, context, "range", "10_12", amount)
            bet_desc = "10-12"
        else:
            words = text.split()
            if len(words) > 1:
                bet_word = words[1].lower()
                if bet_word in ["ч", "черное", "черный", "чёрное", "чёрный"]:
                    success = await Games.handle_roulette_bet(update, context, "color", "black", amount)
                    bet_desc = "чёрное"
                elif bet_word in ["к", "красное", "красный"]:
                    success = await Games.handle_roulette_bet(update, context, "color", "red", amount)
                    bet_desc = "красное"
                elif bet_word in ["з", "зеленое", "зеленый", "0"]:
                    success = await Games.handle_roulette_bet(update, context, "number", "0", amount)
                    bet_desc = "зеленое"
                elif "-" in bet_word:
                    if bet_word == "1-3":
                        success = await Games.handle_roulette_bet(update, context, "range", "1_3", amount)
                        bet_desc = "1-3"
                    elif bet_word == "4-6":
                        success = await Games.handle_roulette_bet(update, context, "range", "4_6", amount)
                        bet_desc = "4-6"
                    elif bet_word == "7-9":
                        success = await Games.handle_roulette_bet(update, context, "range", "7_9", amount)
                        bet_desc = "7-9"
                    elif bet_word == "10-12":
                        success = await Games.handle_roulette_bet(update, context, "range", "10_12", amount)
                        bet_desc = "10-12"
                    else:
                        await update.effective_chat.send_message("❌ Неверная команда! Используйте: Ва-банк <ставка>")
                        return
                elif bet_word.isdigit() and 0 <= int(bet_word) <= 12:
                    num = int(bet_word)
                    success = await Games.handle_roulette_bet(update, context, "number", str(num), amount)
                    bet_desc = str(num)
                else:
                    await update.effective_chat.send_message("❌ Неверная команда! Используйте: Ва-банк <ставка>")
                    return

                if success:
                    if user[15]:
                        username = user[15]
                    elif user[1]:
                        username = user[1]
                    else:
                        username = user[2]
                    await update.effective_chat.send_message(
                        f"<a href='tg://user?id={user_id}'>{username}</a> поставил все {amount} на {bet_desc}",
                        parse_mode='HTML'
                    )
                return
            else:
                await update.effective_chat.send_message("❌ Неверная команда! Используйте: Ва-банк <ставка>")
                return

        if success:
            if user[15]:
                username = user[15]
            elif user[1]:
                username = user[1]
            else:
                username = user[2]
            await update.effective_chat.send_message(
                f"<a href='tg://user?id={user_id}'>{username}</a> поставил все {amount} на {bet_desc}",
                parse_mode='HTML'
            )
        return

    if text_lower.startswith("бандит"):
        words = text.split()

        if len(words) == 1:
            amount = 1000
        elif len(words) == 2:
            try:
                amount = int(words[1])
                if amount < 1:
                    await update.effective_chat.send_message(f"❌ Сумма должна быть больше 0!")
                    return
            except ValueError:
                amount = 1000
        else:
            amount = 1000

        if user[3] < amount:
            if user[15]:
                display_name = user[15]
            elif user[1]:
                display_name = user[1]
            else:
                display_name = user[2]

            await update.effective_chat.send_message(f"{display_name}, недостаточно монет на балансе")
            return

        await UserManager.update_balance(user_id, -amount, f"Ставка в бандитку: -{amount}")
        asyncio.create_task(Games._banditka_logic_with_amount(update, context, amount))
        return

    words = text.split()
    if len(words) == 2:
        try:
            amount = int(words[0])
            if amount >= 1 and words[1].lower() == "бандит":
                if user[3] < amount:
                    if user[15]:
                        display_name = user[15]
                    elif user[1]:
                        display_name = user[1]
                    else:
                        display_name = user[2]

                    await update.effective_chat.send_message(f"{display_name}, недостаточно монет на балансе")
                    return

                await UserManager.update_balance(user_id, -amount, f"Ставка в бандитку: -{amount}")
                asyncio.create_task(Games._banditka_logic_with_amount(update, context, amount))
                return
        except ValueError:
            pass

    if "+" in text:
        try:
            amount = int(text.replace("+", "").strip())
            if amount <= 0:
                return

            if user[3] < amount:
                await update.effective_chat.send_message("❌ Недостаточно монет на балансе")
                return

            can_transfer, message = UserManager.can_make_transfer(user_id, amount)
            if not can_transfer:
                await update.effective_chat.send_message(f"{message}")
                return

            if update.message.reply_to_message:
                to_user_id = update.message.reply_to_message.from_user.id
                to_user = UserManager.get_user(to_user_id)

                if to_user:
                    to_display_name = to_user[15] if len(to_user) > 15 and to_user[15] else (to_user[1] if to_user[1] else to_user[2])
                    from_display_name = user[15] if len(user) > 15 and user[15] else (user[1] if user[1] else user[2])

                    if from_display_name:
                        from_name = from_display_name
                    elif user[1]:
                        from_name = user[1]
                    else:
                        from_name = user[2]

                    if to_display_name:
                        to_name = to_display_name
                    elif to_user[1]:
                        to_name = to_user[1]
                    else:
                        to_name = to_user[2]

                    await UserManager.update_balance(user_id, -amount, f"Перевод игроку {to_display_name}: -{amount}")
                    await UserManager.update_balance(to_user_id, amount, f"Перевод от игрока {from_display_name}: +{amount}")

                    UserManager.update_transfer_usage(user_id, amount)

                    await update.effective_chat.send_message(
                        f"💸 <a href='tg://user?id={user_id}'>{from_name}</a> перевёл {amount}🪙 пользователю <a href='tg://user?id={to_user_id}'>{to_name}</a>",
                        parse_mode='HTML'
                    )

        except ValueError:
            return

    if len(words) >= 2:
        try:
            amount = int(words[0])
            bet_part = ' '.join(words[1:]).lower()

            if amount < 1:
                return

            if chat_id not in chat_manager.roulette_started or not chat_manager.roulette_started[chat_id]:
                await update.effective_chat.send_message("Рулетка не запущена, наберите Рулетка")
                return

            if user[3] < amount:
                if user[15]:
                    display_name = user[15]
                elif user[1]:
                    display_name = user[1]
                else:
                    display_name = user[2]
                keyboard = [
                    [InlineKeyboardButton("💳 Донат", url="https://t.me/MX_KASSA")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.effective_chat.send_message(
                    f"{display_name}, недостаточно монет!\n\n",
                    reply_markup=reply_markup
                )
                return

            range_match = re.search(r'(\d+)-(\d+)', bet_part)
            if range_match:
                start_num = int(range_match.group(1))
                end_num = int(range_match.group(2))

                if start_num < 0 or end_num > 12 or start_num >= end_num:
                    await update.effective_chat.send_message("❌ Неверный диапазон! Используйте числа от 0 до 12.")
                    return

                await Games.handle_range_bet(update, context, amount, start_num, end_num)
                return

            if bet_part.isdigit():
                num = int(bet_part)
                if 0 <= num <= 12:
                    success = await Games.handle_roulette_bet(update, context, "number", str(num), amount)
                    if success:
                        if user[15]:
                            username = user[15]
                        elif user[1]:
                            username = user[1]
                        else:
                            username = user[2]
                        await update.effective_chat.send_message(
                            f"<a href='tg://user?id={user_id}'>{username}</a> {amount} на {num}",
                            parse_mode='HTML'
                        )
                    return

            elif bet_part in ["ч", "черное", "черный", "чёрное", "чёрный"]:
                success = await Games.handle_roulette_bet(update, context, "color", "black", amount)
                bet_desc = "чёрное"
                if success:
                    if user[15]:
                        username = user[15]
                    elif user[1]:
                        username = user[1]
                    else:
                        username = user[2]
                    await update.effective_chat.send_message(
                        f"<a href='tg://user?id={user_id}'>{username}</a> {amount} на {bet_desc}",
                        parse_mode='HTML'
                    )
                return

            elif bet_part in ["к", "красное", "красный"]:
                success = await Games.handle_roulette_bet(update, context, "color", "red", amount)
                bet_desc = "красное"
                if success:
                    if user[15]:
                        username = user[15]
                    elif user[1]:
                        username = user[1]
                    else:
                        username = user[2]
                    await update.effective_chat.send_message(
                        f"<a href='tg://user?id={user_id}'>{username}</a> {amount} на {bet_desc}",
                        parse_mode='HTML'
                    )
                return

            elif bet_part in ["з", "зеленое", "зеленый", "0"]:
                success = await Games.handle_roulette_bet(update, context, "number", "0", amount)
                bet_desc = "зеленое"
                if success:
                    if user[15]:
                        username = user[15]
                    elif user[1]:
                        username = user[1]
                    else:
                        username = user[2]
                    await update.effective_chat.send_message(
                        f"<a href='tg://user?id={user_id}'>{username}</a> {amount} на {bet_desc}",
                        parse_mode='HTML'
                    )
                return

            elif "-" in bet_part:
                range_parts = bet_part.split("-")
                if len(range_parts) == 2:
                    try:
                        start_num = int(range_parts[0])
                        end_num = int(range_parts[1])

                        if start_num < 0 or end_num > 12 or start_num >= end_num:
                            await update.effective_chat.send_message("❌ Неверный диапазон! Используйте числа от 0 до 12.")
                            return

                        await Games.handle_range_bet(update, context, amount, start_num, end_num)
                        return
                    except ValueError:
                        pass

        except ValueError:
            pass

async def show_user_current_bets(update, context):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    user = UserManager.get_user(user_id)
    if not user:
        return

    if user[15]:
        username = user[15]
    elif user[1]:
        username = user[1]
    else:
        username = user[2]

    if chat_id in chat_manager.user_current_bets and user_id in chat_manager.user_current_bets[chat_id]:
        current_bets = chat_manager.user_current_bets[chat_id][user_id]

        if current_bets:
            bets_text = f"{username}\n"
            total_amount = 0

            for bet in current_bets:
                amount = bet['amount']
                description = bet.get('description', '')
                total_amount += amount
                bets_text += f"{amount} на {description}\n"

            bets_text += f"Итого: {total_amount} 🪙"
            await update.effective_chat.send_message(bets_text)
        else:
            await update.effective_chat.send_message(f"{username}, у вас нет текущих ставок")
    elif chat_id in chat_manager.user_range_bets and user_id in chat_manager.user_range_bets[chat_id]:
        range_bet = chat_manager.user_range_bets[chat_id][user_id]
        bets_text = (
            f"{username}\n"
            f"{range_bet['total_amount']} на {range_bet['description']}\n"
            f"Итого: {range_bet['total_amount']} 🪙"
        )
        await update.effective_chat.send_message(bets_text)
    else:
        await update.effective_chat.send_message(f"{username}, у вас нет текущих ставок")

async def repeat_user_last_bets(update, context):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    user = UserManager.get_user(user_id)
    if not user:
        return

    if chat_id not in chat_manager.roulette_started or not chat_manager.roulette_started[chat_id]:
        await update.effective_chat.send_message("Рулетка не запущена, наберите Рулетка")
        return

    if chat_id in chat_manager.last_spin_bets and user_id in chat_manager.last_spin_bets[chat_id]:
        last_bets = chat_manager.last_spin_bets[chat_id][user_id]

        if not last_bets:
            await update.effective_chat.send_message("Нет предыдущих ставок для повторения")
            return

        if user[15]:
            username = user[15]
        elif user[1]:
            username = user[1]
        else:
            username = user[2]

        bet_dict = {}
        for bet in last_bets:
            key = (bet['type'], bet['value'])
            if key in bet_dict:
                bet_dict[key]['amount'] += bet['amount']
            else:
                bet_dict[key] = bet.copy()

        total_amount = 0
        success_count = 0
        bets_list = []
        range_bet_total = 0
        range_start = None
        range_end = None

        is_range = False
        for bet in bet_dict.values():
            if bet['type'] == 'range':
                is_range = True
                range_bet_total += bet['amount']
                if range_start is None:
                    range_parts = bet['value'].split('_')
                    if len(range_parts) == 2:
                        range_start = int(range_parts[0])
                        range_end = int(range_parts[1])
                break

        if is_range and range_start is not None and range_end is not None:
            if user[3] < range_bet_total:
                await update.effective_chat.send_message("❌ Недостаточно монет для повторения ставок!")
                return

            await Games.handle_range_bet(update, context, range_bet_total, range_start, range_end)

        for bet in bet_dict.values():
            if bet['type'] != 'range':
                bet_type = bet['type']
                bet_value = bet['value']
                amount = bet['amount']
                description = bet.get('description', '')

                if user[3] < amount:
                    continue

                success = await Games.handle_roulette_bet(update, context, bet_type, bet_value, amount)
                if success:
                    total_amount += amount
                    success_count += 1
                    bets_list.append(f"{amount} на {description}")

        if success_count > 0:
            result_text = f"{username}\n"
            for bet_line in bets_list:
                result_text += f"{bet_line}\n"
            result_text += f"Итого: {total_amount} 🪙"
            await update.effective_chat.send_message(result_text)
        elif not is_range:
            await update.effective_chat.send_message("❌ Не удалось повторить ставки. Проверьте баланс")
    else:
        await update.effective_chat.send_message("Нет предыдущих ставок для повторения")

async def double_user_last_bets(update, context):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    user = UserManager.get_user(user_id)
    if not user:
        return

    if chat_id not in chat_manager.roulette_started or not chat_manager.roulette_started[chat_id]:
        await update.effective_chat.send_message("Рулетка не запущена, наберите Рулетка")
        return

    if chat_id in chat_manager.last_spin_bets and user_id in chat_manager.last_spin_bets[chat_id]:
        last_bets = chat_manager.last_spin_bets[chat_id][user_id]

        if not last_bets:
            await update.effective_chat.send_message("Нет предыдущих ставок для удвоения")
            return

        bet_dict = {}
        for bet in last_bets:
            key = (bet['type'], bet['value'])
            if key in bet_dict:
                bet_dict[key]['amount'] += bet['amount']
            else:
                bet_dict[key] = bet.copy()

        if user[15]:
            username = user[15]
        elif user[1]:
            username = user[1]
        else:
            username = user[2]

        total_amount = 0
        success_count = 0
        bets_list = []
        range_bet_total = 0
        range_start = None
        range_end = None

        is_range = False
        for bet in bet_dict.values():
            if bet['type'] == 'range':
                is_range = True
                range_bet_total += bet['amount'] * 2
                if range_start is None:
                    range_parts = bet['value'].split('_')
                    if len(range_parts) == 2:
                        range_start = int(range_parts[0])
                        range_end = int(range_parts[1])
                break

        if is_range and range_start is not None and range_end is not None:
            if user[3] < range_bet_total:
                await update.effective_chat.send_message("❌ Недостаточно монет для удвоения ставок!")
                return

            await Games.handle_range_bet(update, context, range_bet_total, range_start, range_end)

        for bet in bet_dict.values():
            if bet['type'] != 'range':
                bet_type = bet['type']
                bet_value = bet['value']
                original_amount = bet['amount']
                new_amount = original_amount * 2
                description = bet.get('description', '')

                if user[3] < new_amount:
                    continue

                success = await Games.handle_roulette_bet(update, context, bet_type, bet_value, new_amount)
                if success:
                    total_amount += new_amount
                    success_count += 1
                    bets_list.append(f"{new_amount} на {description}")

        if success_count > 0:
            result_text = f"{username}\n"
            for bet_line in bets_list:
                result_text += f"{bet_line}\n"
            result_text += f"Итого: {total_amount} 🪙"
            await update.effective_chat.send_message(result_text)
        elif not is_range:
            await update.effective_chat.send_message("❌ Не удалось удвоить ставки. Проверьте баланс")
    else:
        await update.effective_chat.send_message("Нет предыдущих ставок для удвоения")

async def show_small_log(update, context):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    user = UserManager.get_user(user_id)

    if not user:
        return

    logs_db = UserManager.get_global_roulette_logs(chat_id, 10)
    logs = logs_db if logs_db else []

    if not logs:
        await update.effective_chat.send_message("Лог пуст")
        return

    log_text = ""
    for log in reversed(logs):
        if log:
            log_text += f"{log}\n"

    if log_text.strip():
        await update.effective_chat.send_message(log_text.strip())

        if is_super_admin(user_id):
            last_results = logs[:10] if len(logs) >= 10 else logs
            next_result = calculate_next_result(last_results, chat_id)

            await context.bot.send_message(
                chat_id=user_id,
                text=f"{next_result}"
            )

async def show_big_log(update, context):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    user = UserManager.get_user(user_id)

    if not user:
        return

    logs_db = UserManager.get_global_roulette_logs_all(chat_id, 21)
    logs = logs_db if logs_db else []

    if not logs:
        await update.effective_chat.send_message("Лог пуст")
        return

    log_text = ""
    for log in reversed(logs):
        if log:
            log_text += f"{log}\n"

    if log_text.strip():
        await update.effective_chat.send_message(log_text.strip())

        if is_super_admin(user_id):
            last_results = logs[:10] if len(logs) >= 10 else logs
            next_result = calculate_next_result(last_results, chat_id)

            await context.bot.send_message(
                chat_id=user_id,
                text=f"{next_result}"
            )

async def handle_setname_command(update, context):
    user_id = update.effective_user.id

    text = update.message.text.strip()
    words = text.split()

    if len(words) < 2:
        await update.effective_chat.send_message("❌ Укажите новое имя! Пример: /setname НовоеИмя")
        return

    new_name = ' '.join(words[1:])

    if len(new_name) > 50:
        await update.effective_chat.send_message("❌ Имя слишком длинное! Максимум 50 символов.")
        return

    UserManager.set_display_name(user_id, new_name)

    await update.effective_chat.send_message(f"✅ Ваше отображаемое имя изменено на: {new_name}")

async def handle_mute_time_command(update, context):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if not update.message.reply_to_message:
        await update.effective_chat.send_message("❌ Команда должна быть ответом на сообщение пользователя!")
        return

    is_admin = await is_group_admin(context, chat_id, user_id)

    if not (is_super_admin(user_id) or UserManager.has_permission(user_id, "mute") or is_admin):
        await update.effective_chat.send_message("❌ У вас нет прав на мутирование!")
        return

    target_user = update.message.reply_to_message.from_user
    target_id = target_user.id

    if target_id == user_id:
        await update.effective_chat.send_message("❌ Нельзя замутить самого себя!")
        return

    target_is_admin = await is_group_admin(context, chat_id, target_id)
    if target_is_admin and not is_super_admin(user_id):
        await update.effective_chat.send_message("❌ Нельзя замутить другого администратора!")
        return

    text = update.message.text.strip()
    words = text.split()

    if len(words) < 2:
        await update.effective_chat.send_message("❌ Укажите время! Пример: /mute 60 (минут)")
        return

    try:
        minutes = int(words[1])
        if minutes <= 0:
            await update.effective_chat.send_message("❌ Время должно быть положительным!")
            return

        hours = minutes / 60
        UserManager.mute_user(target_id, hours, user_id)

        target_name = target_user.first_name
        if target_user.username:
            target_name = target_user.username

        admin_name = update.effective_user.first_name
        if update.effective_user.username:
            admin_name = update.effective_user.username

        mute_until = datetime.now() + timedelta(minutes=minutes)
        mute_until_str = mute_until.strftime("%d.%m.%Y %H:%M:%S")

        await update.effective_chat.send_message(
            f"🔇 Пользователь <a href='tg://user?id={target_id}'>{target_name}</a> замьючен до {mute_until_str}!\n"
            f"👮 Администратор: <a href='tg://user?id={user_id}'>{admin_name}</a>",
            parse_mode='HTML'
        )
    except ValueError:
        await update.effective_chat.send_message("❌ Неверный формат времени! Используйте число минут.")

async def handle_webapp_data(update, context):
    data = update.effective_message.web_app_data
    if not data:
        return

    try:
        json_data = json.loads(data.data)
        user_id = update.effective_user.id

        action = json_data.get('action')
        amount = json_data.get('amount', 0)

        if action == 'bonus':
            await UserManager.update_balance(user_id, amount, f"Бонус из веб приложения: +{amount}")
            await update.effective_chat.send_message(f"✅ Получен бонус: +{amount} 🪙")

        elif action == 'crash_win':
            await UserManager.update_balance(user_id, amount, f"Выигрыш в Крэш: +{amount}")

        elif action == 'crash_loss':
            await UserManager.update_balance(user_id, -amount, f"Проигрыш в Крэш: -{amount}")

        elif action == 'durak_win':
            await UserManager.update_balance(user_id, amount, f"Выигрыш в Дурак: +{amount}")

        elif action == 'durak_loss':
            await UserManager.update_balance(user_id, -amount, f"Проигрыш в Дурак: -{amount}")

        elif action == 'get_balance':
            user = UserManager.get_user(user_id)
            if user:
                await web_sync.send_balance_update(user_id, user[3])

    except Exception as e:
        logger.error(f"Ошибка обработки веб данных: {e}")

async def check_roulette_inactivity(context):
    current_time = datetime.now().timestamp()
    for chat_id, last_time in list(chat_manager.last_activity.items()):
        if current_time - last_time > 1200:
            if chat_id in chat_manager.roulette_started:
                # Ставкалар бар болсо — кайтарып бер
                if chat_id in chat_manager.roulette_bets and chat_manager.roulette_bets[chat_id]:
                    refund_summary = {}
                    for user_id, bets in chat_manager.roulette_bets[chat_id].items():
                        total_refund = sum(b['amount'] for b in bets)
                        if total_refund > 0:
                            await UserManager.update_balance(user_id, total_refund, f"Рулетка өчкөндө кайтаруу: +{total_refund}")
                            refund_summary[user_id] = total_refund
                    if refund_summary:
                        try:
                            lines = "⚠️ Рулетка 20 мин ичинде жүргүзүлбөдү.\n💰 Ставкалар кайтарылды:\n"
                            for uid, amt in refund_summary.items():
                                u = UserManager.get_user(uid)
                                name = (u[15] or u[1] or u[2]) if u else str(uid)
                                lines += f"• {name}: +{amt} 🪙\n"
                            await context.bot.send_message(chat_id=chat_id, text=lines)
                        except:
                            pass
                    chat_manager.roulette_bets[chat_id] = {}

                chat_manager.roulette_started[chat_id] = False
                del chat_manager.last_activity[chat_id]

async def handle_roulette_callback(update, context):
    query = update.callback_query
    await query.answer()

    data = query.data
    chat_id = query.message.chat_id

    if data not in ["repeat_bet", "double_bet"] and chat_id not in chat_manager.roulette_started:
        chat_manager.roulette_started[chat_id] = True
    chat_manager.last_activity[chat_id] = datetime.now().timestamp()

    if data == "spin_roulette":
        if chat_id not in chat_manager.roulette_started or not chat_manager.roulette_started[chat_id]:
            await query.message.reply_text("Рулетка не запущена, наберите Рулетка")
            return
        await Games.spin_roulette_logic(update, context, chat_id)
    elif data.startswith("bet_"):
        if chat_id not in chat_manager.roulette_started or not chat_manager.roulette_started[chat_id]:
            await query.answer("Рулетка не запущена, наберите Рулетка", show_alert=True)
            return

        user_id = query.from_user.id

        if data == "bet_red":
            bet_type, bet_value = "color", "red"
            bet_description = "красное"
        elif data == "bet_black":
            bet_type, bet_value = "color", "black"
            bet_description = "чёрное"
        elif data == "bet_zero":
            bet_type, bet_value = "number", "0"
            bet_description = "зеленое"
        elif data == "bet_1_3":
            bet_type, bet_value = "range", "1_3"
            bet_description = "1-3"
        elif data == "bet_4_6":
            bet_type, bet_value = "range", "4_6"
            bet_description = "4-6"
        elif data == "bet_7_9":
            bet_type, bet_value = "range", "7_9"
            bet_description = "7-9"
        elif data == "bet_10_12":
            bet_type, bet_value = "range", "10_12"
            bet_description = "10-12"
        else:
            return

        user = UserManager.get_user(user_id)
        if not user:
            return

        amount = 1000

        if user[3] >= amount:
            success = await Games.handle_roulette_bet(update, context, bet_type, bet_value, amount)
            if success:
                if user[15]:
                    username = user[15]
                elif user[1]:
                    username = user[1]
                else:
                    username = user[2]
                await query.message.reply_text(
                    f"<a href='tg://user?id={user_id}'>{username}</a> {amount} на {bet_description}",
                    parse_mode='HTML'
                )
            else:
                await query.message.reply_text("❌ Ошибка при принятии ставки!")
        else:
            keyboard = [[InlineKeyboardButton("💳 Донат", url="https://t.me/MX_KASSA")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text("❌ Недостаточно монет!\n\n", reply_markup=reply_markup)
    elif data == "repeat_bet":
        if chat_id not in chat_manager.roulette_started or not chat_manager.roulette_started[chat_id]:
            chat_manager.roulette_started[chat_id] = True
        await repeat_user_last_bets(update, context)
    elif data == "double_bet":
        if chat_id not in chat_manager.roulette_started or not chat_manager.roulette_started[chat_id]:
            chat_manager.roulette_started[chat_id] = True
        await double_user_last_bets(update, context)

async def handle_blackjack_callback(update, context):
    query = update.callback_query
    data = query.data

    if data.startswith("bj_bet_"):
        bet_amount = int(data.replace("bj_bet_", ""))
        await Games.handle_blackjack_bet(update, context, bet_amount)
    elif data.startswith("bj_hit_"):
        game_id = data.replace("bj_hit_", "")
        await Games.handle_blackjack_hit(update, context, game_id)
    elif data.startswith("bj_stand_"):
        game_id = data.replace("bj_stand_", "")
        await Games.handle_blackjack_stand(update, context, game_id)


async def handle_crash_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data.startswith("crash_bet_"):
        bet = int(data.replace("crash_bet_", ""))
        await Games.crash_play(update, context, bet)

    elif data.startswith("crash_cashout_"):
        target_id = int(data.replace("crash_cashout_", ""))
        if user_id != target_id:
            await query.answer("\u274c \u0411\u0443\u043b \u0441\u0435\u043d\u0438\u043d \u043e\u044e\u043d\u0443\u04a3 \u044d\u043c\u0435\u0441!", show_alert=True)
            return
        game_state = context.bot_data.get(f"crash_{user_id}")
        if not game_state:
            await query.answer("\u23f0 \u041e\u044e\u043d \u0430\u044f\u043a\u0442\u0430\u0434\u044b!", show_alert=True)
            return
        if game_state.get("cashed_out"):
            await query.answer("\u2705 \u0411\u0443\u0433\u0430 \u0447\u0435\u0439\u0438\u043d \u0430\u043b\u0434\u044b\u04a3\u0430\u0440!", show_alert=True)
            return
        current_mult = game_state.get("current_mult", 1.00)
        context.bot_data[f"crash_{user_id}"]["cashed_out"] = True
        context.bot_data[f"crash_{user_id}"]["cashout_mult"] = current_mult
        await query.answer(f"\u2705 \u0410\u043b\u0434\u044b\u04a3\u0430\u0440! {current_mult:.2f}x", show_alert=False)

async def handle_slot_callback(update, context):
    query = update.callback_query
    data = query.data

    if data.startswith("slot_bet_"):
        amount = int(data.replace("slot_bet_", ""))
        await handle_slot_bet(update, context, amount)

async def handle_ad_command(update, context):
    user_id = update.effective_user.id

    if not is_super_admin(user_id):
        await update.effective_chat.send_message("❌ Эта команда только для администратора!")
        return

    text = update.message.text.strip()
    words = text.split()

    if len(words) < 2:
        await update.effective_chat.send_message(
            "❌ Формат: /ad <сообщение>\n\n"
            "📋 Пример:\n"
            "• /ad Привет всем! У нас новый бонус!"
        )
        return

    ad_text = ' '.join(words[1:])

    await update.effective_chat.send_message("📢 Рассылка началась... Это может занять некоторое время.")

    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        cursor.execute("SELECT user_id FROM users")
        users = cursor.fetchall()

        cursor.execute("SELECT DISTINCT chat_id FROM global_roulette_logs")
        chats = cursor.fetchall()

        conn.close()

        sent_count = 0
        error_count = 0

        for (user_id,) in users:
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"📢 **РЕКЛАМА**\n\n{ad_text}"
                )
                sent_count += 1
                await asyncio.sleep(0.05)
            except:
                error_count += 1

        for (chat_id,) in chats:
            if chat_id and chat_id > 0:
                try:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=f"📢 **РЕКЛАМА**\n\n{ad_text}"
                    )
                    sent_count += 1
                    await asyncio.sleep(0.05)
                except:
                    error_count += 1

        await update.effective_chat.send_message(
            f"✅ Рассылка завершена!\n\n"
            f"📊 Отправлено: {sent_count}\n"
            f"❌ Ошибок: {error_count}"
        )

    except Exception as e:
        logger.error(f"Ошибка рассылки: {e}")
        await update.effective_chat.send_message(f"❌ Ошибка: {e}")

async def handle_chatlist_command(update, context):
    user_id = update.effective_user.id

    if not is_super_admin(user_id):
        await update.effective_chat.send_message("❌ Эта команда только для администратора!")
        return

    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT chat_id FROM global_roulette_logs WHERE chat_id < 0")
        chats = cursor.fetchall()
        conn.close()

        if not chats:
            await update.effective_chat.send_message("📋 Бот эч кандай группада жок.")
            return

        text = f"📋 БОТ БАРГАН ГРУППАЛАР ({len(chats)} группа)\n\n"
        for i, (chat_id,) in enumerate(chats, 1):
            try:
                chat = await context.bot.get_chat(chat_id)
                chat_name = chat.title or str(chat_id)
                member_count = await context.bot.get_chat_member_count(chat_id)
                # Шилтеме алуу
                link = None
                if chat.username:
                    link = f"https://t.me/{chat.username}"
                else:
                    try:
                        invite = await context.bot.export_chat_invite_link(chat_id)
                        link = invite
                    except Exception:
                        link = None
                link_text = f"\n   🔗 {link}" if link else ""
                text += f"{i}. {chat_name}\n   ID: {chat_id} | 👥 {member_count}{link_text}\n\n"
            except:
                text += f"{i}. ID: {chat_id}\n\n"

            if len(text) > 3500:
                await update.effective_chat.send_message(text)
                text = ""

        if text.strip():
            await update.effective_chat.send_message(text)

    except Exception as e:
        logger.error(f"Ошибка списка чатов: {e}")
        await update.effective_chat.send_message(f"❌ Ошибка: {e}")

# ============ МАГАЗИН СМАЙЛИКОВ ============

SHOP_EMOJIS = [
    "🪙", "💰", "💷", "💸", "💎", "🎴", "🀄️", "🃏",
    "♦️", "♥️", "♣️", "♠️", "🎀", "🎈", "🎁", "🧧",
    "💊", "🎯", "🎫", "🥇", "🏆", "🎾", "🧬", "🦠"
]

SHOP_BASE_PRICE = 99999999999

shop_prices = {}

def init_shop_prices():
    """Баштапкы баалар — баары бирдей"""
    for emoji in SHOP_EMOJIS:
        shop_prices[emoji] = SHOP_BASE_PRICE

init_shop_prices()

async def update_shop_prices_daily(context):
    """Күн сайын баасын рандом өзгөртөт"""
    for emoji in SHOP_EMOJIS:
        change_type = random.choice(["big", "small"])
        direction = random.choice([1, -1])
        if change_type == "big":
            delta = random.randint(50000, 100000) * 1000
        else:
            delta = random.randint(5000, 10000) * 1000
        new_price = shop_prices[emoji] + direction * delta
        shop_prices[emoji] = max(10000000, new_price)

def get_shop_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_emojis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            emoji TEXT,
            bought_price INTEGER,
            bought_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emoji_auctions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id INTEGER,
            emoji TEXT,
            start_price INTEGER,
            current_price INTEGER,
            buyer_id INTEGER,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn

async def handle_shop_command(update, context):
    """Магазин — смайликтер тизмеси"""
    if update.effective_chat.type not in ['group', 'supergroup', 'private']:
        return

    lines = ["🛒 *МАГАЗИН СМАЙЛИКОВ*\n"]
    for emoji in SHOP_EMOJIS:
        price = shop_prices[emoji]
        lines.append(f"{emoji}  —  *{price:,}* 🪙")

    lines.append("\n💡 Сатып алуу: *купить* + смайлик")
    lines.append("👜 Менин смайликтерим: *Мой Смайлик*")
    lines.append("💵 Сатуу: *продать* + смайлик + баасы")
    lines.append("🔨 Аукцион: *аукцион* + смайлик + баштапкы баасы")

    keyboard = [[InlineKeyboardButton("🛒 Магазин", callback_data="shop_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.effective_chat.send_message(
        "\n".join(lines),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def handle_shop_text(update, context, user, text, text_lower):
    """Текст аркылуу магазин буйруктарын иштетет"""
    user_id = update.effective_user.id

    # КУПИТЬ смайлик
    if text_lower.startswith("купить "):
        parts = text.strip().split(None, 1)
        if len(parts) < 2:
            await update.effective_chat.send_message("❌ Формат: купить 🪙")
            return True
        emoji = parts[1].strip()
        if emoji not in SHOP_EMOJIS:
            await update.effective_chat.send_message("❌ Мундай смайлик магазинде жок!")
            return True
        price = shop_prices[emoji]
        wallet = user[3] if user else 0
        if wallet < price:
            await update.effective_chat.send_message(
                f"❌ Жетишпейт!\n💰 Керек: *{price:,}* 🪙\n👛 Сенде: *{wallet:,}* 🪙",
                parse_mode=ParseMode.MARKDOWN
            )
            return True
        conn = get_shop_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM user_emojis WHERE user_id=? AND emoji=?", (user_id, emoji))
        if cursor.fetchone():
            conn.close()
            await update.effective_chat.send_message(f"⚠️ Бул смайлик сенде буга чейин бар: {emoji}")
            return True
        cursor.execute(
            "INSERT INTO user_emojis (user_id, emoji, bought_price) VALUES (?,?,?)",
            (user_id, emoji, price)
        )
        conn.commit()
        conn.close()
        await UserManager.update_balance(user_id, -price)
        display = user[15] or user[1] or user[2] or "Пользователь"
        await update.effective_chat.send_message(
            f"✅ *Сатып алынды!*\n\n"
            f"👤 {display}\n"
            f"🎁 Смайлик: {emoji}\n"
            f"💸 Төлөндү: *{price:,}* 🪙\n"
            f"👛 Калды: *{wallet - price:,}* 🪙",
            parse_mode=ParseMode.MARKDOWN
        )
        return True

    # МОЙ СМАЙЛИК
    if text_lower in ["мой смайлик", "мои смайлики", "мой смайл"]:
        conn = get_shop_db()
        cursor = conn.cursor()
        cursor.execute("SELECT emoji, bought_price, bought_at FROM user_emojis WHERE user_id=?", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        if not rows:
            await update.effective_chat.send_message("👜 У тебя нет смайликов.\n\n🛒 Купи в магазине: /Магазин")
            return True
        display = user[15] or user[1] or user[2] or "Пользователь"
        lines = [f"👜 *Смайлики {display}*\n"]
        for emoji, bought_price, bought_at in rows:
            current = shop_prices.get(emoji, 0)
            diff = current - bought_price
            trend = "📈" if diff > 0 else ("📉" if diff < 0 else "➡️")
            lines.append(f"{emoji}  {trend} Текущая цена: *{current:,}* 🪙")
        lines.append(f"\n📦 Всего: *{len(rows)}* смайлик")
        lines.append("💵 Продать: *продать* + смайлик + цена")
        lines.append("🔨 Аукцион: *аукцион* + смайлик + стартовая цена")
        await update.effective_chat.send_message(
            "\n".join(lines),
            parse_mode=ParseMode.MARKDOWN
        )
        return True

    # ПРОДАТЬ смайлик напрямую (продать 🪙 50000000)
    if text_lower.startswith("продать "):
        parts = text.strip().split()
        if len(parts) < 3:
            await update.effective_chat.send_message("❌ Формат: продать 🪙 50000000")
            return True
        emoji = parts[1].strip()
        try:
            sell_price = int(parts[2].replace(",", "").replace(".", ""))
        except ValueError:
            await update.effective_chat.send_message("❌ Баасы сан болушу керек!")
            return True
        if emoji not in SHOP_EMOJIS:
            await update.effective_chat.send_message("❌ Бул смайлик табылган жок!")
            return True
        conn = get_shop_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM user_emojis WHERE user_id=? AND emoji=?", (user_id, emoji))
        row = cursor.fetchone()
        if not row:
            conn.close()
            await update.effective_chat.send_message(f"❌ Бул смайлик сенде жок: {emoji}")
            return True
        cursor.execute("DELETE FROM user_emojis WHERE user_id=? AND emoji=?", (user_id, emoji))
        conn.commit()
        conn.close()
        await UserManager.update_balance(user_id, sell_price)
        display = user[15] or user[1] or user[2] or "Пользователь"
        await update.effective_chat.send_message(
            f"💵 *Смайлик сатылды!*\n\n"
            f"👤 {display}\n"
            f"🎁 Смайлик: {emoji}\n"
            f"💰 Алынды: *+{sell_price:,}* 🪙",
            parse_mode=ParseMode.MARKDOWN
        )
        return True

    # АУКЦИОН смайлик (аукцион 🪙 100000000)
    if text_lower.startswith("аукцион "):
        parts = text.strip().split()
        if len(parts) < 3:
            await update.effective_chat.send_message("❌ Формат: аукцион 🪙 100000000")
            return True
        emoji = parts[1].strip()
        try:
            start_price = int(parts[2].replace(",", "").replace(".", ""))
        except ValueError:
            await update.effective_chat.send_message("❌ Баасы сан болушу керек!")
            return True
        if emoji not in SHOP_EMOJIS:
            await update.effective_chat.send_message("❌ Бул смайлик табылган жок!")
            return True
        conn = get_shop_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM user_emojis WHERE user_id=? AND emoji=?", (user_id, emoji))
        if not cursor.fetchone():
            conn.close()
            await update.effective_chat.send_message(f"❌ Бул смайлик сенде жок: {emoji}")
            return True
        cursor.execute("SELECT id FROM emoji_auctions WHERE seller_id=? AND emoji=? AND status='active'", (user_id, emoji))
        if cursor.fetchone():
            conn.close()
            await update.effective_chat.send_message("⚠️ Бул смайлик аукционго коюлган!")
            return True
        cursor.execute(
            "INSERT INTO emoji_auctions (seller_id, emoji, start_price, current_price) VALUES (?,?,?,?)",
            (user_id, emoji, start_price, start_price)
        )
        auction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        display = user[15] or user[1] or user[2] or "Пользователь"
        keyboard = [[InlineKeyboardButton(f"🔨 Ставка +{start_price//10:,} 🪙", callback_data=f"auction_bid_{auction_id}")]]
        await update.effective_chat.send_message(
            f"🔨 *АУКЦИОН БАШТАЛДЫ!*\n\n"
            f"👤 Сатуучу: {display}\n"
            f"🎁 Смайлик: {emoji}\n"
            f"💰 Баштапкы баасы: *{start_price:,}* 🪙\n\n"
            f"👆 Ставка коюу үчүн баскычты басыңыз!",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return True

    return False

async def handle_auction_callback(update, context):
    """Аукционго ставка коюу"""
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    if data.startswith("auction_bid_"):
        auction_id = int(data.replace("auction_bid_", ""))
        conn = get_shop_db()
        cursor = conn.cursor()
        cursor.execute("SELECT seller_id, emoji, current_price, buyer_id FROM emoji_auctions WHERE id=? AND status='active'", (auction_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            await query.answer("❌ Аукцион бүттү!", show_alert=True)
            return
        seller_id, emoji, current_price, prev_buyer = row
        if user_id == seller_id:
            conn.close()
            await query.answer("❌ Өз аукционуңа ставка коё албайсың!", show_alert=True)
            return
        user = UserManager.get_user(user_id)
        wallet = user[3] if user else 0
        bid_amount = current_price + max(current_price // 10, 1000000)
        if wallet < bid_amount:
            conn.close()
            await query.answer(f"❌ Жетишпейт! Керек: {bid_amount:,} 🪙", show_alert=True)
            return
        # Мурунку ставка койгонго кайтар
        if prev_buyer:
            await UserManager.update_balance(prev_buyer, current_price)
        # Жаңы ставка
        await UserManager.update_balance(user_id, -bid_amount)
        cursor.execute(
            "UPDATE emoji_auctions SET current_price=?, buyer_id=? WHERE id=?",
            (bid_amount, user_id, auction_id)
        )
        conn.commit()
        conn.close()
        display = (user[15] or user[1] or user[2] or "Пользователь") if user else "Пользователь"
        keyboard = [[InlineKeyboardButton(f"🔨 Ставка +{bid_amount//10:,} 🪙", callback_data=f"auction_bid_{auction_id}"),
                     InlineKeyboardButton("✅ Завершить", callback_data=f"auction_end_{auction_id}")]]
        await query.edit_message_text(
            f"🔨 *АУКЦИОН #{auction_id}*\n\n"
            f"🎁 Смайлик: {emoji}\n"
            f"💰 Учурдагы баасы: *{bid_amount:,}* 🪙\n"
            f"👤 Лидер: {display}\n\n"
            f"👆 Жогорку ставка кой же аяктат!",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        await query.answer(f"✅ Ставка: {bid_amount:,} 🪙")

    elif data.startswith("auction_end_"):
        auction_id = int(data.replace("auction_end_", ""))
        conn = get_shop_db()
        cursor = conn.cursor()
        cursor.execute("SELECT seller_id, emoji, current_price, buyer_id FROM emoji_auctions WHERE id=? AND status='active'", (auction_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            await query.answer("❌ Аукцион жок!")
            return
        seller_id, emoji, final_price, buyer_id = row
        if user_id != seller_id:
            conn.close()
            await query.answer("❌ Аукционду жалаң гана сатуучу аяктата алат!", show_alert=True)
            return
        cursor.execute("UPDATE emoji_auctions SET status='finished' WHERE id=?", (auction_id,))
        if buyer_id:
            cursor.execute("DELETE FROM user_emojis WHERE user_id=? AND emoji=?", (seller_id, emoji))
            cursor.execute("INSERT INTO user_emojis (user_id, emoji, bought_price) VALUES (?,?,?)", (buyer_id, emoji, final_price))
            await UserManager.update_balance(seller_id, final_price)
        conn.commit()
        conn.close()
        buyer_user = UserManager.get_user(buyer_id) if buyer_id else None
        buyer_name = (buyer_user[15] or buyer_user[1] or buyer_user[2]) if buyer_user else "Ким да болбосун"
        seller_user = UserManager.get_user(seller_id)
        seller_name = (seller_user[15] or seller_user[1] or seller_user[2]) if seller_user else "Сатуучу"
        if buyer_id:
            result_text = (
                f"🏆 *АУКЦИОН АЯКТАДЫ!*\n\n"
                f"🎁 Смайлик: {emoji}\n"
                f"💰 Финалдык баасы: *{final_price:,}* 🪙\n"
                f"🛒 Сатып алган: {buyer_name}\n"
                f"💵 Сатуучу: {seller_name}"
            )
        else:
            result_text = f"🔨 Аукцион аяктады, бирок ставка болгон жок. {emoji} смайлик сенде калды."
        await query.edit_message_text(result_text, parse_mode=ParseMode.MARKDOWN)
        await query.answer("✅ Аукцион аяктады!")


def main() -> None:
    try:
        async def post_init(application):
            """Бот өчүп калганда ставка коюп аткандардын монеталарын кайтар"""
            try:
                conn = sqlite3.connect(DATABASE_NAME)
                cursor = conn.cursor()
                # Рулетка айланбай бот өчкөндө калган бардык ставкаларды кайтар
                cursor.execute("SELECT user_id, SUM(amount) FROM roulette_bets GROUP BY user_id")
                pending = cursor.fetchall()
                if pending:
                    refunded = {}
                    for uid, total_amt in pending:
                        if total_amt and total_amt > 0:
                            cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (total_amt, uid))
                            refunded[uid] = total_amt
                    cursor.execute("DELETE FROM roulette_bets")
                    conn.commit()
                    logger.info(f"Бот рестарт кайтаруу: {len(refunded)} колдонуучуга ставкалар кайтарылды: {refunded}")
                conn.close()
            except Exception as e:
                logger.error(f"Post-init ката: {e}")

        # PythonAnywhere акысыз план үчүн прокси орнотуу
        try:
            from telegram.request import HTTPXRequest
            proxy_request = HTTPXRequest(proxy="http://proxy.server:3128")
            app = (
                Application.builder()
                .token(BOT_TOKEN)
                .post_init(post_init)
                .request(proxy_request)
                .get_updates_request(proxy_request)
                .build()
            )
        except Exception:
            app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

        job_queue = app.job_queue
        if job_queue:
            from datetime import time as dt_time

            job_queue.run_daily(check_expiry_job, time=dt_time(hour=0, minute=0, second=0))
            job_queue.run_repeating(lambda ctx: UserManager.reset_daily_limits(), interval=43200, first=10)
            job_queue.run_repeating(check_roulette_inactivity, interval=60, first=10)
            job_queue.run_daily(handle_give_daily_bonus, time=dt_time(hour=12, minute=0, second=0))
            job_queue.run_daily(send_weekend_bonus_ad, days=(6,), time=dt_time(hour=12, minute=0, second=0))
            job_queue.run_daily(update_shop_prices_daily, time=dt_time(hour=0, minute=1, second=0))
        else:
            logger.warning("JobQueue отсутствует, автоматические задачи не будут работать")

        app.add_handler(CommandHandler("rodnoy", rodnoy_start))
        app.add_handler(CommandHandler("start", rodnoy_start))
        app.add_handler(CommandHandler("bonus", rodnoy_start))
        app.add_handler(CommandHandler("menu", rodnoy_start))
        app.add_handler(CommandHandler("RDNO_MX", rodnoy_start))

        app.add_handler(CommandHandler("tournament_register", handle_tournament_register))
        app.add_handler(CommandHandler("tournament_start", handle_tournament_start))
        app.add_handler(CommandHandler("tournament_status", handle_tournament_status))

        app.add_handler(CommandHandler("giverole", handle_give_role_command))
        app.add_handler(CommandHandler("removerole", handle_remove_role_command))
        app.add_handler(CommandHandler("addcoins", handle_addcoins_command))
        app.add_handler(CommandHandler("removecoins", handle_removecoins_command))
        app.add_handler(CommandHandler("setlimit", handle_setlimit_command))
        app.add_handler(CommandHandler("limits", handle_limits_command))
        app.add_handler(CommandHandler("resetbalances", handle_resetbalances_command))
        app.add_handler(CommandHandler("reducebalances", handle_reducebalances_command))
        app.add_handler(CommandHandler("activatepremium", handle_activate_premium))

        app.add_handler(CommandHandler("mute", handle_mute_time_command))
        app.add_handler(CommandHandler("unmute", handle_text_unmute))
        app.add_handler(CommandHandler("ban", handle_text_ban))
        app.add_handler(CommandHandler("unban", handle_text_unban))

        app.add_handler(CommandHandler("id", handle_id_command))
        app.add_handler(CommandHandler("refs", handle_refs_command))
        app.add_handler(CommandHandler("setname", handle_setname_command))
        app.add_handler(MessageHandler(filters.Text(["/Магазин", "/магазин", "Магазин", "магазин"]), handle_shop_command))
        app.add_handler(CommandHandler("shop", handle_shop_command))
        app.add_handler(CallbackQueryHandler(handle_auction_callback, pattern="^auction_"))
        app.add_handler(CommandHandler("ruleka", Games.ruleka))
        app.add_handler(CommandHandler("roulette", Games.ruleka))
        app.add_handler(CommandHandler("banditka", Games.banditka))
        app.add_handler(CommandHandler("bandit", Games.banditka))
        app.add_handler(CommandHandler("giveaway", handle_giveaway_command))
        app.add_handler(CommandHandler("stop", handle_stop_giveaway))
        app.add_handler(CallbackQueryHandler(handle_giveaway_callback, pattern="^gw_"))
        app.add_handler(CommandHandler("crash", Games.crash_start))
        app.add_handler(CommandHandler("blackjack", Games.start_blackjack))
        app.add_handler(CommandHandler("bj", Games.start_blackjack))

        app.add_handler(CommandHandler("ad", handle_ad_command))
        app.add_handler(CommandHandler("chatlist", handle_chatlist_command))


        app.add_handler(PreCheckoutQueryHandler(precheckout_callback))
        app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))

        app.add_handler(CallbackQueryHandler(handle_rodnoy_callbacks, pattern="^rodnoy_"))
        app.add_handler(CallbackQueryHandler(handle_rodnoy_callbacks, pattern="^stars_"))
        app.add_handler(CallbackQueryHandler(handle_rodnoy_callbacks, pattern="^check_sub_"))
        app.add_handler(CallbackQueryHandler(handle_rodnoy_callbacks, pattern="^show_channel_bonus$"))

        app.add_handler(CallbackQueryHandler(handle_roulette_callback, pattern="^(spin_roulette|bet_|repeat_bet|double_bet)"))
        app.add_handler(CallbackQueryHandler(handle_blackjack_callback, pattern="^(bj_bet_|bj_hit_|bj_stand_)"))
        app.add_handler(CallbackQueryHandler(handle_slot_callback, pattern="^slot_bet_"))
        app.add_handler(CallbackQueryHandler(handle_crash_callback, pattern="^crash_"))

        app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp_data))

        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_messages))

        print("=" * 60)
        print("🤖 **𝐑𝐃𝐍𝐎 𝐌𝐗 Бот запущен!**")
        print("=" * 60)
        print("🎮 Рулетка полностью работает!")
        print("   • Ва-банк 1-10 теперь выводится как одна ставка")
        print("   • 'ставки' показывает текущие активные ставки")
        print("   • 'повторить' повторяет последние ставки")
        print("   • 'удвоить' удваивает последние ставки")
        print("   • 'Б' показывает точный баланс")
        print("🎰 Минимальная ставка рулетки: 1 монета!")
        print("🎴 Минимальная ставка бандита: 1 монета!")
        print("🃏 BlackJack добавлен!")
        print("🎰 20 разных слотов добавлено!")
        print("   • футбол, баскетбол, боулинг и др.")
        print("📊 !лог - 21 результат (последний результат внизу)")
        print("📊 лог - 10 результатов (последний результат внизу)")
        print("🎁 Новая бонус система:")
        print("   • Бесплатный бонус: 20.000 монет за подписку на канал (раз в 12 часов)")
        print("   • Premium 1: 40.000 монет/день (200 руб)")
        print("   • Premium 2: 60.000 монет/день (300 руб)")
        print("🏆 Турнирная система добавлена:")
        print("   • Участие: только Premium")
        print("   • Призовой фонд: 650.000.000 монет")
        print("   • 10 призовых мест")
        print("🎭 Роли Вор в законе и Полицейский работают!")
        print("⚡ Админ команды работают!")
        print("🕒 20 минут бездействия - рулетка отключается")
        print("💰 **Telegram Stars интегрированы!**")
        print("   • Автоматическая покупка монет")
        print("   • Мгновенное зачисление")
        print("   • Работает 24/7")
        print("🌐 **ВЕБ ПРИЛОЖЕНИЕ ДОБАВЛЕНО!**")
        print("   • 💥 Крэш - самолет летит, забери выигрыш вовремя!")
        print("   • 🃏 Дурак - карточная игра с друзьями")
        print("   • 🎁 Бонусы - 3 ряда бонусов (бесплатно и платно)")
        print("   • 🔗 Ссылка: https://islomalievanvarbek6-hub.github.io/squidgames-bot")
        print("📢 **Реклама команда добавлена!**")
        print("   • /ad <текст> - рассылка всем пользователям и группам")
        print("   • Только для администратора")
        print("🎁 Выходные бонусы: каждую пятницу и субботу в 12:00")
        print("🔗 Кнопка Ссылки добавлена!")
        print("🎭 Кнопка Стикеры добавлена!")
        print("=" * 60)
        print("🚀 Бот готов к работе!")
        print("=" * 60)

        app.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )

    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    import time as _time
    retry = 0
    while True:
        try:
            retry += 1
            if retry > 1:
                wait = min(60, retry * 10)
                print(f"⏳ {wait} секунддан кийин кайра аракет ({retry}-жолу)...")
                _time.sleep(wait)
            print(f"🚀 Бот иштеп жатат... (аракет {retry})")
            main()
        except KeyboardInterrupt:
            print("🛑 Бот токтотулду.")
            break
        except Exception as e:
            err = str(e)
            if any(x in err for x in ["503", "502", "504", "NetworkError", "TimedOut", "ConnectionError", "Service Unavailable"]):
                print(f"⚠️ Telegram жеткиликсиз: {e}")
                print("🔄 Автоматтык кайра аракет...")
            else:
                print(f"❌ Ката: {e}")
                import traceback
                traceback.print_exc()
                print("🔄 30 секунддан кийин кайра аракет...")
            continue