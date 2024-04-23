from models.base import Base


class Card:
    def __init__(self, id_, url, en, ru, transcription=None, type_=None, points=0):
        super().__init__()
        self.id_ = id_
        self.url = url
        self.en = en
        self.ru = ru
        self.transcription = transcription
        self.type_ = type_
        self.points = points


class Cards(Base):
    def __init__(self):
        super().__init__()
        self.cards = self.get_cards()

    def get_cards(self):
        try:
            results = self.cur_.execute(
                "SELECT * FROM cards"
            ).fetchall()
            ans = []
            for i in results:
                ans.append(Card(*i))
            return ans
        except Exception as e:
            print("Cards Error (get_cards):", e)

    def reload(self):
        self.cards = self.get_cards()

    def post_card(self, TOKEN):
        try:
            self.cur_.execute("INSERT INTO cards VALUES (NULL, ?, ?, ?, ?, 'card', 0)",
                              (TOKEN[1], TOKEN[2], TOKEN[3], TOKEN[4]))
            self.db.commit()
            self.reload()
        except Exception as e:
            print("Cards Error (post_card):", e)

    def delete(self, id_):
        try:
            self.cur_.execute("DELETE FROM cards WHERE id=?", (id_, ))
            self.db.commit()
            self.reload()
        except Exception as e:
            print("Cards Error (delete):", e)