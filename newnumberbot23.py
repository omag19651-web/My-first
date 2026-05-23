import asyncio
import logging
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message
from google import genai
from google.genai import types

# ━━━━━━━━━━━━ কনফিগারেশন ━━━━━━━━━━━━
BOT_TOKEN = "8706371463:AAHBp3UxQ0RQOZbsb0LU0P7SRe241vcXuaE"
GEMINI_API_KEY = "AIzaSyAKpsVf73Q7dMEIadLFzGVbyqhEIDCt-w4"  # আপনার জেমিনি এপিআই কি এখানে বসান
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()
ai_client = genai.Client(api_key=GEMINI_API_KEY)

# মেসেজ অটো-ডিলিট করার ব্যাকগ্রাউন্ড টাস্ক
async def delete_message_after_delay(chat_id: int, message_id: int, delay: int = 180):
    await asyncio.sleep(delay)
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
        print(f"Successfully deleted message {message_id} after {delay} seconds.")
    except Exception as e:
        logging.error(f"Failed to delete message: {e}")

@dp.business_message()
async def ai_business_auto_reply(message: Message):
    if not message.text:
        return

    user_message = message.text
    # ইউজারের অফিশিয়াল টেলিগ্রাম প্রোফাইল নেম (সেভ করা নাম নয়)
    telegram_profile_name = message.from_user.full_name 

    try:
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=(
                    f"তুমি একজন অত্যন্ত প্রফেশনাল এবং ফ্রেন্ডলি এআই অ্যাসিস্ট্যান্ট। "
                    f"তুমি 'আশিক আহমেদ'-এর হয়ে তার টেলিগ্রাম বিজনেস চ্যাটে উত্তর দিচ্ছ। "
                    f"ইউজারের প্রোফাইল নাম: {telegram_profile_name}। "
                    f"⚠️ অত্যন্ত গুরুত্বপূর্ণ নিয়ম: উত্তর অবশ্যই খুব সংক্ষিপ্ত (সর্বোচ্চ ২-৩ লাইন) হতে হবে। "
                    f"কোনো অতিরিক্ত কথা না বাড়িয়ে সরাসরি টু-দ্য-পয়েন্ট উত্তর দেবে। "
                    f"মেসেজে সুন্দর সুন্দর প্রিমিয়াম ইমোজি (💎, ✨, ⚡) ব্যবহার করবে এবং বাংলায় কথা বলবে।"
                )
            )
        )
        
        ai_reply = response.text
        
        footer_buttons = (
            f"\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📢 <a href='https://t.me/redoxsms'>🔔 জয়েন করুন redoxsms চ্যানেল</a>\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        
        final_message = f"{ai_reply}{footer_buttons}"
        
        # স্বয়ংক্রিয় রিপ্লাই পাঠানো
        sent_msg = await message.reply(final_message, link_preview_options={"is_disabled": True})
        
        # ৩ মিনিট (১৮০ সেকেন্ড) পর বটের রিপ্লাইটি ডিলিট করার টাস্ক চালু করা
        asyncio.create_task(delete_message_after_delay(chat_id=sent_msg.chat.id, message_id=sent_msg.message_id, delay=180))

    except Exception as e:
        logging.error(f"Gemini API Error: {e}")
        backup_message = (
            f"✨ <b>হ্যালো {html.bold(telegram_profile_name)}!</b>\n"
            f"আমি বর্তমানে কিছুটা ব্যস্ত আছি, দ্রুতই নক দিচ্ছি! 💎\n"
            f"📢 <a href='https://t.me/redoxsms'>redoxsms</a>"
        )
        sent_backup = await message.reply(backup_message, link_preview_options={"is_disabled": True})
        # ব্যাকআপ মেসেজটিও ৩ মিনিট পর ডিলিট হবে
        asyncio.create_task(delete_message_after_delay(chat_id=sent_backup.chat.id, message_id=sent_backup.message_id, delay=180))

async def main():
    print("💎 Short Answers & Auto-Delete Bot is running successfully... 🚀")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
