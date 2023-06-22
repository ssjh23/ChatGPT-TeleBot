from enum import Enum
import logging
import time
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    error
)
from telegram.ext import (
    filters, 
    ConversationHandler,
    MessageHandler, 
    Application,
    ContextTypes
)
import openai

END = ConversationHandler.END
class ChatGPT:
    def __init__(self, update:Update, context: ContextTypes.DEFAULT_TYPE, id:str, application:Application):
        self.update = update
        self.context = context
        self.id = id
        self.application = application
        self.messages = []
        self.max_tokens = 4000
        self.last_back_message_id = None
        self.gpt_handlers = []

    async def run(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chatgpt_new_chat_welcome_text = "You are now on a new chat on chatgpt! Just start typing as you would using chatgpt"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=chatgpt_new_chat_welcome_text)
        await self.add_chat_handlers()

    async def add_chat_handlers(self):
        gpt_message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, self.gpt_message_handler)
        self.gpt_handlers.append(gpt_message_handler)
        self.application.add_handler(gpt_message_handler)
    
    async def gpt_message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE): 
        if (self.last_back_message_id != None):
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=self.last_back_message_id)
        self.messages.append({"role":"user", "content": update.message.text})
        # Call the OpenAI API to generate a response
        global max_tokens
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.messages,
                max_tokens=self.max_tokens,
                n=1,
                stop=None,
                temperature=0.5,
            )
            print(response)
            # Send the response back to the user
            self.messages.append({"role":"assistant", "content": response.choices[0].message.content})
            self.max_tokens = self.max_tokens - response.usage.total_tokens
            await self.context.bot.send_message(chat_id=update.effective_chat.id, text=response.choices[0].message.content)
            await self.back_to_menu_option_handler(self.update, self.context)
        except openai.error.InvalidRequestError as e:
            print(e)
        
    async def back_to_menu_option_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        buttons = [
            [
                InlineKeyboardButton(text="Back", callback_data="END_CHATGPT"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        last_back_message = await context.bot.send_message(chat_id=update.effective_chat.id, text="Press to end the chat, Continue typing to continue the chat  ", reply_markup=reply_markup)
        self.last_back_message_id = last_back_message.message_id
        return
    
    async def remove_chatgpt_handlers(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        for handler in self.gpt_handlers:
            self.application.remove_handler(handler=handler)
        self.messages.clear()
        self.gpt_handlers.clear()
        return 

    # def retry_on_error(func, wait=0.1, retry=0, *args, **kwargs):
    #     i = 0
    #     while True:
    #         try:
    #             return func(*args, **kwargs)
    #         except error.NetworkError:
    #             logging.exception(f"Network Error. Retrying...{i}")
    #             i += 1
    #             time.sleep(wait)
    #             if retry != 0 and i == retry:
    #                 break
    
    