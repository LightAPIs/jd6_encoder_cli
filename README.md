# jd6_encoder_cli

> Rime版本星空键道6编码器CLI

## 命令

```bash
usage: main.py [-h] -d DICT [-c CHAR] [-e EXT] [-u USER] [-g GDQ] [-i IGNORE] [-v]

键道6编码器

optional arguments:
  -h, --help            show this help message and exit
  -d DICT, --dict DICT  输入词库控制文件路径
  -c CHAR, --char CHAR  可选，输入单字码表名称，默认为 xkjd6.danzi
  -e EXT, --ext EXT     可选，输入扩展的单字码表名称，默认为 xkjd6.chaojizici
  -u USER, --user USER  可选，输入用户码表名称，默认为 xkjd6.user
  -g GDQ, --gdq GDQ     可选，生成跟打器所用的码表文件路径
  -i IGNORE, --ignore IGNORE
                        可选，忽略错码检测的列表文件路径
  -v, --verify          可选，校验简码所对应的声韵词组
```
