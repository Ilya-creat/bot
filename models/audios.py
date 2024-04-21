import os

from models.base import Base
from models.telegram_api import TgAPI


class Audio:
    def __init__(self, id_, url, en, ru, type_=None, points=0):
        super().__init__()
        self.id_ = id_
        self.url = url
        self.en = en
        self.ru = ru
        self.type_ = type_
        self.points = points

    def get_pwd(self, TOKEN):
        if "tg::" in self.url:
            return TgAPI(TOKEN).getFile(self.url[4:])
        else:
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

    def reloads_cards(self):
        self.audios = self.get_audios()

    def post_audio(self, TOKEN):
        try:
            self.cur_.execute("INSERT INTO audios VALUES (NULL, ?, ?, ?, 'audio', 0)",
                              (TOKEN[1], TOKEN[2], TOKEN[3]))
            self.db.commit()
            self.reloads_cards()
        except Exception as e:
            print("Cards Error (post_card):", e)

    def delete(self, id_):
        try:
            self.cur_.execute("DELETE FROM audios WHERE id=?", (id_, ))
            self.db.commit()
            self.reloads_cards()
        except Exception as e:
            print("Cards Error (delete):", e)