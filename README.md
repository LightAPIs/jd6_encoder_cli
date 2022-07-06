# jd6_encoder_cli

> Rime版本星空键道6编码器CLI

用于编码用户新增的词组，同时支持校验码表中重码及错码等问题。

## 命令

```bash
usage: main.py [-h] -d DICT [-u USER] [-g GDQ] [-i IGNORE] [-v] [-f] [-r]

optional arguments:
  -h, --help            show this help message and exit
  -d DICT, --dict DICT  输入词库控制文件路径，如 /path/to/xkjd6.extended.dict.yaml
  -u USER, --user USER  可选，输入用户词库名称，默认为 xkjd6.user
  -g GDQ, --gdq GDQ     可选，生成跟打器所用的码表文件路径
  -i IGNORE, --ignore IGNORE
                        可选，忽略错码检测的列表文件路径
  -v, --verify          可选，启用校验简码所对应的声韵词组
  -f, --fly             可选，启用校验飞键词组的编码是否缺失
  -r, --remote          可选，启用远程 API 获取多音字的拼音，需填写 config.ini
```

## 外部依赖

- `yaml` 文件解析：[yaml/pyyaml](https://github.com/yaml/pyyaml) ([MIT license](https://github.com/yaml/pyyaml/blob/master/LICENSE))
- HTTP 网络请求：[psf/requests](https://github.com/psf/requests) ([Apache-2.0 license](https://github.com/psf/requests/blob/main/LICENSE))
- 本地拼音转换：[mozillazg/python-pinyin](https://github.com/mozillazg/python-pinyin) ([MIT license](https://github.com/mozillazg/python-pinyin/blob/master/LICENSE.txt))
