# import telegram
# import openai
# from telegram.ext import Updater, CommandHandler, MessageHandler, filters

# # Set up the OpenAI API
# openai.api_key = "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"
# token='6066250189:AAEdtY22a4qZzYmBL96khPq5BUrVRk7ZbHs'

# # Set up the Telegram Bot API
# bot = telegram.Bot(token)

# # Define a function to handle incoming messages
# def handle_message(update, context):
    # message = update.message.text
    # # Call the OpenAI API to generate a response
    # response = openai.Completion.create(
    #     engine="davinci",
    #     prompt=message,
    #     max_tokens=60,
    #     n=1,
    #     stop=None,
    #     temperature=0.5,
    # )
    # # Send the response back to the user
    # context.bot.send_message(chat_id=update.effective_chat.id, text=response.choices[0].text)

# # Define a function to start the bot
# def start(update, context):
#     context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a ChatGPT bot. Send me a message!")

# # Set up the handlers
# updater = Updater(bot, use_context=True)
# dispatcher = updater.dispatcher
# dispatcher.add_handler(CommandHandler('start', start))
# dispatcher.add_handler(MessageHandler(filters.text, handle_message))

# # Start the bot
# updater.start_polling()
# updater.idle()

import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
import openai
token='6066250189:AAEdtY22a4qZzYmBL96khPq5BUrVRk7ZbHs'
# Set up the OpenAI API
openai.api_key = "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"


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


async def chatgpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    # Call the OpenAI API to generate a response
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"},
            {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
            {"role": "user", "content": "Where was it played?"}
        ],
        max_tokens=60,
        n=1,
        stop=None,
        temperature=0.5,
    )
    # Send the response back to the user
    print(response)
    print(message)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response.choices[0].message.content)


if __name__ == '__main__':
    application = ApplicationBuilder().token(token).build()
    gpt_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), chatgpt)
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    application.add_handler(gpt_handler)
    
    application.run_polling()