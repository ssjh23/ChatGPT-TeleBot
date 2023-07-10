#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.


"""
First, a few callback functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using nested ConversationHandlers.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import os
import openai
from enum import Enum
from chatgpt import ChatGPT
from imagegen import ImageGen
from typing import Any, Dict, Tuple

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# State definitions for top level conversation
SELECTING_ACTION, CHAT_GPT, IMAGE_GEN, DESCRIBING_SELF = map(chr, range(4))
# State definitions for second level conversation
SELECTING_LEVEL, SELECTING_GENDER = map(chr, range(4, 6))
# State definitions for descriptions conversation
SELECTING_FEATURE, TYPING = map(chr, range(6, 8))
# Meta states
STOPPING, BACK_TO_START = map(chr, range(8, 10))
# Shortcut for ConversationHandler.END
NEW_IMAGE = "NEW_IMAGE"
END_CHATGPT = "END_CHATGPT"
IMAGE_SIZE = "IMAGE_SIZE"
IMAGE_PROMPT = "IMAGE_PROMPT"
IMAGE_GEN = "IMAGE_GEN"
END = ConversationHandler.END
class ImageSize(Enum):
    SMALL = 256
    MEDIUM = 512
    LARGE = 1024

# Different constants for this example
(
    NEW_CHAT,
    CHAT_HIST,
    SELF,
    GENDER,
    MALE,
    FEMALE,
    AGE,
    NAME,
    START_OVER,
    FEATURES,
    CURRENT_FEATURE,
    CURRENT_LEVEL,
) = map(chr, range(10, 22))

application = None
ChatGPT_instance:ChatGPT = None
ImageGen_instance:ImageGen = None

# Top level conversation callbacks
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Select an action: ChatGPT or Image Generation"""
    text = (
       "Select an option to get started. /stop to stop the bot at anytime"
    )

    buttons = [
        [
            InlineKeyboardButton(text="ChatGPT", callback_data=str(CHAT_GPT)),
            InlineKeyboardButton(text="Image Generation", callback_data=str(IMAGE_GEN)),
        ],
        [
            InlineKeyboardButton(text="Done", callback_data=str(END)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    # If we're starting over we don't need to send a new message
    if context.user_data.get(START_OVER):
        if update.callback_query != None:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=keyboard)
    else:
        await update.message.reply_text(
            "Welcome to your personal OpenAI bot, " + update.effective_user.name
        )
        await update.message.reply_text(text=text, reply_markup=keyboard)
    context.user_data[START_OVER] = False
    return SELECTING_ACTION

async def new_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ImageGen_instance
    ImageGen_instance = ImageGen(update, context, update.effective_chat.id, application)
    await ImageGen_instance.run()

async def end_imagegen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ImageGen_instance.remove_image_handlers()
    """Return to top level conversation."""
    context.user_data[START_OVER] = True
    await start(update, context)
    return END

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End Conversation by command."""
    await update.message.reply_text("Okay, bye.")
    return END


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End conversation from InlineKeyboardButton."""
    await update.callback_query.answer()

    text = "See you around!"
    await update.callback_query.edit_message_text(text=text)

    return END

async def new_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    global ChatGPT_instance
    global application
    """Start a new chat."""
    level = update.callback_query.data
    context.user_data[CURRENT_LEVEL] = level
    ChatGPT_instance = ChatGPT(update, context, update.effective_chat.id, application)
    await ChatGPT_instance.run(update, context)
    return SELECTING_LEVEL

async def end_chatgpt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await ChatGPT_instance.remove_chatgpt_handlers(update=update, context=context)
    """Return to top level conversation."""
    context.user_data[START_OVER] = True
    await start(update, context)
    return END

async def reset_convo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data[START_OVER] = True
    await start(update=update, context=context)
    return 

async def stop_nested(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Completely end conversation from within nested conversation."""
    await update.message.reply_text("Okay, bye.")

    return STOPPING

async def back(update :Update, context: ContextTypes.DEFAULT_TYPE):
    if ChatGPT_instance != None:
        await end_chatgpt(update=update, context=context)
    elif ImageGen_instance != None:
        await end_imagegen(update=update, context=context)
    
def main() -> None:
    
    global application
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    test_token = os.getenv("OPENAI_API_KEY")
    telebot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    logger.info('%s',telebot_token)
    application = Application.builder().token(telebot_token).build()
    openai.api_key=test_token

    # Main Menu Conversation handler containing nested conversations
    selection_handlers = [
        CallbackQueryHandler(new_chat, pattern="^" + str(CHAT_GPT) + "$"),
        CallbackQueryHandler(reset_convo, pattern="^" + str(BACK_TO_START) + "$"),
        CallbackQueryHandler(new_image, pattern="^" + str(IMAGE_GEN) + "$"),
        CommandHandler("back_to_main", back)
    ]
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
        ],
        states={
            SELECTING_ACTION: selection_handlers,
            SELECTING_LEVEL: selection_handlers,
            STOPPING: [CommandHandler("start", start)],
        },
        fallbacks=[
            CommandHandler("stop", stop),
        ],
    )
    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()   