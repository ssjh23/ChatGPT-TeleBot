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

class ImageSize(Enum):
    SMALL = 256
    MEDIUM = 512
    LARGE = 1024

class ImageGen:
    def __init__(self, update:Update, context: ContextTypes.DEFAULT_TYPE, id:str, application:Application):
        self.update = update
        self.context = context
        self.id = id
        self.application = application
        self.messages = []
        self.max_tokens = 4000
        self.last_back_message_id = None
        self.gpt_handlers = []
    
    async def run(self):
        print("HEre")
        try:
            result = openai.Image.create(
                prompt="A cute baby sea otter",
                n=2,
                size="1024x1024"
                )
            print(result)
            print("End")
            await self.context.bot.send_photo(chat_id=self.id, photo=result.data[0].url)
        except error as e:
            print(e)

    
