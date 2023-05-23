
import logging
from chatgpt import Chat
from telegram import Update, Bot
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, Application
from dotenv import load_dotenv
import os
import openai
max_tokens = 4097
application = None
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.effective_chat.id)
    global application
    chat = Chat(update.effective_chat.id, application)
    chat.run()
    # await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


# async def chatgpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     print("HERE")
#     messages.append({"role":"user", "content": update.message.text})
#     print(messages)
#     # Call the OpenAI API to generate a response
#     global max_tokens
#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=messages,
#             max_tokens=max_tokens,
#             n=1,
#             stop=None,
#             temperature=0.5,
#         )
#         print(response)
#         # Send the response back to the user
#         messages.append({"role":"assistant", "content": response.choices[0].message.content})
#         max_tokens - response.usage.total_tokens
#         await context.bot.send_message(chat_id=update.effective_chat.id, text=response.choices[0].message.content)
#     except openai.error.InvalidRequestError as e:
#         print(e)

if __name__ == '__main__':
    load_dotenv('/Users/seansoo/Documents/github-repos/ChatGPT-TeleBot/.env')
    token= os.getenv('TELEGRAM_BOT_TOKEN')
    # Set up the OpenAI API
    openai.api_key = os.getenv('OPENAI_TOKEN')
    application = ApplicationBuilder().token(token).build()
    start_handler = CommandHandler('start', start)
    # gpt_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), chatgpt)
    application.add_handler(start_handler)
    # application.add_handler(gpt_handler)
    application.run_polling()
    
