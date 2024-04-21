import requests as requests

from models.telegram_api import TgAPI


class ImageBan(TgAPI):
    def __init__(self, token):
        super().__init__(token)

    def get_image(self, url):
        if 'tg::' in url:
            return self.getFile(url[4:])
        else:
            s = requests.get(url).content
            return s
