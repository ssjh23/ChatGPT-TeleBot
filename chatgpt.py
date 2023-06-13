from enum import Enum
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    filters, 
    CommandHandler,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler, 
    Application,
    ContextTypes
)
import openai

END = "END"
class ChatGPT:
    def __init__(self, update:Update, context: ContextTypes.DEFAULT_TYPE, id:str, application:Application):
        self.update = update
        self.context = context
        self.id = id
        self.application = application
        self.messages = []
        self.max_tokens = 4000
        self.last_back_message = None

    async def run(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chatgpt_new_chat_welcome_text = "You are now on a new chat on chatgpt! Just start typing as you would using chatgpt"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=chatgpt_new_chat_welcome_text)
        await self.add_chat_handlers()
        # gpt_conv_handler = ConversationHandler(
        #     entry_points=[CommandHandler("gpt", self.chatgpt_menu)],
        #     states={
        #         SELECTING_ACTION: [CallbackQueryHandler(self.gpt_message_handler, pattern="^"+str(NEW_CHAT)+"$")],
        #         # SELECTING_ACTION:[CallbackQueryHandler(start_chat_gpt, pattern="^"+str(CHATGPT)+"$")]
        #     },
        #     fallbacks=[CallbackQueryHandler(self.end_chatgpt, pattern="^"+str(BACK)+"$")]
        # )
        # self.application.add_handler(gpt_conv_handler)
    async def add_chat_handlers(self):
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.gpt_message_handler))
    
    async def gpt_message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE): 
        if (self.last_back_message != None):
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=self.last_back_message)
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
                InlineKeyboardButton(text="Back", callback_data=str(END)),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        last_back_message = await context.bot.send_message(chat_id=update.effective_chat.id, text="Press to end the chat, Continue typing to continue the chat  ", reply_markup=reply_markup)
        self.last_back_message = last_back_message.message_id
        return END

    
    