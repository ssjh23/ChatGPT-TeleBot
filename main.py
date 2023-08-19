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

import html
import json
import traceback
import os
import openai
from enum import Enum
from chatgpt import ChatGPT
from imagegen import ImageGen
from typing import Any, Dict, Tuple
from functools import wraps
from logger import UserActionLogger
from telegram.constants import ParseMode

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
    MessageHandler,
    filters
)


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
FAILED_ACCESS = "FAILED_ACCESS"
WAITING_FOR_PIN = "WAITING_FOR_PIN"
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
has_access = False
logger = UserActionLogger


# Error handler
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Log the error first
    logger.error('%s', "Exception while handling an update:", exc_info=context.error)

    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"Oops! An exception was raised while handling an update:\n"
        f"<pre>update_str = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML
    )


# Top level conversation callbacks
@logger("invalid command")
async def echo_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # echo /start message
    echo_text = (
        "Invalid command or text. /start to start using the bot."
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=echo_text)

@logger("started bot")
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    # Login
    login_text = (
        "Please key in the appropriate PIN to access the bot"
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=login_text)
    return WAITING_FOR_PIN

async def getting_pin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global has_access
    """Select an action: ChatGPT or Image Generation"""
    text = (
        "Select an option to get started. /stop to stop the bot at anytime"
    )

    buttons = [
        [
            InlineKeyboardButton(text="ChatGPT", callback_data=str(CHAT_GPT)),
            InlineKeyboardButton(text="Image Generation", callback_data=str(IMAGE_GEN)),
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    entered_pin = update.message.text
    access_pin = os.getenv("ACCESS_PIN")
    if not has_access:
        if entered_pin != access_pin:
            await failed_login(update, context)
            return FAILED_ACCESS
    has_access = True

    if context.user_data.get(START_OVER):
        await start_over(update, context, text, keyboard)
    else:
        await success_login(update, context, text, keyboard)
    context.user_data[START_OVER] = False
    return SELECTING_ACTION

@logger("failed login")
async def failed_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    failed_login_text = (
        "The entered PIN is incorrect. Type /start to try again"
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=failed_login_text)

async def start_over(update: Update, context: ContextTypes.DEFAULT_TYPE, text, keyboard):
    if update.callback_query != None:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=keyboard)

@logger("successful login")
async def success_login(update: Update, context: ContextTypes.DEFAULT_TYPE, text, keyboard):
    await update.message.reply_text(
        "Welcome to your personal OpenAI bot, " + update.effective_user.name
    )
    await update.message.reply_text(text=text, reply_markup=keyboard)

@logger("stopped bot")
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End Conversation by command."""
    await update.message.reply_text("Okay, bye loser 👋🏻")
    return END

async def new_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    global ChatGPT_instance
    global application
    """Start a new chat."""
    level = update.callback_query.data
    context.user_data[CURRENT_LEVEL] = level
    ChatGPT_instance = ChatGPT(update, context, update.effective_user.username, update.effective_chat.id, application, logger)
    await ChatGPT_instance.run()
    return SELECTING_LEVEL

async def new_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ImageGen_instance
    ImageGen_instance = ImageGen(update, context, update.effective_user.username, update.effective_chat.id, application, logger)
    await ImageGen_instance.run()

# async def reset_convo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     context.user_data[START_OVER] = True
#     await start(update=update, context=context)
#     return 

@logger("return back to main menu")
async def back_to_main(update :Update, context: ContextTypes.DEFAULT_TYPE):
    if ChatGPT_instance != None:
        await end_chatgpt(update=update, context=context)
    elif ImageGen_instance != None:
        await end_imagegen(update=update, context=context)

@logger("ending chatgpt instance")
async def end_chatgpt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await ChatGPT_instance.remove_chatgpt_handlers(update=update, context=context)
    """Return to top level conversation."""
    context.user_data[START_OVER] = True
    await getting_pin(update=update, context=context)
    return SELECTING_ACTION

@logger("ending imagegen instance")
async def end_imagegen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ImageGen_instance.remove_image_handlers()
    """Return to top level conversation."""
    context.user_data[START_OVER] = True
    await getting_pin(update=update, context=context)
    return SELECTING_ACTION


''' sample bad command for testing'''
async def bad_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Raise an error to trigger the error handler."""
    await context.bot.wrong_method_name()  # type: ignore[attr-defined]
    
def main() -> None:
    
    global application
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    api_token = os.getenv("OPENAI_API_KEY")
    telebot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    # logger.log_info('%s',telebot_token)
    application = Application.builder().token(telebot_token).build()
    openai.api_key=api_token

    # Main Menu Conversation handler containing nested conversations
    selection_handlers = [
        CallbackQueryHandler(new_chat, pattern="^" + str(CHAT_GPT) + "$"),
        # CallbackQueryHandler(reset_convo, pattern="^" + str(BACK_TO_START) + "$"),
        CallbackQueryHandler(new_image, pattern="^" + str(IMAGE_GEN) + "$"),
        CommandHandler("back_to_main", back_to_main)
    ]
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            MessageHandler(filters.TEXT | filters.COMMAND, echo_start),
        ],
        states={
            WAITING_FOR_PIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, getting_pin)],
            SELECTING_ACTION: selection_handlers,
            SELECTING_LEVEL: selection_handlers,
            STOPPING: [CommandHandler("start", start)],
            FAILED_ACCESS: [
                CommandHandler("start", start), 
                MessageHandler(filters.TEXT | filters.COMMAND, echo_start),
            ]
        },
        fallbacks=[
            CommandHandler("stop", stop),
        ],
    )
    application.add_error_handler(error_handler)

    ''' Sample command to instantiate error '''
    application.add_handler(CommandHandler("bad_command", bad_command))
    
    application.add_handler(conv_handler)
    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()   