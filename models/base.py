import os
import sqlite3


class Base:
    def __init__(self):
        print(os.path.abspath("base/base.db"))
        self.db = sqlite3.connect(os.path.abspath("base/base.db"))
        self.cur_ = self.db.cursor()