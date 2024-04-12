import json

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
        ans = self.cur_.execute(
            f"SELECT * FROM lessons"
        ).fetchall()
        res = []
        for i in ans:
            print(i[4])
            res.append(Lesson(*i[:4], [Question(*self.get_question(j)) for j in json.loads(i[4])["questions"]] if i[4]
                       else [], *i[5:]))
        return res

    def get_lesson(self, id_):
        for i in self.lessons:
            if i.id_ == id_:
                return i

    def get_question(self, id_):
        ans = self.cur_.execute(
            f"SELECT * FROM questions WHERE id = ?", (id_,)
        ).fetchone()
        return ans
