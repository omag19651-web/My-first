import requests
import re
import asyncio
import sys
import json
from datetime import datetime
import phonenumbers
from phonenumbers import geocoder
from pytz import timezone
import html
import unicodedata
import aiohttp

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command

# ========== CONFIG ==========
SKIP_OLD = True  # Always skip old SMS on startup
TOKENS = [
    "8706371463:AAGSepawUA6MGAh5c6Uyn1HvP-6H-aLLJF4", # Main Bot (এটি দিয় পোলিং হবে)
    "8527339076:AAHfKEH4V_1sMEesVY1oY58NiFjZ1JLrQhg", # ২য় বট
]

ADMIN_ID     = 7061346269
GROUP_FULL   = -1003939266694
GROUP_MASKED = -1003397597597

API_URL   = "http://51.77.216.195/crapi/mait/viewstats"
API_TOKEN = "Q1JURjRSQnpIb5JTYpCBVENrgnprhHOIYnaIc1J4ZH1BhE9Xa3Fx"

# ========== INLINE BUTTONS URLS ==========
JOIN_CHANNEL_URL = "https://t.me/your_channel"   # 🔵 নীল - Join Channel
BOT_URL          = "https://t.me/your_bot"        # 🟢 সবুজ - Bot

# ========== BOT ROTATION LOGIC ==========
_bot_pulse = 0

def get_bot_api_by_index(idx):
    """নির্দিষ্ট ইনডেক্সের বটের API URL রিটার্ন করে"""
    token = TOKENS[idx % len(TOKENS)]
    return f"https://api.telegram.org/bot{token}"

def get_main_bot_api():
    """পোলিং বা এডমিন মেসেজের জন্য ১ম বট ব্যবহার হবে"""
    return f"https://api.telegram.org/bot{TOKENS[0]}"

