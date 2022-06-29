# -*- coding: utf-8 -*-
from config import Config
from remote.tianapi import TianApi


class PinYin:

    yin_dict = {
        "a": ["xs"],
        "ai": ["xh"],
        "an": ["xf"],
        "ang": ["xp"],
        "ao": ["xz"],
        "e": ["xe"],
        "ei": ["xw"],
        "en": ["xn"],
        "eng": ["xr"],
        "er": ["xj"],
        "o": ["xl"],
        "ou": ["xd"],
        "chai": ["jh"],
        "chan": ["jf"],
        "chang": ["jp"],
        "chen": ["jn"],
        "cheng": ["jr"],
        "chu": ["jj"],
        "chun": ["jw"],
        "cha": ["ws"],
        "chi": ["wk"],
        "chong": ["wd"],
        "chuan": ["wt"],
        "chuang": ["wx", "wm"],
        "chui": ["wb"],
        "chuo": ["wl"],
        "chao": ["jz", "wz"],
        "che": ["je", "we"],
        "zhan": ["qf"],
        "zhang": ["qp"],
        "zhen": ["qn"],
        "zheng": ["qr"],
        "zhu": ["qj"],
        "zhun": ["qw"],
        "zha": ["fs"],
        "zhi": ["fk"],
        "zhong": ["fy"],
        "zhou": ["fd"],
        "zhua": ["fq"],
        "zhuai": ["fg"],
        "zhuan": ["ft"],
        "zhuang": ["fx", "fm"],
        "zhui": ["fb"],
        "zhuo": ["fl"],
        "zhai": ["qh", "fh"],
        "zhao": ["qz", "fz"],
        "zhe": ["qe", "fe"],
        "ju": ["jl"],
        "qu": ["ql"],
        "xu": ["xl"],
        "yu": ["yl"]
    }

    sheng_dict = {
        "b": "b",
        "c": "c",
        "d": "d",
        "sh": "e",
        "f": "f",
        "g": "g",
        "h": "h",
        "j": "j",
        "k": "k",
        "l": "l",
        "m": "m",
        "n": "n",
        "p": "p",
        "q": "q",
        "r": "r",
        "s": "s",
        "t": "t",
        "w": "w",
        "x": "x",
        "y": "y",
        "z": "z"
    }

    yun_dict = {
        "a": ["s"],
        "ai": ["h"],
        "an": ["f"],
        "ang": ["p"],
        "ao": ["z"],
        "e": ["e"],
        "ei": ["w"],
        "en": ["n"],
        "eng": ["r"],
        "er": ["j"],
        "i": ["k"],
        "ia": ["s"],
        "ian": ["m"],
        "iang": ["x"],
        "iao": ["c"],
        "ie": ["d"],
        "in": ["b"],
        "ing": ["g"],
        "iong": ["y"],
        "iu": ["q"],
        "o": ["l"],
        "ong": ["y"],
        "ou": ["d"],
        "u": ["j"],
        "ua": ["q"],
        "uai": ["g"],
        "uan": ["t"],
        "uang": ["x", "m"],
        "ue": ["h"],
        "ui": ["b"],
        "un": ["w"],
        "uo": ["l"],
        "v": ["l"]
    }

    def __init__(self, xlog, single_dict, code_dict, remote=False):
        self.xlog = xlog
        self.single_dict = single_dict
        self.code_dict = code_dict
        self.remote = None
        if remote:
            conf = Config()
            if conf.get_type() == "tianapi":
                self.remote = TianApi(conf.get_key())

    def get_code_dict(self):
        return self.code_dict

    def add_code_to_dict(self, word_list):
        ct = word_list[0]
        bm = word_list[1]
        if bm in self.code_dict:
            self.code_dict[bm].append(ct)
        else:
            self.code_dict[bm] = [ct]

    def convert(self, pinyin_str, word_str):
        qm = []
        p_list = pinyin_str.split(" ")
        w_len = len(word_str)
        p_len = len(p_list)
        if w_len != p_len:
            return []
        for i in range(p_len):
            if i < 3 or i == p_len - 1:
                qm.append(
                    PinYin._get_code_from_pinyin(
                        p_list[i], self.single_dict[word_str[i]][0][2:4]))
        return qm

    def encode_word(self, word):
        word_len = len(word)
        qm = []
        for i in range(word_len):
            if i < 3 or i == word_len - 1:
                if word[i] in self.single_dict:
                    qm.append(self.single_dict[word[i]])
                else:
                    self.xlog.warning(f"码表中不存在该字：{word[i]}，故无法编码词条：{word}")
                    return [{"status": -1, "val": word[i], "ext": ""}]

        qm_len = len(qm)
        if self.remote and PinYin._is_polyphonic(qm):
            res = self.remote.get_pinyin(word)
            if len(res) > 0:
                self.xlog.info(f"从远程 API 读取到\"{word}\"的拼音：" + res)
                new_qm = self.convert(res, word)
                if len(new_qm) == qm_len:
                    qm = new_qm

        encoded = []
        code_val = ""
        if qm_len == 2:
            # *二字词
            for qm0 in qm[0]:
                for qm1 in qm[1]:
                    code_val = qm0[:2] + qm1[:2]
                    if code_val in self.code_dict:
                        if self.code_dict[code_val].count(word) > 0:
                            encoded.append({
                                "status": 0,
                                "val": code_val,
                                "ext": ""
                            })
                            continue
                        old_val = code_val
                        code_val += qm0[2]
                        if code_val in self.code_dict:
                            if self.code_dict[code_val].count(word) > 0:
                                encoded.append({
                                    "status": 0,
                                    "val": code_val,
                                    "ext": ""
                                })
                                continue
                            old_val = code_val
                            code_val += qm1[2]
                            if code_val in self.code_dict:
                                if self.code_dict[code_val].count(word) > 0:
                                    encoded.append({
                                        "status": 0,
                                        "val": code_val,
                                        "ext": ""
                                    })
                                    continue
                                self.code_dict[code_val].append(word)
                                encoded.append({
                                    "status":
                                    3,
                                    "val":
                                    code_val,
                                    "ext":
                                    self.code_dict[code_val][0] + "\t" +
                                    code_val
                                })
                            else:
                                self.code_dict[code_val] = [word]
                                encoded.append({
                                    "status":
                                    2,
                                    "val":
                                    code_val,
                                    "ext":
                                    self.code_dict[old_val][0] + "\t" + old_val
                                })
                        else:
                            self.code_dict[code_val] = [word]
                            encoded.append({
                                "status":
                                2,
                                "val":
                                code_val,
                                "ext":
                                self.code_dict[old_val][0] + "\t" + old_val
                            })
                    else:
                        self.code_dict[code_val] = [word]
                        encoded.append({
                            "status": 1,
                            "val": code_val,
                            "ext": ""
                        })
        elif qm_len == 3:
            # *三字词
            for qm0 in qm[0]:
                for qm1 in qm[1]:
                    for qm2 in qm[2]:
                        code_val = qm0[0] + qm1[0] + qm2[0]
                        if code_val in self.code_dict:
                            if self.code_dict[code_val].count(word) > 0:
                                encoded.append({
                                    "status": 0,
                                    "val": code_val,
                                    "ext": ""
                                })
                                continue
                            old_val = code_val
                            code_val += qm0[2]
                            if code_val in self.code_dict:
                                if self.code_dict[code_val].count(word) > 0:
                                    encoded.append({
                                        "status": 0,
                                        "val": code_val,
                                        "ext": ""
                                    })
                                    continue
                                old_val = code_val
                                code_val += qm1[2]
                                if code_val in self.code_dict:
                                    if self.code_dict[code_val].count(
                                            word) > 0:
                                        encoded.append({
                                            "status": 0,
                                            "val": code_val,
                                            "ext": ""
                                        })
                                        continue
                                    old_val = code_val
                                    code_val += qm2[2]
                                    if code_val in self.code_dict:
                                        if self.code_dict[code_val].count(
                                                word) > 0:
                                            encoded.append({
                                                "status": 0,
                                                "val": code_val,
                                                "ext": ""
                                            })
                                            continue
                                        self.code_dict[code_val].append(word)
                                        encoded.append({
                                            "status":
                                            3,
                                            "val":
                                            code_val,
                                            "ext":
                                            self.code_dict[code_val][0] +
                                            "\t" + code_val
                                        })
                                    else:
                                        self.code_dict[code_val] = [word]
                                        encoded.append({
                                            "status":
                                            2,
                                            "val":
                                            code_val,
                                            "ext":
                                            self.code_dict[old_val][0] + "\t" +
                                            old_val
                                        })
                                else:
                                    self.code_dict[code_val] = [word]
                                    encoded.append({
                                        "status":
                                        2,
                                        "val":
                                        code_val,
                                        "ext":
                                        self.code_dict[old_val][0] + "\t" +
                                        old_val
                                    })
                            else:
                                self.code_dict[code_val] = [word]
                                encoded.append({
                                    "status":
                                    2,
                                    "val":
                                    code_val,
                                    "ext":
                                    self.code_dict[old_val][0] + "\t" + old_val
                                })
                        else:
                            self.code_dict[code_val] = [word]
                            encoded.append({
                                "status": 1,
                                "val": code_val,
                                "ext": ""
                            })
        elif qm_len > 3:
            # *多字词
            for qm0 in qm[0]:
                for qm1 in qm[1]:
                    for qm2 in qm[2]:
                        for qm3 in qm[3]:
                            code_val = qm0[0] + qm1[0] + qm2[0] + qm3[0]
                            if code_val in self.code_dict:
                                if self.code_dict[code_val].count(word) > 0:
                                    encoded.append({
                                        "status": 0,
                                        "val": code_val,
                                        "ext": ""
                                    })
                                    continue
                                old_val = code_val
                                code_val += qm0[2]
                                if code_val in self.code_dict:
                                    if self.code_dict[code_val].count(
                                            word) > 0:
                                        encoded.append({
                                            "status": 0,
                                            "val": code_val,
                                            "ext": ""
                                        })
                                        continue
                                    old_val = code_val
                                    code_val += qm1[2]
                                    if code_val in self.code_dict:
                                        if self.code_dict[code_val].count(
                                                word) > 0:
                                            encoded.append({
                                                "status": 0,
                                                "val": code_val,
                                                "ext": ""
                                            })
                                            continue
                                        self.code_dict[code_val].append(word)
                                        encoded.append({
                                            "status":
                                            3,
                                            "val":
                                            code_val,
                                            "ext":
                                            self.code_dict[code_val][0] +
                                            "\t" + code_val
                                        })
                                    else:
                                        self.code_dict[code_val] = [word]
                                        encoded.append({
                                            "status":
                                            2,
                                            "val":
                                            code_val,
                                            "ext":
                                            self.code_dict[old_val][0] + "\t" +
                                            old_val
                                        })
                                else:
                                    self.code_dict[code_val] = [word]
                                    encoded.append({
                                        "status":
                                        2,
                                        "val":
                                        code_val,
                                        "ext":
                                        self.code_dict[old_val][0] + "\t" +
                                        old_val
                                    })
                            else:
                                self.code_dict[code_val] = [word]
                                encoded.append({
                                    "status": 1,
                                    "val": code_val,
                                    "ext": ""
                                })

        return encoded

    @staticmethod
    def _is_polyphonic(qm):
        for item in qm:
            if len(item) > 1:
                return True
        return False

    @staticmethod
    def _get_code_from_pinyin(pinyin_str, suffix):
        res = []
        if pinyin_str in PinYin.yin_dict:
            for yin in PinYin.yin_dict[pinyin_str]:
                res.append(yin + suffix)
        else:
            if pinyin_str[:2] in PinYin.sheng_dict:
                for yun in PinYin.yun_dict[pinyin_str[2:]]:
                    res.append(PinYin.sheng_dict[pinyin_str[:2]] + yun +
                               suffix)
            else:
                for yun in PinYin.yun_dict[pinyin_str[1:]]:
                    res.append(PinYin.sheng_dict[pinyin_str[:1]] + yun +
                               suffix)
        return res
