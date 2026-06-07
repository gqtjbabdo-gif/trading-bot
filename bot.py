import os
import requests
from threading import Thread
from flask import Flask
from telegram.ext import ApplicationBuilder

# Setup configuration
BOT_TOKEN = os.environ.get('BOT_TOKEN')
SHRINKME_API = os.environ.get('SHRINKME_API')

# Flask app for Render health check
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

def run_web():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    # 1. Start Flask in a background thread
    Thread(target=run_web, daemon=True).start()
    
    # 2. Start the Telegram Bot
    print("Bot is starting...")
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Start polling
    app_bot.run_polling()
