from telegram import Update
from telegram.ext import filters, MessageHandler, Application, ContextTypes

class Chat:
    def __init__(self, id:str, application:Application):
        self.id = id
        self.application = application
        self.messages = []

    def run(self):
        gpt_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), self.chatgpt)
        self.application.add_handler(gpt_handler)
    
    async def chatgpt(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.messages.append({"role":"user", "content": update.message.text})
        print(self.messages)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")
    
    