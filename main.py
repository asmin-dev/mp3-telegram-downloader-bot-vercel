from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from flask import Flask, request
from unduh import Main
import requests
import telepot
import time
import os

app = Flask(__name__)

bot = telepot.Bot("1468139592:AAFoNdHFTpOWWeYQAyT4yAWbQ3Y6mPb-j_0")

__MESSAGES_NOW__ = []


class Downloader:
    def __init__(self, Token: None = str):
        self.__position = []
        self._bot = None
        self._song = Main()

    def _received_msg(self, new_msg):
        uid = new_msg["from"]["id"]
        if "reply_markup" in str(new_msg):
            for count, msg in enumerate(__MESSAGES_NOW__):
                if msg["uid"] == uid:
                    __MESSAGES_NOW__.pop(count)  # Delete element if user reply
                    delete = msg["identifier"]
                    for item in new_msg["message"]["reply_markup"]["inline_keyboard"]:
                        if item[0]["callback_data"] == new_msg["data"]:
                            judul = item[0]["text"]
                            ident = telepot.message_identifier(delete)
                            bot.editMessageReplyMarkup(
                                ident, reply_markup=None)
                            bot.editMessageText(
                                msg_identifier=ident, text="Downloading %s" % judul
                            )
                            url = self._song.get_source(new_msg["data"])
                            a = requests.get(url).content
                            now = str(int(time.time())) + ".mp3"
                            with open(now, "wb") as f:
                                f.write(a)
                            bot.sendAudio(uid, open(now, "rb"), title=judul)
                            os.system("rm " + now)
                            return
            return
        else:
            pesan = new_msg.get("text")
            if pesan:
                if len(self.__position) != 0 and str(uid) in str(self.__position):
                    [
                        self.__position.pop(count)
                        for count, item in enumerate(self.__position)
                        if item["uid"] == uid
                    ]  # Delete element if user reply
                    self._unduh(uid, pesan)
                else:

                    if pesan.startswith("/dl"):
                        query = pesan.split(" ", maxsplit=1)
                        if len(query) != 2:
                            markup = ForceReply(selective=False)
                            bot.sendMessage(
                                uid,
                                "Ok, berikan saya judul lagu yang mau dicari",
                                reply_markup=markup,
                            )
                            self.__position.append(
                                dict(uid=uid, position="waitmsg"))
                        else:
                            self._unduh(uid, query[1])
                    else:
                        bot.sendMessage(uid, "Pesan tidak dikenali")
            else:
                bot.sendMessage(
                    uid, "Bot hanya mengenali pesan yang berupa text ")

    def _unduh(self, uid, query):
        arr = []
        results = self._song.get_data(query)
        for item in results:
            arr.append(
                [InlineKeyboardButton(text=item["judul"],
                                      callback_data=item["id"])]
            )
        markup = InlineKeyboardMarkup(inline_keyboard=arr)
        text = bot.sendMessage(uid, "Select song", reply_markup=markup)
        data = {"uid": uid, "identifier": text}
        __MESSAGES_NOW__.append(data)
        return "ok"


mp = Downloader()


@app.route("/", methods=["POST"])
def index():
    new_msg = request.get_json()
    if "message" in str(new_msg):
        mp._received_msg(new_msg["message"])
        return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(
        os.environ.get("PORT", "5000")), debug=True)
