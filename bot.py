import os
import sqlite3
import requests
from threading import Thread
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters

# 1. Retrieve environment variables from Render settings
BOT_TOKEN = os.environ.get('BOT_TOKEN')
SHRINKME_API = os.environ.get('SHRINKME_API')

# 2. Setup Flask web server
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

def run_web():
    # Use the PORT environment variable provided by Render, defaulting to 10000
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

# 3. URL shortener function
def shorten_url(url):
    # Use the API key retrieved from Render environment settings
    api_url = f"https://shrinkme.io/api?api={SHRINKME_API}&url={url}"
    try:
        response = requests.get(api_url)
        return response.json().get('shortenedUrl', url)
    except Exception as e:
        print(f"Error shortening URL: {e}")
        return url

# 4. Main execution
if __name__ == '__main__':
    # Start the Flask web server in a background thread
    Thread(target=run_web, daemon=True).start()
    
    # Start the Telegram bot
    print("Bot is starting...")
    app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
