import logging
import json
import time
import asyncio
import aiohttp
import os
import re
import sys
import random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote_plus

# উইন্ডোজ কনসোল ফিক্স
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

# ==============================================================================
# ⚙️ CONFIGURATION
# ==============================================================================
BOT_TOKEN = "8529763332:AAGfCPuYDxNb6GErkuejg37t4eglsIiEz7U"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

OTP_CHANNEL_ID = -1003538501693 
DEFAULT_ADMIN_ID = 7061346269  # MAIN OWNER
SUPPORT_USERNAME = "mdfarukofficial22" 
OTP_GROUP_LINK = "https://t.me/+hbM8wsKkgcthMGI1"

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("BOT_ENGINE")

# ==============================================================================
# 🎨 CUSTOM EMOJI CONFIG (Bot API 9.4)
# এখানে প্রতিটা জায়গার জন্য আলাদা emoji ID দিন।
# Emoji ID পেতে: Telegram এ @Stickers bot এ যান, অথবা
# যেকোনো custom emoji তে right-click করে ID নিন।
# ==============================================================================
EMOJI = {
    # 🔘 KEYBOARD BUTTONS
    "btn_get_number":   "6307313006371936255",  # 📲 Get Number বাটন
    "btn_balance":      "6001434068435079689",  # 💰 Balance বাটন
    "btn_withdraw":     "5368324170671202286",  # 💸 Withdraw বাটন
    "btn_traffic":      "5368324170671202286",  # 🚦 Live Traffic বাটন
    "btn_countries":    "5368324170671202286",  # 🌍 Countries বাটন
    "btn_support":      "5293991227513914037",  # 📞 Support বাটন
    "btn_admin":        "5368324170671202286",  # ⚙️ Admin Panel বাটন

    # 💬 MESSAGE EMOJIS
    "welcome":          "5368324170671202286",  # 👋 Welcome message
    "get_number":       "5293991227513914037",  # 📲 Get number line
    "earn":             "5368324170671202286",  # 💰 Earn line
    "withdraw_icon":    "5368324170671202286",  # 💸 Withdraw line
    "otp_country":      "5368324170671202286",  # 🌎 OTP country line
    "otp_number":       "5293991227513914037",  # 🔢 OTP number line
    "otp_code":         "5368324170671202286",  # 🔑 OTP code line
    "otp_reward":       "5293991227513914037",  # 💸 OTP reward line
    "otp_balance":      "5368324170671202286",  # 💵 OTP balance line
    "otp_msg":          "5293991227513914037",  # 📩 OTP message line
    "balance_icon":     "5368324170671202286",  # 💰 Balance display
    "balance_usd":      "5293991227513914037",  # 💵 USD amount
    "number_flag":      "5368324170671202286",  # 🌍 Number assigned flag
    "number_copy":      "5293991227513914037",  # 📋 Copy instruction
    "number_timer":     "5368324170671202286",  # ⏱ Valid timer
    "wd_icon":          "5368324170671202286",  # 💸 Withdraw title
    "wd_balance":       "5293991227513914037",  # 💰 Withdraw balance
    "cooldown_lock":    "5368324170671202286",  # 🔒 Cooldown lock
    "cooldown_done":    "5368324170671202286",  # ✅ Cooldown done
    "traffic_icon":     "5368324170671202286",  # 🚦 Traffic monitor
    "traffic_top1":     "5368324170671202286",  # 🥇 Rank 1
    "traffic_top2":     "5368324170671202286",  # 🥈 Rank 2
    "traffic_top3":     "5368324170671202286",  # 🥉 Rank 3
    "traffic_success":  "5293991227513914037",  # 🔥 Traffic success
    "traffic_rate":     "5368324170671202286",  # 💰 Traffic rate
    "country_select":   "5368324170671202286",  # 🌍 Select Country
    
    # 🔘 INLINE KEYBOARDS
    "in_stats":         "5368324170671202286",
    "in_admins":        "5368324170671202286",
    "in_back":          "5368324170671202286",
    "in_settings":      "5368324170671202286",
    "in_users":         "5368324170671202286",
    "in_add":           "5368324170671202286",
    "in_rem":           "5368324170671202286",
    "in_edit":          "5368324170671202286",
    "in_refresh":       "5368324170671202286",
    "in_money":         "5368324170671202286",
    "in_toggle":        "5368324170671202286",
    "in_warn":          "5368324170671202286",
    "in_chat":          "5368324170671202286",
    "in_country":       "5368324170671202286",
    "in_copy":          "5368324170671202286",
    "in_broadcast":     "5368324170671202286",
    "in_del":           "5368324170671202286",


    # 🔤 AUTO-GENERATED MESSAGE EMOJIS
    "icon_pin": "5368324170671202286",  # 📌
    "icon_gift": "5368324170671202286",  # 🎁
    "icon_lock2": "5368324170671202286",  # 🔐
    "icon_mail": "5368324170671202286",  # 📩
    "icon_money_wings": "5368324170671202286",  # 💸
    "icon_red_circle": "5368324170671202286",  # 🔴
    "icon_phone_arrow": "5368324170671202286",  # 📲
    "icon_phone": "5368324170671202286",  # 📞
    "icon_numbers": "5368324170671202286",  # 🔢
    "icon_package": "5368324170671202286",  # 📦
    "icon_chat": "5368324170671202286",  # 💬
    "icon_namebadge": "5368324170671202286",  # 📛
    "icon_reply": "5368324170671202286",  # ↩
    "icon_repeat": "5368324170671202286",  # 🔁
    "icon_warning": "5368324170671202286",  # ⚠️
    "icon_card": "5368324170671202286",  # 💳
    "icon_mobile": "5368324170671202286",  # 📱
    "icon_medal1": "5368324170671202286",  # 🥇
    "icon_tick": "5368324170671202286",  # ✅
    "icon_white_circle": "5368324170671202286",  # ⚪
    "icon_stop": "5368324170671202286",  # 🛑
    "icon_trophy": "5368324170671202286",  # 🏆
    "icon_tools": "5368324170671202286",  # 🛠
    "icon_dollar": "5368324170671202286",  # 💵
    "icon_wave": "5368324170671202286",  # 👋
    "icon_key": "5368324170671202286",  # 🔑
    "icon_globe_eu": "5368324170671202286",  # 🌍
    "icon_stopwatch": "5368324170671202286",  # ⏱
    "icon_zap": "5368324170671202286",  # ⚡
    "icon_blue_circle": "5368324170671202286",  # 🔵
    "icon_cross": "5368324170671202286",  # ❌
    "icon_hourglass": "5368324170671202286",  # ⏳
    "icon_megaphone": "5368324170671202286",  # 📢
    "icon_radio": "5368324170671202286",  # 🔘
    "icon_star": "5368324170671202286",  # ⭐
    "icon_siren": "5368324170671202286",  # 🚨
    "icon_keyboard": "5368324170671202286",  # ⌨
    "icon_moneybag": "6001434068435079689",  # 💰
    "icon_clipboard": "5368324170671202286",  # 📋
    "icon_lock": "5368324170671202286",  # 🔒
    "icon_art": "5368324170671202286",  # 🎨
    "icon_chart_bar": "5368324170671202286",  # 📊
    "icon_medal3": "5368324170671202286",  # 🥉
    "icon_bank": "5368324170671202286",  # 🏦
    "icon_fire": "5368324170671202286",  # 🔥
    "icon_gear": "5368324170671202286",  # ⚙️
    "icon_chart_down": "5368324170671202286",  # 📉
    "icon_green_circle": "5368324170671202286",  # 🟢
    "icon_folder": "5368324170671202286",  # 📁
    "icon_globe_am": "5368324170671202286",  # 🌎
    "icon_id": "5368324170671202286",  # 🆔
    "icon_no_entry": "5368324170671202286",  # ⛔️
    "icon_link": "5368324170671202286",  # 🔗
    "icon_clock": "5368324170671202286",  # 🕒
    "icon_inbox": "5368324170671202286",  # 📥
    "icon_clock1": "5368324170671202286",  # 🕐
    "icon_medal2": "5368324170671202286",  # 🥈
    "icon_rocket": "5368324170671202286",  # 🚀
    "icon_crown": "5368324170671202286",  # 👑
    "icon_trash": "5368324170671202286",  # 🗑
    "icon_pencil": "5368324170671202286",  # ✏️
    "icon_runner": "5368324170671202286",  # 🏃
    "icon_joystick": "5368324170671202286",  # 🕹
    "icon_traffic_light": "5368324170671202286",  # 🚦
    "icon_open_folder": "5368324170671202286",  # 📂
    "icon_sync": "5368324170671202286",  # 🔄
    "icon_user": "5368324170671202286",  # 👤
    "icon_plug": "5368324170671202286",  # 🔌
    "icon_memo": "5368324170671202286",  # 📝
}



def replace_emojis_in_text(text):
    if not text: return text
    emoji_to_key = {
        "📌": "icon_pin",
        "🎁": "icon_gift",
        "🔐": "icon_lock2",
        "📩": "icon_mail",
        "💸": "icon_money_wings",
        "🔴": "icon_red_circle",
        "📲": "icon_phone_arrow",
        "📞": "icon_phone",
        "🔢": "icon_numbers",
        "📦": "icon_package",
        "💬": "icon_chat",
        "📛": "icon_namebadge",
        "↩": "icon_reply",
        "🔁": "icon_repeat",
        "⚠️": "icon_warning",
        "⚠": "icon_warning",
        "💳": "icon_card",
        "📱": "icon_mobile",
        "🥇": "icon_medal1",
        "✅": "icon_tick",
        "⚪": "icon_white_circle",
        "🛑": "icon_stop",
        "🏆": "icon_trophy",
        "🛠": "icon_tools",
        "💵": "icon_dollar",
        "👋": "icon_wave",
        "🔑": "icon_key",
        "🌍": "icon_globe_eu",
        "⏱": "icon_stopwatch",
        "⚡": "icon_zap",
        "🔵": "icon_blue_circle",
        "❌": "icon_cross",
        "⏳": "icon_hourglass",
        "📢": "icon_megaphone",
        "🔘": "icon_radio",
        "⭐": "icon_star",
        "🚨": "icon_siren",
        "⌨": "icon_keyboard",
        "💰": "icon_moneybag",
        "📋": "icon_clipboard",
        "🔒": "icon_lock",
        "🎨": "icon_art",
        "📊": "icon_chart_bar",
        "🥉": "icon_medal3",
        "🏦": "icon_bank",
        "🔥": "icon_fire",
        "⚙️": "icon_gear",
        "⚙": "icon_gear",
        "📉": "icon_chart_down",
        "🟢": "icon_green_circle",
        "📁": "icon_folder",
        "🌎": "icon_globe_am",
        "🆔": "icon_id",
        "⛔️": "icon_no_entry",
        "⛔": "icon_no_entry",
        "🔗": "icon_link",
        "🕒": "icon_clock",
        "📥": "icon_inbox",
        "🕐": "icon_clock1",
        "🥈": "icon_medal2",
        "🚀": "icon_rocket",
        "👑": "icon_crown",
        "🗑": "icon_trash",
        "✏️": "icon_pencil",
        "✏": "icon_pencil",
        "🏃": "icon_runner",
        "🕹": "icon_joystick",
        "🚦": "icon_traffic_light",
        "📂": "icon_open_folder",
        "🔄": "icon_sync",
        "👤": "icon_user",
        "🔌": "icon_plug",
        "📝": "icon_memo",
    }
    parts = re.split(r'(<tg-emoji.*?</tg-emoji>)', text)
    for i in range(0, len(parts), 2):
        part = parts[i]
        for emj, key in emoji_to_key.items():
            if emj in part:
                eid = EMOJI.get(key, "5368324170671202286")
                part = part.replace(emj, f"<tg-emoji emoji-id='{eid}'>{emj}</tg-emoji>")
        parts[i] = part
    return "".join(parts)