# ========== AIOGRAM BOT (Primary) ==========
bot = Bot(token=TOKENS[0], default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp  = Dispatcher()

# ========== RAW API: STYLED BUTTON SENDER ==========
def _clean_inline_kb(kb: dict) -> dict:
    """
    Bot API 9.4 inline button valid fields.
    'style' অফিশিয়াল ফিল্ড — raw JSON দিয়ে পাঠালে Telegram গ্রহণ করে।
    """
    import copy
    VALID = {
        'text', 'url', 'callback_data', 'web_app', 'login_url',
        'switch_inline_query', 'switch_inline_query_current_chat',
        'switch_inline_query_chosen_chat', 'callback_game', 'pay',
        'icon_custom_emoji_id', 'copy_text', 'style'
    }
    cleaned = copy.deepcopy(kb)
    if 'inline_keyboard' in cleaned:
        for row in cleaned['inline_keyboard']:
            for btn in row:
                for k in list(btn.keys()):
                    if k not in VALID or btn[k] is None:
                        del btn[k]
    return cleaned


async def send_styled_message(chat_id: int, text: str, kb: dict, bot_idx: int, retries: int = 5):
    """নির্দিষ্ট ইনডেক্সের বট দিয়ে মেসেজ পাঠায়"""
    payload = {
        "chat_id":      chat_id,
        "text":         text,
        "parse_mode":   "HTML",
        "reply_markup": json.dumps(_clean_inline_kb(kb))
    }
    
    api_url = get_bot_api_by_index(bot_idx)
    for attempt in range(retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{api_url}/sendMessage", json=payload, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                    if resp.status == 429:
                        data = await resp.json()
                        wait_time = data.get("parameters", {}).get("retry_after", 5)
                        await asyncio.sleep(wait_time)
                        continue
                        
                    result = await resp.json()
                    if result.get("ok"): return result
                    
                    desc = result.get("description", "")
                    if "retry after" in desc.lower():
                        try:
                            wait_time = int(re.search(r'(\d+)', desc).group(1))
                            await asyncio.sleep(wait_time)
                            continue
                        except: pass
                    return result
        except:
            await asyncio.sleep(1)
    return None


async def safe_send_full(chat_id: int, text: str, bot_idx: int, retries: int = 5):
    """নির্দিষ্ট ইনডেক্সের বট দিয়ে Full Message পাঠায়"""
    payload = {
        "chat_id":      chat_id,
        "text":         text,
        "parse_mode":   "HTML"
    }

    api_url = get_bot_api_by_index(bot_idx)
    for attempt in range(retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{api_url}/sendMessage", json=payload, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 429:
                        data = await resp.json()
                        wait_time = data.get("parameters", {}).get("retry_after", 5)
                        await asyncio.sleep(wait_time)
                        continue
                    result = await resp.json()
                    if result.get("ok"): return True
        except:
            await asyncio.sleep(1)
    return False


async def notify_admin_on_start():
    """বট শুরু হলে এডমিনকে মেসেজ পাঠায়"""
    count = len(TOKENS)
    msg = (
        f"🚀 <b>Bot system is ONLINE!</b>\n\n"
        f"👤 Admin: <code>{ADMIN_ID}</code>\n"
        f"🤖 Active Bots: <b>{count}</b>\n"
        f"📡 Main Bot: <i>Primary Polling Active</i>"
    )
    payload = {"chat_id": ADMIN_ID, "text": msg, "parse_mode": "HTML"}
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(f"{get_main_bot_api()}/sendMessage", json=payload)
    except Exception as e:
        print(f"Admin Notify Error: {e}")

# ========== PREMIUM FLAG EMOJI MAP ==========
# Pack: FlagsEmoji2024 — Country Name → (unicode_flag, premium_emoji_id)
PREMIUM_FLAG_MAP = {
    "AF": ("🇦🇫", 5291937511591925566),
    "AX": ("🇦🇽", 5294077418917616055),
    "AL": ("🇦🇱", 5294202819077756005),
    "DZ": ("🇩🇿", 5294048127240655242),
    "AS": ("🇦🇸", 5291994273879709721),
    "AD": ("🇦🇩", 5294215205763434181),
    "AO": ("🇦🇴", 5294516785482062829),
    "AI": ("🇦🇮", 5292186323342350940),
    "AG": ("🇦🇬", 5294005972136647964),
    "AR": ("🇦🇷", 5292208210495689627),
    "AM": ("🇦🇲", 5291978717508164018),
    "AW": ("🇦🇼", 5294007002928798927),
    "AU": ("🇦🇺", 5294444247779399477),
    "AT": ("🇦🇹", 5291975174160145850),
    "AZ": ("🇦🇿", 5294323533428579078),
    "BS": ("🇧🇸", 5294031587321600012),
    "BH": ("🇧🇭", 5294108398516720753),
    "BD": ("🇧🇩", 5291824687096027834),
    "BB": ("🇧🇧", 5294526187165471742),
    "BY": ("🇧🇾", 5294134426018536120),
    "BE": ("🇧🇪", 5291774466043435275),
    "BZ": ("🇧🇿", 5294171848068584842),
    "BJ": ("🇧🇯", 5293984969746566866),
    "BT": ("🇧🇹", 5294121983498277263),
    "BO": ("🇧🇴", 5294201479047957700),
    "BW": ("🇧🇼", 5294026179957772585),
    "BR": ("🇧🇷", 5291892229751723900),
    "BN": ("🇧🇳", 5292098293692650297),
    "BG": ("🇧🇬", 5294308947719640437),
    "BF": ("🇧🇫", 5294153164960848949),
    "BI": ("🇧🇮", 5294051631933967760),
    "KH": ("🇰🇭", 5294225191562400452),
    "CM": ("🇨🇲", 5291997306126626950),
    "CA": ("🇨🇦", 5292290347450259214),
    "CV": ("🇨🇻", 5292203503211535593),
    "CF": ("🇨🇫", 5294210571493724819),
    "TD": ("🇹🇩", 5291780728105753403),
    "CL": ("🇨🇱", 5294231037012888049),
    "CN": ("🇨🇳", 5294068833277990704),
    "CO": ("🇨🇴", 5294010206974397371),
    "KM": ("🇰🇲", 5294351381996521508),
    "CG": ("🇨🇬", 5294035229453865597),
    "CK": ("🇨🇰", 5292098684534675100),
    "CR": ("🇨🇷", 5292063805105263554),
    "CI": ("🇨🇮", 5293991322003200135),
    "HR": ("🇭🇷", 5291999676948569127),
    "CU": ("🇨🇺", 5291963947115631526),
    "CY": ("🇨🇾", 5294062721539526918),
    "CZ": ("🇨🇿", 5294242852467923382),
    "DK": ("🇩🇰", 5294531860817268837),
    "DJ": ("🇩🇯", 5294127214768468283),
    "DM": ("🇩🇲", 5294485513825178032),
    "DO": ("🇩🇴", 5294522197140857947),
    "EC": ("🇪🇨", 5292083733753517221),
    "EG": ("🇪🇬", 5293992082212409502),
    "SV": ("🇸🇻", 5294337307388695687),
    "GQ": ("🇬🇶", 5292170045416297012),
    "ER": ("🇪🇷", 5291922054004625949),
    "EE": ("🇪🇪", 5291951143818123103),
    "ET": ("🇪🇹", 5292245976143124155),
    "GI": ("🇬🇮", 5292055799286224027),
    "GM": ("🇬🇲", 5294399820637688352),
    "GL": ("🇬🇱", 5292014752283774878),
    "FI": ("🇫🇮", 5294049961191690629),
    "FR": ("🇫🇷", 5291817660529533837),
    "GA": ("🇬🇦", 5294321325815389139),
    "GE": ("🇬🇪", 5294349389131697267),
    "DE": ("🇩🇪", 5292013274815028523),
    "GH": ("🇬🇭", 5294347396266873249),
    "GR": ("🇬🇷", 5291948395039054764),
    "GW": ("🇬🇼", 5294409819321550432),
    "GT": ("🇬🇹", 5294336633078831209),
    "GN": ("🇬🇳", 5291892096607739008),
    "GY": ("🇬🇾", 5292062692708736193),
    "HT": ("🇭🇹", 5292045130587462814),
    "HN": ("🇭🇳", 5291901034434682297),
    "HK": ("🇭🇰", 5292166459118606932),
    "HU": ("🇭🇺", 5294229581018975260),
    "IS": ("🇮🇸", 5294354358408859664),
    "IN": ("🇮🇳", 5291933173674957761),
    "IR": ("🇮🇷", 5294220170745630736),
    "IQ": ("🇮🇶", 5294325010897327367),
    "IE": ("🇮🇪", 5294471971793293647),
    "IM": ("🇮🇲", 5294318478252070646),
    "IL": ("🇮🇱", 5294069056616289553),
    "IT": ("🇮🇹", 5291826830284709120),
    "JM": ("🇯🇲", 5294505107465982830),
    "JP": ("🇯🇵", 5291799063321139445),
    "JE": ("🇯🇪", 5291950280529697493),
    "JO": ("🇯🇴", 5291988613112814801),
    "KZ": ("🇰🇿", 5294227175837290463),
    "KE": ("🇰🇪", 5292111852904416801),
    "KI": ("🇰🇮", 5294538934628405146),
    "KP": ("🇰🇵", 5294193812531333564),
    "KR": ("🇰🇷", 5294408281723262763),
    "KW": ("🇰🇼", 5292066437920218075),
    "KG": ("🇰🇬", 5292091954320922577),
    "LA": ("🇱🇦", 5291981530711746037),
    "LV": ("🇱🇻", 5292236016113966127),
    "LB": ("🇱🇧", 5294193108156699621),
    "LS": ("🇱🇸", 5292040693886247604),
    "LR": ("🇱🇷", 5291793810576137439),
    "LY": ("🇱🇾", 5291858711826946840),
    "LI": ("🇱🇮", 5292048742654957785),
    "LT": ("🇱🇹", 5294343084119708700),
    "LU": ("🇱🇺", 5294423709245787718),
    "MK": ("🇲🇰", 5294023611567332075),
    "MG": ("🇲🇬", 5291991568050312348),
    "MW": ("🇲🇼", 5294241881805312589),
    "MY": ("🇲🇾", 5291858351049696702),
    "MV": ("🇲🇻", 5292004203844097218),
    "ML": ("🇲🇱", 5292086972158858331),
    "MT": ("🇲🇹", 5294532213004588353),
    "MH": ("🇲🇭", 5294180730060954484),
    "MR": ("🇲🇷", 5294429743674840973),
    "MU": ("🇲🇺", 5294127824653797277),
    "MX": ("🇲🇽", 5294535073452809778),
    "FM": ("🇫🇲", 5291838156113470124),
    "MD": ("🇲🇩", 5294158486425325375),
    "MC": ("🇲🇨", 5294378161117614233),
    "MN": ("🇲🇳", 5294316532631883496),
    "MA": ("🇲🇦", 5292108962391414885),
    "MZ": ("🇲🇿", 5294086708931874940),
    "MM": ("🇲🇲", 5294254478944393569),
    "NA": ("🇳🇦", 5292021761670404922),
    "NR": ("🇳🇷", 5294463274484521342),
    "NP": ("🇳🇵", 5294458756178924088),
    "NL": ("🇳🇱", 5291917797692042265),
    "NZ": ("🇳🇿", 5294189019347833274),
    "NI": ("🇳🇮", 5294240825243358100),
    "NE": ("🇳🇪", 5291809418487290691),
    "NG": ("🇳🇬", 5294456308047563965),
    "NU": ("🇳🇺", 5294471336138134209),
    "NO": ("🇳🇴", 5291761718580502030),
    "OM": ("🇴🇲", 5291813666209946812),
    "PK": ("🇵🇰", 5291825606219029010),
    "PS": ("🇵🇸", 5294289826525238172),
    "PA": ("🇵🇦", 5291959935616178405),
    "PG": ("🇵🇬", 5291917995260533077),
    "PY": ("🇵🇾", 5294525611639852679),
    "PH": ("🇵🇭", 5291798075478661634),
    "PE": ("🇵🇪", 5292099427564018941),
    "PL": ("🇵🇱", 5292190970496963836),
    "PT": ("🇵🇹", 5294436555492973610),
    "PR": ("🇵🇷", 5292121516580820347),
    "QA": ("🇶🇦", 5292166360334357676),
    "RO": ("🇷🇴", 5294107724206856227),
    "RU": ("🇷🇺", 5294335323113807278),
    "RW": ("🇷🇼", 5294191265615729158),
    "SM": ("🇸🇲", 5292147350809106831),
    "ST": ("🇸🇹", 5292183188016222701),
    "SA": ("🇸🇦", 5294163983983463099),
    "SN": ("🇸🇳", 5292087023698466689),
    "RS": ("🇷🇸", 5294458584380230360),
    "SC": ("🇸🇨", 5291891186074672309),
    "SL": ("🇸🇱", 5294494314213167952),
    "SG": ("🇸🇬", 5294451304410663668),
    "SK": ("🇸🇰", 5294538440707166931),
    "SI": ("🇸🇮", 5294279359689938006),
    "SB": ("🇸🇧", 5294283890880433237),
    "SO": ("🇸🇴", 5294058817414255960),
    "ZA": ("🇿🇦", 5294325281480266304),
    "ES": ("🇪🇸", 5294513087515216901),
    "LK": ("🇱🇰", 5292102670264328257),
    "SD": ("🇸🇩", 5294177148058228060),
    "SR": ("🇸🇷", 5294396668131692138),
    "SZ": ("🇸🇿", 5294312482477724867),
    "SE": ("🇸🇪", 5291737091238026321),
    "CH": ("🇨🇭", 5291791748991835084),
    "SY": ("🇸🇾", 5294013428199869487),
    "TW": ("🇹🇼", 5294095745543069603),
    "TJ": ("🇹🇯", 5294120269806328883),
    "TZ": ("🇹🇿", 5292146096678658977),
    "TH": ("🇹🇭", 5293994384314882755),
    "TG": ("🇹🇬", 5294097669688415562),
    "TO": ("🇹🇴", 5294283689016973348),
    "TT": ("🇹🇹", 5294362935458548705),
    "TN": ("🇹🇳", 5294484680601521871),
    "TR": ("🇹🇷", 5293993400767367408),
    "TM": ("🇹🇲", 5294098958178603764),
    "TC": ("🇹🇨", 5294320866253884749),
    "US": ("🇺🇸", 5294244076533600593),
    "UG": ("🇺🇬", 5294192317882716626),
    "AE": ("🇦🇪", 5294314831824835370),
    "GB": ("🇬🇧", 5293993521026453119),
    "UA": ("🇺🇦", 5294263837678131580),
    "VU": ("🇻🇺", 5294448585696368047),
    "UZ": ("🇺🇿", 5294217645304864345),
    "UY": ("🇺🇾", 5291928449210932974),
    "VE": ("🇻🇪", 5294476442854247878),
    "VN": ("🇻🇳", 5294235963340379688),
    "VI": ("🇻🇮", 5294228039125718124),
    "YE": ("🇾🇪", 5294058972033076492),
    "ZM": ("🇿🇲", 5294100109229838880),
    "ZW": ("🇿🇼", 5294422158762592930),
}

# ========== SERVICE DETECTION ==========
# SMS টেক্সট থেকে সার্ভিস ডিটেক্ট করা হবে
SERVICE_PATTERNS = [
    ("Instagram",  r"instagram"),
    ("TikTok",     r"tiktok"),
    ("WhatsApp",   r"whatsapp"),
    ("Facebook",   r"facebook"),
    ("Google",     r"google"),
    ("Telegram",   r"telegram"),
    ("Twitter",    r"twitter|x\.com"),
    ("Snapchat",   r"snapchat"),
    ("Amazon",     r"amazon"),
    ("Microsoft",  r"microsoft"),
    ("Apple",      r"apple"),
    ("PayPal",     r"paypal"),
    ("Uber",       r"uber"),
    ("Netflix",    r"netflix"),
    ("Spotify",    r"spotify"),
    ("Discord",    r"discord"),
    ("LinkedIn",   r"linkedin"),
    ("Binance",    r"binance"),
    ("Bybit",      r"bybit"),
    ("OKX",        r"okx"),
    ("Coinbase",   r"coinbase"),
]

# ========== SERVICE PREMIUM EMOJI MAP ==========
# কান্ট্রি ফ্ল্যাগের মতই এখানে (ইমোজি, আইডি) বসাবেন। আইডি না থাকলে ০ দিন।
SERVICE_PREMIUM_MAP = {
    "Instagram": ("📸", 5393603871434099925),
    "TikTok":    ("🎵", 5327982530702359565),
    "WhatsApp":  ("💬", 5233354831984353090),
    "Facebook":  ("👤", 5393310276059678201),
    "Google":    ("🔍", 5321244246705989720),
    "Telegram":  ("✈️", 5364125616801073577),
    "Twitter":   ("🐦", 5393608179286297620),
    "Snapchat":  ("👻", 5330248916224983855),
    "Amazon":    ("📦", 5346056560537779652),
    "Microsoft": ("🪟", 5370857634440170316),
    "Apple":     ("🍎", 5318795767454923927),
    "PayPal":    ("💳", 5364111181415996352),
    "Uber":      ("🚗", 5393587224140859569),
    "Netflix":   ("🎬", 5366477429223209600),
    "Spotify":   ("🎶", 5233578612665375810),
    "Discord":   ("🎮", 5233582387941630314),
    "LinkedIn":  ("💼", 5321272434576355870),
    "Binance":   ("🟡", 5388622778817589921),
    "Bybit":     ("🔵", 5472387796574418157),
    "OKX":       ("⚫", 5319005477823083314),
    "Coinbase":  ("🔷", 5393583096677286721),
    "SMS":       ("📩", 5843511788863232957),
}


def get_service_emoji_tag(service_name: str) -> str:
    """সার্ভিসের জন্য premium tg-emoji ট্যাগ রিটার্ন করে।"""
    icon, emoji_id = SERVICE_PREMIUM_MAP.get(service_name, ("📱", 0))
    if emoji_id:
        return f'<tg-emoji emoji-id="{emoji_id}">{icon}</tg-emoji>'
    return icon


def detect_service(msg: str) -> str:
    """
    SMS টেক্সট থেকে সার্ভিসের নাম ডিটেক্ট করে।
    Returns: service_name  e.g. "Instagram" or "SMS"
    """
    msg_lower = msg.lower()
    for name, pattern in SERVICE_PATTERNS:
        if re.search(pattern, msg_lower):
            return name
    return "SMS"


# ========== COUNTRY ==========
def get_flag_emoji(cc: str) -> str:
    """Fallback: unicode regional indicator flag"""
    return ''.join(chr(ord(c) + 127397) for c in cc.upper()) if cc else "🌐"


def get_premium_flag(cc: str) -> str:
    """
    দেশ কোড থেকে premium custom emoji ট্যাগ রিটার্ন করে।
    যদি premium না থাকলে Unicode flag ফিরিয়ে দেয়।
    """
    cc = cc.upper()
    if cc in PREMIUM_FLAG_MAP:
        _, emoji_id = PREMIUM_FLAG_MAP[cc]
        return f'<tg-emoji emoji-id="{emoji_id}">🏳</tg-emoji>'
    return get_flag_emoji(cc)


def get_country(number):
    try:
        parsed  = phonenumbers.parse("+" + str(number), None)
        region  = phonenumbers.region_code_for_number(parsed)
        name    = geocoder.description_for_number(parsed, "en")
        return region, name
    except:
        return "UN", "Unknown"


# ========== FETCH ==========
def get_sms():
    try:
        r    = requests.get(API_URL, params={"token": API_TOKEN, "records": 100}, timeout=10)
        data = r.json()
        return data.get("data", []) if data.get("status") == "success" else []
    except:
        return []


# ========== OTP ==========
def normalize(x):
    return ''.join([str(unicodedata.digit(c)) if c.isdigit() else c for c in x])


def get_otp(msg):
    msg = str(msg)
    patterns = re.findall(
        r'[\d\u0660-\u0669\u06F0-\u06F9]{2,8}(?:[-\s._][\d\u0660-\u0669\u06F0-\u06F9]{2,8})*',
        msg
    )
    best, best_len = "", 0
    for p in patterns:
        digits = re.sub(r'[^0-9\u0660-\u0669\u06F0-\u06F9]', '', p)
        digits = normalize(digits)
        if 4 <= len(digits) <= 8 and len(digits) > best_len:
            best     = digits
            best_len = len(digits)
    return best


# ========== BUTTON EMOJI IDs ==========
# বাটনের বামে প্রিমিয়াম ইমোজি দেখানোর জন্য এখানে আইডি বসান। না থাকলে ০ দিন।
BUTTON_EMOJI_IDS = {
    "copy":6176966310920983412,    # 🔴 Copy OTP বাটনের জন্য
    "join":6131801190750491907,    # 🔵 Join Chnl বাটনের জন্য
    "bot":5355051922862653659# 🟢 Bot বাটনের জন্য
}


# ========== MASK NUMBER ==========
def mask_number(num):
    """Hide middle 4 digits with ⁕, show first part + last 4"""
    n = str(num).lstrip('+')
    if len(n) <= 4:
        return '+' + n
    elif len(n) > 8:
        return '+' + n[:len(n)-8] + '⁕⁕⁕⁕' + n[-4:]
    else:
        return '+' + n[:len(n)-4] + '⁕⁕⁕⁕'


# ========== MASKED GROUP MESSAGE ==========
def masked_text(num, cli, msg):
    """
    Masked group এর জন্য মেসেজ।
    ফরম্যাট:
      🇧🇩[premium] BD-[ServicePremiumEmoji] +880⁕⁕⁕⁕1234
    """
    region, _ = get_country(num)
    masked     = mask_number(num)

    # Premium flag emoji
    flag_tag = get_premium_flag(region)

    # সার্ভিস ডিটেক্ট → premium emoji
    service_name = detect_service(msg)
    svc_emoji    = get_service_emoji_tag(service_name)

    # cli (সার্ভিস নাম) এর জায়গায় emoji বসানো হয়েছে
    return f"{flag_tag} <b>{region}-{svc_emoji} {masked}</b>"


# ========== FULL GROUP MESSAGE ==========
def full_text(num, cli, msg, dt):
    number  = mask_number(num)
    message = str(msg).strip()

    if not message:
        return None

    otp_code     = get_otp(message)
    service_name = detect_service(message)
    svc_emoji    = get_service_emoji_tag(service_name)

    if otp_code:
        title = f"{svc_emoji} {service_name} OTP"
    else:
        title = f"{svc_emoji} {service_name} SMS"

    text = (
        f"📩 <b>{title}</b>\n"
        f"📞 {number}\n\n"
        f"🔐 OTP:\n"
        f"<code>{html.escape(otp_code) if otp_code else 'N/A'}</code>\n\n"
        f"Message:\n"
        f"<pre>{html.escape(message)}</pre>"
    )
    return text


# ========== BUTTON ==========
def build_btn(otp, full_msg):
    """
    Row 1: OTP Code Only — style: danger (লাল)
    Row 2: Join Chnl — style: primary (নীল) | Bot — style: success (সবুজ)
    """
    rows = []

    # Row 1 — Copy OTP / Copy SMS (লাল বাটন)
    if otp:
        copy_btn = {
            "text": str(otp),  # শুধু OTP কোড থাকবে, কোনো লেখা থাকবে না
            "copy_text": {"text": str(otp)},
            "style": "danger",
            "icon_custom_emoji_id": BUTTON_EMOJI_IDS["copy"]
        }
    else:
        copy_btn = {
            "text": "Full SMS",
            "copy_text": {"text": str(full_msg)},
            "style": "danger",
            "icon_custom_emoji_id": BUTTON_EMOJI_IDS["copy"]
        }
    rows.append([copy_btn])

    # Row 2 — Join Channel (নীল) | Bot (সবুজ)
    join_btn = {
        "text":  "Join Chnl",
        "url":   JOIN_CHANNEL_URL,
        "style": "primary",
        "icon_custom_emoji_id": BUTTON_EMOJI_IDS["join"]
    }
    bot_btn = {
        "text":  "Bot",
        "url":   BOT_URL,
        "style": "success",
        "icon_custom_emoji_id": BUTTON_EMOJI_IDS["bot"]
    }
    rows.append([join_btn, bot_btn])

    return {"inline_keyboard": rows}


# ========== SENT TRACKER ==========
sent = set()


# ========== SEND OLD SMS ==========
async def send_old_sms():
    """Fetch and send all old SMS that haven't been sent yet."""
    data  = get_sms()
    count = 0
    bot_ptr = 0 # রোটেশন ট্র্যাক রাখার জন্য
    for sms in data:
        sid = f"{sms['num']}|{sms['message']}|{sms['dt']}"
        if sid in sent:
            continue

        otp = get_otp(sms["message"])

        try:
            # এই এসএমএস এর জন্য বট ইনডেক্স নির্ধারণ
            current_bot_idx = bot_ptr % len(TOKENS)

            await send_styled_message(
                GROUP_MASKED,
                masked_text(sms["num"], sms["cli"], sms["message"]),
                build_btn(otp, sms["message"]),
                bot_idx=current_bot_idx
            )

            ft = full_text(sms["num"], sms["cli"], sms["message"], sms["dt"])
            if ft:
                await safe_send_full(GROUP_FULL, ft, bot_idx=current_bot_idx)

            sent.add(sid)
            count += 1
            bot_ptr += 1 # পরের এসএমএস এর জন্য বট অটো-চেঞ্জ হবে
            await asyncio.sleep(0.3)
        except Exception as e:
            print(f"Error sending old SMS: {e}")

    return count


# ========== /sendold COMMAND ==========
@dp.message(Command("sendold"))
async def cmd_sendold(message: Message):
    """Admin command to manually send all old/pending SMS."""
    await message.reply("⏳ Sending old SMS...")
    count = await send_old_sms()
    await message.reply(f"✅ Done! Sent {count} old SMS.")


# ========== MAIN LOOP ==========
async def main_loop():
    if SKIP_OLD:
        data = get_sms()
        for sms in data:
            sid = f"{sms['num']}|{sms['message']}|{sms['dt']}"
            sent.add(sid)
        print(f"⏭ Skip mode ON: {len(sent)} old SMS ignored")
    else:
        print("📨 Sending old SMS on startup...")
        count = await send_old_sms()
        print(f"✅ Sent {count} old SMS on startup")

    # 🔁 LOOP — only new SMS from here
    bot_ptr = 0 # রোটেশন ট্র্যাক
    while True:
        try:
            data = get_sms()

            for sms in data:
                sid = f"{sms['num']}|{sms['message']}|{sms['dt']}"

                if sid in sent:
                    continue

                otp = get_otp(sms["message"])
                current_bot_idx = bot_ptr % len(TOKENS)

                await send_styled_message(
                    GROUP_MASKED,
                    masked_text(sms["num"], sms["cli"], sms["message"]),
                    build_btn(otp, sms["message"]),
                    bot_idx=current_bot_idx
                )

                ft = full_text(sms["num"], sms["cli"], sms["message"], sms["dt"])
                if ft:
                    await safe_send_full(GROUP_FULL, ft, bot_idx=current_bot_idx)

                sent.add(sid)
                bot_ptr += 1 # পটার এসএমএস এর জন্য বট পরিবর্তন
                await asyncio.sleep(0.3)

            await asyncio.sleep(5)

        except Exception as e:
            print("Error:", e)
            await asyncio.sleep(5)


# ========== RUN ==========
async def main():
    await notify_admin_on_start() # এডমিনকে জানানো
    asyncio.create_task(main_loop())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
