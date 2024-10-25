from flask import Flask, request
import logging
from dotenv import load_dotenv
import telegram
import os
import asyncio  # Import asyncio for asynchronous operations

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

# Load environment variables
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telegram.Bot(token=TOKEN)

# Route to confirm the server is alive
@app.route('/')
def index():
    return "Alive"

# Route to handle webhook requests from Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json(force=True)
    logging.info(f'Incoming update: {update}')
    
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    if update.message:
        chat_id = update.message.chat_id
        text = update.message.text
        asyncio.run(send_message_async(chat_id, text))  # Run async function to send message
    
    return 'ok', 200

# Function to send a message asynchronously
async def send_message_async(chat_id, text):
    await bot.send_message(chat_id=chat_id, text=text)

def keep_alive():
    port = int(os.environ.get('PORT', 5000))  # Use the port provided by Render
    app.run(host='0.0.0.0', port=port, debug=True)  # Bind to 0.0.0.0
