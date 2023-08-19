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
from logger import UserActionLogger
import openai

CHAT_GPT = "CHATGPT"
NEW_CHAT = "NEW_CHAT"
END_CHATGPT = "END_CHATGPT"
SELECTING_ACTION = "SELECTING_ACTION"
TYPING_PROMPT = "TYPING_PROMPT"

START_CHATGPT_COMMAND = "chatgpt"
BACK_TO_MAIN_COMMAND = "back_to_main"
RESTART_CHATGPT_COMMAND = "restart_chatgpt"

class ChatGPT:
    def __init__(self, update:Update, context: ContextTypes.DEFAULT_TYPE, username:str, id:str, application:Application, logger:UserActionLogger):
        self.update = update
        self.context = context
        self.username = username
        self.id = id    # unique chatid
        self.application = application
        self.logger = logger
        self.messages = []
        self.max_tokens = 4000
        self.last_back_message_id = None
        self.gpt_handlers = []

    async def run(self):
        self.logger.log_inline('%s', self.username, self.id, CHAT_GPT)
        
        chatgpt_new_chat_welcome_text = (
            f"You are now on a new chat on ChatGPT!\n"
            f"Type /{START_CHATGPT_COMMAND} to start.\n"
            f"Type /{BACK_TO_MAIN_COMMAND} to return to the main menu."
        )
        await self.update.callback_query.edit_message_text(text=chatgpt_new_chat_welcome_text)
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
    
    async def chat_gpt_entry(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """Choose to add a parent or a child."""
        self.logger.log_action('%s', self.username, self.id, '/chatgpt')
        
        chatgpt_menu_text = (
            f"Start a new chat by clicking on the button below.\n"
            f"Type /{BACK_TO_MAIN_COMMAND} to return to the main menu.\n"
            "Type /help for more info on the bot."
        )
        buttons = [
            [
                InlineKeyboardButton(text="New Chat", callback_data=str(NEW_CHAT)),
            ],
        ]
        chatgpt_keyboard = InlineKeyboardMarkup(buttons)
        await context.bot.send_message(chat_id=self.id, text=chatgpt_menu_text, reply_markup=chatgpt_keyboard)
        return SELECTING_ACTION 
    
    # handler applicable to 'New Chat'
    async def ask_for_initial_prompt(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.logger.log_inline('%s', self.username, self.id, NEW_CHAT)
        
        chat_gpt_text = (
            f"Type your initial prompt just like you would in ChatGPT!\n"
            f"To restart to a new chat, type /{RESTART_CHATGPT_COMMAND} at any point.\n"
            f"Type /{BACK_TO_MAIN_COMMAND} to return to the main menu.\n"
        )
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=chat_gpt_text)
        return TYPING_PROMPT

    # handler called everytime ChatGPT generates a response
    async def gpt_message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE): 
        # default helper text with each response sent
        helper_text = (
            f"Type /{RESTART_CHATGPT_COMMAND} to restart to a new chat.\n"
            f"Type /{BACK_TO_MAIN_COMMAND} to return to the main menu.\n"
            f"Continue typing to continue this chat."
        )
            
        if (self.last_back_message_id != None):
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=self.last_back_message_id)
        self.messages.append({"role":"user", "content": update.message.text})
        self.logger.log_action('%s', self.username, self.id, update.message.text)
        # Call the OpenAI API to generate a response
        global max_tokens
        
        self.logger.log_bot('%s', self.username, self.id, 'generating ChatGPT response')
        
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
            tokens_used = response.usage.total_tokens
            self.max_tokens = self.max_tokens - tokens_used
            await self.context.bot.send_message(chat_id=self.id, text=response.choices[0].message.content)
            
            self.logger.log_bot('%s', self.username, self.id, f'ChatGPT response generated ({tokens_used}) - {self.max_tokens} tokens remaining')
            last_helper_message = await self.context.bot.send_message(chat_id=self.id, text=helper_text)
            self.last_back_message_id = last_helper_message.message_id
            return TYPING_PROMPT
            # await back_to_menu_option_handler(self.update, self.context)
        except openai.error.InvalidRequestError as e:
            print(e)

    async def restart(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.logger.log_action('%s', self.username, self.id, '/restart_chatgpt')
        self.messages.clear()
        return await self.chat_gpt_entry(update=self.update, context=self.context)
    
    async def remove_chatgpt_handlers(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        for handler in self.gpt_handlers:
            self.application.remove_handler(handler=handler)
        self.messages.clear()
        self.gpt_handlers.clear()
        return 
    