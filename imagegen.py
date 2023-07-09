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
    CallbackQueryHandler,
    Application,
    ContextTypes
)
import openai

WELCOME = "WELCOME"
IMAGE_GEN = "IMAGE_GEN"
IMAGE_SIZE = "IMAGE_SIZE"
IMAGE_PROMPT = "IMAGE_PROMPT"
SELECTING_LEVEL = "SELECTING_LEVEL"
TYPING = "TYPING"
BACK_TO_START = "BACK_TO_START"

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
        self.imagegen_handlers = []
        self.welcome = False
    
    async def run(self):
        image_gen_welcome_text = "You are now using the Image Generation tool!"
        if (self.welcome == False):
            await self.context.bot.send_message(chat_id=self.update.effective_chat.id, text=image_gen_welcome_text)
            self.welcome = True
        await self.add_image_handlers()
        await self.image_gen_entry(update=self.update, context=self.context)

    # Saves the image prompt typed in by user, transits to image generation state
    async def ask_for_image_prompt(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        image_prompt_text = (
            "Type in your prompt for the image"
        )
        context.user_data[IMAGE_SIZE] = update.callback_query.data
        await update.callback_query.edit_message_text(text=image_prompt_text)
        return TYPING

    async def save_image_prompt(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            context.user_data[IMAGE_PROMPT] = update.message.text
            return await self.gen_image()\
        
        # Prevent the user from typing into the text box when choosing options
        except KeyError as e:
            await self.context.bot.send_message(chat_id=self.id, text="Please only select options from the message")
            return await self.image_gen_entry(update=self.update, context=self.context)

    async def image_gen_entry(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """Selecting Image Size"""
        image_size_text = (
            "Select an image size for the generated photo"
        )
        image_size_buttons = [
            [        
                InlineKeyboardButton(text="256", callback_data=str(ImageSize.SMALL.value)),
                InlineKeyboardButton(text="512", callback_data=str(ImageSize.MEDIUM.value)),
                InlineKeyboardButton(text="1024", callback_data=str(ImageSize.LARGE.value))
            ],
            [
                InlineKeyboardButton(text="Back", callback_data=str(BACK_TO_START))
            ]
        ]
        image_size_keyboard = InlineKeyboardMarkup(image_size_buttons)
        await context.bot.send_message(chat_id=self.id, text=image_size_text, reply_markup=image_size_keyboard)


    async def add_image_handlers(self):
        print(self.update.callback_query)
        ask_for_image_prompt_handler = CallbackQueryHandler(self.ask_for_image_prompt, pattern=f"^{ImageSize.SMALL.value}$|^{ImageSize.MEDIUM.value}$|^{ImageSize.LARGE.value}$")
        image_gen_entry_handler = CallbackQueryHandler(self.image_gen_entry, pattern="^" + str(IMAGE_GEN) + "$")
        save_image_prompt_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, self.save_image_prompt)
        image_gen_conv = ConversationHandler(
            entry_points=[ask_for_image_prompt_handler],
            states= {
                TYPING: [
                    save_image_prompt_handler
                ]
            },
            fallbacks = [

            ]
        )
        
        self.imagegen_handlers.append(ask_for_image_prompt_handler)
        self.imagegen_handlers.append(image_gen_entry_handler)
        self.imagegen_handlers.append(save_image_prompt_handler)
        self.imagegen_handlers.append(image_gen_conv)
        self.application.add_handlers(self.imagegen_handlers)

    def get_image_size(self):
        image_size_string = self.context.user_data[IMAGE_SIZE]
        image_size_param = f"{image_size_string}x{image_size_string}"
        return image_size_param
    
    def get_image_prompt(self):
        image_prompt = self.context.user_data[IMAGE_PROMPT]
        return image_prompt

    async def gen_image(self):
        print(self.context.user_data[IMAGE_PROMPT])
        print(self.context.user_data[IMAGE_SIZE])
        try:
            result = openai.Image.create(
                prompt=self.get_image_prompt(),
                n=2,
                size= self.get_image_size()
                )
            print(result)
            print("End")
            await self.context.bot.send_photo(chat_id=self.id, photo=result.data[0].url)
        except error as e:
            print(e)
    

    

    
