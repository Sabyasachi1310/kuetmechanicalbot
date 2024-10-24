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
    
    update = telegram.Update.de_json(update, bot)

    # Log incoming updates
     if update.message:
        chat_id = update.message.chat.id
        text = update.message.text
        logging.info(f'Message from {chat_id}: {text}')
        
        # Send a response asynchronously
        thread = Thread(target=send_message, args=(chat_id, text))
        thread.start()

    return 'ok', 200

# Function to start the Flask server
def run():
    app.run(host='0.0.0.0', port=8080)

# Function to start the Flask server in a separate thread
def keep_alive():
    t = Thread(target=run)
    t.start()
