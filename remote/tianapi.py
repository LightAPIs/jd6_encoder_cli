# -*- coding: utf-8 -*-
import requests
import json
import time


class TianApi:

    def __init__(self, key=""):
        self.url = "http://api.tianapi.com/pinyin/index"
        self.interval = 0.2
        self.key = key

    def get_pinyin(self, word):
        if len(self.key) == 0:
            return ""
        time.sleep(self.interval)
        try:
            payload = {"key": self.key, "text": word}
            headers = {"content-type": "application/x-www-form-urlencoded"}

            response = requests.request("POST",
                                        self.url,
                                        data=payload,
                                        headers=headers)
            response = json.loads(response.text)
            if response["code"] == 200:
                return response["newslist"][0]["pinyin"]
            else:
                return ""
        except ValueError:
            return ""
