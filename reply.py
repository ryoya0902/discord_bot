import re
import requests
from bs4 import BeautifulSoup
import datetime
import random
from model import transformer
import mojimoji
import model_utils
import pickle
from asari.api import Sonar
from googletrans import Translator


class Reply:
    def __init__(
        self, tokenizer_path, hparams_path, model_paths, back_tr=False, text_pp=True
    ):
        self.tokenizer_path = tokenizer_path
        self.tokenizer = self.load_pickle(tokenizer_path)
        self.hparams_path = hparams_path
        self.hparams = self.load_pickle(hparams_path)
        self.model_paths = model_paths
        self.models = self.load_model(model_paths)
        self.back_tr = back_tr
        self.text_pp = text_pp
        self.negative_reactions = ["🥺", "🥴", "😭"]
        self.positive_reactions = ["🥳", "🥰", "😘"]
        self.sonar = Sonar()
        self.translator = Translator()

    def reply_help(self):
        help = "使用可能なコマンドです\n/image [word] : wordの画像検索\n/news : 技術系ニュース\n/tenki : 現在の天気\n/clear : ログ削除\n/kill : 強制終了\n"
        return help

    def reply_image(self, content):
        word = content.split()[-1]
        url = f"http://image.search.yahoo.co.jp/search?n=60&p={word}&search.x=1"
        html = requests.get(url)
        links = re.findall("https://[\w/:%#\$&\?\(\)~\.\+\-]+[jpgpng]{3}", html.text)
        clean_urls = []
        for link in links:
            if "yimg" in link:
                continue
            else:
                clean_urls.append(link)
        if len(clean_urls) == 0:
            link = links[0]
        else:
            link = random.choice(clean_urls)
        text = "取得した画像です\n" + link
        return text

    def reply_news(self):
        url = "https://qiita.com/"
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        items = soup.find_all(class_="css-qrra2n")
        text = "今日の技術系ニュースです\n"
        text += "############################################\n"
        for i in range(min(len(items), 5)):
            item = items[i]
            text += "タイトル：" + item.text + "\n"
            text += "URL：" + item.get("href") + "\n"
            text += "############################################\n"
        return text

    def reply_forecast(self):
        url = "https://tenki.jp/forecast/5/27/5310/24205/1hour.html"
        r = requests.get(url)
        html = r.text.encode(r.encoding)
        soup = BeautifulSoup(html, "lxml")
        n_hour = max(abs(int(datetime.datetime.now().hour) - 1), 0)
        hour = soup.select(".hour > td")[n_hour].text.strip()
        weather = soup.select(".weather > td")[n_hour].text.strip()
        temperature = soup.select(".temperature > td")[n_hour].text.strip()
        prob_precip = soup.select(".prob-precip > td")[n_hour].text.strip()
        precipitation = soup.select(".precipitation > td")[n_hour].text.strip()
        humidity = soup.select(".humidity > td")[n_hour].text.strip()
        wind_blow = soup.select(".wind-blow > td")[n_hour].text.strip()

        w_info = (
            "今日の天気です" + "\n"
            "時刻         ： "
            + hour
            + "時"
            + "\n"
            + "天気         ： "
            + weather
            + "\n"
            + "気温(C)      ： "
            + temperature
            + "\n"
            + "降水確率(%)  ： "
            + prob_precip
            + "\n"
            + "降水量(mm/h) ： "
            + precipitation
            + "\n"
            + "湿度(%)      ： "
            + humidity
            + "\n"
            + "風向         ： "
            + wind_blow
            + "\n"
            + "風速(m/s)    ： "
            + weather
            + "\n"
        )

        return w_info

    def reply_chat(self, user_name, content):
        content_pp = re.sub("<.+>", "", content).lstrip()
        text = mojimoji.han_to_zen(content_pp)
        text = model_utils.predict(self.hparams, self.models, self.tokenizer, text)
        reaction = None
        response = self.sonar.ping(text=content_pp)
        negative = response["classes"][0]["confidence"]
        positive = response["classes"][1]["confidence"]
        if negative >= 0.95:
            reaction = random.choice(self.negative_reactions)
        if positive >= 0.97:
            reaction = random.choice(self.positive_reactions)
        if self.back_tr:
            text = self.translator.translate(text, src="ja", dest="en").text
            text = self.translator.translate(text, src="en", dest="ja").text
        if self.text_pp:
            text = self.text_postprocessing(text, user_name)
        return text, reaction

    def text_postprocessing(self, text, user_name):
        text = text.replace("あなた", user_name + "さん")
        text = text.replace("お前", user_name + "さん")
        text = text.replace("御坂さん", user_name + "さん")
        text = text.replace("先輩", user_name + "さん")
        text = text.replace("お嬢様", user_name + "さん")
        text = text.replace("ご主人様", user_name + "さん")
        text = text.replace("長男", user_name + "さん")
        text = text.replace("男性", user_name + "さん")
        text = text.replace("女性", user_name + "さん")
        text = text.replace("少女", user_name + "さん")
        text = text.replace("男さん", user_name + "さん")
        text = text.replace("男", user_name + "さん")
        text = text.replace("女", user_name + "さん")
        text = text.replace("貴様", user_name + "さん")
        text = text.replace("お父さん", user_name + "さん")
        text = text.replace("お兄ちゃん", user_name + "さん")
        text = text.replace("トモB", user_name + "さん")
        text = text.replace("トッモＢ", user_name + "さん")
        text = text.replace("鹿目さん", user_name + "さん")
        text = text.replace("お姉ちゃん", user_name + "さん")
        text = text.replace("原田美世", user_name + "さん")
        text = text.replace("貴方", user_name + "さん")
        text = text.replace("菜々さん", user_name + "さん")
        text = text.replace("母さん", user_name + "さん")
        text = text.replace("未央", user_name + "さん")
        text = text.replace("アッコさん", user_name + "さん")
        text = text.replace("姉ちゃん", user_name + "さん")
        text = text.replace("俺様", "私")
        text = text.replace("俺", "私")
        text = text.replace("僕", "私")
        text = text.replace("私さん", "私")
        text = text.replace("さんさん", "さん")
        text = text.replace("e？", "え？")
        text = re.sub("(その、)+", "その、", text)
        text = re.sub("(これ、)+", "これ、", text)
        text = re.sub("(今日、)+", "今日、", text)
        text = re.sub("(あの、)+", "あの、", text)
        text = re.sub("(あれ、)+", "あれ、", text)
        text = re.sub("(この、)+", "この、", text)
        text = re.sub("(ずっと、)+", "ずっと、", text)
        text = re.sub("(んー、)+", "んー、", text)
        text = re.sub("(毎日、)+", "毎日、", text)
        text = re.sub("(毎日)+", "毎日", text)
        text = re.sub("(私、)+", "私、", text)
        text = re.sub("私は、私は", "私は", text)
        if "＞＞" in text or ">>" in text:
            text = "あ、あの"
        if text == "ああああ":
            text = "そうですか"
        if text == "そうだな":
            text = "そうですか"
        return text

    def load_pickle(self, path):
        with open(path, "rb") as handle:
            obj = pickle.load(handle)
        return obj

    def load_model(self, paths):
        models = []
        for i in range(len(paths)):
            path = paths[i]
            model = transformer(self.hparams)
            model.load_weights(path)
            models.append(model)
        return models
