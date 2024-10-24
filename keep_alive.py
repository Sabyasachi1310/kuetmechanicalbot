from flask import Flask, request
from threading import Thread
import logging
from dotenv import load_dotenv
import telegram
import os

logging.basicConfig(level=logging.INFO)
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

# Route to handle webhook requests from Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json(force=True)
    logging.info(f'Incoming update: {update}')
    
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    # Incorrect indentation here
    if update.message:
        chat_id = update.message.chat_id
        text = update.message.text
        asyncio.run(send_message_async(chat_id, text))
    
    return 'ok', 200

# Function to start the Flask server
def run():
    app.run(host='0.0.0.0', port=8080)

# Function to start the Flask server in a separate thread
def keep_alive():
    t = Thread(target=run)
    t.start()
