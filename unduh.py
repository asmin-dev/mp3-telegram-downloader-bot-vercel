from bs4 import BeautifulSoup as bs
import requests

requests.urllib3.disable_warnings()


class Main:
    def __init__(self):
        self.__url = "https://www.downloadlagu321.net"

    def get_data(self, query):
        array = []
        data = requests.get(
            self.__url + "/api/search/%s" % query.replace(" ", "%20"), verify=False
        ).json()
        array.extend(
            [
                {
                    "judul": item.get("title"),
                    "id": item.get("id"),
                }
                for item in data
            ]
        )
        return array

    def get_source(self, raw_link):
        a = bs(
            requests.get(
                "https://www.yt2mp3s.me/api/button/mp3/" + raw_link).content,
            "html.parser",
        )
        for i in a.find_all('a', {'class': 'shadow-xl'}):
            if '128 kbps' in str(i):
                return i.get('href')
