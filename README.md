## LearnEnglishBot

Запуск бота осуществляется через команду:
```cmd
сd /<path>/<to>/<directory>
./main.py
```

Файл *config.py* содержит системные настройки, которые администратор изменяет вручную.
По умолчанию:

```angular2html
BOT_TOKEN = "<token>" // telegram
PROGRESS = { // уровни прогресса пользователей
    "100": "beginner",
    "500": "student",
    "1200": "specialist",
    "3500": "expert",
    "6900": "candidate for the master",
    "12000": "master"
}

POINTS = { // основные баллы, помимо индивидуальных
    "lesson": 0,
    "card": 5,
    "audio": 10,
    "question": 0
}
```

Загрузка карточек и аудио происходит через интерфейс telegram у администратора. Для загрузки уроков нужно воспользоваться JSON-файлом.
Возможная конфигурация:

```angular2html
{
    "name": "<название>",
    "text": "<текст>",
    "questions": [
        {
            "question": "<вопрос>",
            "answers": ["<ответ 1>", "<ответ 2>"],
            "correct": "<ответ 1>",
            "points": 0
        },
      ...
    ]
}
```
