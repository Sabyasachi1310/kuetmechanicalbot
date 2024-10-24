from flask import Flask, request
from threading import Thread
from dotenv import load_dotenv
import telegram
import os

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
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    # Log incoming updates
    if update.message:
        chat_id = update.message.chat_id
        text = update.message.text
        print(f"Received message: {text}")  # Debug log
        bot.send_message(chat_id=chat_id, text=f"You said: {text}")

    return 'ok', 200

# Function to start the Flask server
def run():
    app.run(host='0.0.0.0', port=8080)

# Function to start the Flask server in a separate thread
def keep_alive():
    t = Thread(target=run)
    t.start()
