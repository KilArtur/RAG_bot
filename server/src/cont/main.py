from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (Application, CommandHandler, MessageHandler,
                          filters, ContextTypes, ConversationHandler)
from db import register_student, register_employee, add_question, get_student_by_name

MENU, REGISTER, QUESTION = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [
        ["Зарегистрироваться", "Войти как студент", "Войти как сотрудник кафедры", "Войти как сотрудник деканата"]
    ]
    await update.message.reply_text(
        "Добро пожаловать! Выберите действие:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return MENU

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_choice = update.message.text
    if user_choice == "Зарегистрироваться":
        await update.message.reply_text("Введите ваше ФИО:")
        return REGISTER
    elif user_choice == "Войти как студент":
        await update.message.reply_text("Введите ваше ФИО:")
        return REGISTER
    elif user_choice in ["Войти как сотрудник кафедры", "Войти как сотрудник деканата"]:
        context.user_data['role'] = user_choice
        await update.message.reply_text("Введите ваше ФИО:")
        return REGISTER
    return ConversationHandler.END

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_name = update.message.text.strip()
    context.user_data['name'] = user_name

    await update.message.reply_text("Введите вашу группу:")
    return 1

async def get_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    group = update.message.text.strip()
    context.user_data['group'] = group

    await update.message.reply_text("Введите вашу кафедру:")
    return 2

async def get_department(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    department = update.message.text.strip()
    context.user_data['department'] = department

    user_name = context.user_data['name']
    group = context.user_data['group']
    department = context.user_data['department']
    user_role = context.user_data.get('role')

    if user_role == "Войти как студент":
        register_student(user_name, group, department)
    elif user_role in ["Войти как сотрудник кафедры", "Войти как сотрудник деканата"]:
        register_employee(user_name, group, department)

    await update.message.reply_text(f"Регистрация прошла успешно! Добро пожаловать, {user_name}.")
    return ConversationHandler.END

async def question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_name = context.user_data.get('name')
    if not user_name:
        await update.message.reply_text("Пожалуйста, сначала зарегистрируйтесь.")
        return MENU

    question_text = update.message.text
    user_id = context.user_data.get('id')

    if user_id:
        add_question(question_text, user_id)
    else:
        add_question(question_text, None)

    await update.message.reply_text("Ваш вопрос отправлен.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Действие отменено.")
    return ConversationHandler.END

def main():
    application = Application.builder().token("7798142780:AAEJM-FeNJbI4J3QQNOPAh4O9Ki_JRh45a8").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu)],
            REGISTER: [MessageHandler(filters.TEXT & ~filters.COMMAND, register)],
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_group)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_department)],
            QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, question)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
