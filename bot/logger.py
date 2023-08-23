import logging
from functools import wraps
from telegram import Update

# Configure logging to control how log messages are recorded
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO,
    handlers=[
        logging.FileHandler("telebot.log"),     # save to .log file
        logging.StreamHandler()
    ]
)

class UserActionLogger:
    def __init__(self, action):
        self.action = action
        self.logger = logging.getLogger()

    # main method wrapper
    def __call__(self, func):
        @wraps(func)
        def wrapper(update: Update, context, *args, **kwargs):
            
            if hasattr(update, "message"):
                chat = update.message.chat
                user_input = update.message.text
                log_message = f"User '{chat.username}' in chat '{chat.id}' performed '{user_input}' - {self.action}"

            logging.info(log_message)

            return func(update, context, *args, **kwargs)
        return wrapper
    
    # logging methods for inline cases
    def log_bot(self, username, chatid, action):
        log_message = f"User '{username}' in chat '{chatid}': BOT {action}"
        logging.info(log_message)

    def error(self, error_msg, exc_info):
        logging.error(msg=error_msg, exc_info=exc_info)

    def log_inline(self, username, chatid, action):
        log_message = f"User '{username}' in chat '{chatid}' clicked on inline '{action}'"
        logging.info(log_message)
    
    def log_action(self, username, chatid, action):
        log_message = f"User '{username}' in chat '{chatid}' typed in '{action}'"
        logging.info(log_message)