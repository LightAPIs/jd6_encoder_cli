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


def get_first_level_dict(source_dict, word_list):
    level_dict = source_dict
    for word in word_list:
        item = word.strip()
        if is_word_item(item):
            item_arr = item.split("\t")
            if len(item_arr) < 2:
                continue
            ct = item_arr[0]
            bm = item_arr[1]
            if len(bm) == 1 and "abcdefghijklmnopqrstuvwxyz".count(bm) == 1:
                dup = 0
                for ch in level_dict:
                    if level_dict[ch] == bm:
                        dup += 1
                if dup < 2:
                    level_dict[ct] = bm
    return level_dict


def get_gdq_list(encode_dict):
    gdq_list = []
    for code in encode_dict:
        for word in encode_dict[code]:
            gdq_list.append(word + "\t" + code + "\n")
    return gdq_list


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
    ap.add_argument("-g", "--gdq", required=False, help="可选，生成跟打器所用的码表文件路径")
    ap.add_argument("-i", "--ignore", required=False, help="可选，忽略错码检测的列表文件路径")
    ap.add_argument("-v",
                    "--verify",
                    required=False,
                    action="store_true",
                    help="可选，校验简码所对应的声韵词组")

    args = vars(ap.parse_args())
    xlog = Logger("DEBUG", "log")

    xlog.info("************************************************")
    xlog.info("词库控制文件：" + args["dict"])
    xlog.info("单字码表名称：" + args["char"])
    xlog.info("扩展的单字码表名称：" + args["ext"])
    xlog.info("用户码表名称：" + args["user"])
    if args["gdq"]:
        xlog.info("生成跟打器所用的码表文件：" + args["gdq"])
    if args["ignore"]:
        xlog.info("忽略错码检测的列表文件：" + args["ignore"])
    if args["verify"]:
        xlog.info("校验简码所对应的声韵词组。")
    xlog.info("************************************************")

    if not os.path.exists(args["dict"]):
        xlog.error("词库控制文件不存在！操作终止。")
    else:
        # *编码工作
        xlog.info("开始编码...")
        dir_name = os.path.dirname(args["dict"])
        xlog.info("码表所在目录：" + dir_name)

        source_data = []
        with io.open(args["dict"], mode="r", encoding="utf-8") as f:
            r_data = yaml.load(f, Loader=yaml.BaseLoader)
            source_data = r_data["import_tables"]

        code_dict = {}
        single_dict = {}
        first_level_dict = {}
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

            # ?收集一级简码词条
            if args["verify"]:
                first_level_dict = get_first_level_dict(
                    first_level_dict, read_list)
        xlog.info("共读取到 " + str(len(code_dict)) + " 组编码。")
        xlog.info("共读取到 " + str(len(single_dict)) + " 个单字。")
        if args["verify"]:
            xlog.info("共读取到 " + str(len(first_level_dict)) + " 个一级简码。")

        count = 0
        results = []
        need_write = False
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
                    need_write = True
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
                                                xlog.warning("已经存在词条：" + item +
                                                             "\t" + code_val)
                                                continue
                                            old_val = code_val
                                            code_val += qm0[2]
                                            if code_val in code_dict:
                                                if code_dict[code_val].count(
                                                        item) > 0:
                                                    xlog.warning("已经存在词条：" +
                                                                 item + "\t" +
                                                                 code_val)
                                                    continue
                                                old_val = code_val
                                                code_val += qm1[2]
                                                if code_val in code_dict:
                                                    if code_dict[
                                                            code_val].count(
                                                                item) > 0:
                                                        xlog.warning(
                                                            "已经存在词条：" + item +
                                                            "\t" + code_val)
                                                        continue
                                                    code_dict[code_val].append(
                                                        item)
                                                    count += 1
                                                    results.append(item +
                                                                   "\t" +
                                                                   code_val +
                                                                   "\n")
                                                    xlog.info(
                                                        "编码词条：" + item + "\t" +
                                                        code_val + " [同位编码：" +
                                                        code_dict[code_val][0]
                                                        + "\t" + code_val +
                                                        "]")
                                                else:
                                                    code_dict[code_val] = [
                                                        item
                                                    ]
                                                    count += 1
                                                    results.append(item +
                                                                   "\t" +
                                                                   code_val +
                                                                   "\n")
                                                    xlog.info(
                                                        "编码词条：" + item + "\t" +
                                                        code_val + " [前置编码：" +
                                                        code_dict[old_val][0] +
                                                        "\t" + old_val + "]")
                                            else:
                                                code_dict[code_val] = [item]
                                                count += 1
                                                results.append(item + "\t" +
                                                               code_val + "\n")
                                                xlog.info(
                                                    "编码词条：" + item + "\t" +
                                                    code_val + " [前置编码：" +
                                                    code_dict[old_val][0] +
                                                    "\t" + old_val + "]")
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
                                                    xlog.warning("已经存在词条：" +
                                                                 item + "\t" +
                                                                 code_val)
                                                    continue
                                                old_val = code_val
                                                code_val += qm0[2]
                                                if code_val in code_dict:
                                                    if code_dict[
                                                            code_val].count(
                                                                item) > 0:
                                                        xlog.warning(
                                                            "已经存在词条：" + item +
                                                            "\t" + code_val)
                                                        continue
                                                    old_val = code_val
                                                    code_val += qm1[2]
                                                    if code_val in code_dict:
                                                        if code_dict[
                                                                code_val].count(
                                                                    item) > 0:
                                                            xlog.warning(
                                                                "已经存在词条：" +
                                                                item + "\t" +
                                                                code_val)
                                                            continue
                                                        old_val = code_val
                                                        code_val += qm2[2]
                                                        if code_val in code_dict:
                                                            if code_dict[
                                                                    code_val].count(
                                                                        item
                                                                    ) > 0:
                                                                xlog.warning(
                                                                    "已经存在词条：" +
                                                                    item +
                                                                    "\t" +
                                                                    code_val)
                                                                continue
                                                            code_dict[
                                                                code_val].append(
                                                                    item)
                                                            count += 1
                                                            results.append(
                                                                item + "\t" +
                                                                code_val +
                                                                "\n")
                                                            xlog.info(
                                                                "编码词条：" +
                                                                item + "\t" +
                                                                code_val +
                                                                " [同位编码：" +
                                                                code_dict[
                                                                    code_val]
                                                                [0] + "\t" +
                                                                code_val + "]")
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
                                                            xlog.info(
                                                                "编码词条：" +
                                                                item + "\t" +
                                                                code_val +
                                                                " [前置编码：" +
                                                                code_dict[
                                                                    old_val][0]
                                                                + "\t" +
                                                                old_val + "]")
                                                    else:
                                                        code_dict[code_val] = [
                                                            item
                                                        ]
                                                        count += 1
                                                        results.append(
                                                            item + "\t" +
                                                            code_val + "\n")
                                                        xlog.info(
                                                            "编码词条：" + item +
                                                            "\t" + code_val +
                                                            " [前置编码：" +
                                                            code_dict[old_val]
                                                            [0] + "\t" +
                                                            old_val + "]")
                                                else:
                                                    code_dict[code_val] = [
                                                        item
                                                    ]
                                                    count += 1
                                                    results.append(item +
                                                                   "\t" +
                                                                   code_val +
                                                                   "\n")
                                                    xlog.info(
                                                        "编码词条：" + item + "\t" +
                                                        code_val + " [前置编码：" +
                                                        code_dict[old_val][0] +
                                                        "\t" + old_val + "]")
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
                                                    if code_dict[
                                                            code_val].count(
                                                                item) > 0:
                                                        xlog.warning(
                                                            "已经存在词条：" + item +
                                                            "\t" + code_val)
                                                        continue
                                                    old_val = code_val
                                                    code_val += qm0[2]
                                                    if code_val in code_dict:
                                                        if code_dict[
                                                                code_val].count(
                                                                    item) > 0:
                                                            xlog.warning(
                                                                "已经存在词条：" +
                                                                item + "\t" +
                                                                code_val)
                                                            continue
                                                        old_val = code_val
                                                        code_val += qm1[2]
                                                        if code_val in code_dict:
                                                            if code_dict[
                                                                    code_val].count(
                                                                        item
                                                                    ) > 0:
                                                                xlog.warning(
                                                                    "已经存在词条：" +
                                                                    item +
                                                                    "\t" +
                                                                    code_val)
                                                                continue
                                                            code_dict[
                                                                code_val].append(
                                                                    item)
                                                            count += 1
                                                            results.append(
                                                                item + "\t" +
                                                                code_val +
                                                                "\n")
                                                            xlog.info(
                                                                "编码词条：" +
                                                                item + "\t" +
                                                                code_val +
                                                                " [同位编码：" +
                                                                code_dict[
                                                                    code_val]
                                                                [0] + "\t" +
                                                                code_val + "]")
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
                                                            xlog.info(
                                                                "编码词条：" +
                                                                item + "\t" +
                                                                code_val +
                                                                " [前置编码：" +
                                                                code_dict[
                                                                    old_val][0]
                                                                + "\t" +
                                                                old_val + "]")
                                                    else:
                                                        code_dict[code_val] = [
                                                            item
                                                        ]
                                                        count += 1
                                                        results.append(
                                                            item + "\t" +
                                                            code_val + "\n")
                                                        xlog.info(
                                                            "编码词条：" + item +
                                                            "\t" + code_val +
                                                            " [前置编码：" +
                                                            code_dict[old_val]
                                                            [0] + "\t" +
                                                            old_val + "]")
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
        if need_write:
            xlog.info("开始写入新码表内容...")
            with io.open(splicing_dict_file(dir_name, args["user"]),
                         mode="w",
                         encoding="utf-8") as f:
                f.writelines(results)
            xlog.info("写入新码表内容完成，编码工作结束。")

        # *校验工作
        # ?因为存在飞键的设计，所以不检验同一词条重码的情况
        xlog.info("开始校验...")
        redundancy_list = []
        multiple_list = []
        error_list = []

        second_level_dict = {}
        simplified_list = []

        for key in code_dict:
            key_len = len(key)
            for item in code_dict[key]:
                item_len = len(item)
                if item_len <= 1 or "aiouv;".find(key[0]) != -1:
                    continue

                # ?收集二级简码词条
                if args["verify"] and item_len == 2 and key_len <= 3:
                    second_level_dict[item] = key

                # *检验冗余的情况
                is_redundancy = False
                if item_len == 2:
                    # *二字词组
                    if key_len > 4:
                        if not key[:-1] in code_dict:
                            is_redundancy = True
                elif item_len == 3:
                    # *三字词组
                    if key_len > 3:
                        if not key[:-1] in code_dict:
                            is_redundancy = True
                elif item_len >= 4:
                    # *多字词组
                    if key_len > 4:
                        if not key[:-1] in code_dict:
                            is_redundancy = True

                if is_redundancy:
                    redundancy_list.append(item + "\t" + key)

                # *检验重码的情况
                is_multiple = False
                if item_len == 2:
                    # *二字词组
                    if key_len >= 4 and key_len < 6 and len(
                            code_dict[key]) > 1:
                        is_multiple = True
                elif item_len == 3:
                    # *三字词组
                    if key_len >= 3 and key_len < 6 and len(
                            code_dict[key]) > 1:
                        is_multiple = True
                elif item_len >= 4:
                    # *多字词组
                    if key_len >= 4 and key_len < 6 and len(
                            code_dict[key]) > 1:
                        is_multiple = True

                if is_multiple:
                    multiple_list.append(item + "\t" + key)

                # *检验错码的情况
                is_error = True
                if item_len == 2:
                    # *二字词组
                    if (not item[0] in single_dict) or (not item[1]
                                                        in single_dict):
                        is_error = False
                        continue

                    if key_len == 2:
                        for ele in single_dict[item[0]]:
                            if ele[0] == key[0]:
                                is_error = False
                                break
                        if not is_error:
                            is_error = True
                            if "bcdefghjklmnpqrstwxyz".find(key[1]) != -1:
                                # *二级简码
                                for ele in single_dict[item[1]]:
                                    if ele[0] == key[1]:
                                        is_error = False
                                        break
                            else:
                                for ele in single_dict[item[1]]:
                                    if ele[2] == key[1]:
                                        is_error = False
                                        break
                    elif key_len == 3:
                        # !在我的码表中这种情况只会是 525
                        for ele in single_dict[item[0]]:
                            if ele[0] == key[0]:
                                is_error = False
                                break
                        if not is_error:
                            is_error = True
                            for ele in single_dict[item[1]]:
                                if ele[2:4] == key[1:3]:
                                    is_error = False
                                    break
                    elif key_len == 4:
                        for ele in single_dict[item[0]]:
                            if ele[0:2] == key[0:2]:
                                is_error = False
                                break
                        if not is_error:
                            is_error = True
                            for ele in single_dict[item[1]]:
                                if ele[0:2] == key[2:4]:
                                    is_error = False
                                    break
                    elif key_len == 5:
                        for ele in single_dict[item[0]]:
                            if ele[0:2] == key[0:2] and ele[2] == key[4]:
                                is_error = False
                                break
                        if not is_error:
                            is_error = True
                            for ele in single_dict[item[1]]:
                                if ele[0:2] == key[2:4]:
                                    is_error = False
                                    break
                    elif key_len == 6:
                        for ele in single_dict[item[0]]:
                            if ele[0:2] == key[0:2] and ele[2] == key[4]:
                                is_error = False
                                break
                        if not is_error:
                            is_error = True
                            for ele in single_dict[item[1]]:
                                if ele[0:2] == key[2:4] and ele[2] == key[5]:
                                    is_error = False
                                    break
                elif item_len == 3:
                    # *三字词组
                    if (not item[0] in single_dict) or (
                            not item[1] in single_dict) or (not item[2]
                                                            in single_dict):
                        is_error = False
                        continue

                    if key_len == 3:
                        for ele in single_dict[item[0]]:
                            if ele[0] == key[0]:
                                is_error = False
                                break
                        if not is_error:
                            is_error = True
                            for ele in single_dict[item[1]]:
                                if ele[0] == key[1]:
                                    is_error = False
                                    break
                        if not is_error:
                            is_error = True
                            for ele in single_dict[item[2]]:
                                if ele[0] == key[2]:
                                    is_error = False
                                    break
                    elif key_len == 4:
                        for ele in single_dict[item[0]]:
                            for ele in single_dict[item[0]]:
                                if ele[0] == key[0] and ele[2] == key[3]:
                                    is_error = False
                                    break
                        if not is_error:
                            is_error = True
                            for ele in single_dict[item[1]]:
                                if ele[0] == key[1]:
                                    is_error = False
                                    break
                        if not is_error:
                            is_error = True
                            for ele in single_dict[item[2]]:
                                if ele[0] == key[2]:
                                    is_error = False
                                    break
                    elif key_len == 5:
                        for ele in single_dict[item[0]]:
                            for ele in single_dict[item[0]]:
                                if ele[0] == key[0] and ele[2] == key[3]:
                                    is_error = False
                                    break
                        if not is_error:
                            is_error = True
                            for ele in single_dict[item[1]]:
                                if ele[0] == key[1] and ele[2] == key[4]:
                                    is_error = False
                                    break
                        if not is_error:
                            is_error = True
                            for ele in single_dict[item[2]]:
                                if ele[0] == key[2]:
                                    is_error = False
                                    break
                    elif key_len == 6:
                        for ele in single_dict[item[0]]:
                            for ele in single_dict[item[0]]:
                                if ele[0] == key[0] and ele[2] == key[3]:
                                    is_error = False
                                    break
                        if not is_error:
                            is_error = True
                            for ele in single_dict[item[1]]:
                                if ele[0] == key[1] and ele[2] == key[4]:
                                    is_error = False
                                    break
                        if not is_error:
                            is_error = True
                            for ele in single_dict[item[2]]:
                                if ele[0] == key[2] and ele[2] == key[5]:
                                    is_error = False
                                    break
                elif key_len >= 4:
                    # *多字词组
                    if (not item[0] in single_dict) or (
                            not item[1] in single_dict) or (
                                not item[2] in single_dict) or (
                                    not item[-1] in single_dict):
                        is_error = False
                        continue

                    if key_len == 4:
                        for ele in single_dict[item[0]]:
                            if ele[0] == key[0]:
                                is_error = False
                                break
                        if not is_error:
                            is_error = True
                            for ele in single_dict[item[1]]:
                                if ele[0] == key[1]:
                                    is_error = False
                                    break
                        if not is_error:
                            is_error = True
                            for ele in single_dict[item[2]]:
                                if ele[0] == key[2]:
                                    is_error = False
                                    break
                        if not is_error:
                            is_error = True
                            for ele in single_dict[item[-1]]:
                                if ele[0] == key[3]:
                                    is_error = False
                                    break
                    elif key_len == 5:
                        for ele in single_dict[item[0]]:
                            if ele[0] == key[0] and ele[2] == key[4]:
                                is_error = False
                                break
                        if not is_error:
                            is_error = True
                            for ele in single_dict[item[1]]:
                                if ele[0] == key[1]:
                                    is_error = False
                                    break
                        if not is_error:
                            is_error = True
                            for ele in single_dict[item[2]]:
                                if ele[0] == key[2]:
                                    is_error = False
                                    break
                        if not is_error:
                            is_error = True
                            for ele in single_dict[item[-1]]:
                                if ele[0] == key[3]:
                                    is_error = False
                                    break
                    elif key_len == 6:
                        for ele in single_dict[item[0]]:
                            if ele[0] == key[0] and ele[2] == key[4]:
                                is_error = False
                                break
                        if not is_error:
                            is_error = True
                            for ele in single_dict[item[1]]:
                                if ele[0] == key[1] and ele[2] == key[5]:
                                    is_error = False
                                    break
                        if not is_error:
                            is_error = True
                            for ele in single_dict[item[2]]:
                                if ele[0] == key[2]:
                                    is_error = False
                                    break
                        if not is_error:
                            is_error = True
                            for ele in single_dict[item[-1]]:
                                if ele[0] == key[3]:
                                    is_error = False
                                    break

                if is_error:
                    error_list.append({"word": item, "code": key})

        redundancy_count = len(redundancy_list)
        multiple_count = len(multiple_list)

        if args["ignore"] and os.path.exists(args["ignore"]):
            ignore_list = read_file_2_list(args["ignore"])
            if len(ignore_list) > 0:
                new_error_list = []
                for error_item in error_list:
                    if ignore_list.count(error_item["word"]) > 0:
                        continue
                    new_error_list.append(error_item)
                error_list = new_error_list

        error_count = len(error_list)

        if redundancy_count > 0:
            xlog.info("================================================")
            xlog.warning("共检测到 " + str(redundancy_count) + " 组冗余码：")
            for r_item in redundancy_list:
                xlog.warning(r_item)
            xlog.info("================================================")
        if multiple_count > 0:
            xlog.info("================================================")
            xlog.warning("共检测到 " + str(multiple_count) + " 组重码：")
            for m_item in multiple_list:
                xlog.warning(m_item)
            xlog.info("================================================")
        if error_count > 0:
            xlog.info("================================================")
            xlog.warning("共检测到 " + str(error_count) + " 组错码：")
            for e_item in error_list:
                xlog.warning(e_item["word"] + "\t" + e_item["code"])
            xlog.info("================================================")

        if args["verify"]:
            xlog.info("开始校验简码所对应的声韵词组...")
            for key in code_dict:
                for item in code_dict[key]:
                    if len(item) == 2 and len(key) > 3:
                        if item in second_level_dict:
                            simplified_list.append(
                                f"{item}\t{key}\t({item}\t{second_level_dict[item]})"
                            )
                            continue
                        if (item[0]
                                in first_level_dict) and (item[1]
                                                          in first_level_dict):
                            simplified_list.append(
                                f"{item}\t{key}\t({item[0]}|{item[1]}\t{first_level_dict[item[0]]}_{first_level_dict[item[1]]}_)"
                            )
            simplified_count = len(simplified_list)
            if simplified_count > 0:
                xlog.info("================================================")
                xlog.warning("共检测到 " + str(simplified_count) + " 组存在简码的声韵词组：")
                for s_item in simplified_list:
                    xlog.warning(s_item)
                xlog.info("================================================")

        xlog.info("校验已完成。")

        if args["gdq"]:
            xlog.info("开始生成跟打器所用的码表文件...")
            gdq_list = get_gdq_list(code_dict)
            with io.open(args["gdq"], mode="w", encoding="utf-8-sig") as f:
                f.writelines(gdq_list)
            xlog.info("生成跟打器所用的码表文件完成。")

        xlog.info("************************************************")
        xlog.info("所有操作都已完成。")
