import json

import requests

from models.telegram_api import TgAPI
from models.base import Base


class Lesson:
    def __init__(self, id_, name, text, url, questions, type_="lesson", points=0):
        self.id_ = id_
        self.name = name
        self.text = text
        self.url = url
        self.type = type_
        self.points = points
        self.questions = questions


class Question:
    def __init__(self, id_, question, answers, answer_corr, type_='question', points=0):
        self.id_ = id_
        self.question = question
        self.answers = json.loads(answers)["answers"]
        self.answer_corr = answer_corr
        self.type_ = type_
        self.points = points


class Lessons(Base):
    def __init__(self):
        super().__init__()
        self.lessons = self.get_lessons()

    def get_lessons(self):
        try:
            ans = self.cur_.execute(
                f"SELECT * FROM lessons"
            ).fetchall()
            res = []
            for i in ans:
                print(i[4])
                res.append(
                    Lesson(*i[:4], [Question(*self.get_question(j)) for j in json.loads(i[4])["questions"]] if i[4]
                    else [], *i[5:]))
            return res
        except Exception as e:
            print("Lessons Error (get_lessons):", e)

    def get_lesson(self, id_):
        try:
            for i in self.lessons:
                if i.id_ == id_:
                    return i
        except Exception as e:
            print("Lessons Error (get_lesson):", e)

    def get_question(self, id_):
        try:
            ans = self.cur_.execute(
                f"SELECT * FROM questions WHERE id = ?", (id_,)
            ).fetchone()
            return ans
        except Exception as e:
            print("Lessons Error (get_lessons):", e)

    def post_lesson(self, TOKEN, id_):
        try:
            file = json.loads(TgAPI(TOKEN).getFile(id_))
            if not file["name"] or not file["text"] or not file["questions"]:
                return {
                    "result": "error",
                    "error": f'not file["name"] or not file["text"] or not file["questions"]'
                }
            name = file["name"]
            text = file["text"]
            questions = file["questions"]
            q_id = []
            for i in range(len(questions)):
                self.cur_.execute(
                    "INSERT INTO questions VALUES (NULL, ?, ?, ?, 'question', ?)",
                    (
                        questions[i]["question"],
                        json.dumps({
                            "answers": list(questions[i]["answers"])
                        }),
                        questions[i]["correct"],
                        questions[i]["points"])
                )
                q_id.append(self.cur_.lastrowid)
            self.db.commit()
            self.cur_.execute(
                "INSERT INTO lessons VALUES (NULL, ?, ?, NULL, ?, 'lesson', 0)",
                (
                    name,
                    text,
                    json.dumps({
                        "questions": list(q_id)
                    })
                )
            )

            self.db.commit()
            self.reload()
            return {
                "result": "ok",
                "error": None
            }
        except Exception as e:
            print("Lessons Error (add_lesson):", e)
            return {
                "result": "error",
                "error": e
            }

    def delete(self, id_):
        try:
            lesson = None
            for i in self.lessons:
                if i.id_ == id_:
                    lesson = i
            self.cur_.execute(
                "DELETE FROM lessons WHERE id = ?",
                (lesson.id_, )
            )
            for i in lesson.questions:
                self.cur_.execute(
                    "DELETE FROM questions WHERE id = ?",
                    (i,)
                )
            self.db.commit()
            self.reload()
            return {
                "result": "ok",
                "error": None,
            }
        except Exception as e:
            print("Lessons Error (add_lesson):", e)
            return {
                "result": "error",
                "error": e
            }

    def reload(self):
        self.lessons = self.get_lessons()