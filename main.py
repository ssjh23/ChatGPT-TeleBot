
import logging
from enum import Enum
from chatgpt import ChatGPT
from telegram import (
    Update, 
    Bot, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup
)
from telegram.ext import (
    filters, 
    MessageHandler, 
    ApplicationBuilder, 
    ConversationHandler,
    CommandHandler, 
    CallbackQueryHandler,
    ContextTypes, 
    Application
)
from dotenv import load_dotenv
import os
import openai

global application
application = None
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# State definitions for top level conversation
SELECTING_ACTION, IMAGE_GENERATION, TRANSCRIPTIONS= map(chr, range(3))
CHATGPT = "CHATGPT"
MAIN_MENU = "MAIN_MENU"
# State definitions for second level conversation
END = ConversationHandler.END
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.effective_chat.id)
    text = "Welcome to your personal OpenAI bot"
    # Sends a message with three inline buttons attached
    keyboard = [
        [
            InlineKeyboardButton("ChatGPT", callback_data=CHATGPT),
            InlineKeyboardButton("Image Generation", callback_data= "2"),
        ],
        [InlineKeyboardButton("Transcriptions", callback_data= "3")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text=text, reply_markup=reply_markup)
    return SELECTING_ACTION


async def start_chat_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(application)
    ChatGPT_instance = ChatGPT(update.effective_chat.id, application)
    await ChatGPT_instance.run(update, context)

if __name__ == '__main__':
    load_dotenv('/Users/seansoo/Documents/github-repos/ChatGPT-TeleBot/.env')
    token= os.getenv('TELEGRAM_BOT_TOKEN')
    # Set up the OpenAI API
    openai.api_key = os.getenv('OPENAI_TOKEN')
    application = ApplicationBuilder().token(token).build()
    bot_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN_MENU: [CallbackQueryHandler(start, pattern="^"+str(END)+"$")],
            SELECTING_ACTION:[CallbackQueryHandler(start_chat_gpt, pattern="^"+CHATGPT+"$")]
        },
        fallbacks=[CommandHandler('start', start)]
    )
    application.add_handler(bot_conv_handler)
    application.run_polling()
    
