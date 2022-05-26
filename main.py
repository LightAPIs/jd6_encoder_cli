# -*- coding: utf-8 -*-
import os
import io
import yaml
import argparse
from log import Logger


def read_file_2_list(path):
    read_list = []
    if path and (os.path.exists(path)):
        with io.open(path, mode="r", encoding="utf-8") as f:
            read_list = f.read().splitlines()  # 不读入行尾的换行符
    return read_list


def splicing_dict_file(dir_name, dict_name):
    return os.path.join(dir_name, dict_name + ".dict.yaml")


def is_word_item(word):
    return word and "#-.abcdefghijklmnopqrstuvwxyz".count(
        word[0]) == 0 and word.find(" ") == -1


def get_code_dict(source_dict, word_list):
    code_dict = source_dict
    for word in word_list:
        item = word.strip()
        if is_word_item(item):
            item_arr = item.split("\t")
            if len(item_arr) < 2:
                continue
            ct = item_arr[0]
            bm = item_arr[1]
            if bm in code_dict:
                code_dict[bm].append(ct)
            else:
                code_dict[bm] = [ct]
    return code_dict


def get_single_dict(source_dict, word_list):
    single_dict = source_dict
    for word in word_list:
        item = word.strip()
        if is_word_item(item):
            item_arr = item.split("\t")
            if len(item_arr) < 2:
                continue
            ct = item_arr[0]
            bm = item_arr[1]
            if len(bm) >= 4:
                # !1. 字的全码为四码或者六码
                # !2. 用于编码词条，故最多只需要四码
                cut_bm = bm[:4]
                if ct in single_dict:
                    if single_dict[ct].count(cut_bm) == 0:
                        single_dict[ct].append(cut_bm)
                else:
                    single_dict[ct] = [cut_bm]
    return single_dict


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="键道6编码器")
    ap.add_argument("-d", "--dict", required=True, help="输入词库控制文件路径")
    ap.add_argument("-c",
                    "--char",
                    required=False,
                    default="xkjd6.danzi",
                    help="可选，输入单字码表名称，默认为 xkjd6.danzi")
    ap.add_argument("-e",
                    "--ext",
                    required=False,
                    default="xkjd6.chaojizici",
                    help="可选，输入扩展的单字码表名称，默认为 xkjd6.chaojizici")
    ap.add_argument("-u",
                    "--user",
                    required=False,
                    default="xkjd6.user",
                    help="可选，输入用户码表名称，默认为 xkjd6.user")

    args = vars(ap.parse_args())
    xlog = Logger("DEBUG", "log")

    xlog.info("************************************************")
    xlog.info("词库控制文件：" + args["dict"])
    xlog.info("单字码表名称：" + args["char"])
    xlog.info("扩展的单字码表名称：" + args["ext"])
    xlog.info("用户码表名称：" + args["user"])
    xlog.info("************************************************")

    if not os.path.exists(args["dict"]):
        xlog.error("词库控制文件不存在！操作终止。")
    else:
        xlog.info("开始编码...")
        dir_name = os.path.dirname(args["dict"])
        xlog.info("码表所在目录：" + dir_name)

        source_data = []
        with io.open(args["dict"], mode="r", encoding="utf-8") as f:
            r_data = yaml.load(f, Loader=yaml.BaseLoader)
            source_data = r_data["import_tables"]

        code_dict = {}
        single_dict = {}
        user_list = []
        for d_name in source_data:
            file_name = splicing_dict_file(dir_name, d_name)
            read_list = read_file_2_list(file_name)
            if d_name != args["user"]:
                code_dict = get_code_dict(code_dict, read_list)
            else:
                user_list = read_list

            if d_name == args["char"] or d_name == args["ext"]:
                single_dict = get_single_dict(single_dict, read_list)
        xlog.info("共读取到 " + str(len(code_dict)) + " 组词条。")
        xlog.info("共读取到 " + str(len(single_dict)) + " 个单字。")

        count = 0
        results = []
        for item in user_list:
            item = item.strip()
            if is_word_item(item):
                if item.find("\t") != -1:
                    # 已编码的词条
                    item_arr = item.split("\t")
                    ct = item_arr[0]
                    bm = item_arr[1]
                    if bm in code_dict:
                        code_dict[bm].append(ct)
                    else:
                        code_dict[bm] = [ct]
                    results.append(item + "\n")
                else:
                    item_len = len(item)
                    if item_len <= 1:
                        xlog.warning("无法编码单字词条：" + item)
                        continue
                    else:
                        had_error = False
                        qm = []
                        for i in range(item_len):
                            if i < 3 or i == item_len - 1:
                                if item[i] in single_dict:
                                    qm.append(single_dict[item[i]])
                                else:
                                    xlog.warning("码表中不存在该字：" + item[i] +
                                                 "，故无法编码词条：" + item)
                                    had_error = True
                                    break

                        if not had_error:
                            qm_len = len(qm)
                            code_val = ""
                            is_new = False
                            if qm_len == 2:
                                # *二字词
                                for qm0 in qm[0]:
                                    for qm1 in qm[1]:
                                        code_val = qm0[:2] + qm1[:2]
                                        if code_val in code_dict:
                                            if code_dict[code_val].count(
                                                    item) > 0:
                                                continue
                                            code_val += qm0[2]
                                            if code_val in code_dict:
                                                if code_dict[code_val].count(
                                                        item) > 0:
                                                    continue
                                                code_val += qm1[2]
                                                if code_val in code_dict:
                                                    if code_dict[code_val].count(
                                                            item) > 0:
                                                        continue
                                                    code_dict[code_val].append(
                                                        item)
                                                    count += 1
                                                    results.append(item +
                                                                   "\t" +
                                                                   code_val +
                                                                   "\n")
                                                    xlog.info("编码词条：" + item +
                                                              "\t" + code_val)
                                                else:
                                                    code_dict[code_val] = [
                                                        item
                                                    ]
                                                    count += 1
                                                    results.append(item +
                                                                   "\t" +
                                                                   code_val +
                                                                   "\n")
                                                    xlog.info("编码词条：" + item +
                                                              "\t" + code_val)
                                            else:
                                                code_dict[code_val] = [item]
                                                count += 1
                                                results.append(item + "\t" +
                                                               code_val + "\n")
                                                xlog.info("编码词条：" + item +
                                                          "\t" + code_val)
                                        else:
                                            code_dict[code_val] = [item]
                                            count += 1
                                            results.append(item + "\t" +
                                                           code_val + "\n")
                                            xlog.info("编码词条：" + item + "\t" +
                                                      code_val)
                            elif qm_len == 3:
                                # *三字词
                                for qm0 in qm[0]:
                                    for qm1 in qm[1]:
                                        for qm2 in qm[2]:
                                            code_val = qm0[0] + qm1[0] + qm2[0]
                                            if code_val in code_dict:
                                                if code_dict[code_val].count(
                                                        item) > 0:
                                                    continue
                                                code_val += qm0[2]
                                                if code_val in code_dict:
                                                    if code_dict[code_val].count(
                                                            item) > 0:
                                                        continue
                                                    code_val += qm1[2]
                                                    if code_val in code_dict:
                                                        if code_dict[
                                                                code_val].count(
                                                                    item
                                                                ) > 0:
                                                            continue
                                                        code_val += qm2[2]
                                                        if code_val in code_dict:
                                                            if code_dict[
                                                                    code_val].count(
                                                                        item
                                                                    ) > 0:
                                                                continue
                                                            code_dict[
                                                                code_val].append(
                                                                    item)
                                                            count += 1
                                                            results.append(
                                                                item + "\t" +
                                                                code_val +
                                                                "\n")
                                                            xlog.info("编码词条：" +
                                                                      item +
                                                                      "\t" +
                                                                      code_val)
                                                        else:
                                                            code_dict[
                                                                code_val] = [
                                                                    item
                                                                ]
                                                            count += 1
                                                            results.append(
                                                                item + "\t" +
                                                                code_val +
                                                                "\n")
                                                            xlog.info("编码词条：" +
                                                                      item +
                                                                      "\t" +
                                                                      code_val)
                                                    else:
                                                        code_dict[code_val] = [
                                                            item
                                                        ]
                                                        count += 1
                                                        results.append(
                                                            item + "\t" +
                                                            code_val + "\n")
                                                        xlog.info("编码词条：" +
                                                                  item + "\t" +
                                                                  code_val)
                                                else:
                                                    code_dict[code_val] = [
                                                        item
                                                    ]
                                                    count += 1
                                                    results.append(item +
                                                                   "\t" +
                                                                   code_val +
                                                                   "\n")
                                                    xlog.info("编码词条：" + item +
                                                              "\t" + code_val)
                                            else:
                                                code_dict[code_val] = [item]
                                                count += 1
                                                results.append(item + "\t" +
                                                               code_val + "\n")
                                                xlog.info("编码词条：" + item +
                                                          "\t" + code_val)
                            elif qm_len > 3:
                                # *多字词
                                for qm0 in qm[0]:
                                    for qm1 in qm[1]:
                                        for qm2 in qm[2]:
                                            for qm3 in qm[3]:
                                                code_val = qm0[0] + qm1[
                                                    0] + qm2[0] + qm3[0]
                                                if code_val in code_dict:
                                                    if code_dict[code_val].count(
                                                            item) > 0:
                                                        continue
                                                    code_val += qm0[2]
                                                    if code_val in code_dict:
                                                        if code_dict[
                                                                code_val].count(
                                                                    item
                                                                ) > 0:
                                                            continue
                                                        code_val += qm1[2]
                                                        if code_val in code_dict:
                                                            if code_dict[
                                                                    code_val].count(
                                                                        item
                                                                    ) > 0:
                                                                continue
                                                            code_dict[
                                                                code_val].append(
                                                                    item)
                                                            count += 1
                                                            results.append(
                                                                item + "\t" +
                                                                code_val +
                                                                "\n")
                                                            xlog.info("编码词条：" +
                                                                      item +
                                                                      "\t" +
                                                                      code_val)
                                                        else:
                                                            code_dict[
                                                                code_val] = [
                                                                    item
                                                                ]
                                                            count += 1
                                                            results.append(
                                                                item + "\t" +
                                                                code_val +
                                                                "\n")
                                                            xlog.info("编码词条：" +
                                                                      item +
                                                                      "\t" +
                                                                      code_val)
                                                    else:
                                                        code_dict[code_val] = [
                                                            item
                                                        ]
                                                        count += 1
                                                        results.append(
                                                            item + "\t" +
                                                            code_val + "\n")
                                                        xlog.info("编码词条：" +
                                                                  item + "\t" +
                                                                  code_val)
                                                else:
                                                    code_dict[code_val] = [
                                                        item
                                                    ]
                                                    count += 1
                                                    results.append(item +
                                                                   "\t" +
                                                                   code_val +
                                                                   "\n")
                                                    xlog.info("编码词条：" + item +
                                                              "\t" + code_val)
            else:
                # 非词条
                results.append(item + "\n")

        xlog.info("编码完成。共新增 " + str(count) + " 组词条。")
        xlog.info("开始写入新码表内容...")
        with io.open(splicing_dict_file(dir_name, args["user"]),
                     mode="w",
                     encoding="utf-8") as f:
            f.writelines(results)

        xlog.info("写入新码表内容完成，编码工作全部结束。")
