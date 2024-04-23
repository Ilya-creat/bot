## LearnEnglishBot

Запуск бота осуществляется через команду:
```cmd
сd /<path>/<to>/<directory>
./main.py
```

Файл *cofig.py* содержит системные настройки, которые администратор изменяет вручную.
По умолчанию:

```json
BOT_TOKEN = "<token>" // telegram
PROGRESS = { // уровни прогресса пользователей
    "100": "beginner",
    "500": "student",
    "1200": "specialist",
    "3500": "expert",
    "6900": "candidate for the master",
    "12000": "master"
}

POINTS = { // основные баллы, по мимо индивидуальных
    "lesson": 0,
    "card": 5,
    "audio": 10,
    "question": 0
}

```