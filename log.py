# -*- coding: utf-8 -*-
import logging
import datetime
import os
import io
import re


class Logger:
    def __init__(self, level="ERROR", dir_name="log"):
        self.logger = logging.getLogger("mylogger")
        self.setLevel(level)
        self.setHandler(dir_name)
        self.debug("开始运行...")

    def setLevel(self, level):
        if level == "DEBUG":
            self.level = logging.DEBUG
        elif level == "INFO":
            self.level = logging.INFO
        elif level == "WARNING":
            self.level = logging.WARNING
        elif level == "ERROR":
            self.level = logging.ERROR
        else:
            self.level = logging.CRITICAL

    def setHandler(self, dir_name):
        now = datetime.datetime.now()
        filename = re.sub(r"[\s:]", "-", str(now)) + ".txt"
        dir_path = os.path.join(os.getcwd(), dir_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        file_path = os.path.join(dir_path, filename)
        with io.open(file_path, mode="w", encoding="utf-8") as f:
            f.write("")

        self.logger.setLevel(self.level)
        handler = logging.FileHandler(file_path, encoding="utf-8")
        handler.setLevel(self.level)
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
        self.logger.addHandler(handler)

    def debug(self, message):
        print(message)
        self.logger.debug(message)

    def info(self, message):
        print(message)
        self.logger.info(message)

    def warning(self, message):
        print(message)
        self.logger.warning(message)

    def error(self, message):
        print(message)
        self.logger.error(message)

    def critical(self, message):
        print(message)
        self.logger.critical(message)
