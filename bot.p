import os
import logging
from threading import Thread
from flask import Flask
from telegram.ext import ApplicationBuilder, MessageHandler, filters

# Setup logging to monitor the bot's status in the Render logs
logging.basicConfig(level=logging.INFO)

# Retrieve the bot token from Render's Environment Variables
# Ensure you have set 'BOT_TOKEN' in the Render dashboard settings
BOT_TOKEN = os.getenv('BOT_TOKEN')

# 1. Flask Web Server setup (to keep the Render service alive)
app = Flask(__name__)

@app.route('/')
def home():
    return "The bot is running successfully, Abdo!"

def run_web():
    app.run(host='0.0.0.0', port=10000)

# 2. Bot logic setup
async def handle_message(update, context):
    url = update.message.text
    # Add your custom link shortening or management logic here
    await update.message.reply_text(f"Link received: {url}")

if __name__ == '__main__':
    # Start the Flask web server in a background thread
    t = Thread(target=run_web)
    t.start()
    
    # Start the Telegram bot
    print("Bot is starting...")
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app_bot.run_polling()
