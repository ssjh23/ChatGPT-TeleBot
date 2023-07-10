
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    filters, 
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    Application,
    ContextTypes,
    CommandHandler
)
import openai

CHAT_GPT = "CHATGPT"
NEW_CHAT = "NEW_CHAT"
END_CHATGPT = "END_CHATGPT"
SELECTING_ACTION = "SELECTING_ACTION"
TYPING_PROMPT = "TYPING_PROMPT"
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
        chatgpt_new_chat_welcome_text = "You are now on a new chat on chatgpt! Just start typing /chatgpt to start. /back_to_menu to return to the main menu"
        await update.callback_query.edit_message_text(text=chatgpt_new_chat_welcome_text)
        await self.add_chat_handlers()

    async def add_chat_handlers(self):
        chat_gpt_entry_handler = CommandHandler("chatgpt", self.chat_gpt_entry)
        gpt_message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, self.gpt_message_handler)
        initial_prompt_handler = CallbackQueryHandler(self.ask_for_initial_prompt, pattern=f"^{NEW_CHAT}$")
        restart = CommandHandler("restart_chatgpt", self.restart)
            # ChatGPT Conversation
        chat_gpt_conv = ConversationHandler(
            entry_points=[chat_gpt_entry_handler],
            states={
                SELECTING_ACTION: [
                    initial_prompt_handler
                ],
                TYPING_PROMPT: [
                    gpt_message_handler
                ]
                
            },
            fallbacks=[
                restart
            ]
        )
        self.gpt_handlers.append(chat_gpt_conv)
        self.application.add_handler(chat_gpt_conv)
    
    async def restart(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.messages.clear()
        return await self.chat_gpt_entry(update=self.update, context=self.context)


    async def ask_for_initial_prompt(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_gpt_text = (
            "Type your initial prompt just like you would in chatgpt! To create a new chat, type /restart_chatgpt at any point. To return to the main menu, type /back_to_main"
        )
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=chat_gpt_text)
        return TYPING_PROMPT

    async def chat_gpt_entry(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """Choose to add a parent or a child."""
        chatgpt_menu_text = (
            "Start a new chat by clicking on the button below. Type /back_to_main to return to the main menu" 
            "Type /help for more info on the bot"
        )
        buttons = [
            [
                InlineKeyboardButton(text="New Chat", callback_data=str(NEW_CHAT)),
            ],
        ]
        chatgpt_keyboard = InlineKeyboardMarkup(buttons)
        await context.bot.send_message(chat_id=self.id, text=chatgpt_menu_text, reply_markup=chatgpt_keyboard)
        return SELECTING_ACTION
    
    async def gpt_message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE): 
        helper_text = (
            "Type /back_to_main or /restart_chatgpt to end this chat and go to the respective menus. Continue typing to continue the chat"
        )
            
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
            # Send the response back to the user
            self.messages.append({"role":"assistant", "content": response.choices[0].message.content})
            self.max_tokens = self.max_tokens - response.usage.total_tokens
            await self.context.bot.send_message(chat_id=self.id, text=response.choices[0].message.content)
            last_helper_message = await self.context.bot.send_message(chat_id=self.id, text=helper_text)
            self.last_back_message_id = last_helper_message.message_id
            return TYPING_PROMPT
            # await back_to_menu_option_handler(self.update, self.context)
        except openai.error.InvalidRequestError as e:
            print(e)
        
    
    async def remove_chatgpt_handlers(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        for handler in self.gpt_handlers:
            self.application.remove_handler(handler=handler)
        self.messages.clear()
        self.gpt_handlers.clear()
        return 

    
    