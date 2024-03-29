# -*- coding: utf-8 -*-
from config import Config
from localapi import LocalApi
from remote.tianapi import TianApi
from remote.hanlp import HanLP


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

    fly_key_dict = {
        "wx": "chuang",
        "wm": "chuang",
        "jz": "chao",
        "wz": "chao",
        "je": "che",
        "we": "che",
        "fx": "zhuang",
        "fm": "zhuang",
        "qz": "zhao",
        "fz": "zhao",
        "qe": "zhe",
        "fe": "zhe",
        "ex": "shuang",
        "em": "shuang",
        "gx": "guang",
        "gm": "guang",
        "hx": "huang",
        "hm": "huang",
        "kx": "kuang",
        "km": "kuang",
        "fh": "zhai",
        "qh": "zhai"
    }

    def __init__(self, xlog, single_dict, code_dict, remote=False):
        self.xlog = xlog
        self.single_dict = single_dict
        self.code_dict = code_dict
        self.fly_dict = self.find_fly_dict()
        self.local_api = LocalApi()
        self.remote = remote
        self.remote_api = None
        if remote:
            conf = Config()
            if conf.get_type() == "tianapi":
                self.remote_api = TianApi(conf.get_key())
            elif conf.get_type() == "hanlp":
                self.remote_api = HanLP(conf.get_key())
            else:
                self.remote = False

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

    def find_fly_dict(self):
        fly_dict = {}
        for ch in self.single_dict:
            if len(self.single_dict[ch]) > 1:
                res_dict = PinYin._filter_fly_dict(self.single_dict[ch], 2)
                if len(res_dict) > 0:
                    fly_dict[ch] = [
                        x for j in list(res_dict.values()) for x in j
                    ]
        return fly_dict

    def get_fly_dict(self):
        return self.fly_dict

    def get_clean_qm(self, qm):
        c_qm = []
        qm_len = len(qm)
        if qm_len == 2:
            for i in range(2):
                bm = []
                for single in qm[i]:
                    sl = single[0:3]
                    if bm.count(sl) == 0:
                        bm.append(sl)
                c_qm.append(bm)
        elif qm_len == 3:
            for i in range(3):
                bm = []
                for single in qm[i]:
                    sl = single[0] + '_' + single[2]
                    if bm.count(sl) == 0:
                        bm.append(sl)
                c_qm.append(bm)
        elif qm_len > 3:
            for i in range(2):
                bm = []
                for single in qm[i]:
                    sl = single[0] + '_' + single[2]
                    if bm.count(sl) == 0:
                        bm.append(sl)
                c_qm.append(bm)
            bm2 = []
            for single in qm[2]:
                sl = single[0]
                if bm2.count(sl) == 0:
                    bm2.append(sl)
            c_qm.append(bm2)
            bm3 = []
            for single in qm[qm_len - 1]:
                sl = single[0]
                if bm3.count(sl) == 0:
                    bm3.append(sl)
            c_qm.append(bm3)
        return c_qm

    def is_polyphonic(self, qm, word):
        word_len = len(qm)
        for i in range(word_len):
            item_len = len(qm[i])
            if item_len > 1:
                if word_len == 2:
                    res_dict = PinYin._filter_fly_dict(qm[i], len(qm[i]))
                    return len(res_dict) == 0
                elif word_len > 2:
                    if word[i] in self.fly_dict:
                        return len(self.fly_dict[word[i]]) < len(
                            self.single_dict[word[i]])
                    else:
                        return True
        return False

    def encode_word(self, word):
        word_len = len(word)
        qm = []
        for i in range(word_len):
            if i < 3 or i == word_len - 1:
                if word[i] in self.single_dict:
                    qm.append(self.single_dict[word[i]])
                else:
                    return [{"status": -1, "val": word[i], "ext": ""}]

        qm_len = len(qm)
        qm = self.get_clean_qm(qm)
        if self.is_polyphonic(qm, word):
            res = ""
            remote = self.remote
            if remote:
                res = self.remote_api.get_pinyin(word)
                if len(res) == 0:
                    res = self.local_api.get_pinyin(word)
                    remote = False
            else:
                res = self.local_api.get_pinyin(word)
            if len(res) > 0:
                log_str = "从远程" if remote else "由本地"
                self.xlog.info(f"{log_str} API 读取到\"{word}\"的拼音：{res}")
                new_qm = self.convert(res, word)
                if len(new_qm) == qm_len:
                    qm = self.get_clean_qm(new_qm)

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
    def _filter_fly_dict(bm_list, limit_len):
        fly_code_dict = {
            "chuang": [],
            "chao": [],
            "che": [],
            "zhuang": [],
            "zhao": [],
            "zhe": [],
            "shuang": [],
            "guang": [],
            "huang": [],
            "kuang": [],
            "zhai": []
        }
        for bm in bm_list:
            if len(bm) >= 2 and bm[:2] in PinYin.fly_key_dict:
                fly_code_dict[PinYin.fly_key_dict[bm[:2]]].append(bm)
        res_dict = {
            k: v
            for k, v in fly_code_dict.items() if len(v) >= limit_len
        }
        return res_dict

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
