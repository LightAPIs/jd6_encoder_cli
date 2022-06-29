# -*- coding: utf-8 -*-
import os
import configparser


class Config:

    def __init__(self, path="config.ini"):
        if os.path.exists(path):
            self.conf = configparser.ConfigParser()
            try:
                self.conf.read(path, encoding="utf-8-sig")
            except Exception:
                self.conf.read(path, encoding="utf-8")
        else:
            self.conf = self._default_config()

    def get_type(self):
        return self.conf.get("engine", "type")

    def get_key(self):
        return self.conf.get(self.get_type(), "key")

    @staticmethod
    def _default_config():
        conf = configparser.ConfigParser()

        sec1 = "engine"
        conf.add_section(sec1)
        conf.set(sec1, "type", "tianapi")

        sec2 = "tianapi"
        conf.add_section(sec2)
        conf.set(sec2, "key", "")

        return conf
