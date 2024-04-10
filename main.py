import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler, CallbackContext
from config import BOT_TOKEN
from models.register import User

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
logger = logging.getLogger(__name__)
help_msg = (
    "/start - Перезапустить бота\n"
    "/help - Команды помощи\n"
)
admin_msg = (
    "/add {id_lessons} (add file .json)\n"
    "/delete {id_lessons}\n"
    "/add_q {id_lessons}\n"

)

user = None

async def help_handler(update, context):
    await update.message.reply_text(help_msg)


async def start_handler(update, context):
    global user
    print(update)
    user = User(update.message.chat.id)
    if user.status["role"] != "admin":
        await update.message.reply_text(f"""
            Привет {update.effective_user.name}!
        """)
    else:
        await update.message.reply_text(f"""
            Привет {update.effective_user.name}! (Админ)
            
        """)


async def echo(update, context):
    await update.message.reply_text(update.message.text)

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_handler))
    application.run_polling()


if __name__ == '__main__':
    main()