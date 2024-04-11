import requests as requests


class ImageBan:
    def get_image(self, url):
        s = requests.get(url).content
        return s