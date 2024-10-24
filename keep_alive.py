from flask import Flask, request
from threading import Thread
from dotenv import load_dotenv
import telegram
import os
import asyncio

# Initialize the Flask app
app = Flask(__name__)

# Your bot's token (ensure you store this securely, such as in an environment variable)
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telegram.Bot(token=TOKEN)

# Route to confirm the server is alive
@app.route('/')
def index():
    return "Alive"

# Asynchronous function to send a message
async def send_message_async(chat_id, text):
    await bot.send_message(chat_id=chat_id, text=f"You said: {text}")

# Synchronous function to handle the webhook requests and run async operations
@app.route('/webhook', methods=['POST'])
def webhook():
    # Process the incoming update from Telegram
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    # Example: handle a message (you can expand this to handle more updates)
    if update.message:
        chat_id = update.message.chat_id
        text = update.message.text

        # Run the async function within the synchronous context
        asyncio.run(send_message_async(chat_id, text))

    return 'ok', 200

# Function to start the Flask server
def run():
    app.run(host='0.0.0.0', port=8080)

# Function to start the Flask server in a separate thread
def keep_alive():
    t = Thread(target=run)
    t.start()