def E(key, fallback="⭐"):
    """
    Helper: <tg-emoji emoji-id='ID'>fallback</tg-emoji> বানায়।
    ব্যবহার: E('welcome', '👋')  →  <tg-emoji ...>👋</tg-emoji>
    """
    eid = EMOJI.get(key, "5368324170671202286")
    return f"<tg-emoji emoji-id='{eid}'>{fallback}</tg-emoji>"

class AsyncTelegramBot:
    def __init__(self):
        self.last_update_id = 0
        self.running = False
        self.session = None
        
        # 📂 FILE SYSTEM
        self.files = {
            'users': 'users.json',
            'countries': 'countries.json',
            'withdrawals': 'pending_withdrawals.json',
            'config': 'config.json'
        }
        
        self.ensure_files_exist()

        # 📥 LOAD DATA INTO MEMORY
        self.users_data = self.load_json(self.files['users'])
        self.countries_data = self.load_json(self.files['countries'])
        self.pending_withdrawals = self.load_json(self.files['withdrawals'])
        self.system_config = self.load_system_config()
        
        # 🚀 PERFORMANCE BOOSTER: ACTIVE NUMBER MAP
        self.active_number_map = {}
        self.rebuild_active_map()

        logger.info(f"✅ Loaded {len(self.users_data)} users.")
        logger.info(f"🚀 Optimized Map: {len(self.active_number_map)} active numbers tracked.")
        
        # States & Executors
        self.admin_states = {}
        self.withdraw_sessions = {}
        self.processed_msgs = set()
        self.io_executor = ThreadPoolExecutor(max_workers=1)
        self.data_changed = False
        self.cooldown_tasks = {}  # 🕐 Realtime countdown tasks per user

        # 🎨 COLORFUL KEYBOARDS
        # ✅ Bot API 9.4: icon_custom_emoji_id + style এখন reply keyboard এ valid!
        self.main_keyboard = {
            "keyboard": [
                [
                    {"text": "Get Number", "style": "success", "icon_custom_emoji_id": EMOJI["btn_get_number"]},
                    {"text": "Balance",    "style": "primary", "icon_custom_emoji_id": EMOJI["btn_balance"]}
                ],
                [
                    {"text": "Withdraw",     "style": "success", "icon_custom_emoji_id": EMOJI["btn_withdraw"]},
                    {"text": "Live Traffic", "style": "primary", "icon_custom_emoji_id": EMOJI["btn_traffic"]}
                ],
                [
                    {"text": "Countries", "style": "primary", "icon_custom_emoji_id": EMOJI["btn_countries"]},
                    {"text": "Support",   "style": "primary", "icon_custom_emoji_id": EMOJI["btn_support"]}
                ]
            ],
            "resize_keyboard": True, "is_persistent": True
        }

        self.admin_keyboard = {
            "keyboard": [
                [
                    {"text": "Get Number", "style": "success", "icon_custom_emoji_id": EMOJI["btn_get_number"]},
                    {"text": "Balance",    "style": "primary", "icon_custom_emoji_id": EMOJI["btn_balance"]}
                ],
                [
                    {"text": "Withdraw",     "style": "success", "icon_custom_emoji_id": EMOJI["btn_withdraw"]},
                    {"text": "Live Traffic", "style": "primary", "icon_custom_emoji_id": EMOJI["btn_traffic"]}
                ],
                [
                    {"text": "Countries",  "style": "primary", "icon_custom_emoji_id": EMOJI["btn_countries"]},
                    {"text": "Admin Panel", "style": "danger",  "icon_custom_emoji_id": EMOJI["btn_admin"]}
                ]
            ],
            "resize_keyboard": True, "is_persistent": True
        }

    # ==========================================================================
    # 📂 SMART FILE OPERATIONS
    # ==========================================================================
    def ensure_files_exist(self):
        for key, filename in self.files.items():
            if not os.path.exists(filename):
                with open(filename, 'w', encoding='utf-8') as f:
                    if key == 'config':
                        json.dump({
                            "maintenance_mode": False, 
                            "min_withdraw": 0.50, 
                            "per_refer": 0.05,
                            "admins": [DEFAULT_ADMIN_ID],
                            "force_join": {"enabled": False, "channels": []},
                            "number_cooldown": 60
                        }, f, indent=2)
                    else:
                        json.dump({}, f, indent=2)

    def load_json(self, filename):
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: return {}
        return {}

    def load_system_config(self):
        if os.path.exists(self.files['config']):
            with open(self.files['config'], 'r', encoding='utf-8') as f: 
                conf = json.load(f)
                
                if "force_join" not in conf:
                    conf["force_join"] = {"enabled": False, "channels": []}
                elif "channels" not in conf["force_join"]:
                    old_chan = conf["force_join"].get("channel_id")
                    old_link = conf["force_join"].get("link")
                    channels = []
                    if old_chan and old_link:
                        channels.append({"id": old_chan, "link": old_link, "name": "Channel 1"})
                    conf["force_join"]["channels"] = channels
                
                if "admins" not in conf:
                    conf["admins"] = [DEFAULT_ADMIN_ID]
                if DEFAULT_ADMIN_ID not in conf["admins"]:
                    conf["admins"].append(DEFAULT_ADMIN_ID)
                return conf
        return {}

    def mark_dirty(self):
        self.data_changed = True

    async def background_save_task(self):
        loop = asyncio.get_running_loop()
        while self.running:
            await asyncio.sleep(30)
            if self.data_changed:
                await loop.run_in_executor(self.io_executor, self.save_all_sync)
                self.data_changed = False

    def save_all_sync(self):
        try:
            temp_users = self.files['users'] + '.tmp'
            with open(temp_users, 'w', encoding='utf-8') as f: 
                json.dump(self.users_data, f, indent=2)
            os.replace(temp_users, self.files['users'])

            with open(self.files['countries'], 'w', encoding='utf-8') as f: json.dump(self.countries_data, f, indent=2)
            with open(self.files['withdrawals'], 'w', encoding='utf-8') as f: json.dump(self.pending_withdrawals, f, indent=4)
            with open(self.files['config'], 'w', encoding='utf-8') as f: json.dump(self.system_config, f, indent=2)
        except Exception as e:
            logger.error(f"Save Error: {e}")

    # ==========================================================================
    # 🚀 LOGIC: MASKING & MAP
    # ==========================================================================
    def mask_phone_number(self, full_number):
        if not full_number or len(full_number) < 9: return full_number
        prefix = full_number[:-8]
        suffix = full_number[-4:]
        return f"{prefix}⁕⁕⁕⁕{suffix}"

    def rebuild_active_map(self):
        self.active_number_map.clear()
        for uid, data in self.users_data.items():
            assigned_numbers = data.get('last_assigned_numbers') or []
            if not assigned_numbers and data.get('last_assigned_number'):
                assigned_numbers = [data['last_assigned_number']]

            for full_number in assigned_numbers:
                masked = self.mask_phone_number(full_number)
                self.active_number_map[masked] = {
                    'uid': uid,

                    'full_number': full_number,
                    'country': data.get('last_country')
                }

    # ==========================================================================
    # 🔌 NETWORK API
    # ==========================================================================
    async def start_session(self):
        self.session = aiohttp.ClientSession()
        # Webhook থাকলে long polling কাজ করে না, তাই delete করো
        await self.api_call("deleteWebhook", {"drop_pending_updates": False})
        logger.info("✅ Webhook cleared. Long polling শুরু হবে।")

    def clean_markup(self, markup):
        """
        ✅ Bot API 9.4: icon_custom_emoji_id ও style এখন valid field।
        শুধু সম্পূর্ণ unknown/unofficial key গুলো filter করে।
        """
        import copy
        # Reply keyboard valid fields (Bot API 9.4 সহ)
        VALID_REPLY_KEYS = {
            'text', 'request_users', 'request_chat', 'request_contact',
            'request_location', 'request_poll', 'web_app',
            'icon_custom_emoji_id', 'style'  # ✅ Bot API 9.4 এ যোগ হয়েছে
        }
        # Inline keyboard valid fields
        VALID_INLINE_KEYS = {
            'text', 'url', 'callback_data', 'web_app', 'login_url',
            'switch_inline_query', 'switch_inline_query_current_chat',
            'switch_inline_query_chosen_chat', 'callback_game', 'pay',
            'icon_custom_emoji_id', 'style', 'copy_text'  # ✅ Bot API 9.4 এ যোগ হয়েছে
        }
        cleaned = copy.deepcopy(markup)
        if 'keyboard' in cleaned:
            for row in cleaned['keyboard']:
                for btn in row:
                    for k in list(btn.keys()):
                        if k not in VALID_REPLY_KEYS:
                            del btn[k]
        if 'inline_keyboard' in cleaned:
            for row in cleaned['inline_keyboard']:
                for btn in row:
                    for k in list(btn.keys()):
                        if k not in VALID_INLINE_KEYS:
                            del btn[k]
        return cleaned


    async def api_call(self, method, payload=None):
        try:
            url = f"{API_URL}/{method}"
            # ✅ FIX: aiohttp-তে timeout integer হিসেবে দেওয়া যায় না, ClientTimeout দিতে হয়
            timeout = aiohttp.ClientTimeout(total=35)
            async with self.session.post(url, json=payload, timeout=timeout) as response:
                result = await response.json()
                if not result.get('ok'):
                    desc = result.get('description', '')
                    # "message is not modified" — harmless, suppress করা হলো
                    if 'message is not modified' not in desc:
                        logger.warning(f"Telegram API Error [{method}]: {desc}")
                return result
        except Exception as e:
            logger.error(f"API Error [{method}]: {e}")
            return None

    async def send_message(self, chat_id, text, reply_markup=None, parse_mode=None):
        text = replace_emojis_in_text(text)
        payload = {'chat_id': chat_id, 'text': text}
        # ✅ FIX: "style" বাদ দিয়ে clean markup পাঠাও
        if reply_markup: payload['reply_markup'] = json.dumps(self.clean_markup(reply_markup))
        payload['parse_mode'] = 'HTML'
        return await self.api_call("sendMessage", payload)

    async def edit_message(self, chat_id, message_id, text, reply_markup=None, parse_mode=None):
        text = replace_emojis_in_text(text)
        payload = {'chat_id': chat_id, 'message_id': message_id, 'text': text}
        # ✅ FIX: "style" বাদ দিয়ে clean markup পাঠাও
        if reply_markup: payload['reply_markup'] = json.dumps(self.clean_markup(reply_markup))
        payload['parse_mode'] = 'HTML'
        return await self.api_call("editMessageText", payload)

    async def copy_message(self, chat_id, from_chat_id, message_id):
        payload = {'chat_id': chat_id, 'from_chat_id': from_chat_id, 'message_id': message_id}
        return await self.api_call("copyMessage", payload)

    async def answer_callback(self, callback_id, text=None, show_alert=False):
        payload = {'callback_query_id': callback_id, 'show_alert': show_alert}
        if text: payload['text'] = text
        await self.api_call("answerCallbackQuery", payload)

    async def get_chat_member(self, chat_id, user_id):
        payload = {'chat_id': chat_id, 'user_id': user_id}
        return await self.api_call("getChatMember", payload)

    # ==========================================================================
    # 🔥 OTP DETECTION & ADMIN CHECK
    # ==========================================================================
    def is_admin(self, chat_id): 
        return chat_id in self.system_config.get('admins', [])

    async def process_channel_post(self, post):
        msg_id = post.get('message_id')
        if msg_id in self.processed_msgs: return
        self.processed_msgs.add(msg_id)
        text = post.get('text', '')
        
        number_match = re.search(r'📞\s*([+\d\u2055]+)', text)
        otp_match = re.search(r'🔐 OTP:\s*\n?(\d+)', text)
        
        if not number_match or not otp_match:
            number_match = re.search(r'📞\s*(.*)', text)
            otp_match = re.search(r'OTP:?\s*(\d+)', text)

        if number_match and otp_match:
            masked_number = number_match.group(1).strip()
            otp_code = otp_match.group(1).strip()
            full_msg_match = re.search(r'Message:\s*(.*)', text, re.DOTALL)
            full_message = full_msg_match.group(1).strip() if full_msg_match else "OTP Message"
            active_info = self.active_number_map.get(masked_number)
            
            if active_info:
                user_id = active_info['uid']
                matched_full_number = active_info['full_number']
                # 🛑 20 MINUTE LIMIT CHECK (UPDATED FROM 10) 🛑
                user_data = self.users_data.get(user_id, {})
                assigned_time = user_data.get('assigned_time', 0)
                time_diff = time.time() - assigned_time
                
                # 1200 seconds = 20 minutes
                if time_diff > 1200:
                    logger.info(f"⏳ OTP Expired for {masked_number} (Time: {time_diff}s)")
                    return # Do not deliver OTP

                logger.info(f"⚡ OTP Matched: {masked_number} -> User {user_id}")
                await self.deliver_otp_to_user(user_id, otp_code, full_message, matched_full_number)

    async def deliver_otp_to_user(self, user_id_str, otp_code, full_message, matched_number=None):
        chat_id = int(user_id_str)
        user_data = self.users_data[user_id_str]
        phone_number = matched_number or user_data.get('last_assigned_number', 'Unknown')
        country_id = user_data.get('last_country', '000')
        country_info = self.countries_data.get(country_id, {})
        country_info['otp_count'] = country_info.get('otp_count', 0) + 1
        
        flag = country_info.get('flag', '🌍')
        name = country_info.get('name', 'Country')
        
        # 🔥 PENALTY CHECK LOGIC 🔥
        is_penalty_active = country_info.get('negative_balance', False)
        
        if is_penalty_active:
            # Negative Balance Logic
            deduction_amount = 0.015
            user_data['balance_usd'] = user_data.get('balance_usd', 0.0) - deduction_amount
            
            # Construct Penalty Message
            otp_msg = f"⚠️ <b>PENALTY ALERT</b>\n\n" \
                      f"❌ <b>{name}</b> এর লিমিট শেষ, নিষেধ করার পরও ওটিপি সেন্ড করায় আপনার ব্যালেন্স থেকে ১৫ টাকা (${deduction_amount}) কেটে নেয়া হলো।\n\n" \
                      f"🔢 Number: <code>{phone_number.replace('+','')}</code>\n" \
                      f"📉 New Balance: ${user_data['balance_usd']:.4f}"
            
        else:
            # Normal Reward Logic
            per_otp_earn = country_info.get('per_otp_earn', 0.0)
            user_data['balance_usd'] = user_data.get('balance_usd', 0.0) + per_otp_earn
            
            flag_html = f"<tg-emoji emoji-id='{country_info['flag_custom_emoji_id']}'>{flag}</tg-emoji>" if country_info.get('flag_custom_emoji_id') else flag
            otp_msg = (
                f"{E('otp_country', '🌎')} <b>Country:</b> {name} {flag_html}\n"
                f"{E('otp_number', '🔢')} <b>Number:</b> <code>{phone_number.replace('+','')}</code>\n"
                f"{E('otp_code', '🔑')} <b>OTP:</b> <code>{otp_code}</code>\n"
                f"{E('otp_reward', '💸')} <b>Reward:</b> ${per_otp_earn:.4f}\n"
                f"{E('otp_balance', '💵')} <b>Balance:</b> ${user_data['balance_usd']:.4f}\n\n"
                f"{E('otp_msg', '📩')} <b>Msg:</b> {full_message[:50]}..."
            )

        # Common History Update
        if 'recent_otps' not in user_data: user_data['recent_otps'] = []
        user_data['recent_otps'].insert(0, {
            'code': otp_code, 'number': phone_number, 
            'timestamp': datetime.now().isoformat(), 'msg': full_message
        })
        self.mark_dirty() 

        kb = self.admin_keyboard if self.is_admin(chat_id) else self.main_keyboard
        
        sent = False
        if user_data.get('last_mid'):
            try:
                # সব সময় HTML — tg-emoji সাপোর্টের জন্য
                parse_mode = "HTML"
                res = await self.edit_message(chat_id, user_data['last_mid'], otp_msg, kb, parse_mode)
                if res and res.get('ok'): sent = True
            except: pass
        
        if not sent:
            parse_mode = "HTML"  # সব সময় HTML (tg-emoji সাপোর্টের জন্য)
            await self.send_message(chat_id, otp_msg, kb, parse_mode)

    # ==========================================================================
    # 🕹️ MENU HANDLERS
    # ==========================================================================
    async def handle_admin_panel(self, chat_id, mid=None):
        if not self.is_admin(chat_id): return
        kb = {
            "inline_keyboard": [
                [{"text": "Add Country", "icon_custom_emoji_id": EMOJI["in_add"], "callback_data": "add_country_wiz", "style": "success"}],
                [{"text": "Manage Countries", "icon_custom_emoji_id": EMOJI["in_country"], "callback_data": "admin_countries", "style": "primary"}],
                [
                    {"text": "Stats", "icon_custom_emoji_id": EMOJI["in_stats"], "callback_data": "view_stats", "style": "primary"},
                    {"text": "Admins", "icon_custom_emoji_id": EMOJI["in_admins"], "callback_data": "manage_admins", "style": "danger"}
                ],
                [{"text": "Withdrawals", "icon_custom_emoji_id": EMOJI["in_money"], "callback_data": "manage_withdrawals", "style": "success"}],
                [{"text": "Broadcast", "icon_custom_emoji_id": EMOJI["in_broadcast"], "callback_data": "broadcast_wiz", "style": "primary"}],
                [{"text": "Settings", "icon_custom_emoji_id": EMOJI["in_settings"], "callback_data": "bot_settings", "style": "danger"}]
            ]
        }
        msg = "⚙️ <b>Admin Panel</b>\nSelect an option:"
        if mid: await self.edit_message(chat_id, mid, msg, kb, "Markdown")
        else: await self.send_message(chat_id, msg, kb, "Markdown")

    async def handle_view_stats(self, chat_id, mid):
        kb = {
            "inline_keyboard": [
                [{"text": "Today's OTPs", "icon_custom_emoji_id": EMOJI["in_stats"], "callback_data": "todays_stats", "style": "primary"}],
                [{"text": "Top 10 Users", "icon_custom_emoji_id": EMOJI["in_users"], "callback_data": "top_users", "style": "primary"}],
                [{"text": "Back", "icon_custom_emoji_id": EMOJI["in_back"], "callback_data": "back_to_admin", "style": "danger"}]
            ]
        }
        await self.edit_message(chat_id, mid, "📊 <b>Statistics Menu</b>", kb, "Markdown")

    async def handle_top_users(self, chat_id, mid):
        # Sort users by balance
        sorted_users = sorted(
            self.users_data.items(), 
            key=lambda item: item[1].get('balance_usd', 0.0), 
            reverse=True
        )[:10]

        msg = "🏆 <b>Top 10 Users by Balance</b>\n\n"
        for idx, (uid, data) in enumerate(sorted_users, 1):
            name = data.get('first_name', 'Unknown')
            bal = data.get('balance_usd', 0.0)
            msg += f"{idx}. {name} (<code>{uid}</code>) : ${bal:.4f}\n"

        kb = {"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": EMOJI["in_back"], "callback_data": "view_stats", "style": "danger"}]]}
        await self.edit_message(chat_id, mid, msg, kb, "Markdown")

    async def handle_manage_admins(self, chat_id, mid):
        admins = self.system_config.get('admins', [])
        msg = f"👤 <b>Admin Management</b>\n\nCurrent Admins: {len(admins)}\n"
        for i, aid in enumerate(admins, 1):
            if aid == DEFAULT_ADMIN_ID:
                msg += f"{i}. <code>{aid}</code> (Owner 👑)\n"
            else:
                msg += f"{i}. <code>{aid}</code>\n"
            
        kb = {
            "inline_keyboard": [
                [{"text": "Add Admin", "icon_custom_emoji_id": EMOJI["in_add"], "callback_data": "add_admin_wiz", "style": "success"}, {"text": "Remove Admin", "icon_custom_emoji_id": EMOJI["in_rem"], "callback_data": "rem_admin_wiz", "style": "danger"}],
                [{"text": "Back", "icon_custom_emoji_id": EMOJI["in_back"], "callback_data": "back_to_admin", "style": "danger"}]
            ]
        }
        await self.edit_message(chat_id, mid, msg, kb, "Markdown")

    async def handle_remove_admin_list(self, chat_id, mid):
        admins = self.system_config.get('admins', [])
        buttons = []
        for aid in admins:
            if aid == DEFAULT_ADMIN_ID: continue
            txt = f"❌ Remove {aid}"
            buttons.append([{"text": txt, "callback_data": f"del_adm_{aid}", "style": "danger"}])
        buttons.append([{"text": "Back", "icon_custom_emoji_id": EMOJI["in_back"], "callback_data": "manage_admins", "style": "primary"}])
        await self.edit_message(chat_id, mid, "🗑 Select Admin to Remove:", {"inline_keyboard": buttons}, "Markdown")

    async def handle_bot_settings(self, chat_id, mid):
        m_mode = "🟢 ON" if self.system_config.get('maintenance_mode') else "🔴 OFF"
        min_wd = self.system_config.get('min_withdraw', 0.0)
        ref_b = self.system_config.get('per_refer', 0.0)
        cooldown = self.system_config.get('number_cooldown', 60)

        fj = self.system_config.get('force_join', {})
        fj_status = "🟢 ON" if fj.get('enabled') else "🔴 OFF"
        fj_channels_count = len(fj.get('channels', []))

        mins, secs = divmod(cooldown, 60)
        cooldown_str = f"{mins}m {secs}s" if mins else f"{secs}s"

        msg = (
            f"⚙️ <b>System Settings</b>\n\n"
            f"Maintenance: {m_mode}\n"
            f"Min Withdraw: ${min_wd}\n"
            f"Refer Bonus: ${ref_b}\n"
            f"⏳ Number Cooldown: {cooldown_str} ({cooldown}s)\n\n"
            f"🔒 <b>Force Join:</b> {fj_status}\n"
            f"Active Channels: {fj_channels_count}/4"
        )
        kb = {
            "inline_keyboard": [
                [{"text": "Toggle Maintenance", "icon_custom_emoji_id": EMOJI["in_toggle"], "callback_data": "set_maint", "style": "danger"}],
                [{"text": "Edit Min Withdraw", "icon_custom_emoji_id": EMOJI["in_edit"], "callback_data": "set_minwd", "style": "primary"}],
                [{"text": "Edit Refer Bonus", "icon_custom_emoji_id": EMOJI["in_edit"], "callback_data": "set_refbonus", "style": "success"}],
                [{"text": f"⏳ Set Cooldown ({cooldown_str})", "callback_data": "set_cooldown", "style": "primary"}],
                [{"text": "Manage Force Join", "icon_custom_emoji_id": EMOJI["in_settings"], "callback_data": "manage_fj", "style": "primary"}],
                [{"text": "Toggle Force Join", "icon_custom_emoji_id": EMOJI["in_toggle"], "callback_data": "toggle_fj", "style": "danger"}],
                [{"text": "Back", "icon_custom_emoji_id": EMOJI["in_back"], "callback_data": "back_to_admin", "style": "danger"}]
            ]
        }
        await self.edit_message(chat_id, mid, msg, kb, "Markdown")

    async def handle_manage_force_join(self, chat_id, mid):
        fj = self.system_config.get('force_join', {})
        channels = fj.get('channels', [])
        
        msg = f"🔒 <b>Force Join Channels</b>\n\nActive Channels: {len(channels)}"
        buttons = []
        for idx, ch in enumerate(channels):
            buttons.append([{"text": f"🗑 {ch.get('name', 'Channel')}", "callback_data": f"del_fj_{idx}"}])
        
        if len(channels) < 4:
            buttons.append([{"text": "Add New Channel", "icon_custom_emoji_id": EMOJI["in_add"], "callback_data": "add_fj", "style": "success"}])
        
        buttons.append([{"text": "Back", "icon_custom_emoji_id": EMOJI["in_back"], "callback_data": "bot_settings", "style": "danger"}])
        await self.edit_message(chat_id, mid, msg, {"inline_keyboard": buttons}, "Markdown")

    async def handle_admin_countries(self, chat_id, mid):
        buttons = []
        for uid, data in self.countries_data.items():
            status = "✅" if data['enabled'] else "❌"
            penalty = "⚠️" if data.get('negative_balance') else ""
            code_display = data.get('code', uid)
            
            btn_text = f"{status} {penalty} {data['name']} (+{code_display})"
            btn = {"text": btn_text, "callback_data": f"edit_cnt_{uid}"}
            if data.get('flag_custom_emoji_id'):
                btn['icon_custom_emoji_id'] = data['flag_custom_emoji_id']
            else:
                btn['text'] = f"{status} {penalty} {data['flag']} {data['name']} (+{code_display})"
            buttons.append([btn])
        
        buttons.append([{"text": "Back", "icon_custom_emoji_id": EMOJI["in_back"], "callback_data": "back_to_admin", "style": "danger"}])
        total_stock = sum(d['stock'] for d in self.countries_data.values())
        msg = f"🌍 <b>Country Manager</b>\n📦 Total Stock: {total_stock}"
        await self.edit_message(chat_id, mid, msg, {"inline_keyboard": buttons}, "Markdown")

    async def handle_edit_country(self, chat_id, uid, mid):
        d = self.countries_data.get(uid)
        if not d: return
        code_display = d.get('code', uid)
        
        # PENALTY STATUS
        neg_status = "🔴 ON" if d.get('negative_balance') else "⚪ OFF"
        
        kb = {
            "inline_keyboard": [
                [{"text": "Edit Name", "icon_custom_emoji_id": EMOJI["in_edit"], "callback_data": f"ec_name_{uid}", "style": "primary"}, {"text": "Edit Flag", "icon_custom_emoji_id": EMOJI["in_edit"], "callback_data": f"ec_flag_{uid}", "style": "primary"}],
                [{"text": "Edit Rate", "icon_custom_emoji_id": EMOJI["in_edit"], "callback_data": f"ec_rate_{uid}", "style": "success"}, {"text": "Add Numbers", "icon_custom_emoji_id": EMOJI["in_add"], "callback_data": f"ec_addnum_{uid}", "style": "success"}],
                [{"text": "Toggle Status", "icon_custom_emoji_id": EMOJI["in_toggle"], "callback_data": f"ec_toggle_{uid}", "style": "primary"}, {"text": "Clear Stock", "icon_custom_emoji_id": EMOJI["in_del"], "callback_data": f"ec_clear_{uid}", "style": "danger"}],
                [{"text": f"⚠️ Penalty: {neg_status}", "callback_data": f"ec_neg_{uid}", "style": "danger"}],
                [{"text": "DELETE COUNTRY", "icon_custom_emoji_id": EMOJI["in_del"], "callback_data": f"ec_del_{uid}", "style": "danger"}],
                [{"text": "Back", "icon_custom_emoji_id": EMOJI["in_back"], "callback_data": "admin_countries", "style": "primary"}]
            ]
        }
        msg = f"🛠 <b>Edit: {d['name']}</b>\nCode: +{code_display}\nStock: {d['stock']}\nRate: ${d['per_otp_earn']}\nTraffic: {d.get('otp_count',0)}\n\n<b>Status:</b> {'Active' if d['enabled'] else 'Disabled'}\n<b>Penalty Mode:</b> {neg_status}"
        await self.edit_message(chat_id, mid, msg, kb, "Markdown")

    # ==========================================================================
    # 🚦 SMART LIVE TRAFFIC
    # ==========================================================================
    async def handle_live_traffic(self, chat_id, mid=None):
        sorted_countries = sorted(
            [c for c in self.countries_data.values() if c['enabled']], 
            key=lambda x: x.get('otp_count', 0), 
            reverse=True
        )

        msg = f"{E('traffic_icon', '🚦')} <b>LIVE TRAFFIC MONITOR</b>\n"
        msg += "<i>Real-time OTP delivery stats</i>\n"
        msg += "━━━━━━━━━━━━━━━━━━━━\n\n"

        if not sorted_countries:
            msg += "📉 <b>No traffic data available right now.</b>"
        else:
            for idx, d in enumerate(sorted_countries[:10], 1):
                code = d.get('code', '00')
                count = d.get('otp_count', 0)
                rate = d.get('per_otp_earn', 0.0)
                
                if idx == 1: rank_icon = E('traffic_top1', '🥇')
                elif idx == 2: rank_icon = E('traffic_top2', '🥈')
                elif idx == 3: rank_icon = E('traffic_top3', '🥉')
                else: rank_icon = f"<b>{idx:02d}.</b>"

                flag_html = f"<tg-emoji emoji-id='{d['flag_custom_emoji_id']}'>{d['flag']}</tg-emoji>" if d.get('flag_custom_emoji_id') else E('number_flag', d['flag'])
                msg += f"{rank_icon} {flag_html} <b>{d['name']}</b> (+{code})\n"
                msg += f"    └ {E('traffic_success', '🔥')} <b>Success:</b> {count}  |  {E('traffic_rate', '💰')} <b>Rate:</b> ${rate}\n\n"

        msg += "━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"🕒 Updated: {datetime.now().strftime('%I:%M %p')}"

        kb = {
            "inline_keyboard": [[{"text": "Refresh Traffic", "icon_custom_emoji_id": EMOJI["in_refresh"], "callback_data": "refresh_traffic", "style": "primary"}]]
        }

        if mid:
            try:
                await self.edit_message(chat_id, mid, msg, kb, "HTML")
            except: pass 
        else:
            await self.send_message(chat_id, msg, kb, "HTML")

    async def check_force_join(self, chat_id, mid_to_edit=None):
        if self.is_admin(chat_id): return True
        
        fj = self.system_config.get('force_join', {})
        if not fj.get('enabled'): return True
        channels = fj.get('channels', [])
        if not channels: return True

        not_joined = []
        
        for ch in channels:
            try:
                res = await self.get_chat_member(ch['id'], chat_id)
                if res and res.get('ok'):
                    status = res['result']['status']
                    if status in ['left', 'kicked']:
                        not_joined.append(ch)
                else:
                    not_joined.append(ch)
            except:
                not_joined.append(ch)

        if not not_joined:
            return True

        buttons = []
        for ch in channels:
            buttons.append([{"text": f"📢 Join {ch.get('name', 'Channel')}", "url": ch['link']}])
        
        buttons.append([{"text": "✅ Verify Joined", "callback_data": "verify_fj", "style": "success"}])
        
        msg_text = "🔒 <b>Action Required!</b>\n\nPlease join our channels to use this bot.\nAfter joining all, click 'Verify Joined'."
        
        if mid_to_edit:
            try:
                await self.edit_message(chat_id, mid_to_edit, msg_text, {"inline_keyboard": buttons}, "Markdown")
            except:
                await self.send_message(chat_id, msg_text, {"inline_keyboard": buttons}, "Markdown")
        else:
            await self.send_message(chat_id, msg_text, {"inline_keyboard": buttons}, "Markdown")
        
        return False

    # ==========================================================================
    # 🔄 MAIN UPDATE LOOP
    # ==========================================================================
    async def process_update(self, update):
        try:
            # 1. CHANNEL POST
            if 'channel_post' in update:
                if str(update['channel_post']['chat']['id']) == str(OTP_CHANNEL_ID): 
                    await self.process_channel_post(update['channel_post'])
                return

            # 2. MESSAGES
            if 'message' in update:
                msg = update['message']
                cid = msg['chat']['id']
                text = msg.get('text', '')

                if not text.startswith('/start'):
                    if not await self.check_force_join(cid): return

                # ⌨️ State Management
                state = self.admin_states.get(cid)
                if state:
                    if state.get('action') == 'add_admin_id':
                        try:
                            new_aid = int(text)
                            if new_aid not in self.system_config['admins']:
                                self.system_config['admins'].append(new_aid)
                                self.mark_dirty()
                                await self.send_message(cid, f"✅ Admin {new_aid} Added!")
                            else:
                                await self.send_message(cid, "⚠️ Already Admin.")
                            del self.admin_states[cid]
                            await self.handle_manage_admins(cid, state['mid'])
                        except:
                            await self.send_message(cid, "❌ Invalid ID. Try again.")
                        return

                    if state.get('action') == 'ec_addnum':
                        if 'document' in msg:
                             uid = state['code']
                             f_info = await self.api_call("getFile", {'file_id': msg['document']['file_id']})
                             url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{f_info['result']['file_path']}"
                             async with self.session.get(url) as resp: content = await resp.text()
                             new_nums = [l.strip() for l in content.split('\n') if l.strip().isdigit()]
                             
                             if uid in self.countries_data:
                                 self.countries_data[uid]['numbers'].extend(new_nums)
                                 self.countries_data[uid]['stock'] = len(self.countries_data[uid]['numbers'])
                                 self.mark_dirty()
                                 await self.send_message(cid, f"✅ Added {len(new_nums)} numbers!\nTotal Stock: {self.countries_data[uid]['stock']}")
                                 await self.handle_edit_country(cid, uid, state['mid'])
                             del self.admin_states[cid]
                        else:
                             await self.send_message(cid, "❌ Please upload a .txt file.")
                        return

                    if state.get('action', '').startswith('ec_'):
                        uid = state['code']
                        prop = state['action'].replace('ec_', '')
                        val = text
                        
                        if prop == 'rate': 
                            try: val = float(text)
                            except: val = 0.0
                            self.countries_data[uid]['per_otp_earn'] = val
                        elif prop == 'flag':
                            self.countries_data[uid]['flag'] = val
                            if 'entities' in msg:
                                for ent in msg['entities']:
                                    if ent['type'] == 'custom_emoji':
                                        self.countries_data[uid]['flag_custom_emoji_id'] = ent['custom_emoji_id']
                                        break
                                else:
                                    self.countries_data[uid].pop('flag_custom_emoji_id', None)
                            else:
                                self.countries_data[uid].pop('flag_custom_emoji_id', None)
                        elif prop == 'name':
                            self.countries_data[uid]['name'] = val
                        
                        if uid in self.countries_data:
                            self.mark_dirty()
                            await self.send_message(cid, f"✅ Updated {prop} to {val}")
                            await self.handle_edit_country(cid, uid, state['mid'])
                        del self.admin_states[cid]
                        return

                    if state.get('action') == 'add_c':
                        if state['step'] == 'name': 
                            state['name'] = text; state['step'] = 'code'; await self.send_message(cid, "Send Country Code (e.g. 880):")
                        elif state['step'] == 'code': 
                            state['code'] = text; state['step'] = 'flag'; await self.send_message(cid, "Send Flag Emoji:")
                        elif state['step'] == 'flag': 
                            state['flag'] = text
                            if 'entities' in msg:
                                for ent in msg['entities']:
                                    if ent['type'] == 'custom_emoji':
                                        state['flag_custom_emoji_id'] = ent['custom_emoji_id']
                                        break
                            state['step'] = 'rate'; await self.send_message(cid, "Send Per OTP Rate (e.g. 0.20):")
                        elif state['step'] == 'rate': 
                            try: state['rate'] = float(text)
                            except: state['rate'] = 0.0
                            state['step'] = 'file'; await self.send_message(cid, "📁 Upload Numbers File (.txt):")
                        elif 'document' in msg and state['step'] == 'file':
                             f_info = await self.api_call("getFile", {'file_id': msg['document']['file_id']})
                             url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{f_info['result']['file_path']}"
                             async with self.session.get(url) as resp: content = await resp.text()
                             nums = [l.strip() for l in content.split('\n') if l.strip().isdigit()]
                             
                             unique_id = f"{state['code']}_{int(time.time())}"
                             self.countries_data[unique_id] = {
                                 'name': state['name'], 'code': state['code'], 'flag': state['flag'], 
                                 'enabled': True, 'stock': len(nums), 'per_otp_earn': state['rate'], 
                                 'numbers': nums, 'otp_count': 0, 'negative_balance': False
                             }
                             if 'flag_custom_emoji_id' in state:
                                 self.countries_data[unique_id]['flag_custom_emoji_id'] = state['flag_custom_emoji_id']
                             self.mark_dirty()
                             del self.admin_states[cid]
                             await self.send_message(cid, f"✅ Country Added! {len(nums)} numbers loaded.")
                             flag_html = f"<tg-emoji emoji-id='{state['flag_custom_emoji_id']}'>{state['flag']}</tg-emoji>" if 'flag_custom_emoji_id' in state else state['flag']
                             asyncio.create_task(self.run_broadcast(None, text_msg=f"🚨 <b>NEW COUNTRY</b>\n\n🌍 <b>{state['name']}</b> {flag_html}\n💰 Rate: ${state['rate']}\n⚡ Get Number Now!"))
                        return
                    
                    if state.get('action') == 'fj_add_id':
                        state['id'] = text
                        state['action'] = 'fj_add_link'
                        await self.send_message(cid, "🔗 Send Invite Link:")
                        return
                    if state.get('action') == 'fj_add_link':
                        state['link'] = text
                        state['action'] = 'fj_add_name'
                        await self.send_message(cid, "📝 Send Short Name (e.g. Main Channel):")
                        return
                    if state.get('action') == 'fj_add_name':
                        new_ch = {"id": state['id'], "link": state['link'], "name": text}
                        if 'channels' not in self.system_config['force_join']: self.system_config['force_join']['channels'] = []
                        self.system_config['force_join']['channels'].append(new_ch)
                        self.mark_dirty()
                        mid = state['mid']
                        del self.admin_states[cid]
                        await self.send_message(cid, "✅ Channel Added!")
                        await self.handle_manage_force_join(cid, mid)
                        return

                    if state.get('action') == 'set_minwd':
                        try: self.system_config['min_withdraw'] = float(text)
                        except: pass
                        self.mark_dirty()
                        del self.admin_states[cid]
                        await self.handle_bot_settings(cid, state['mid'])
                        return
                    if state.get('action') == 'set_refbonus':
                        try: self.system_config['per_refer'] = float(text)
                        except: pass
                        self.mark_dirty()
                        del self.admin_states[cid]
                        await self.handle_bot_settings(cid, state['mid'])
                        return

                    if state.get('action') == 'set_cooldown':
                        try:
                            secs = int(text)
                            if secs < 0: secs = 0
                            self.system_config['number_cooldown'] = secs
                            self.mark_dirty()
                            mins, s = divmod(secs, 60)
                            t = f"{mins}m {s}s" if mins else f"{s}s"
                            await self.send_message(cid, f"\u2705 Cooldown set to <b>{t}</b> ({secs}s)", parse_mode="HTML")
                        except:
                            await self.send_message(cid, "\u274c Invalid value. Send a number in seconds (e.g. 120)")
                            return
                        del self.admin_states[cid]
                        await self.handle_bot_settings(cid, state['mid'])
                        return

                    if state.get('action') == 'broadcast':
                        if text.lower() == 'cancel':
                             await self.send_message(cid, "❌ Cancelled")
                        else:
                             asyncio.create_task(self.run_broadcast(cid, msg_id=msg['message_id']))
                        del self.admin_states[cid]
                        return

                if cid in self.withdraw_sessions:
                    await self.handle_withdraw_input(cid, text)
                    return

                if text.startswith('/start'):
                    ref = text.split()[1] if len(text.split()) > 1 else None
                    await self.handle_start(cid, msg['from'].get('first_name'), msg['from'].get('username'), ref)
                    if not await self.check_force_join(cid): return
                
                elif text in ('Get Number', '📲 Get Number'): await self.handle_get_number(cid)
                elif text in ('Balance', '💰 Balance'):
                    b = self.users_data.get(str(cid), {}).get('balance_usd', 0)
                    bal_msg = (
                        f"{E('balance_icon', '💰')} <b>Your Balance</b>\n\n"
                        f"{E('balance_usd', '💵')} <b>${b:.4f} USD</b>"
                    )
                    await self.send_message(cid, bal_msg, parse_mode="HTML")
                elif text in ('Withdraw', '💸 Withdraw'): await self.handle_withdraw(cid)
                elif text in ('Live Traffic', '🚦 Live Traffic'): await self.handle_live_traffic(cid)
                elif text in ('Countries', '🌍 Countries'):
                     lines = []
                     for d in self.countries_data.values():
                         if d['enabled']:
                             flag_html = f"<tg-emoji emoji-id='{d['flag_custom_emoji_id']}'>{d['flag']}</tg-emoji>" if d.get('flag_custom_emoji_id') else d['flag']
                             lines.append(f"{flag_html} {d['name']}: {d['stock']}")
                     msg_txt = "🌍 <b>Countries:</b>\n" + "\n".join(lines)
                     await self.send_message(cid, msg_txt, parse_mode="HTML")
                elif text in ('Support', '📞 Support'):
                    kb = {"inline_keyboard": [[{"text": "Chat with Support", "icon_custom_emoji_id": EMOJI["in_chat"], "url": f"https://t.me/{SUPPORT_USERNAME}"}]]}
                    await self.send_message(cid, "📞 Click below to contact support:", reply_markup=kb)
                elif text in ('Admin Panel', '⚙️ Admin Panel'): await self.handle_admin_panel(cid)

            if 'callback_query' in update:
                cb = update['callback_query']
                data, cid, mid = cb['data'], cb['message']['chat']['id'], cb['message']['message_id']
                cb_id = cb['id']
                
                # Auto-answer if it's not going to show a specific alert
                no_auto = data.startswith(('copy_num_', 'get_', 'ec_', 'del_adm_', 'wda_', 'rj_')) or data in ('change_num', 'verify_fj', 'add_admin_wiz')
                if not no_auto:
                    await self.answer_callback(cb_id)

                # Verify Force Join
                if data == 'verify_fj':
                    if await self.check_force_join(cid, mid_to_edit=mid):
                        await self.answer_callback(cb_id)
                        await self.send_message(cid, "✅ <b>Verified!</b> You can now use the bot.", self.main_keyboard)
                    else:
                        await self.answer_callback(cb_id, "❌ You haven't joined all channels!", show_alert=True)
                    return
                
                # Refresh Traffic
                if data == 'refresh_traffic':
                    await self.handle_live_traffic(cid, mid)
                    return

                if data == 'back_to_admin': await self.handle_admin_panel(cid, mid)
                elif data == 'manage_admins': await self.handle_manage_admins(cid, mid)
                elif data == 'add_admin_wiz':
                    if cid != DEFAULT_ADMIN_ID:
                        await self.answer_callback(cb_id, "⛔ Permission Denied! Only Owner can add admins.", show_alert=True)
                    else:
                        await self.answer_callback(cb_id)
                        self.admin_states[cid] = {'action': 'add_admin_id', 'mid': mid}
                        await self.send_message(cid, "👤 Send the Telegram ID of the new admin:")
                
                elif data == 'rem_admin_wiz': await self.handle_remove_admin_list(cid, mid)
                elif data.startswith('del_adm_'):
                    tgt_id = int(data.replace('del_adm_', ''))
                    if tgt_id == DEFAULT_ADMIN_ID:
                        await self.answer_callback(cb_id, "❌ Cannot remove the OWNER!", show_alert=True)
                    elif cid != DEFAULT_ADMIN_ID:
                        await self.answer_callback(cb_id, "⛔ Permission Denied!", show_alert=True)
                    elif tgt_id in self.system_config['admins']:
                        self.system_config['admins'].remove(tgt_id)
                        self.mark_dirty()
                        await self.answer_callback(cb_id, "🗑 Removed!", show_alert=True)
                        await self.handle_manage_admins(cid, mid)

                elif data == 'add_country_wiz': 
                    self.admin_states[cid] = {'action': 'add_c', 'step': 'name'}
                    await self.send_message(cid, "🌍 Send Country Name:")
                elif data == 'admin_countries': await self.handle_admin_countries(cid, mid)
                
                # STATS MENU
                elif data == 'view_stats': await self.handle_view_stats(cid, mid)
                elif data == 'todays_stats': 
                    today = datetime.now().strftime('%Y-%m-%d')
                    count = sum(1 for u in self.users_data.values() for o in u.get('recent_otps',[]) if o['timestamp'].startswith(today))
                    await self.edit_message(cid, mid, f"📊 Today's OTPs: {count}", {"inline_keyboard":[[{"text":"Back","callback_data":"view_stats", "style": "primary"}]]})
                elif data == 'top_10_users': await self.handle_top_users(cid, mid)

                elif data == 'manage_withdrawals':
                    pending = {k:v for k,v in self.pending_withdrawals.items() if v['status'] == 'pending'}
                    if not pending: await self.edit_message(cid, mid, "✅ No Pending Requests", {"inline_keyboard":[[{"text":"Back","callback_data":"back_to_admin", "style": "danger"}]]})
                    else:
                        btns = []
                        for tid, v in list(pending.items())[:5]:
                            btns.append([{"text": f"✅ {v['bdt']} BDT", "callback_data": f"ap_{tid}", "style": "success"}, {"text": "❌", "callback_data": f"rj_{tid}", "style": "danger"}])
                        btns.append([{"text": "Back", "callback_data": "back_to_admin", "style": "danger"}])
                        await self.edit_message(cid, mid, "💸 Pending Withdrawals:", {"inline_keyboard": btns})
                elif data == 'broadcast_wiz':
                    self.admin_states[cid] = {'action': 'broadcast'}
                    await self.edit_message(cid, mid, "📢 Send msg to broadcast (or type 'cancel'):", {"inline_keyboard":[[{"text":"Cancel","callback_data":"back_to_admin", "style": "danger"}]]})
                elif data == 'bot_settings': await self.handle_bot_settings(cid, mid)

                elif data == 'set_maint':
                    self.system_config['maintenance_mode'] = not self.system_config.get('maintenance_mode', False)
                    self.mark_dirty()
                    await self.handle_bot_settings(cid, mid)
                elif data == 'set_minwd':
                    self.admin_states[cid] = {'action': 'set_minwd', 'mid': mid}
                    await self.send_message(cid, "💰 Send new Min Withdraw amount:")
                elif data == 'set_refbonus':
                    self.admin_states[cid] = {'action': 'set_refbonus', 'mid': mid}
                    await self.send_message(cid, "🎁 Send new Refer Bonus amount:")
                elif data == 'set_cooldown':
                    self.admin_states[cid] = {'action': 'set_cooldown', 'mid': mid}
                    curr = self.system_config.get('number_cooldown', 60)
                    await self.send_message(cid, f"⏳ Current Cooldown: {curr}s\n\nনতুন cooldown কত seconds হবে তা পাঠান (0 = disabled):")
                
                # Force Join Management
                elif data == 'manage_fj': await self.handle_manage_force_join(cid, mid)
                elif data == 'toggle_fj':
                    if not self.system_config.get('force_join'): self.system_config['force_join'] = {}
                    self.system_config['force_join']['enabled'] = not self.system_config['force_join'].get('enabled', False)
                    self.mark_dirty()
                    await self.handle_bot_settings(cid, mid)
                elif data == 'add_fj':
                    self.admin_states[cid] = {'action': 'fj_add_id', 'mid': mid}
                    await self.send_message(cid, "🆔 Send Channel ID (e.g. -100xxx or @channel):")
                elif data.startswith('del_fj_'):
                    idx = int(data.replace('del_fj_', ''))
                    try:
                        del self.system_config['force_join']['channels'][idx]
                        self.mark_dirty()
                        await self.handle_manage_force_join(cid, mid)
                    except: pass

                elif data.startswith('edit_cnt_'): await self.handle_edit_country(cid, data[9:], mid)
                
                elif data.startswith('ec_'):
                    try:
                        parts = data.split('_', 2)
                        act = parts[1]
                        uid = parts[2]

                        if act == 'toggle':
                            self.countries_data[uid]['enabled'] = not self.countries_data[uid]['enabled']
                            self.mark_dirty()
                            await self.answer_callback(cb_id)
                            await self.handle_edit_country(cid, uid, mid)
                        elif act == 'neg':
                            # Toggle Negative Balance
                            curr = self.countries_data[uid].get('negative_balance', False)
                            self.countries_data[uid]['negative_balance'] = not curr
                            self.mark_dirty()
                            await self.answer_callback(cb_id)
                            await self.handle_edit_country(cid, uid, mid)
                        elif act == 'del':
                            del self.countries_data[uid]
                            self.mark_dirty()
                            await self.answer_callback(cb_id, "🗑 Country Deleted", show_alert=True)
                            await self.handle_admin_countries(cid, mid)
                        elif act == 'clear':
                            self.countries_data[uid]['numbers'] = []
                            self.countries_data[uid]['stock'] = 0
                            self.mark_dirty()
                            await self.answer_callback(cb_id, "🗑 Stock Cleared!", show_alert=True)
                            await self.handle_edit_country(cid, uid, mid)
                        elif act == 'addnum':
                            self.admin_states[cid] = {'action': 'ec_addnum', 'code': uid, 'mid': mid}
                            await self.answer_callback(cb_id)
                            await self.send_message(cid, "📁 Upload the Numbers file (.txt) to append:")
                        elif act in ['name', 'flag', 'rate']:
                            self.admin_states[cid] = {'action': f'ec_{act}', 'code': uid, 'mid': mid}
                            await self.answer_callback(cb_id)
                            await self.send_message(cid, f"✏️ Send new {act}:")
                    except Exception as e:
                        logger.error(f"EC Error: {e}")

                elif data.startswith('ap_'):
                    tid = data[3:]
                    if tid in self.pending_withdrawals:
                        self.pending_withdrawals[tid]['status'] = 'approved'
                        self.mark_dirty()
                        await self.answer_callback(cb_id, "✅ Approved", show_alert=False)
                        await self.send_message(self.pending_withdrawals[tid]['uid'], f"✅ Withdraw Approved: {self.pending_withdrawals[tid]['bdt']} BDT")
                        await self.edit_message(cid, mid, "✅ Approved")
                elif data.startswith('rj_'):
                    tid = data[3:]
                    if tid in self.pending_withdrawals:
                        wd = self.pending_withdrawals[tid]
                        wd['status'] = 'rejected'
                        self.users_data[str(wd['uid'])]['balance_usd'] += wd['usd']
                        self.mark_dirty()
                        await self.answer_callback(cb_id, "❌ Rejected", show_alert=False)
                        await self.send_message(wd['uid'], f"❌ Withdraw Rejected. Refunded: ${wd['usd']:.4f}")
                        await self.edit_message(cid, mid, "❌ Rejected")

                elif data.startswith('copy_num_'):
                    try:
                        index = int(data.replace('copy_num_', ''))
                        user_numbers = self.users_data.get(str(cid), {}).get('last_assigned_numbers', [])
                        style_map = {0: '🔵 PRIMARY', 1: '🔴 DANGER', 2: '🟢 SUCCESS'}
                        if 0 <= index < len(user_numbers):
                            await self.answer_callback(cb_id, '✅ Number sent below')
                            await self.send_copyable_number(cid, user_numbers[index], style_map.get(index, '📋 NUMBER'))
                        else:
                            await self.answer_callback(cb_id, '❌ Number not found', show_alert=True)
                    except Exception:
                        await self.answer_callback(cb_id, '❌ Copy failed', show_alert=True)
                elif data.startswith('get_'): await self.assign_number(cid, data[4:], mid, cb_id)
                elif data == 'change_num':
                    lc = self.users_data.get(str(cid), {}).get('last_country')
                    if lc:
                        if not self.is_admin(cid):
                            cooldown_total = int(self.system_config.get('number_cooldown', 60))
                            if cooldown_total > 0:
                                u_data = self.users_data.get(str(cid), {})
                                cooldown_until = float(u_data.get('number_cooldown_until', 0))
                                # ✅ int() নয়, real float comparison
                                if time.time() < cooldown_until:
                                    remaining = max(0.0, cooldown_until - time.time())
                                    secs_left  = int(remaining) + 1  # ceil — যাতে 0s না দেখায়
                                    mins, secs = divmod(secs_left, 60)
                                    time_str   = f"{mins}m {secs:02d}s" if mins else f"{secs:02d}s"
                                    alert_text = (
                                        f"⏳ Cooldown Active!\n\n"
                                        f"🕐 আরও {time_str} পর Change করতে পারবেন।\n"
                                        f"📌 Total Cooldown: {cooldown_total}s\n\n"
                                        f"সময় শেষ হলে আবার বাটন চাপুন।"
                                    )
                                    await self.answer_callback(cb_id, alert_text, show_alert=True)
                                    # Ticker শুধু একবারই চালু হবে
                                    existing = self.cooldown_tasks.get(cid)
                                    if not existing or existing.done():
                                        task = asyncio.create_task(
                                            self._ticker_update_number_msg(cid, mid, cooldown_until, lc)
                                        )
                                        self.cooldown_tasks[cid] = task
                                    return
                        # ✅ Cooldown শেষ বা admin
                        existing = self.cooldown_tasks.pop(cid, None)
                        if existing and not existing.done():
                            existing.cancel()
                        await self.assign_number(cid, lc, mid, cb_id)
                elif data == 'change_cnt': await self.handle_get_number(cid, mid)
                elif data == 'wd_back':
                    if cid in self.withdraw_sessions: del self.withdraw_sessions[cid]
                    await self.handle_withdraw(cid, mid)
                elif data.startswith('wda_'): await self.finalize_withdraw(cid, data, mid, cb_id)
                elif data.startswith('wd_'):
                    m = data.replace('wd_', '')
                    self.withdraw_sessions[cid] = {'method': m, 'step': 'account'}
                    await self.edit_message(cid, mid, f"✏️ Send {m} account:", {"inline_keyboard":[[{"text":"↩️ Back","callback_data":"wd_back", "style": "danger"}]]})

        except Exception as e:
            logger.error(f"Update Error: {e}")

    # ==========================================================================
    # 🏃 RUNNER
    # ==========================================================================
    async def run_broadcast(self, admin_id, msg_id=None, text_msg=None):
        users = list(self.users_data.keys())
        if admin_id: await self.send_message(admin_id, f"🚀 Sending to {len(users)} users...")
        
        sem = asyncio.Semaphore(25)
        success, blocked = 0, 0
        
        async def send(uid):
            nonlocal success, blocked
            async with sem:
                try:
                    if msg_id: res = await self.copy_message(int(uid), admin_id, msg_id)
                    else: res = await self.send_message(int(uid), text_msg, parse_mode="HTML")
                    if res and res.get('ok'): success += 1
                    else: blocked += 1
                except: blocked += 1
                await asyncio.sleep(0.04)

        await asyncio.gather(*[send(uid) for uid in users])
        if admin_id: await self.send_message(admin_id, f"📊 <b>Done</b>\n✅ Sent: {success}\n❌ Failed: {blocked}", parse_mode="HTML")

    async def handle_start(self, chat_id, name, username, ref):
        uid = str(chat_id)
        if uid not in self.users_data:
            self.users_data[uid] = {'first_name': name, 'username': username, 'balance_usd': 0.0, 'join_date': datetime.now().isoformat()}
            if ref and ref.startswith('ref_'):
                referrer = ref[4:]
                if referrer in self.users_data:
                    self.users_data[referrer]['balance_usd'] += self.system_config.get('per_refer', 0.0)
            self.mark_dirty()
            
        kb = self.admin_keyboard if self.is_admin(chat_id) else self.main_keyboard
        welcome_msg = (
            f"{E('welcome', '👋')} <b>Welcome, {name}!</b>\n\n"
            f"{E('get_number', '📲')} Get a number to receive OTPs\n"
            f"{E('earn', '💰')} Earn money for each OTP\n"
            f"{E('withdraw_icon', '💸')} Withdraw your earnings anytime"
        )
        await self.send_message(chat_id, welcome_msg, kb, "HTML")

    # 🔄 UPDATED: CLEAN UI WITH BRACKET STOCK
    async def handle_get_number(self, chat_id, mid=None):
        if self.system_config.get('maintenance_mode') and not self.is_admin(chat_id):
            return await self.send_message(chat_id, "⚠️ Maintenance Mode")
        if not await self.check_force_join(chat_id): return

        buttons = []
        for uid, d in self.countries_data.items():
            if d['enabled'] and d['stock'] > 0:
                # CLEAN FORMAT: Flag Name (Stock)
                btn = {"text": f"{d['name']} ({d['stock']})", "callback_data": f"get_{uid}", "style": "primary"}
                if d.get('flag_custom_emoji_id'):
                    btn['icon_custom_emoji_id'] = d['flag_custom_emoji_id']
                else:
                    btn['text'] = f"{d['flag']} {d['name']} ({d['stock']})"
                buttons.append([btn])
        
        if not buttons: return await self.send_message(chat_id, "❌ No Stock Available")

        msg = f"{E('country_select', '🌍')} <b>Select Country:</b>\nTap a country to get a number."
        if mid:
            try:
                await self.edit_message(chat_id, mid, msg, {"inline_keyboard": buttons}, "HTML")
            except: pass
        else:
            await self.send_message(chat_id, msg, {"inline_keyboard": buttons}, "HTML")

    # ==========================================================================
    # ⏳ COOLDOWN TICKER — Number message এ realtime timer দেখায়
    # ==========================================================================
    async def _ticker_update_number_msg(self, chat_id, mid, cooldown_until, last_country):
        """
        Number message এর নিচে realtime countdown দেখায়।
        int() truncation এড়াতে time.time() >= cooldown_until দিয়ে loop চালায়।
        """
        try:
            cooldown_total = int(self.system_config.get('number_cooldown', 60))
            u_data = self.users_data.get(str(chat_id), {})
            country_id = u_data.get('last_country', last_country)
            c_data = self.countries_data.get(country_id, {})

            def build_kb():
                nums = self.users_data.get(str(chat_id), {}).get('last_assigned_numbers', [])
                rows = [[{"text": f"  {fn}  ✦ Copy", "copy_text": {"text": fn}}] for fn in nums]
                rows += [
                    [
                        {"text": "Change Number", "icon_custom_emoji_id": EMOJI["in_refresh"], "callback_data": "change_num", "style": "primary"},
                        {"text": "Change Country", "icon_custom_emoji_id": EMOJI["in_country"],  "callback_data": "change_cnt",  "style": "danger"}
                    ],
                    [{"text": "Join OTP Group", "icon_custom_emoji_id": EMOJI["in_users"], "url": OTP_GROUP_LINK, "style": "success"}]
                ]
                return {"inline_keyboard": rows}

            last_text = ""

            # 🔁 actual time.time() >= cooldown_until দিয়ে loop
            while time.time() < cooldown_until:
                remaining = max(0, cooldown_until - time.time())
                secs_left  = int(remaining)
                mins, secs = divmod(secs_left, 60)
                time_str   = f"{mins}m {secs:02d}s" if mins else f"{secs:02d}s"

                flag_html = f"<tg-emoji emoji-id='{c_data['flag_custom_emoji_id']}'>{c_data.get('flag','🌍')}</tg-emoji>" if c_data.get('flag_custom_emoji_id') else E('number_flag', c_data.get('flag','🌍'))
                new_text = (
                    f"{flag_html} <b>{c_data.get('name','')}</b> — Numbers Assigned:\n\n"
                    f"{E('number_copy', '📋')} নিচের বাটনে ক্লিক করলে নম্বর কপি হবে!\n"
                    f"{E('number_timer', '⏱')} Valid for 20 Minutes\n\n"
                    f"{E('cooldown_lock', '🔒')} Change cooldown: <b>{time_str}</b> / {cooldown_total}s"
                )

                if new_text != last_text:
                    try:
                        await self.edit_message(chat_id, mid, new_text, build_kb(), "HTML")
                        last_text = new_text
                    except Exception:
                        pass  # edit fail হলেও loop চলবে, break করবে না

                await asyncio.sleep(1)

            # ✅ Cooldown সত্যিই শেষ — তারপর message update করো
            flag_html = f"<tg-emoji emoji-id='{c_data['flag_custom_emoji_id']}'>{c_data.get('flag','🌍')}</tg-emoji>" if c_data.get('flag_custom_emoji_id') else E('number_flag', c_data.get('flag','🌍'))
            done_text = (
                f"{flag_html} <b>{c_data.get('name','')}</b> — Numbers Assigned:\n\n"
                f"{E('number_copy', '📋')} নিচের বাটনে ক্লিক করলে নম্বর কপি হবে!\n"
                f"{E('number_timer', '⏱')} Valid for 20 Minutes\n\n"
                f"{E('cooldown_done', '✅')} Cooldown শেষ! এখন Change Number করতে পারবেন।"
            )
            try:
                await self.edit_message(chat_id, mid, done_text, build_kb(), "HTML")
            except Exception:
                pass

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Ticker Error: {e}")
        finally:
            self.cooldown_tasks.pop(chat_id, None)

    async def assign_number(self, chat_id, uid, mid=None, cb_id=None):
        if not await self.check_force_join(chat_id): 
            if cb_id: await self.answer_callback(cb_id)
            return

        # ⏳ COOLDOWN CHECK — absolute timestamp দিয়ে check করা হচ্ছে
        if not self.is_admin(chat_id):
            cooldown_secs = int(self.system_config.get('number_cooldown', 60))
            if cooldown_secs > 0:
                u_data = self.users_data.get(str(chat_id), {})
                cooldown_until = float(u_data.get('number_cooldown_until', 0))
                # ✅ real float comparison — int() truncation এড়ানো
                if time.time() < cooldown_until:
                    remaining  = max(0.0, cooldown_until - time.time())
                    secs_left  = int(remaining) + 1
                    mins, secs = divmod(secs_left, 60)
                    time_str   = f"{mins}m {secs:02d}s" if mins else f"{secs:02d}s"
                    cooldown_msg = (
                        f"{E('cooldown_lock', '⏳')} <b>Cooldown Active!</b>\n\n"
                        f"নতুন নম্বর নিতে আরও {time_str} অপেক্ষা করুন।\n"
                        f"{E('number_timer', '⏱')} Total Cooldown: {cooldown_secs}s"
                    )
                    back_kb = {"inline_keyboard": [
                        [{"text": "Change Country", "icon_custom_emoji_id": EMOJI["in_country"], "callback_data": "change_cnt"}]
                    ]}
                    if mid:
                        try: await self.edit_message(chat_id, mid, cooldown_msg, back_kb, "HTML")
                        except: await self.send_message(chat_id, cooldown_msg, back_kb, "HTML")
                        await self.send_message(chat_id, cooldown_msg, back_kb, "HTML")
                    
                    if cb_id: await self.answer_callback(cb_id)
                    return
            # ✅ Cooldown পাস — এখনই timestamp set করো
            u_id = str(chat_id)
            if u_id not in self.users_data:
                self.users_data[u_id] = {}
            self.users_data[u_id]['number_cooldown_until'] = time.time() + cooldown_secs
            self.mark_dirty()

        data = self.countries_data.get(uid)
        if not data or not data['numbers']: 
            if cb_id: await self.answer_callback(cb_id, "❌ Out of Stock", True)
            await self.handle_get_number(chat_id, mid)
            return
        
        # ✅ UPDATED: Assign up to 3 numbers at once
        count = min(3, len(data['numbers']))
        raw_nums = [data['numbers'].pop(0) for _ in range(count)]
        data['stock'] = len(data['numbers'])
        code = data.get('code', uid)
        full_nums = [f"+{r}" if r.startswith(code) else f"+{code}{r}" for r in raw_nums]
        
        u_id = str(chat_id)
        self.users_data[u_id].update({
            'last_assigned_number': full_nums[0], 
            'last_assigned_numbers': full_nums,
            'last_country': uid, 
            'last_mid': mid,
            'assigned_time': time.time()
        })
        # Track all 3 numbers in active map
        for fn in full_nums:
            self.active_number_map[self.mask_phone_number(fn)] = {
                'uid': u_id, 'full_number': fn, 'country': uid
            }
        self.mark_dirty()
        
        flag_html = f"<tg-emoji emoji-id='{data['flag_custom_emoji_id']}'>{data['flag']}</tg-emoji>" if data.get('flag_custom_emoji_id') else E('number_flag', data['flag'])
        msg = (
            f"{flag_html} <b>{data['name']}</b> — Numbers Assigned:\n\n"
            f"{E('number_copy', '📋')} নিচের বাটনে ক্লিক করলে নম্বর কপি হবে!\n"
            f"{E('number_timer', '⏱')} Valid for 20 Minutes"
        )
        
        # Each number on its own full-width row with copy_text
        copy_rows = [
            [{"text": f"  {fn}  ✦ Copy", "copy_text": {"text": fn}}]
            for fn in full_nums
        ]
        
        kb = {
            "inline_keyboard": copy_rows + [
                [
                    {"text": "Change Number", "icon_custom_emoji_id": EMOJI["in_refresh"], "callback_data": "change_num", "style": "primary"},
                    {"text": "Change Country", "icon_custom_emoji_id": EMOJI["in_country"], "callback_data": "change_cnt", "style": "danger"}
                ],
                [{"text": "Join OTP Group", "icon_custom_emoji_id": EMOJI["in_users"], "url": OTP_GROUP_LINK, "style": "success"}]
            ]
        }
        
        if mid: await self.edit_message(chat_id, mid, msg, kb, "HTML")
        else: await self.send_message(chat_id, msg, kb, "HTML")
        
        if cb_id: await self.answer_callback(cb_id)

    async def send_copyable_number(self, chat_id, number_text, style_label):
        msg = (
            f"{style_label} <b>Copy Number</b>\n\n"
            f"<code>{number_text}</code>\n\n"
            f"এখন number টা press করে copy করতে পারবে।"
        )
        await self.send_message(chat_id, msg, parse_mode="HTML")

    async def handle_withdraw(self, chat_id, mid=None):
        bal = self.users_data.get(str(chat_id), {}).get('balance_usd', 0)
        min_w = self.system_config.get('min_withdraw', 0.0001)
        if bal < min_w: return await self.send_message(chat_id, f"❌ Min Withdraw: ${min_w}")
        
        kb = {"inline_keyboard": [
            [{"text": "bKash", "icon_custom_emoji_id": EMOJI["in_money"], "callback_data": "wd_bkash", "style": "success"}, {"text": "Nagad", "icon_custom_emoji_id": EMOJI["in_money"], "callback_data": "wd_nagad", "style": "primary"}],
            [{"text": "USDT", "icon_custom_emoji_id": EMOJI["in_money"], "callback_data": "wd_usdt", "style": "primary"}, {"text": "Back", "icon_custom_emoji_id": EMOJI["in_back"], "callback_data": "wd_back", "style": "danger"}]
        ]}
        msg = (
            f"{E('wd_icon', '💸')} <b>Withdraw</b>\n\n"
            f"{E('wd_balance', '💰')} Balance: <b>${bal:.4f}</b>\n"
            f"Select Method:"
        )
        if mid: await self.edit_message(chat_id, mid, msg, kb, "HTML")
        else: await self.send_message(chat_id, msg, kb, "HTML")

    async def handle_withdraw_input(self, chat_id, text):
        session = self.withdraw_sessions.get(chat_id)
        if not session: return
        
        if session['step'] == 'account':
            session['account'] = text
            session['step'] = 'amt'
            bal = self.users_data[str(chat_id)]['balance_usd']
            
            btns = []
            for amt in [100, 300, 500, 1000]:
                usd = amt / 110
                cb = f"wda_{amt}" if usd <= bal else "ignore"
                txt = f"{amt} BDT" if usd <= bal else f"🔒 {amt}"
                style = "success" if usd <= bal else "danger"
                btns.append({"text": txt, "callback_data": cb, "style": style})
            
            kb = {"inline_keyboard": [btns[:2], btns[2:], [{"text": "Full Balance", "icon_custom_emoji_id": EMOJI["in_money"], "callback_data": "wda_full", "style": "success"}], [{"text": "Cancel", "icon_custom_emoji_id": EMOJI["in_back"], "callback_data":"wd_back", "style": "danger"}]]}
            await self.send_message(chat_id, f"💳 Acct: {text}\nSelect Amount:", kb)

    # 🔄 UPDATED: DETAILED ADMIN NOTIFICATION
    async def finalize_withdraw(self, chat_id, data, mid, cb_id=None):
        session = self.withdraw_sessions.get(chat_id)
        if not session: return
        bal = self.users_data[str(chat_id)]['balance_usd']
        
        amt_str = data.replace('wda_', '')
        if amt_str == 'full': amt_usd = bal; amt_bdt = int(bal * 110)
        else: amt_bdt = int(amt_str); amt_usd = amt_bdt / 110
        
        if bal < amt_usd: 
            if cb_id: await self.answer_callback(cb_id, "❌ Low Balance", True)
            return
        
        self.users_data[str(chat_id)]['balance_usd'] -= amt_usd
        tid = f"WD{chat_id}{int(time.time())}"
        self.pending_withdrawals[tid] = {
            'uid': chat_id, 'method': session['method'], 'acct': session['account'],
            'usd': amt_usd, 'bdt': amt_bdt, 'status': 'pending', 'ts': datetime.now().isoformat()
        }
        
        # Get User Info for Notification
        user_info = self.users_data.get(str(chat_id), {})
        username = user_info.get('username', 'No Username')
        first_name = user_info.get('first_name', 'User')

        # Admin Notification Message (HTML)
        admin_msg = (
            f"🚨 <b>NEW WITHDRAWAL REQUEST</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>User:</b> <a href='tg://user?id={chat_id}'>{first_name}</a>\n"
            f"🆔 <b>ID:</b> <code>{chat_id}</code>\n"
            f"📛 <b>Username:</b> @{username}\n\n"
            f"💰 <b>Amount:</b> {amt_bdt} BDT (${amt_usd:.2f})\n"
            f"🏦 <b>Method:</b> {session['method'].replace('wd_', '').upper()}\n"
            f"📱 <b>Account:</b> <code>{session['account']}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"<i>Check /admin > Withdrawals to approve/reject.</i>"
        )
        
        for aid in self.system_config.get('admins', []):
             await self.send_message(aid, admin_msg, parse_mode="HTML")

        del self.withdraw_sessions[chat_id]
        self.mark_dirty()
        if cb_id: await self.answer_callback(cb_id, "✅ Request Submitted!", show_alert=True)
        await self.edit_message(chat_id, mid, f"✅ Request Submitted!\nAmount: {amt_bdt} BDT")

    async def run(self):
        self.running = True
        await self.start_session()
        logger.info(f"🚀 Bot Started! Listening to {OTP_CHANNEL_ID}")
        
        asyncio.create_task(self.background_save_task())
        
        retry_delay = 1
        while self.running:
            try:
                updates = await self.api_call("getUpdates", {'offset': self.last_update_id + 1, 'timeout': 30})
                if updates and updates.get('ok'):
                    retry_delay = 1  # reset on success
                    for u in updates['result']:
                        self.last_update_id = u['update_id']
                        asyncio.create_task(self.process_update(u))
            except Exception as e:
                logger.error(f"Polling: {e}")
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 30)  # max 30s backoff

if __name__ == "__main__":
    bot = AsyncTelegramBot()
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        bot.save_all_sync()