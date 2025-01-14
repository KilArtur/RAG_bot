from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, filters, Application, \
    CallbackQueryHandler
from twisted.internet.defer import passthru

from bot.BaseBotModule import BaseBotModule
from config.Config import CONFIG
from services.GPTService import GPTService
from services.QueryService import QueryService
from services.RAGService import RAGService
from services.context_var import request_id_var
from services.registry import REGISTRY
from utils.logger import get_logger

log = get_logger("main")

request_id = 0

async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id


async def handle_message(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    user_message = update.message.text
    log.info(f"Запрос от пользователя:\n{user_message}\nИз чата:\n{chat_id}")
    query_service: QueryService = REGISTRY.get(QueryService)
    await query_service.process(user_message, update,context)

async def handle_callback(update: Update, context: CallbackContext):
    global request_id

    request_id += 1
    request_id_var.set(request_id)

    query = update.callback_query
    await query.answer()

def main() -> None:
    """Start the bot."""
    REGISTRY.put(GPTService())
    REGISTRY.put(RAGService())
    REGISTRY.put(QueryService())
    print("Starting server ...")
    application = Application.builder().token(CONFIG.bot_token).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_callback))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()


class BotClass:

    def start(self):
        get_user = ""
        action = get_user.pipeline()


    def __init__(self):
        application = Application.builder().token(CONFIG.bot_token).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_handler(CallbackQueryHandler(handle_callback))

        application.run_polling(allowed_updates=Update.ALL_TYPES)

class UserModule:
    chat_id = ""
    user = UserClass()


    def start(self):
        action