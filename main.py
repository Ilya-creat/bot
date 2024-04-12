import logging
import random

from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, Bot, \
    InputMediaPhoto, InputMediaAudio
from telegram.ext import Application, MessageHandler, filters, CommandHandler, CallbackContext, CallbackQueryHandler

import config
from config import BOT_TOKEN
from models.audios import Audios
from models.imageban import ImageBan
from models.lessons import Lessons
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
lessons = Lessons()


def check_admin(user_model):
    return user_model.role != "admin"


def MarkdownV2(s):
    return re.escape(s)


async def cards_handler(update, context):
    global user
    global cards, bot
    keyboard_user = [[
        InlineKeyboardButton('Выйти', callback_data='exit'),
        InlineKeyboardButton('Далее', callback_data='next?cards')
    ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard_user)
    us_card = random.choice(cards.cards)
    s = imban.get_image(us_card.url)
    user = User(update.message.chat.id)
    user.completed_cards.add(us_card.id_)
    user.update_user()
    await bot.send_photo(chat_id=update.message.chat.id, photo=s, caption=f"*English*: {MarkdownV2(us_card.en)}\n"
                                                                          f"*Русский*: {MarkdownV2(us_card.ru)}\n*"
                                                                          f"Транскрипция*: "
                                                                          f"{MarkdownV2(us_card.transcription)}"
                         , reply_markup=reply_markup, parse_mode="MarkdownV2")


async def audio_handler(update, context):
    global audios, bot, user
    keyboard_user = [[
        InlineKeyboardButton('Выйти', callback_data='exit'),
        InlineKeyboardButton('Далее', callback_data='next?audio')
    ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard_user)
    us_audio = random.choice(audios.audios)
    s = open(us_audio.get_pwd(), 'rb')
    user = User(update.message.chat.id)
    user.completed_audio.add(us_audio.id_)
    user.update_user()
    print(user.completed_audio)
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


async def lesson_handler(update, context, id_=1, call_back=False):
    global lessons
    lesson = lessons.get_lesson(id_)
    keyboard = [[
        InlineKeyboardButton('Назад', callback_data=f'next?lessons&id=0'),
    ]
    ]
    if lesson.questions:
        keyboard[0].append(InlineKeyboardButton('Проверить себя', callback_data=f'next?question&idx={lesson.id_}'))
    reply_markup = InlineKeyboardMarkup(keyboard)
    if not call_back:
        if lesson.url:
            await bot.send_video(chat_id=update.message.chat.id,
                                 video=lesson.url, context=
                                 f"*Урок*: {MarkdownV2(lesson.name)}\n\n"
                                 f"{MarkdownV2(lesson.text)}",
                                 parse_mode="MarkdownV2",
                                 reply_markup=reply_markup
                                 )
        else:
            await bot.send_message(chat_id=update.message.chat.id,
                                   text=
                                   f"*Урок*: {MarkdownV2(lesson.name)}\n\n"
                                   f"{MarkdownV2(lesson.text)}",
                                   parse_mode="MarkdownV2",
                                   reply_markup=reply_markup
                                   )


async def question_handler(update, context, id_=0, idx=0, call_back=False):
    global lessons
    lesson = lessons.get_lesson(id_)
    question = lesson.questions

    if len(question) <= idx:
        await update.message.edit_text(text="Вы прошли все вопросы!")
        await lessons_handler(update, context)
    else:
        text = question[idx].question
        answer = question[idx].answer_corr
        keyboard = [
            [InlineKeyboardButton(i, callback_data=f'check?question&ans={i}&corr={answer}&id_={id_}&x={idx}')]
            for i in question[idx].answers
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if not call_back:
            await bot.send_message(
                chat_id=update.message.chat.id,
                text=
                f"*{MarkdownV2(text)}*",
                parse_mode="MarkdownV2",
                reply_markup=reply_markup
            )
        else:
            await update.message.edit_text(
                text=
                f"*{MarkdownV2(text)}*",
                parse_mode="MarkdownV2",
                reply_markup=reply_markup
            )


async def lessons_handler(update, context, id_=0, call_back=False):
    global bot, lessons, user
    cnt = len(lessons.lessons)
    rs = []
    if id_ != 0:
        rs.append(InlineKeyboardButton('Назад', callback_data=f'next?lessons&id={id_ - 1}'))

    rs.append(InlineKeyboardButton('Выйти', callback_data='exit'))
    if cnt - id_ * 5 - 5 > 0:
        rs.append(InlineKeyboardButton('Вперед', callback_data=f'next?lessons&id={id_ + 1}'))
    keyboard_user = [
        *[
            [InlineKeyboardButton(f'Урок {i + 1}. {lessons.lessons[i].name}',
                                  callback_data=f"lessons?text&id={lessons.lessons[i].id_}")]
            for i in range(id_ * 5, min(id_ + 5, cnt))
        ],
        [
            *rs
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard_user)
    if not call_back:
        await bot.send_message(chat_id=update.message.chat.id,
                               text="Выберите урок:", reply_markup=reply_markup)
    else:
        await update.message.edit_text(text="Выберите урок:",
                                       reply_markup=reply_markup)


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


async def profile_handler(update, context):
    global user
    user = User(update.message.chat.id)
    if check_admin(user):
        await update.message.reply_text(
            f"""
            *Ник*: {update.effective_user.name}\n
*Роль*: Пользователь
*Количество просмотренных карточек*: {len(user.completed_cards)}
*Количество прослушанных аудио*: {len(user.completed_audio)}
*Баллы*: {user.points}
*Звание*: {user.status}
            """
            , parse_mode='MarkdownV2')
    else:
        await update.message.reply_text(admin_msg)


async def check_message(update, context):
    print(update.message)
    if update.message.text == 'Уроки':
        await update.message.reply_text(
            "Вы вошли в режим изучения уроков 😄"
        )
        await lessons_handler(update, context)
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
    elif update.message.text == 'Профиль':
        await update.message.reply_text(
            "Вы вошли в профиль 😄"
        )
        await profile_handler(update, context)
    else:
        await update.message.reply_text("Неизвестная команда")


async def help_handler(update, context):
    global user
    user = User(update.message.chat.id)
    if check_admin(user):
        await update.message.reply_text(help_msg)
    else:
        await update.message.reply_text(admin_msg)


async def points(call, id_):
    global user
    user = User(id_)
    user.points += call.points + config.POINTS[call.type_]
    user.update_user()


async def callback_handler(update, context):
    global bot, user
    query = update.callback_query
    query.answer()
    choice = query.data
    user = User(update.callback_query.message.chat.id)
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
        user.completed_cards.add(us_card.id_)
        user.update_user()
        await points(us_card, update.callback_query.message.chat.id)
        await update.callback_query.message.edit_media(media=InputMediaPhoto(s))
        await update.callback_query.message.edit_caption(caption=f"""
        *English*: {MarkdownV2(us_card.en)}\n*Русский*: {MarkdownV2(us_card.ru)}\n*Транскрипция*: {
        MarkdownV2(us_card.transcription)}
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
        user.completed_audio.add(us_audio.id_)
        user.update_user()
        await points(us_audio, update.callback_query.message.chat.id)
        await update.callback_query.message.edit_media(media=InputMediaAudio(s))
        await update.callback_query.message.edit_caption(caption=f"""
        *English*: ||{MarkdownV2(us_audio.en)}||\n*Русский*: ||{MarkdownV2(us_audio.ru)}||\n
        """, reply_markup=reply_markup, parse_mode="MarkdownV2")
    elif choice.split('&')[0] == 'next?lessons':
        id_ = int(choice.split('&')[1].split('=')[1])
        await lessons_handler(update.callback_query, context, id_=id_, call_back=True)
    elif choice.split('&')[0] == 'lessons?text':
        id_ = int(choice.split('&')[1].split('=')[1])
        await lesson_handler(update.callback_query, context, id_=id_, call_back=False)
    elif choice.split('&')[0] == 'next?question':
        id_ = int(choice.split('&')[1].split('=')[1])
        await question_handler(update.callback_query, context, id_=id_, idx=0, call_back=False)
    elif choice.split('&')[0] == 'check?question':
        print(choice)
        ans = str(choice.split('&')[1].split('=')[1])
        corr = str(choice.split('&')[2].split('=')[1])
        id_ = int(choice.split('&')[3].split('=')[1])
        idx = int(choice.split('&')[4].split('=')[1])
        if ans == corr:
            global lessons
            lesson = lessons.get_lesson(id_)
            await points(lesson.questions[idx], update.callback_query.message.chat.id)
            await question_handler(update.callback_query, context, id_=id_, idx=idx + 1, call_back=True)
        else:
            await context.bot.answer_callback_query(callback_query_id=query.id,
                                                    text='Неверный ответ',
                                                    show_alert=True)
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
