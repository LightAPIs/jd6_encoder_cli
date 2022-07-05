# -*- coding: utf-8 -*-
import requests
import json
import time


class HanLP:

    def __init__(self, key=""):
        self.url = "http://comdo.hanlp.com/hanlp/v1/pinyin/toPinyin"
        self.interval = 0.5
        self.key = key

    def get_pinyin(self, word):
        if len(self.key) == 0:
            return ""
        time.sleep(self.interval)
        try:
            payload = {"text": word}
            headers = {"token": self.key}

            response = requests.request("POST",
                                        self.url,
                                        data=payload,
                                        headers=headers)
            response = json.loads(response.text)
            if response["code"] == 0:
                res = ""
                data = response["data"]
                for item in data:
                    res += item["pinyinWithoutTone"] + " "
                return res.strip()
            else:
                return ""
        except ValueError:
            return ""
