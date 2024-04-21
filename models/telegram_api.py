import requests


class TgAPI:
    def __init__(self, token):
        self.url = f'https://api.telegram.org/bot{token}'
        self.url_file = f'https://api.telegram.org/file/bot{token}'

    def getFile(self, id_):
        path = self.getFilePath(id_)
        ans = requests.get(self.url_file + f'/{path}').content
        return ans

    def getFilePath(self, id_):
        print(requests.get(self.url + f'/getFile?file_id={id_}').json())
        return requests.get(self.url + f'/getFile?file_id={id_}').json()["result"]["file_path"]