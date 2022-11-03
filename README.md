# jd6_encoder_cli

> Rime版本星空键道6编码器CLI

用于编码用户新增的词组，同时支持校验码表中重码及错码等问题。

## 命令

```bash
usage: main.py [-h] -d DICT [-u USER] [-g GDQ] [-i IGNORE] [-s] [-f] [-v] [-a] [-r]

optional arguments:
  -h, --help            show this help message and exit
  -d DICT, --dict DICT  输入词库控制文件路径，如 /path/to/xkjd6.extended.dict.yaml
  -u USER, --user USER  可选，输入词库控制文件同目录下用户词库文件名称，默认为 xkjd6.user（.dict.yaml）
  -g GDQ, --gdq GDQ     可选，生成跟打器所用的码表文件路径
  -i IGNORE, --ignore IGNORE
                        可选，忽略错码检测的列表文件路径
  -s, --single          可选，额外启用校验单字编码的冗余情况
  -f, --fly             可选，额外启用校验飞键词组的编码是否缺失
  -v, --verify          可选，额外启用校验简码所对应的声韵词组
  -a, --irrational      可选，额外启用校验单字编码编排是否合理
  -r, --remote          可选，启用远程 API 获取多音字的拼音，需填写 config.ini
```

## 外部依赖

- `yaml` 文件解析：[yaml/pyyaml](https://github.com/yaml/pyyaml) ([MIT license](https://github.com/yaml/pyyaml/blob/master/LICENSE))
- HTTP 网络请求：[psf/requests](https://github.com/psf/requests) ([Apache-2.0 license](https://github.com/psf/requests/blob/main/LICENSE))
- 本地拼音转换：[mozillazg/python-pinyin](https://github.com/mozillazg/python-pinyin) ([MIT license](https://github.com/mozillazg/python-pinyin/blob/master/LICENSE.txt))

### 安装依赖

```bash
python -m pip install pyyaml requests pypinyin
