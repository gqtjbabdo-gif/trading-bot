import sqlite3
import yt_dlp
import os
BOT_TOKEN = os.environ.get('BOT_TOKEN')
import requests
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# 1. Initialize the database
def init_db():
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY)')
    conn.commit()
    conn.close()

# 2. ShrinkMe API Function
def shorten_url(url):
    api_token = os.environ.get("SHRINKME_API")
    api_url = f"https://shrinkme.io/api?api={api_token}&url={url}"
    api_token = os.environ.get("SHRINKME_API")
    try:
        response = requests.get(api_url).json()
        return response.get('shortenedUrl', url)
    except Exception:
        return url

# 3. Download Function
def download_video(url):
    ydl_opts = {'format': 'best', 'outtmpl': 'video.mp4'}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return 'video.mp4'

# 4. Message Handler
async def handle_message(update, context):
    url = update.message.text
    if url.startswith("http"):
        await update.message.reply_text("جاري تجهيز الرابط الخاص بك...")
        short_link = shorten_url(url)
        await update.message.reply_text(f"اضغط هنا للتحميل:\n{short_link}")
        
        await update.message.reply_text("جاري تحميل الفيديو، انتظر قليلاً...")
        try:
            file_path = download_video(url)
            await update.message.reply_video(video=open(file_path, 'rb'))
            os.remove(file_path)
        except Exception:
            await update.message.reply_text("حدث خطأ أثناء تحميل الفيديو، حاول مجدداً.")
    else:
        await update.message.reply_text("يرجى إرسال رابط فيديو صحيح (يبدأ بـ http).")

# 5. Run the Bot
if __name__ == '__main__':
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("أرسل لي رابط الفيديو وسأقوم باختصاره وتحميله لك!")))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
