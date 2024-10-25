from telegram.request import HTTPXRequest
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import telegram
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters
import pandas as pd
import os
from dotenv import load_dotenv
from keep_alive import keep_alive

import logging
from flask import Flask, request

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.json
    logging.info(f"Received update: {update}")  # Log the incoming update
    handle_update(update)  # Call your function to handle the update
    return '', 200

def handle_update(update):
    # Your bot logic here
    pass



load_dotenv()
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telegram.Bot(token=BOT_TOKEN)
request = HTTPXRequest(connect_timeout=100, read_timeout=100)

WEBHOOK_URL = 'https://api.render.com/deploy/srv-csckbl2j1k6c739c4mo0?key=UBwowdNvJVw'
async def set_webhook():
    await bot.set_webhook(url=WEBHOOK_URL)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome to the KUET Mechanical Bot!\n\n"
        "Use the following commands to get course materials:\n"
        "/ch1105 - CH-1105 Environmental Chemistry\n"
        "/ch1106 - CH-1106 Engineering Chemistry\n"
        "/math1105 - MATH-1105 Mathematics\n"
        "/me1105 - ME-1105 Thermal Engineering\n"
        "/me1106 - ME-1106 Sessional- Thermal Engineering\n"
        "/me1107 - ME-1107 Manufacturing Process\n"
        "/me1108 - ME-1108 Sessional- Manufacturing Process\n"
        "/mes1102 - MES-1102 Sessional- Work Shop Practice\n"
        "/qb - Question Bank\n"
        "/hum1105 - HUM-1105 English\n"
        "/syllabus - Syllabus(Full)\n"
        "/batch22info - Information about the students of KUET ME'22\n"
    )

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Use the following commands to get course materials:\n"
        "/ch1105 - CH-1105 Environmental Chemistry\n"
        "/ch1106 - CH-1106 Engineering Chemistry\n"
        "/math1105 - MATH-1105 Mathematics\n"
        "/me1105 - ME-1105 Thermal Engineering\n"
        "/me1106 - ME-1106 Sessional- Thermal Engineering\n"
        "/me1107 - ME-1107 Manufacturing Process\n"
        "/me1108 - ME-1108 Sessional- Manufacturing Process\n"
        "/mes1102 - MES-1102 Sessional- Work Shop Practice\n"
        "/qb - Question Bank\n"
        "/hum1105 - HUM-1105 English\n"
        "/syllabus - Syllabus(Full)\n"
        "/batch22info - Information about the students of KUET ME'22\n"
    )

async def syllabus_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    file_id = 'BQACAgUAAxkBAAIFF2cYqG15zPCtFt4ChEMgtr38sg-rAAKjDgAC1-nIVAgJIkN5wvHbNgQ'
    chat_id = update.message.chat_id  
    await context.bot.send_message(chat_id=chat_id, text="Syllabus is Here!")
    await context.bot.send_document(chat_id=chat_id, document=file_id)

#BATCH 22 DATA
import pandas as pd
import pdfplumber

local_pdf_path = 'ME-KUET-22.pdf'

