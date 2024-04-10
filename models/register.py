from models.base import Base
import json


class User(Base):
    def __init__(self, tg_id):
        super().__init__()
        data = self.get_user(tg_id)
        self._id = data[0]
        self.status = json.loads(str(data[2]))

    def get_user(self, _id):
        try:
            data = self.cur_.execute('SELECT * FROM users WHERE id_tg = ?', (_id,)).fetchone()
            if data is None:
                self.register(_id)
                data = self.cur_.execute('SELECT * FROM users WHERE id_tg = ?', (_id,)).fetchone()
            return data
        except Exception as e:
            print("User Error (get_user):", e)

    def register(self, _id):
        try:
            self.cur_.execute(f'INSERT INTO users VALUES (NULL, ?, ?)', (int(_id), json.dumps({
                "status": "beginner",
                "role": "user"
            })))
            self.db.commit()
        except Exception as e:
            print("User Error (register):", e)
