import os

from models.base import Base


class Audio:
    def __init__(self, id_, url, en, ru, type_=None, points=0):
        super().__init__()
        self.id_ = id_
        self.url = url
        self.en = en
        self.ru = ru
        self.type_ = type_
        self.points = points

    def get_pwd(self):
        return f'{os.path.abspath("audios/" + self.url)}'


class Audios(Base):
    def __init__(self):
        super().__init__()
        self.audios = self.get_audios()

    def get_audios(self):
        try:
            results = self.cur_.execute(
                "SELECT * FROM audios"
            ).fetchall()
            ans = []
            for i in results:
                ans.append(Audio(*i))
            return ans
        except Exception as e:
            print("Cards Error (get_cards):", e)
