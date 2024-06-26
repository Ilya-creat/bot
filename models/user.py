import config
from models.base import Base
import json


class User(Base):
    def __init__(self, tg_id):
        super().__init__()
        data = self.get_user(tg_id)
        self.id_ = data[0]
        stat = json.loads(str(data[2]))
        self.status = stat["status"]
        self.role = stat["role"]
        self.completed_cards = set(stat["cards"])
        self.completed_audio = set(stat["audio"])
        self.points = stat["points"]

    def get_user(self, _id):
        try:
            data = self.cur_.execute('SELECT * FROM users WHERE id_tg = ?', (_id,)).fetchone()
            if data is None:
                self.register(_id)
                data = self.cur_.execute('SELECT * FROM users WHERE id_tg = ?', (_id,)).fetchone()
            return data
        except Exception as e:
            print("User Error (get_user):", e)

    def update_user(self):
        try:
            for k, v in config.PROGRESS.items():
                if int(k) > self.points:
                    self.status = v
                    break
            self.cur_.execute('UPDATE users SET status = ? WHERE id = ?',
                              (
                                  json.dumps({
                                      "status": self.status,
                                      "role": self.role,
                                      "points": self.points,
                                      "cards": list(self.completed_cards),
                                      "audio": list(self.completed_audio),
                                      "lessons": list()}), self.id_
                              ))
            self.db.commit()
        except Exception as e:
            print("User Error (update_user):", e)

    def register(self, _id):
        try:
            self.cur_.execute(f'INSERT INTO users VALUES (NULL, ?, ?)', (int(_id), json.dumps({
                "status": "beginner",
                "role": "user",
                "points": 0, "cards": list(),
                "audio": list(),
                "lessons": list()})))
            self.db.commit()
        except Exception as e:
            print("User Error (register):", e)

    def admin_users_info(self):
        try:
            data = self.cur_.execute('SELECT * FROM users').fetchall()
            res = []
            for i in data:
                res.append(i)
            return res
        except Exception as e:
            print("User Error (admin_users_info):", e)

