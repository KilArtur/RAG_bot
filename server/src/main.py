from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, filters, Application, \
    CallbackQueryHandler

from config.Config import CONFIG

# Registered users dictionary
registered_users = {"admin": "Admin User"}

# Authorization state
user_auth_state = {}

async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    user_auth_state[user_id] = False
    await context.bot.send_message(
        chat_id=chat_id,
        text="Введите 'admin' для авторизации."
    )

async def handle_message(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    user_message = update.message.text

    if not user_auth_state.get(user_id, False):  # Check if the user is authorized
        if user_message == "admin":
            user_auth_state[user_id] = True
            registered_users[user_id] = update.effective_user.full_name
            await context.bot.send_message(chat_id=chat_id, text="Вы успешно авторизовались!")
        else:
            await context.bot.send_message(chat_id=chat_id, text="Неверный ввод. Введите 'admin' для авторизации.")
        return

    # If authorized, reply with message and options
    reply_text = f"Ваше сообщение: {user_message}"

    inline_keyboard = [
        [InlineKeyboardButton("Личный кабинет", callback_data="profile")],
        [InlineKeyboardButton("4 деканат", callback_data="dean_office")]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard)

    keyboard = [[KeyboardButton("Новый чат")]]
    reply_keyboard = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await context.bot.send_message(chat_id=chat_id, text=reply_text, reply_markup=reply_markup)
    await context.bot.send_message(chat_id=chat_id, text="Выберите действие:", reply_markup=reply_keyboard)

async def handle_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == "profile":
        await query.edit_message_text(text="Добро пожаловать в личный кабинет.")
    elif query.data == "dean_office":
        await query.edit_message_text(text="Добро пожаловать в 4 деканат.")

def main() -> None:
    """Start the bot."""
    application = Application.builder().token(CONFIG.bot_token).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(handle_callback))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
