import os
import sqlite3
import requests
import time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# التوكن من إعدادات البيئة
BOT_TOKEN = os.environ.get('BOT_TOKEN')

def init_db():
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)')
    conn.commit()
    conn.close()

def shorten_url(url):
    api_token = os.environ.get("SHRINKME_API")
    api_url = f"https://shrinkme.io/api?api={api_token}&url={url}"
    try:
        response = requests.get(api_url, timeout=5).json()
        return response.get('shortenedUrl', url)
    except Exception:
        return url

async def handle_message(update, context):
    url = update.message.text
    if "youtube.com" in url or "youtu.be" in url:
        short_link = shorten_url(url)
        keyboard = [[InlineKeyboardButton("📺 مشاهدة المباراة الآن", url=short_link)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "⚽ **أهلاً بك في خدمة البث المباشر**\n\n"
            "جاري تجهيز البث...\n"
            "⚠️ **ملاحظة:** قد تظهر لك صفحة إعلانية، يرجى تجاوزها للوصول إلى البث مباشرة.\n\n"
            "اضغط على الزر بالأسفل:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("يرجى إرسال رابط يوتيوب صحيح للمباراة.")

if __name__ == '__main__':
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