# Step 1: Read the PDF using pdfplumber
dfs = []  # List to store dataframes for each page's table
with pdfplumber.open(local_pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        
        if text:  # Ensure page has text
            lines = text.split("\n")
            # Split each line into columns
            data = [line.split() for line in lines if line.strip()]  # Customize split logic based on actual format
            df = pd.DataFrame(data)
            
            # Append only DataFrames with expected number of columns (6 here)
            if df.shape[1] == 6:  
                df.columns = ['Roll', 'Name', 'Blood type', 'Hometown', 'Phone No.', 'Hall']
                dfs.append(df)

# Step 3: Combine the DataFrames into one if any were found
if dfs:
    combined_df = pd.concat(dfs, axis=0, ignore_index=True)
    
    # Step 4: Clean the 'Phone No.' column
    combined_df['Phone No.'] = combined_df['Phone No.'].replace({pd.NA: 0, '': 0})
    combined_df['Phone No.'] = combined_df['Phone No.'].astype(str)
    combined_df['Phone No.'] = combined_df['Phone No.'].str.replace(r'\.0$', '', regex=True)
    combined_df['Phone No.'] = combined_df['Phone No.'].str.replace(r'^88', '', regex=True)
    combined_df = combined_df[combined_df['Phone No.'] != '']
    combined_df['Phone No.'] = combined_df['Phone No.'].astype(int, errors='ignore')
    
else:
    print("No tables with the expected structure were found in the PDF.")

# Define states for the conversation
ROLL_NUMBER, = range(1)

async def batch22info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Prompt the user for their roll number."""
    await update.message.reply_text("Please provide your Roll Number:")
    return ROLL_NUMBER  # Move to the next state

async def receive_roll_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive the roll number and search for student information."""
    roll_number = update.message.text
    result = await search_student_by_roll(roll_number)
    await update.message.reply_text(result)
    return ConversationHandler.END  # End the conversation

async def search_student_by_roll(roll_number: str) -> str:
    """Search for the student in the DataFrame by roll number."""
    try:
        roll_number = str(roll_number)  # Ensure roll number is a string
        student_info = combined_df[combined_df['Roll'] == roll_number]

        if not student_info.empty:
            name = student_info['Name'].values[0]
            roll = student_info['Roll'].values[0]
            hall = student_info['Hall'].values[0]
            phone = student_info['Phone No.'].values[0]
            
            return f"""
Name: {name} 
Roll: {roll} 
Hall: {hall}
Phone Number: {0}{phone}
"""
        else:
            return f"Student with Roll number {roll_number} not found."

    except Exception as e:
        return f"An error occurred: {str(e)}"
# Define paths to the PDF files for each button
file_ids_ch1105 = {
    'assignment': [
        'BQACAgUAAxkDAAIC6WcX5O5ZqItCTALhbvwQHIW8xNkcAAKrEgACTSbBVIQx922nkl8iNgQ',
        'BQACAgUAAxkDAAIC6mcX5PSxqmj1jAOr9ykPA5khs4lwAAKsEgACTSbBVEVI7lasu8m7NgQ',
        'BQACAgUAAxkDAAIC62cX5PrM6gnD-VoqOX4-TfLz3QyAAAKtEgACTSbBVK62tg3MGMHmNgQ'
    ],
    'books': [
        'BQACAgUAAxkBAAIC-2cX57g-qi1xGEa3maSRGKvyM1azAAK-EgACTSbBVAQc6FqU3cC2NgQ',
        'BQACAgUAAxkDAAIC7GcX5TigNbQhpWXR6lvR45rjFr4uAAKuEgACTSbBVDGUQfjqt5fUNgQ',
        'BQACAgUAAxkBAAIC_GcX6Cdde8Opj3e9W7pvCDW6P9eeAALDEgACTSbBVMygnHxcMVYNNgQ'
    ],
    'chotha': [
        'BQACAgUAAxkDAAIC7WcX5V1O5V9LAoUWc6M9yjipm8iYAAKvEgACTSbBVHs9L3jQFikcNgQ',
        'BQACAgUAAxkDAAIC7mcX5WAYN5ZUQ9MY7corFHOHjvkUAAKwEgACTSbBVMgzRy_z1inRNgQ'
    ],
    'ct-questions': [
        'BQACAgUAAxkDAAIC72cX5WMIvyBTds9Ng0vDCkUeFbp4AAKxEgACTSbBVMKVwENOq0XnNgQ'
    ],
    'Files By Motin Sir': [
        'BQACAgUAAxkDAAIC8GcX5X0GFYILcYuUqweMfVc8b3rdAAKyEgACTSbBVJidpQABKrJ5GTYE',
        'BQACAgUAAxkBAAIC_WcX6SQAASK9cGVX20nHbuOR3xkzXgACxhIAAk0mwVSGIwcJxYs4kjYE',
        'BQACAgUAAxkDAAIC8WcX5aPXeQABtKuPRZ7onm5E-QK79AACsxIAAk0mwVRlZroJ_VxwbDYE',
        'BQACAgUAAxkDAAIC8mcX5adw3D1TlcKSxvzf2kpPS876AAK0EgACTSbBVAwidP2SJhLSNgQ',
        'BQACAgUAAxkDAAIC82cX5beXlXqZWg5gojODWOnCInHBAAK1EgACTSbBVPN0o_Vl3bQWNgQ',
        'BQACAgUAAxkDAAIC9GcX5cNJyeFs9rhtJdBX9HWnCuknAAK2EgACTSbBVDyj3W9E2H9MNgQ',
        'BQACAgUAAxkDAAIC9WcX5cYeo4yi7sN76d1a1kINnfrfAAK3EgACTSbBVEeJNnN3Hz6aNgQ'
    ],
    'Files By Sadik Sir': [
        'BQACAgUAAxkDAAIC9mcX5cm7VIin2QXj6mOWINY_xoZ1AAK4EgACTSbBVCMW5z0ybU6PNgQ',
        'BQACAgUAAxkDAAIC92cX5dBaax-oyrhdnebT4u9OtCWGAAK5EgACTSbBVDQnvHo9qVQONgQ',
        'BQACAgUAAxkDAAIC-GcX5dpbwaI5fYo5f4rsNlWZXSqEAAK6EgACTSbBVCOfwwbxSQFrNgQ',
        'BQACAgUAAxkDAAIC-WcX5eESfrlo9NkRcE3neVoC7WbFAAK7EgACTSbBVNnHQJCQcUXUNgQ'
    ],
    'syllabus': [
        'BQACAgUAAxkDAAIC-mcX5eSA_vUykAJA9GzbvlqIBIjgAAK8EgACTSbBVMzvdNZoEMNBNgQ'
    ]
}

async def ch1105_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Create an inline keyboard with buttons
    keyboard = [
        [InlineKeyboardButton("Assignment", callback_data='ch1105_assignment')],
        [InlineKeyboardButton("Chotha", callback_data='ch1105_chotha')],
        [InlineKeyboardButton("CT questions", callback_data='ch1105_ct-questions')],
        [InlineKeyboardButton("Files by Motin Sir", callback_data='ch1105_Files By Motin Sir')],
        [InlineKeyboardButton("Files by Sadik Sir", callback_data='ch1105_Files By Sadik Sir')],
        [InlineKeyboardButton("Syllabus", callback_data='ch1105_syllabus')],
        [InlineKeyboardButton("Books", callback_data='ch1105_books')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send the message with buttons
    await update.message.reply_text("CH-1105 Environmental Chemistry", reply_markup=reply_markup)   

async def button_callback_ch1105(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data.split('_')[1]
    
    command_name = query.data.split('_')[0]  # This will extract 'math1105'
    button_name = query.data.split('_')[1]   # This will extract the specific section like 'chotha', 'ct-questions', etc.

    course_title = f"{command_name.upper()} {button_name.replace('-', ' ').capitalize()} files are HERE!"
    
    if data in file_ids_ch1105:
        await context.bot.send_message(chat_id=query.message.chat_id, text=course_title)

        for file_id in file_ids_ch1105[data]:
            await context.bot.send_document(chat_id=query.message.chat_id, document=file_id)
    else:
        await context.bot.send_message(chat_id=query.message.chat_id, text="No files available.")
    await context.bot.send_message(chat_id=query.message.chat_id, text="All files have been uploaded. Completed!")



file_ids_ch1106 = {
    "lab-report": [
        "BQACAgUAAxkDAAIDDGcX8N-ihkPZN5PMOzOB2PMdIbyrAALKEgACTSbBVD63alRUr4XbNgQ",
        "BQACAgUAAxkDAAIDDWcX8ORtwwSzBtSTucV0k5CVCamXAALLEgACTSbBVKbsg2yqnoJQNgQ",
        "BQACAgUAAxkDAAIDDmcX8OsXy5H9u_CkODv4wRlGNNOkAALMEgACTSbBVJ4n-zuhnh-QNgQ",
        "BQACAgUAAxkDAAIDD2cX8PI55M0o4IaxOJ8JTnnEDnnmAALNEgACTSbBVJPlrQ1B256jNgQ",
        "BQACAgUAAxkDAAIDEGcX8PvdLe5ysH4ctjQZz3nPQinJAALOEgACTSbBVNzFlZsd7FM_NgQ"
    ],
    "quiz": [
        "BQACAgUAAxkDAAIDEWcX8P8wffV7L-Nlv2jgZcXq5CUPAALPEgACTSbBVKb3K-OOyklDNgQ",
        "BQACAgUAAxkDAAIDEmcX8QJwTOd6zkgsWY6RyJ2SgaGtAALQEgACTSbBVGMppB2GcO_MNgQ",
        "BQACAgUAAxkDAAIDE2cX8QTrhoCJY4Hnd9TYvxmF8FCZAALREgACTSbBVHwowhMruLc_NgQ"
    ],
    "lab-manuals": [
        "BQACAgUAAxkDAAIDFGcX8Rp9xCf07Lmup7kFM_0COc-jAALSEgACTSbBVLiJ69vLXofZNgQ"
    ]
}

async def ch1106_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Create an inline keyboard with buttons
    keyboard = [
        [InlineKeyboardButton("Lab Report", callback_data='ch1106_lab-report')],
        [InlineKeyboardButton("Quiz", callback_data='ch1106_quiz')],
        [InlineKeyboardButton("Lab Manuals", callback_data='ch1106_lab-manuals')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Send the message with buttons
    await update.message.reply_text("CH1106 Engineering Chemistry", reply_markup=reply_markup)

# Function to handle button callbacks for CH1106
async def button_callback_ch1106(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data.split('_')[1]  # Extract the second part of the callback_data

    command_name = query.data.split('_')[0]  # This will extract 'math1105'
    button_name = query.data.split('_')[1]   # This will extract the specific section like 'chotha', 'ct-questions', etc.

    course_title = f"{command_name.upper()} {button_name.replace('-', ' ').capitalize()} files are HERE!"

    if data in file_ids_ch1106:
        await context.bot.send_message(chat_id=query.message.chat_id, text=course_title)

        for file_id in file_ids_ch1106[data]:
            await context.bot.send_document(chat_id=query.message.chat_id, document=file_id)
    else:
        await context.bot.send_message(chat_id=query.message.chat_id, text="No files available.")
    await context.bot.send_message(chat_id=query.message.chat_id, text="All files have been uploaded. Completed!")

file_ids_math1105 = {
    'chotha' : [
        'BQACAgUAAxkBAAIDMGcYAAHsAAE9pRwep0yPMZ8vY-MOE34AAowUAALX6cBUS2NUjM0OUcA2BA',
        'BQACAgUAAxkBAAIDMWcYAomenXEoWPKq-Fe-r0nJmJ7PAAKOFAAC1-nAVPHvSwYJCuLfNgQ',
        'BQACAgUAAxkBAAIDMmcYA7OjWqv45IsvJ91-kk4BnesCAAKQFAAC1-nAVOlU658YOdPjNgQ',
        'BQACAgUAAxkBAAIDM2cYBC3xV5y4dckONQy0WITnDZgZAAKRFAAC1-nAVAIyMxWC8WP5NgQ',
        'BQACAgUAAxkDAAIDIWcX9XWxF9atrSmZtcWfk1ihjHQKAALXEgACTSbBVPGB_1Pcc2kNNgQ',
        'BQACAgUAAxkDAAIDImcX9XcTjNaq1viGRTnliQ-zCzWmAALYEgACTSbBVG4YbmkWFWMlNgQ',
        'BQACAgUAAxkDAAIDI2cX9XmVxJpZ2IXUwP2-wo7T8pK-AALZEgACTSbBVL9VWzHlqR13NgQ',
        'BQACAgUAAxkDAAIDJGcX9XtGrm5i5gEGPAGhvpTvRHn5AALaEgACTSbBVLdAb_qOUB8oNgQ',
        'BQACAgUAAxkBAAIDNGcYBInoP4or5ZeceKGB2Wo7bv5OAAKTFAAC1-nAVO9BF8ki-39fNgQ'
        ],
    'ct-questions': [
        'BQACAgUAAxkDAAIDJWcX9X2Gj2Fr1HC5GPTIZ4YBpi_QAALbEgACTSbBVLHr261hKWTRNgQ'
    ],
    'sec A': [
        'BQACAgUAAxkBAAIDNWcYDaD_KgQtlHDFw-va4yaeEIaDAAKYFAAC1-nAVKnIITCd9RYXNgQ',
        'BQACAgUAAxkBAAIDNmcYDaODJuyDYHK8tcfvJLi94EggAAKZFAAC1-nAVI3n860cxnbSNgQ',
        'BQACAgUAAxkDAAIDJmcX9YAntCVwK1ad8axm-DnM9AroAALcEgACTSbBVAVl9qZhCKreNgQ',
        'BQACAgUAAxkDAAIDJ2cX9YM0f8MHyJsovdsObUqFtTekAALdEgACTSbBVOeLEzkm4kaWNgQ',
        'BQACAgUAAxkDAAIDKGcX9YWCRoGk2dzzERBITF33oJPsAALeEgACTSbBVJm6lGNCgTsMNgQ',
        'BQACAgUAAxkDAAIDKWcX9YfcjXrTLXXnRglbVHzPk6I4AALfEgACTSbBVHvm03tCXUZDNgQ',
        'BQACAgUAAxkBAAIDN2cYDg4m27blrvJvI05dF0KQ993jAAKaFAAC1-nAVFRG256GUCk5NgQ',
        'BQACAgUAAxkDAAIDKmcX9YjVlZhFEuYorpcvbLavpuG4AALgEgACTSbBVGF8Hv75qAqbNgQ',
        'BQACAgUAAxkDAAIDK2cX9Yr6T1V7vZ1mT2OSoQ7DcdoIAALhEgACTSbBVCqmf09OjzCDNgQ',
        'BQACAgUAAxkBAAIDOGcYD4NY17CLqT3Tq5mW30Bf0vZfAAKcFAAC1-nAVNGlfYQ4IfrxNgQ',
        'BQACAgUAAxkBAAIDOWcYD6vezt-7Z0kk0UdpAAFqc4PmnAACnRQAAtfpwFTj74rV32JhejYE',
        'BQACAgUAAxkDAAIDLGcX9Y1BgRQymrxnxCM6mL3JaeZ1AALiEgACTSbBVHWHuDxpgI2WNgQ',
        'BQACAgUAAxkBAAIDOmcYD9MzRde2HF9PC0Jt5mA-3XcjAAKeFAAC1-nAVHVi1to0MagHNgQ',
        'BQACAgUAAxkDAAIDLWcX9ZCE4K4bBqhLT3rjcNzdb5ICAALjEgACTSbBVA4PfXaPhQnWNgQ',
        'BQACAgUAAxkDAAIDLmcX9ZcZKaAVBzOsqLN8fC0M26IIAALkEgACTSbBVN0ojzo6iceLNgQ',
        'BQACAgUAAxkBAAIDhmcYExXG2_rMDRdfqSpNj4Nw58oHAAKkFAAC1-nAVGfdvJzGvdC_NgQ'
    ],
    'sec B': [
        'BQACAgUAAxkDAAIDL2cX9ZlVfsQ9Sbutpmi5788Cr2lqAALlEgACTSbBVBK9WsQvrE_fNgQ'
    ],
    'books': ['BQACAgUAAxkDAAIEr2cYMOCXpaIM_VVu3Y5-csleQWorAAI7FQAC1-nAVDBwtY-8cr7QNgQ', 
              'BQACAgUAAxkDAAIEsGcYMQ8GYgh9N9kgdCl1gH6BS0CsAAI8FQAC1-nAVL3VCfSiAAEUbDYE', 
              'BQACAgUAAxkDAAIEsWcYMVFXPhDfV0FvnEXUYo5z3cWNAAI9FQAC1-nAVEp94seovQYVNgQ',
              'BQACAgUAAxkBAAIEsmcYMhwQl90SpJmhZXlqKibmMj-6AAI-FQAC1-nAVD4IyGtDQO2GNgQ',
              'BQACAgUAAxkBAAIEs2cYMu2D9uw4TsAvZIulKSuwaFLqAAI_FQAC1-nAVIgQBbnHHA4kNgQ',
              'BQACAgUAAxkBAAIEtGcYnLWkGCXAwV41xxCHhT5895yTAAJ9DgAC1-nIVLRZFGsCzSzoNgQ',
              'BQACAgUAAxkBAAIEtWcYnNSODZcodnnbfBtkLGG8_2XpAAJ_DgAC1-nIVIpRIAABIMAjTzYE',
              'BQACAgUAAxkBAAIEtmcYnPf65FwWQ_wXAAGJyifLcsYROAACgA4AAtfpyFSKzMeIjLcR5zYE',
              'BQACAgUAAxkBAAIEt2cYnR9-M5EN1cW4CbcsoPXl_kxXAAKBDgAC1-nIVETAeYRA5D7ENgQ',
              'BQACAgUAAxkBAAIEuGcYnUf4KJ5ZwhbfssB6A59YTPshAAKCDgAC1-nIVN1l70ZECk5ZNgQ',
              'BQACAgUAAxkBAAIEuWcYnaiJKQ4bYCsQSfSKitegTSV_AAKEDgAC1-nIVBccAAEBU-wT1DYE'
              ]
}

async def math1105_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Create an inline keyboard with buttons
    keyboard = [
        [InlineKeyboardButton("Chotha", callback_data='math1105_chotha')],
        [InlineKeyboardButton("CT questions", callback_data='math1105_ct-questions')],
        [InlineKeyboardButton("Integral Calculus by Azmol Huda", callback_data='math1105_sec A')],
        [InlineKeyboardButton("Differential Calculus by Hasanuzzaman", callback_data='math1105_sec B')],
        [InlineKeyboardButton("Books", callback_data='math1105_books')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send the message with buttons
    await update.message.reply_text("MATH-1105 MATHEMATICS", reply_markup=reply_markup)

async def button_callback_math1105(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data.split('_')[1]

    command_name = query.data.split('_')[0] 
    button_name = query.data.split('_')[1]  
    course_title = f"{command_name.upper()} {button_name.replace('-', ' ').capitalize()} files are HERE!"
    
    
    if data in file_ids_math1105:
        await context.bot.send_message(chat_id=query.message.chat_id, text=course_title)
        for file_id in file_ids_math1105[data]:
            await context.bot.send_document(chat_id=query.message.chat_id, document=file_id)
    else:
        await context.bot.send_message(chat_id=query.message.chat_id, text="No files available.")
    await context.bot.send_message(chat_id=query.message.chat_id, text="All files have been uploaded. Completed!")


file_ids_me1105 = {
    'others': [
        'BQACAgUAAxkDAAICZWcX3XgODVmhnNauLHMUgfq1jVqtAAJuEgACTSbBVGM2cXNzvffCNgQ',
        'BQACAgUAAxkDAAICZmcX3XsUky0Tfqubs87bf_Sgg61SAAJvEgACTSbBVI9xcd3PLXwENgQ',
        'BQACAgUAAxkDAAICZ2cX3YDXc8OnMPWhoo6OQ9eCOykJAAJwEgACTSbBVEC39z4GVeceNgQ',
        'BQACAgUAAxkDAAICaGcX3YIBa54ErnFOip1yLhjsgyqmAAJxEgACTSbBVJtrQx7ILDwONgQ',
        'BQACAgUAAxkDAAICaWcX3YZ72HIhXhnSdbvsiY8WFL1YAAJyEgACTSbBVE1D05TytIIeNgQ',
        'BQACAgUAAxkDAAICamcX3ZWVMRxQLm-qxS50PbuAcGMEAAJzEgACTSbBVKzdKXIczEwkNgQ'
    ],
    'assignment': [
        'BQACAgUAAxkDAAICa2cX3ZdhLxoNwuPgB9qhA9T5zT2aAAJ0EgACTSbBVODgRaXNUZ1ZNgQ'
    ],
    'chotha': [
        'BQACAgUAAxkDAAICbGcX3Z6YCDUmUPItBUBTs7mywIcuAAJ1EgACTSbBVNLlMbvwkpxYNgQ',
        'BQACAgUAAxkDAAICbWcX3aLXuGmVLHbAFRG56f1uwIiMAAJ2EgACTSbBVM7moUCG6UyyNgQ',
        'BQACAgUAAxkDAAICbmcX3aQCl6U4utFgWzhEViT7QWbEAAJ3EgACTSbBVK8nG34M9BwKNgQ',
        'BQACAgUAAxkDAAICb2cX3afpJsGs968OXEYrpI1JIGT2AAJ4EgACTSbBVCP74mCJy17gNgQ',
        'BQACAgUAAxkDAAICcGcX3a7SuN9xgIH-mLRuOuNIpc2QAAJ5EgACTSbBVJyLoLwbaWwyNgQ'
    ],
    'CT questions': [
        'BQACAgUAAxkDAAICcWcX3bNSGRk1YY-3UMF-6Ntk-7YJAAJ6EgACTSbBVAABy6_ckNG8oDYE'
    ],
    'Sobhan Sir': [
        'BQACAgUAAxkDAAICcmcX3bUmm5iaUWrzmjTI0ID9O8SRAAJ7EgACTSbBVPAvbxuZPJTANgQ',
        'BQACAgUAAxkDAAICc2cX3bh3_Bx1vgJGPX8nyGEQn9ArAAJ8EgACTSbBVB7sGujjQNwoNgQ',
        'BQACAgUAAxkDAAICdGcX3bpbhgABG_1lZaxqPOGLzdbRAQACfRIAAk0mwVRwHA8PaQv_9zYE',
        'BQACAgUAAxkDAAICdWcX3bzrud071QHObwlkBfEyaJ_sAAJ-EgACTSbBVPc6gBohcIX4NgQ',
        'BQACAgUAAxkDAAICdmcX3cAnmZ-sKgjTaDcQX0HsJ_laAAJ_EgACTSbBVJ4u_YGFE91QNgQ',
        'BQACAgUAAxkDAAICd2cX3cbFadbHLZAErmfr7xhT-5I2AAKAEgACTSbBVMEf7bQF63umNgQ',
        'BQACAgUAAxkDAAICeGcX3cvePwyiYk4k3ZSVNxc3Qou4AAKBEgACTSbBVOUYMl8ZqptbNgQ'
    ],
    'Sultan Sir': [
        'BQACAgUAAxkDAAICeWcX3c48bhtlSwy3s4Wk0ZdhsV9VAAKCEgACTSbBVIa4r5VSv6aCNgQ',
        'BQACAgUAAxkDAAICemcX3dAU3TZyf4Tu9kts9OePLUnUAAKDEgACTSbBVL-iq6A1hhxYNgQ',
        'BQACAgUAAxkDAAICe2cX3dNeLkXJNNb_-xGHgmY0I_XNAAKEEgACTSbBVD_Kz28EzubXNgQ',
        'BQACAgUAAxkDAAICfGcX3dYaOlAaV3R4Pm2CFYOWJWTCAAKFEgACTSbBVL_o3HJRy3MRNgQ',
        'BQACAgUAAxkDAAICfWcX3dr4vr46Z8NB76Vg6ath8tx6AAKGEgACTSbBVAr2vEZlm_cJNgQ',
        'BQACAgUAAxkDAAICfmcX3d2x2cMV1L2k29FnDt13s8XMAAKHEgACTSbBVCkAAfWZzyxEuTYE',
        'BQACAgUAAxkDAAICf2cX3eCZ4Z7nUYXzCQeYYJiLa0eEAAKIEgACTSbBVNyP3es9pqouNgQ',
        'BQACAgUAAxkDAAICgGcX3eOqWnnKL0KcaCCtA7h-XiPeAAKJEgACTSbBVDI3adWM3CwfNgQ',
        'BQACAgUAAxkDAAICgWcX3eyHzGtaiC7AUV1MV6xRXL4NAAKKEgACTSbBVDOeJzqsU2I3NgQ',
        'BQACAgUAAxkDAAICgmcX3e_BZvIoKOp4x1TJtHjNBVB6AAKLEgACTSbBVEe-sdZTvhZpNgQ',
        'BQACAgUAAxkDAAICg2cX3fhZWWePqV9emLTAuv0G52SzAAKMEgACTSbBVKurYvyXTzweNgQ',
        'BQACAgUAAxkDAAIChGcX3mIeKmIPEn9eFoF0ucAe_z7aAAKNEgACTSbBVM4e23zFsxsONgQ'
    ],
    'Books': ['BQACAgUAAxkDAAIEy2cYoebdAAEu0SrFKTIhktlnfDFRFwACjg4AAtfpyFQyGulK61sHPjYE', 
         'BQACAgUAAxkDAAIEzGcYoeoCwTf4CbmCjea23aieRUFOAAKPDgAC1-nIVGMPMm95-3hGNgQ', 
         'BQACAgUAAxkDAAIEzWcYogQPjyX2BtwDTd3PnFfmowc1AAKQDgAC1-nIVMTDA7BUwoo_NgQ'
         ]
}

async def me1105_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Create an inline keyboard with buttons
    keyboard = [
        [InlineKeyboardButton("Assignment", callback_data='me1105_assignment')],
        [InlineKeyboardButton("Chotha", callback_data='me1105_chotha')],
        [InlineKeyboardButton("CT Questions", callback_data='me1105_CT questions')],
        [InlineKeyboardButton("Books", callback_data='me1105_Books')],
        [InlineKeyboardButton("Files by Sobhan Sir", callback_data='me1105_Sobhan Sir')],
        [InlineKeyboardButton("Files by Sultan Sir", callback_data='me1105_Sultan Sir')],
        [InlineKeyboardButton("Others", callback_data='me1105_others')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send the message with buttons
    await update.message.reply_text("ME-1105 Thermal Engineering", reply_markup=reply_markup)

async def button_callback_me1105(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data.split('_')[1]

    command_name = query.data.split('_')[0] 
    button_name = query.data.split('_')[1]  
    course_title = f"{command_name.upper()} {button_name.replace('-', ' ').capitalize()} files are HERE!"
  
    
    # If "Chotha" is clicked, send the Google Drive link
    if data == 'chotha':
        await context.bot.send_message(chat_id=query.message.chat_id, text=course_title)

        await context.bot.send_message(chat_id=query.message.chat_id, text=f"""
Mollier Diagram: https://www.youtube.com/watch?v=DMI0NMVm_sw&pp=ygUPbW9sbGllciBkaWFncmFt
Psychometric Chart: https://www.youtube.com/watch?v=h5eqbJR4d6Y&pp=ygUXcHN5Y2hyb21ldGVyIGhvdyB0byB1c2U%3D
""")
        if data in file_ids_me1105:
            for file_id in file_ids_me1105[data]:
                await context.bot.send_document(chat_id=query.message.chat_id, document=file_id)
        else:
            await context.bot.send_message(chat_id=query.message.chat_id, text="No files available.")
            # Send files if they exist
    else:
        if data in file_ids_me1105:
            await context.bot.send_message(chat_id=query.message.chat_id, text=course_title)
            for file_id in file_ids_me1105[data]:
                await context.bot.send_document(chat_id=query.message.chat_id, document=file_id)
        else:
            await context.bot.send_message(chat_id=query.message.chat_id, text="No files available.")
            # Once all files are processed, send the completion message
    await context.bot.send_message(chat_id=query.message.chat_id, text="All files have been uploaded. Completed!")

file_ids_me1106 = {
    "brief": [
        "BQACAgUAAxkDAAIDpGcYFjd_VhLA0gHZWRNd_4CnYNkWAAKwFAAC1-nAVDkxq5pbOrXiNgQ",
        "BQACAgUAAxkDAAIDpWcYFjqBI5kIcQJKYqHeChaJ5B3iAAKxFAAC1-nAVPEj7nmOufkUNgQ",
    ],
    "Lab Report": [
        "BQACAgUAAxkDAAIDpmcYFkKSkhqihdO2xkQi53B8cdvsAAKyFAAC1-nAVGFoae92knDqNgQ",
        "BQACAgUAAxkDAAIDp2cYFkq7KAmTaBeyh1D2m7rcHk3PAAKzFAAC1-nAVPbUNyu8FsiRNgQ",
        "BQACAgUAAxkDAAIDqGcYFlEZbMlpQWkAAScbgYazO836cQACtBQAAtfpwFQWE0_qaUSEoTYE",
        "BQACAgUAAxkDAAIDqWcYFleAi3Ao-Pfc_bX0cvbj16QDAAK1FAAC1-nAVIB7d2fK9TQWNgQ",
        "BQACAgUAAxkDAAIDqmcYFl8kNBHSKwABvAHSZA2xvRpfhwACthQAAtfpwFTpItmzvZ3zVjYE",
        "BQACAgUAAxkDAAIDq2cYFmUXZ7YT65-trbICwsd9kBsfAAK3FAAC1-nAVJNtQ68UKCFINgQ",
    ]
}

async def me1106_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Create an inline keyboard with buttons for ME-1106
    keyboard = [
        [InlineKeyboardButton("Brief", callback_data='me1106_brief')],
        [InlineKeyboardButton("Lab Report", callback_data='me1106_Lab Report')],  # Corrected callback data
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send the message with buttons
    await update.message.reply_text("ME - 1106 [Sessional- Thermal Engineering]", reply_markup=reply_markup)

async def button_callback_me1106(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data.split('_')[1]

    command_name = query.data.split('_')[0]  # This will extract 'math1105'
    button_name = query.data.split('_')[1]   # This will extract the specific section like 'chotha', 'ct-questions', etc.

    course_title = f"{command_name.upper()} {button_name.replace('-', ' ').capitalize()} files are HERE!"
    
    
    if data in file_ids_me1106:
        await context.bot.send_message(chat_id=query.message.chat_id, text=course_title)
        for file_id in file_ids_me1106[data]:
            await context.bot.send_document(chat_id=query.message.chat_id, document=file_id)
    else:
        await context.bot.send_message(chat_id=query.message.chat_id, text="No files available.")
    await context.bot.send_message(chat_id=query.message.chat_id, text="All files have been uploaded. Completed!")


file_ids_me1107 = {
    'Assignment': [
        'BQACAgUAAxkDAAID02cYG-uiTCZHQMGARHMLFV2snEW_AAK8FAAC1-nAVF8HvOfpZJr7NgQ',
        'BQACAgUAAxkDAAID1GcYG-4rTYoE6dvJsvRKcyftz_wzAAK9FAAC1-nAVKl2iVkoye7MNgQ'
    ],
    'Books' : [
        'BQACAgUAAxkBAAIFBWcYpHQu90l1kr3EkfZE8m41KmlVAAKbDgAC1-nIVDmzka9fJ23BNgQ',
        'BQACAgUAAxkBAAIFBmcYpHck8mW2tV9_BWRBHi9prmslAAKcDgAC1-nIVDezMdFfO932NgQ',
        'BQACAgUAAxkBAAIFB2cYpa7RRL43B43nRpMZ0TVTQhLVAAKdDgAC1-nIVLL_xkTx4Qm3NgQ'
    ],
    'Chotha by Tahsin': [
        'BQACAgUAAxkDAAID1WcYG_qfGXpOXn0RfPNQ5c5AvtOaAAK-FAAC1-nAVJrgeL6RT2g1NgQ',
        'BQACAgUAAxkDAAID1mcYG_4l70iO6y2-yA9Mqmha5HQRAAK_FAAC1-nAVO0EIIpkKI8tNgQ',
        'BQACAgUAAxkDAAID12cYHBDkBgx1Fjri6QhUcebw0MJpAALAFAAC1-nAVASrUbI7_OLKNgQ',
        'BQACAgUAAxkDAAID2GcYHBEKGM8uRWFkmbfhlYM4ptGhAALBFAAC1-nAVMlwPG_6WGTANgQ'
    ],
    'course plan': [
        'BQACAgUAAxkDAAID2WcYHBOMTvZ7wuZsNptWr3twgMOuAALCFAAC1-nAVHN8TKgpX7VnNgQ'
    ],
    'CT Question': [
        'BQACAgUAAxkDAAID2mcYHBbweeSzgtdZP9jZSQEVRi8LAALDFAAC1-nAVEF0YM5uuuOONgQ'
    ],
    'Files by Dipayan Mondol Sir': [
        'BQACAgUAAxkDAAID22cYHBpjMTMTmkAlRs25hbWXeQlkAALEFAAC1-nAVF7flHq0_qAsNgQ',
        'BQACAgUAAxkDAAID3GcYHB63961DbJ__J54Za_5gu7xUAALFFAAC1-nAVOvVSoWynLIQNgQ',
        'BQACAgUAAxkDAAID3WcYHCX_3sDPL1j111x-c-uS8Nl3AALGFAAC1-nAVKXojLV3On3INgQ',
        'BQACAgUAAxkDAAID3mcYHCwrlEkQNsH_MHLM0S_By19zAALHFAAC1-nAVKPFsJuC_HpLNgQ',
        'BQACAgUAAxkDAAID32cYHC66NQnzNlQaji2JdXazI53xAALIFAAC1-nAVMsDiHCZ-hi5NgQ',
        'BQACAgUAAxkDAAID4GcYHDEq5ow39WYq_9PrJHBCRUynAALJFAAC1-nAVIYDNKhcX3lYNgQ',
        'BQACAgUAAxkDAAID4WcYHDwhgL_VbsPy8-RUnBuEZXcfAALKFAAC1-nAVKa04iId4LTENgQ',
        'BQACAgUAAxkDAAID4mcYHEO0DhY5ruPsKAquTr3PwEioAALLFAAC1-nAVBxPr-DAmDKHNgQ',
        'BQACAgUAAxkDAAID42cYHEo6Z6pw4fMoA6ALwWuJfvucAALMFAAC1-nAVC_dO_sJM7xuNgQ',
        'BQACAgUAAxkDAAID5GcYHFEAATZtUDlJDUoYP455GI4FBgACzRQAAtfpwFTxhVmBK5HfaTYE'
    ],
    'Files by Rubiat Mustak Sir': [
        'BQACAgUAAxkDAAID5WcYHFJQnrU6ZY2xXz59rX1cxLbZAALOFAAC1-nAVM7icMnCGkEgNgQ',
        'BQACAgUAAxkDAAID5mcYHFXpaHnWfBtoSF3fN9dnAePJAALPFAAC1-nAVGe2DGTVuhkINgQ',
        'BQACAgUAAxkDAAID52cYHFnr40r1oB8rgv3GiZ_uayQ1AALQFAAC1-nAVKVXCy9lMcrKNgQ',
        'BQACAgUAAxkDAAID6GcYHF2pLQfTJYklgaaXS3OKSHrNAALRFAAC1-nAVJ_r32eX-EDlNgQ',
        'BQACAgUAAxkDAAID6WcYHF8l9BR5i2jCOprukZSiKUjHAALSFAAC1-nAVLZ0tFbLqWxKNgQ'
    ],
    'others': [
        'BQACAgUAAxkDAAID6mcYHILJtnTal1zUkEY09ZzdWvu6AALTFAAC1-nAVJ98b1wCvywZNgQ',
        'BQACAgUAAxkDAAID62cYHI0d3zYdIUX3wDd6qcyUavryAALUFAAC1-nAVIHy-h_8yXHCNgQ',
        'BQACAgUAAxkDAAID7GcYHJQ9TbDGsEQv8GjnQp536GbDAALVFAAC1-nAVK4bgDu_13oRNgQ',
        'BQACAgUAAxkDAAID7WcYHJpuqVM03iM0A1HQJxzgcFQYAALWFAAC1-nAVArfKH_qxnGlNgQ',
        'BQACAgUAAxkDAAID7mcYHJzxwUSuWS4edtz0dx9xGUjhAALXFAAC1-nAVFtkvOBNQ2vbNgQ',
        'BQACAgUAAxkBAAID-GcYHp_26rCxOVvQpvvuiAVWy4TIAALiFAAC1-nAVDH-WRN-8rzuNgQ'
    ],
    'Sec A- Intro to Manufacturing Process by Dipayan Mondol': [
        'BQACAgUAAxkDAAID72cYHKCT9cHG8thDe_c5V59ICi2NAALYFAAC1-nAVLsR5-LILLw8NgQ',
        'BQACAgUAAxkDAAID8GcYHKdRtDQHOQxtOXkbs7HdIpDtAALZFAAC1-nAVLuMpJ3Zr4HGNgQ',
        'BQACAgUAAxkDAAID8WcYHK4dD7GIuxXFc5vLXgp68auBAALaFAAC1-nAVM33YJhuemQHNgQ',
        'BQACAgUAAxkDAAID8mcYHLBoBtgQ3tOoPvni0QKSK7fBAALbFAAC1-nAVKm1YwaCIjAjNgQ',
        'BQACAgUAAxkDAAID82cYHLPtLMnHgRR5j_5Ql4HslNwZAALcFAAC1-nAVFIfa17hKw5ONgQ',
        'BQACAgUAAxkDAAID9GcYHLsLPxYAAc80E43cebVsYF8n_wAC3hQAAtfpwFSXL5hJ3GwmTTYE'
    ],
    'Sec B- Intro to Machineries by Rubiat Mustak': [
        'BQACAgUAAxkDAAID9WcYHL6kCuMnCLDJZGV2PtZkwH9CAALfFAAC1-nAVGFgeuO_xsi-NgQ',
        'BQACAgUAAxkDAAID9mcYHMOmYzva2wL041x-WCNu4PYtAALgFAAC1-nAVMPb9SqzbxR4NgQ',
        'BQACAgUAAxkDAAID92cYHMV7xtqYFOc7H2YE-OB7cc9yAALhFAAC1-nAVLxlRkl_pAABpjYE'
    ]
}

async def me1107_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Create an inline keyboard with buttons for ME-1107
    keyboard = [
        [InlineKeyboardButton("Assignment", callback_data='me1107_Assignment')],
        [InlineKeyboardButton("Books", callback_data='me1107_Books')],
        [InlineKeyboardButton("Chotha by Tahsin", callback_data='me1107_Chotha by Tahsin')],
        [InlineKeyboardButton("Course Plan", callback_data='me1107_course plan')],
        [InlineKeyboardButton("CT Question", callback_data='me1107_CT Question')],
        [InlineKeyboardButton("Files by Dipayan Mondol Sir", callback_data='me1107_Files by Dipayan Mondol Sir')],
        [InlineKeyboardButton("Files by Rubiat Mustak Sir", callback_data='me1107_Files by Rubiat Mustak Sir')],
        [InlineKeyboardButton("Others", callback_data='me1107_others')],
        [InlineKeyboardButton("Sec A - Intro to Manufacturing Process", callback_data='me1107_Sec A- Intro to Manufacturing Process by Dipayan Mondol')],
        [InlineKeyboardButton("Sec B - Intro to Machineries", callback_data='me1107_Sec B- Intro to Machineries by Rubiat Mustak')],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send the message with buttons
    await update.message.reply_text("ME - 1107 [Manufacturing Process]", reply_markup=reply_markup)

async def button_callback_me1107(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data.split('_')[1]
    
    command_name = query.data.split('_')[0]  # This will extract 'math1105'
    button_name = query.data.split('_')[1]   # This will extract the specific section like 'chotha', 'ct-questions', etc.

    course_title = f"{command_name.upper()} {button_name.replace('-', ' ').capitalize()} files are HERE!"

    if data in file_ids_me1107:
        await context.bot.send_message(chat_id=query.message.chat_id, text=course_title)

        for file_id in file_ids_me1107[data]:
            await context.bot.send_document(chat_id=query.message.chat_id, document=file_id)
    else:
        await context.bot.send_message(chat_id=query.message.chat_id, text="No files available.")
    await context.bot.send_message(chat_id=query.message.chat_id, text="All files have been uploaded. Completed!")


file_ids_me1108 = {
    'brief': ['BQACAgUAAxkDAAIEIWcYIdjCxqh7s3llfE0tQlMpq5jZAALnFAAC1-nAVP8d8iu3hhahNgQ'],
    'Lab Report': [
        'BQACAgUAAxkDAAIEImcYIeBWNOPChXf_h1tU5KnyYrNmAALoFAAC1-nAVCDw7_xJpxpZNgQ',
        'BQACAgUAAxkDAAIEI2cYIfHoPHbpgW7H6IxtGIyqOIPcAALpFAAC1-nAVEdnyxHrnS_sNgQ',
        'BQACAgUAAxkDAAIEJGcYIfmDuEmNoAmXDHsi8ENTCkl_AALqFAAC1-nAVFXS_i7NwJLTNgQ',
        'BQACAgUAAxkDAAIEJWcYIgFoSYyx2kFcSbVHIPLm9ifEAALrFAAC1-nAVAiT13ONjzIVNgQ',
        'BQACAgUAAxkDAAIEJmcYIgtrnMb6aOs5vEu6GImihRvtAALsFAAC1-nAVKlfRZX95uZONgQ'
    ],
    'Quiz': [
        'BQACAgUAAxkDAAIEJ2cYIhDxV1BqKGDnnUab6UGfYMraAALtFAAC1-nAVL6IlBK1Fc1YNgQ',
        'BQACAgUAAxkDAAIEKGcYIhPgjReVZtfNlJ5FHNOfCJ8_AALuFAAC1-nAVC5GeXw74--iNgQ'
    ]
}

async def me1108_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Create an inline keyboard with buttons for ME-1108
    keyboard = [
        [InlineKeyboardButton("Brief", callback_data='me1108_brief')],
        [InlineKeyboardButton("Lab Report", callback_data='me1108_Lab Report')],
        [InlineKeyboardButton("Quiz", callback_data='me1108_Quiz')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send the message with buttons
    await update.message.reply_text("ME - 1108 [Sessional - Manufacturing Process]", reply_markup=reply_markup)

async def button_callback_me1108(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data.split('_')[1]
    
    command_name = query.data.split('_')[0]  
    button_name = query.data.split('_')[1]   
    course_title = f"{command_name.upper()} {button_name.replace('-', ' ').capitalize()} files are HERE!"
    
    if data in file_ids_me1108:
        await context.bot.send_message(chat_id=query.message.chat_id, text=course_title)

        for file_id in file_ids_me1108[data]:
            await context.bot.send_document(chat_id=query.message.chat_id, document=file_id)
    else:
        await context.bot.send_message(chat_id=query.message.chat_id, text="No files available.")
    await context.bot.send_message(chat_id=query.message.chat_id, text="All files have been uploaded. Completed!")



file_ids_mes1102 = {
    'brief': ['BQACAgUAAxkDAAIEOmcYI45DXFOoEaw2Pdu1MXiv6vk9AALwFAAC1-nAVJk5roKygacSNgQ'],
    'Lab Report': [
        'BQACAgUAAxkDAAIEO2cYI5X-ij-4XYAExwKE_3rtxQycAALxFAAC1-nAVHAAATDVvMPfVTYE',
        'BQACAgUAAxkDAAIEPGcYI5xJIsW9tRMTc9xpak-KbegpAALyFAAC1-nAVEz7sKNebcSXNgQ',
        'BQACAgUAAxkDAAIEPWcYI6EH1wvaNTx02W8mH1vY8NR5AALzFAAC1-nAVAtdwRO-IE6CNgQ',
        'BQACAgUAAxkDAAIEPmcYI6r5oSIE2ujvM3ML-hApo3BhAAL0FAAC1-nAVNt4OEwOZOp5NgQ',
        'BQACAgUAAxkDAAIEP2cYI6_3aEwmDIw_C8RqoFfTbVWZAAL1FAAC1-nAVNo3tfNheiGhNgQ',
        'BQACAgUAAxkDAAIEQGcYI7WzWdY7wnm9eDqtkwTqAgEwAAL2FAAC1-nAVKkn7POMAS7JNgQ'
    ]
}

async def mes1102_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Create an inline keyboard with buttons for MES-1102
    keyboard = [
        [InlineKeyboardButton("Brief", callback_data='mes1102_brief')],
        [InlineKeyboardButton("Lab Report", callback_data='mes1102_Lab Report')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send the message with buttons
    await update.message.reply_text("MES - 1102 [Sessional - Work Shop Practice]", reply_markup=reply_markup)

async def button_callback_mes1102(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data.split('_')[1]

    command_name = query.data.split('_')[0]  
    button_name = query.data.split('_')[1]   
    course_title = f"{command_name.upper()} {button_name.replace('-', ' ').capitalize()} files are HERE!" 
    
    if data in file_ids_mes1102:
        await context.bot.send_message(chat_id=query.message.chat_id, text=course_title)

        for file_id in file_ids_mes1102[data]:
            await context.bot.send_document(chat_id=query.message.chat_id, document=file_id)
    else:
        await context.bot.send_message(chat_id=query.message.chat_id, text="No files available.")
    await context.bot.send_message(chat_id=query.message.chat_id, text="All files have been uploaded. Completed!")


file_ids_qb = [
    'BQACAgUAAxkDAAIETGcYJtaBIoEAAVRSCiy3U8L2dkp1_gAC9xQAAtfpwFQW3Ng7-w3Q-DYE',
    'BQACAgUAAxkDAAIETWcYJtuVvx_Lt2YhjpSngsqTEBCJAAL5FAAC1-nAVHdBT0EqyKKgNgQ',
    'BQACAgUAAxkDAAIETmcYJuKtTaDx-JwLRXkjYMO0VHMwAAL6FAAC1-nAVHj62ij6qT7ONgQ'
]

async def qb_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id  # Get the chat ID from the message
    for file_id in file_ids_qb:
        await context.bot.send_document(chat_id=chat_id, document=file_id)


file_ids_hum1105 = {
    'CT Question': [
        'BQACAgUAAxkDAAIEdGcYKfVqXgqjSuhza4UStxW7_8JwAAIcFQAC1-nAVLm6rxruy712NgQ',
        'BQACAgUAAxkDAAIEdWcYKfb_l8XloAJ9COrTBwuJ6BQXAAIdFQAC1-nAVLrC5zmjieebNgQ',
        'BQACAgUAAxkDAAIEdmcYKfvxValbmE2gtj2N5c1pPUoQAAIeFQAC1-nAVBdgN_QnTAi7NgQ'
    ],
    'English Presentation': [
        'BQACAgUAAxkDAAIEd2cYKf3Mo75N080BjIlN4Qug_lTRAAIfFQAC1-nAVHDXGBZJPPFCNgQ',
        'BQACAgUAAxkDAAIEeGcYKgABcgqfVF7ECd3TDubaRyUppAACIBUAAtfpwFQT0Vpp8LIhczYE',
        'BQACAgUAAxkDAAIEeWcYKgGIvmgSTB-LuiIfN9PSI4j6AAIhFQAC1-nAVO3S1iLF5cSaNgQ',
        'BQACAgUAAxkDAAIEemcYKgLkAbOccT87HMoYOJBKb8NGAAIiFQAC1-nAVI1buen2wyPZNgQ',
        'BQACAgUAAxkDAAIEe2cYKgSDCs7eqpgTzAHwa3YEVYDjAAIjFQAC1-nAVElWYmeKlm_FNgQ',
        'BQACAgUAAxkDAAIEfGcYKgjsLYvUjUAhwHvAc8i3r1GxAAIkFQAC1-nAVNhYIQSbbTdCNgQ',
        'BQACAgUAAxkBAAIElWcYLanwFJUFjn2nTMYkhsi6T88hAAIzFQAC1-nAVHIZrrZfy4N6NgQ'
    ],
    'Other documents': [
        'BQACAgUAAxkDAAIEfWcYKgp7DKk3iWSNwXmZX2EfG9VEAAIlFQAC1-nAVFtRcvz8bTmoNgQ',
        'BQACAgUAAxkDAAIEfmcYKgyFiQ_b-ZRwfJcFeDG7_-19AAImFQAC1-nAVODlQAv0jqu1NgQ',
        'BQACAgUAAxkDAAIEf2cYKhIMRTZPM4J_GYJGaRDBFWQRAAInFQAC1-nAVOb9-n5PVz1pNgQ',
        'BQACAgUAAxkDAAIEgGcYKhYSI8bXt5VU4DN_vYf7mCm3AAIoFQAC1-nAVDWiLw4eXYQkNgQ',
        'BQACAgUAAxkDAAIEgWcYKhpz9ivsSAABZdt9SMF1pQABpMIAAikVAALX6cBUvsNSjokPCvo2BA',
        'BQACAgUAAxkDAAIEgmcYKhzZ7hyOdCGKq_kH6N6H2DpuAAIqFQAC1-nAVAXNrzp3ZLdgNgQ',
        'BQACAgUAAxkDAAIEg2cYKiDrLwjKAAH57BZeGupk7KbbmwACKxUAAtfpwFRqiljtRwmwEzYE',
        'BQACAgUAAxkDAAIEhGcYKiONjNIohlvEGWm1938EY9zaAAIsFQAC1-nAVJBUT-uSr8PcNgQ',
        'BQACAgUAAxkDAAIEhWcYKiXN6z1iEsI13I_G4AsJVXdXAAItFQAC1-nAVH5Psm742hq4NgQ',
        'BQACAgUAAxkDAAIEhmcYKigwBTfoK-suFak55W4xWpgnAAIuFQAC1-nAVJEOkRHQMsljNgQ'
    ],
    'books': ['BQACAgUAAxkDAAIEn2cYL0xUShcPNO0-5XVMpTDUFmS2AAI0FQAC1-nAVERcvYGe7imwNgQ', 
              'BQACAgUAAxkDAAIEoGcYL1DW8gy959ae3CUm_HtQ7-fRAAI1FQAC1-nAVHLavdF_frmHNgQ', 
              'BQACAgUAAxkDAAIEoWcYL2WA7-_e_FkRYz2lEOOKm3jCAAI2FQAC1-nAVPCDCC-LfClrNgQ', 
              'BQACAgUAAxkDAAIEomcYL2q7ZHTQT0KnAnE0AAFq0iQ3fAACNxUAAtfpwFS-jYR0041QwzYE', 
              'BQACAgUAAxkDAAIEo2cYL4M_swn8epOL5wqQnewmtk6kAAI4FQAC1-nAVAABZUsG-q5BuzYE'
    ]

}

async def hum1105_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Create an inline keyboard with buttons for HUM-1105
    keyboard = [
        [InlineKeyboardButton("CT Question", callback_data='hum1105_CT Question')],
        [InlineKeyboardButton("English Presentation", callback_data='hum1105_English Presentation')],
        [InlineKeyboardButton("Books", callback_data='hum1105_books')],
        [InlineKeyboardButton("Other documents", callback_data='hum1105_Other documents')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send the message with buttons
    await update.message.reply_text("HUM - 1105 [English]", reply_markup=reply_markup)

async def button_callback_hum1105(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data.split('_')[1]
    command_name = query.data.split('_')[0]  
    button_name = query.data.split('_')[1]   
    course_title = f"{command_name.upper()} {button_name.replace('-', ' ').capitalize()} files are HERE!"
    
    if data in file_ids_hum1105:
        await context.bot.send_message(chat_id=query.message.chat_id, text=course_title)
        for file_id in file_ids_hum1105[data]:
            await context.bot.send_document(chat_id=query.message.chat_id, document=file_id)
    else:
        await context.bot.send_message(chat_id=query.message.chat_id, text="No files available.")
    await context.bot.send_message(chat_id=query.message.chat_id, text="All files have been uploaded. Completed!")


    query = update.callback_query
    await query.answer()
    data = query.data.split('_')[1]
    
    if data in file_ids_try1105:
        for file_id in file_ids_try1105[data]:
            await context.bot.send_document(chat_id=query.message.chat_id, document=file_id)
    else:
        await context.bot.send_message(chat_id=query.message.chat_id, text="No files available.")


# Main function to set up the bot
async def main() -> None:
    # Create the bot application
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('Start', start))
    application.add_handler(CommandHandler('Help', help))
    application.add_handler(CommandHandler('Syllabus', syllabus_command))
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('Batch22info', batch22info)],
        states={
            ROLL_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_roll_number)]
        },
        fallbacks=[],  # Add fallbacks if needed
    )

    # Add the conversation handler to the application
    application.add_handler(conv_handler)

    application.add_handler(CommandHandler('CH1105', ch1105_command))
    application.add_handler(CallbackQueryHandler(button_callback_ch1105, pattern='^ch1105_'))
    
    application.add_handler(CommandHandler('CH1106', ch1106_command))
    application.add_handler(CallbackQueryHandler(button_callback_ch1106, pattern='^ch1106_'))
    
    application.add_handler(CommandHandler('MATH1105', math1105_command))
    application.add_handler(CallbackQueryHandler(button_callback_math1105, pattern='^math1105_'))
    
    application.add_handler(CommandHandler('ME1105', me1105_command))
    application.add_handler(CallbackQueryHandler(button_callback_me1105, pattern='^me1105_'))

    application.add_handler(CommandHandler("me1106", me1106_command))
    application.add_handler(CallbackQueryHandler(button_callback_me1106, pattern='^me1106_'))

    application.add_handler(CommandHandler("me1107", me1107_command))
    application.add_handler(CallbackQueryHandler(button_callback_me1107, pattern='^me1107_'))

    application.add_handler(CommandHandler("me1108", me1108_command))
    application.add_handler(CallbackQueryHandler(button_callback_me1108, pattern='^me1108_'))

    application.add_handler(CommandHandler("mes1102", mes1102_command))
    application.add_handler(CallbackQueryHandler(button_callback_mes1102, pattern='^mes1102_'))

    application.add_handler(CommandHandler("hum1105", hum1105_command))
    application.add_handler(CallbackQueryHandler(button_callback_hum1105, pattern='^hum1105_'))

    application.add_handler(CommandHandler("qb", qb_command))
    await set_webhook()

if __name__ == '__main__':
    # Start the Flask server to keep the bot alive and handle webhooks
    #keep_alive()
    app.run(debug=True)
    # Run the main event loop
    asyncio.run(main())
