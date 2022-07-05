# -*- coding: utf-8 -*-
from pypinyin import lazy_pinyin


class LocalApi:
    def __init__(self):
        pass

    def get_pinyin(self, word):
        py_list = lazy_pinyin(word, strict=False)
        return " ".join(py_list)
