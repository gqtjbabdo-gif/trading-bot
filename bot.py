import os
import sqlite3
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters
from flask import Flask
from threading import Thread

# إعداد Flask لفتح بورت وهمي
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# --- كود البوت الأصلي كما هو ---
BOT_TOKEN = os.environ.get('BOT_TOKEN')

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
            "اضغط على الزر بالأسفل:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

if __name__ == '__main__':
    # تشغيل الويب في خلفية (Thread)
    Thread(target=run_web).start()
    
    # تشغيل البوت
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app_bot.run_polling()
