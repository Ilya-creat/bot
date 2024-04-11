import logging
import random

from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, Bot, \
    InputMediaPhoto, InputMediaAudio
from telegram.ext import Application, MessageHandler, filters, CommandHandler, CallbackContext, CallbackQueryHandler

import config
from config import BOT_TOKEN
from models.audios import Audios
from models.imageban import ImageBan
from models.user import User
from models.сards import Cards
import re

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
    "/add_q {id_lessons} {question} {points} [ans1, ans2, ans3, ans4]\n"
    "/delete {id_question}\n"
    "/info_question_id\n"
)

user = None
cards = Cards()
audios = Audios()
imban = ImageBan()
bot = Bot(token=BOT_TOKEN)


def check_admin(user_model):
    return user_model.role != "admin"


def MarkdownV2(s):
    return re.escape(s)


async def cards_handler(update, context):
    global cards, bot
    keyboard_user = [[
        InlineKeyboardButton('Выйти', callback_data='exit'),
        InlineKeyboardButton('Далее', callback_data='next?cards')
    ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard_user)
    us_card = random.choice(cards.cards)
    s = imban.get_image(us_card.url)
    await bot.send_photo(chat_id=update.message.chat.id, photo=s, caption=f"""
    *English*: {MarkdownV2(us_card.en)}\n*Русский*: {MarkdownV2(us_card.en)}\n*Транскрипция*: {MarkdownV2(us_card.transcription.en)}
    """, reply_markup=reply_markup, parse_mode="MarkdownV2")


async def audio_handler(update, context):
    global audios, bot
    keyboard_user = [[
        InlineKeyboardButton('Выйти', callback_data='exit'),
        InlineKeyboardButton('Далее', callback_data='next?audio')
    ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard_user)
    us_audio = random.choice(audios.audios)
    s = open(us_audio.get_pwd(), 'rb')
    await bot.send_audio(chat_id=update.message.chat.id, audio=s, caption=f"""
    *English*: ||{MarkdownV2(us_audio.en)}||\n*Русский*: ||{MarkdownV2(us_audio.ru)}||\n
    """, reply_markup=reply_markup, parse_mode="MarkdownV2")


async def start_handler(update, context):
    global user
    user = User(update.message.chat.id)
    keyboard_user = [[
        KeyboardButton('Уроки'),
        KeyboardButton('Карточки'),
        KeyboardButton('Аудио')
    ],
        [KeyboardButton('Профиль')]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard_user, resize_keyboard=True)
    if check_admin(user):
        await update.message.reply_text(f"""
        Привет {update.effective_user.name}!\nВыбери режим:
        """, reply_markup=reply_markup)
    else:
        await update.message.reply_text(f"""
            Привет {update.effective_user.name}! (Админ)
        """)


async def start_handler_load(update, context):
    global user
    user = User(update.message.chat.id)
    keyboard_user = [[
        KeyboardButton('Уроки'),
        KeyboardButton('Карточки'),
        KeyboardButton('Аудио')
    ],
        [KeyboardButton('Профиль')]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard_user, resize_keyboard=True)
    if check_admin(user):
        await update.message.reply_text(f"""
        Выбери режим:
        """, reply_markup=reply_markup)
    else:
        await update.message.reply_text(f"""
            Привет {update.effective_user.name}! (Админ)
        """)


async def check_message(update, context):
    print(update.message)
    if update.message.text == 'Уроки':
        await update.message.reply_text("СКОРО")
    elif update.message.text == 'Карточки':
        await update.message.reply_text(
            "Вы вошли в режим изучения по карточкам 😄"
        )
        await cards_handler(update, context)
    elif update.message.text == 'Аудио':
        await update.message.reply_text(
            "Вы вошли в режим изучения по аудио 😄"
        )
        await audio_handler(update, context)
    else:
        await update.message.reply_text("Неизвестная команда")


async def help_handler(update, context):
    global user
    user = User(update.message.chat.id)
    if check_admin(user):
        await update.message.reply_text(help_msg)
    else:
        await update.message.reply_text(admin_msg)


async def profile_handler(update, context):
    global user
    user = User(update.message.chat.id)
    if check_admin(user):
        await update.message.reply_text(
            f"""
            Ник: {update.effective_user.name}\n
            Роль: Пользователь\n
            Количество просмотренных карточек: {user.completed_cards}\n
            """
        )
    else:
        await update.message.reply_text(admin_msg)

async def points(call, id_):
    global user
    user = User(id_)
    user.points += call.points + config.POINTS[call.type_]
    user.update_user()


async def callback_handler(update, context):
    global bot
    query = update.callback_query
    query.answer()
    print(query)
    choice = query.data
    if choice == 'next?cards':
        global cards
        keyboard_user_cards = [[
            InlineKeyboardButton('Выйти', callback_data='exit'),
            InlineKeyboardButton('Далее', callback_data='next?cards')
        ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard_user_cards)
        us_card = random.choice(cards.cards)
        s = imban.get_image(us_card.url)
        await points(us_card, update.callback_query.message.chat.id)
        await update.callback_query.message.edit_media(media=InputMediaPhoto(s))
        await update.callback_query.message.edit_caption(caption=f"""
        *English*: {MarkdownV2(us_card.en)}\n*Русский*: {MarkdownV2(us_card.en)}\n*Транскрипция*: {
        MarkdownV2(us_card.transcription.en)}
    """, reply_markup=reply_markup, parse_mode="MarkdownV2")
    elif choice == 'next?audio':
        global audios
        keyboard_user_audio = [[
            InlineKeyboardButton('Выйти', callback_data='exit'),
            InlineKeyboardButton('Далее', callback_data='next?audio')
        ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard_user_audio)
        us_audio = random.choice(audios.audios)
        s = open(us_audio.get_pwd(), 'rb')
        await points(us_audio, update.callback_query.message.chat.id)
        await update.callback_query.message.edit_media(media=InputMediaAudio(s))
        await update.callback_query.message.edit_caption(caption=f"""
        *English*: ||{MarkdownV2(us_audio.en)}||\n*Русский*: ||{MarkdownV2(us_audio.ru)}||\n
        """, reply_markup=reply_markup, parse_mode="MarkdownV2")
    elif choice == 'exit':
        await update.callback_query.message.delete()
        await bot.send_message(text="Выберите режим:", chat_id=update.callback_query.message.chat.id)
    else:
        await bot.send_message(text="<Бот не распознал *?*>", chat_id=update.callback_query.message.chat.id)


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(MessageHandler(filters.TEXT, check_message))
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.run_polling()


if __name__ == '__main__':
    main()
