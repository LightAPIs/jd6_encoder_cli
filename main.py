# -*- coding: utf-8 -*-
import os
import io
import yaml
import argparse
from log import Logger
from pinyin import PinYin


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


def parse_code_dict(code_dict, single_dict, level_dict, is_verify, word_list):
    for word in word_list:
        item = word.strip()
        if is_word_item(item):
            item_list = item.split("\t")
            if len(item_list) < 2:
                continue
            ct = item_list[0]
            bm = item_list[1]
            if bm in code_dict:
                code_dict[bm].append(ct)
            else:
                code_dict[bm] = [ct]

            if len(ct) != 1:
                continue
            if len(bm) >= 4:
                # !1. 单字的全码至少为四码
                # !2. 仅用于编码和校验词条，故只需要取前四码
                cut_bm = bm[:4]
                if ct in single_dict:
                    if single_dict[ct].count(cut_bm) == 0:
                        single_dict[ct].append(cut_bm)
                else:
                    single_dict[ct] = [cut_bm]

            # ?收集一级简码词条
            if not is_verify:
                continue
            if len(bm) == 1 and "abcdefghijklmnopqrstuvwxyz".count(bm) == 1:
                dup = 0
                for ch in level_dict:
                    if level_dict[ch] == bm:
                        dup += 1
                if dup < 2:
                    level_dict[ct] = bm


def get_word_dict(code_dict):
    word_dict = {}
    for key in code_dict:
        for item in code_dict[key]:
            if item in word_dict:
                word_dict[item].append(key)
            else:
                word_dict[item] = [key]
    return word_dict


def get_gdq_list(encode_dict):
    gdq_list = []
    for code in encode_dict:
        for word in encode_dict[code]:
            gdq_list.append(word + "\t" + code + "\n")
    return gdq_list


def is_part(lhs, rhs):
    if lhs.find(rhs) >= 0 or rhs.find(lhs) >= 0:
        return True
    return False


def is_start_with(lhs, rhs):
    if lhs.find(rhs) == 0 or rhs.find(lhs) == 0:
        return True
    return False

def getSystemInform():
    import platform
    system = platform.system()
    if system == "Windows":
        return "windows"
    elif system == "Linux":
        return "linux"
    else:
        return "mac"

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Rime星空键道6编码器")
    ap.add_argument("-d",
                    "--dict",
                    required=False,
                    help="输入词库控制文件路径，如 /path/to/xkjd6.extended.dict.yaml")
    ap.add_argument("-u",
                    "--user",
                    required=False,
                    default="xkjd6.user",
                    help="可选，输入用户词库名称，默认为 xkjd6.user")
    ap.add_argument("-g", "--gdq", required=False, help="可选，生成跟打器所用的码表文件路径")
    ap.add_argument("-i", "--ignore", required=False, help="可选，忽略错码检测的列表文件路径")
    ap.add_argument("-s",
                    "--single",
                    required=False,
                    action="store_true",
                    help="可选，额外启用校验单字编码的冗余情况")
    ap.add_argument("-f",
                    "--fly",
                    required=False,
                    action="store_true",
                    help="可选，额外启用校验飞键词组的编码是否缺失")
    ap.add_argument("-v",
                    "--verify",
                    required=False,
                    action="store_true",
                    help="可选，额外启用校验简码所对应的声韵词组")
    ap.add_argument("-a",
                    "--irrational",
                    required=False,
                    action="store_true",
                    help="可选，额外启用校验单字编码编排是否合理")
    ap.add_argument("-r",
                    "--remote",
                    required=False,
                    action="store_true",
                    help="可选，启用远程 API 获取多音字的拼音，需填写 config.ini")

    args = vars(ap.parse_args())
    xlog = Logger("DEBUG", "log")

    if args["dict"] is None:
        os_type = getSystemInform()
        if os_type == "windows":
            args["dict"] = os.environ['USERPROFILE']+"\\AppData\\Roaming\\Rime\\xkjd6.extended.dict.yaml"
        elif os_type == "linux":
            args["dict"] = "~/.config/fcitx5/rime/xkjd6.extended.dict.yaml"
            if not os.path.exists(args["dict"]):
                args["dict"] = "~/.config/fcitx/rime/xkjd6.extended.dict.yaml"#兼容fcitx4
        elif os_type == "mac":
            args["dict"] = "~/Library/Rime/xkjd6.extended.dict.yaml"#由copilot提供，未测试是否正确

    xlog.info("************************************************")
    xlog.info("词库控制文件：" + args["dict"])
    xlog.info("用户词库名称：" + args["user"])
    if args["gdq"]:
        xlog.info("生成跟打器所用的码表文件：" + args["gdq"])
    if args["ignore"]:
        xlog.info("忽略错码检测的列表文件：" + args["ignore"])
    if args["single"]:
        xlog.info("额外启用校验单字编码的冗余情况。")
    if args["fly"]:
        xlog.info("额外启用校验飞键词组的编码是否缺失。")
    if args["irrational"]:
        xlog.info("额外启用校验单字编码编排是否合理。")
    if args["verify"]:
        xlog.info("额外启用校验简码所对应的声韵词组。")
    if args["remote"]:
        xlog.info("启用远程 API 获取多音字的拼音。")
    xlog.info("************************************************")

    # if not os.path.exists(args["dict"]):
    #     xlog.error("词库控制文件不存在！操作终止。")
    #     exit()

    # *编码工作
    xlog.info("开始解析词库...")
    dir_name = os.path.dirname(args["dict"])
    xlog.info("词库所在目录：" + dir_name)

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
            parse_code_dict(code_dict, single_dict, first_level_dict,
                            args["verify"], read_list)
            xlog.info("读取并解析词库：" + file_name)
        else:
            user_list = read_list
            xlog.info("读取用户词库：" + file_name)

    xlog.info("共读取到 " + str(len(code_dict)) + " 组编码。")
    xlog.info("共读取到 " + str(len(single_dict)) + " 个单字。")
    if args["verify"]:
        xlog.info("共读取到 " + str(len(first_level_dict)) + " 个一级简码。")

    xlog.info("开始编码词组...")
    py = PinYin(xlog, single_dict, code_dict, args["remote"])

    count = 0
    results = []
    need_write = False
    for item in user_list:
        item = item.strip()
        if is_word_item(item):
            if item.find("\t") != -1:
                # 已编码的词条
                item_list = item.split("\t")
                py.add_code_to_dict(item_list)
                results.append(item + "\n")
            else:
                need_write = True
                if len(item) <= 1:
                    xlog.warning("无法编码单字词条：" + item)
                    continue

                encoded = py.encode_word(item)
                for enc in encoded:
                    if enc["status"] == -1:
                        xlog.warning(f"码表中不存在该字：{enc['val']}，故无法编码词条：{item}")
                    elif enc["status"] == 0:
                        xlog.warning(f"已经存在词条：{item}\t{enc['val']}")
                    elif enc["status"] == 1:
                        count += 1
                        results.append(item + "\t" + enc['val'] + "\n")
                        xlog.info(f"编码词条：{item}\t{enc['val']}")
                    elif enc["status"] == 2:
                        count += 1
                        results.append(item + "\t" + enc['val'] + "\n")
                        xlog.info(
                            f"编码词条：{item}\t{enc['val']} [前置编码：{enc['ext']}]")
                    elif enc["status"] == 3:
                        count += 1
                        results.append(item + "\t" + enc['val'] + "\n")
                        xlog.info(f"编码词条：{item} [同位编码：{enc['ext']}]")
        else:
            # 非词条
            results.append(item + "\n")

    code_dict = py.get_code_dict()
    xlog.info("编码完成。共新增 " + str(count) + " 组词条。")
    if need_write:
        xlog.info("开始写入新码表内容...")
        with io.open(splicing_dict_file(dir_name, args["user"]),
                     mode="w",
                     encoding="utf-8") as f:
            f.writelines(results)
        xlog.info("写入新码表内容完成，编码工作结束。")

    # *校验工作
    xlog.info("开始校验码表...")
    redundancy_list = []
    multiple_list = []
    error_list = []

    second_level_dict = {}

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
                if key_len >= 4 and key_len < 6 and len(code_dict[key]) > 1:
                    is_multiple = True
            elif item_len == 3:
                # *三字词组
                if key_len >= 3 and key_len < 6 and len(code_dict[key]) > 1:
                    is_multiple = True
            elif item_len >= 4:
                # *多字词组
                if key_len >= 4 and key_len < 6 and len(code_dict[key]) > 1:
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
                    # !先判定 525 的情况
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

                    # !再判定三级简码的情况
                    if is_error:
                        for ele in single_dict[item[0]]:
                            if ele[0:2] == key[0:2]:
                                is_error = False
                                break
                        if not is_error:
                            is_error = True
                            for ele in single_dict[item[1]]:
                                if ele[0] == key[2]:
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
                if (not item[0]
                        in single_dict) or (not item[1] in single_dict) or (
                            not item[2] in single_dict) or (not item[-1]
                                                            in single_dict):
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

    word_dict = get_word_dict(code_dict)

    # ?校验同一词条的编码冗余情况
    surplus_list = []
    # ?校验单字的编码冗余情况
    blank_list = []
    # ?校验飞键词组的编码是否缺失
    fly_list = []
    fly_dict = py.get_fly_dict()

    for word in word_dict:
        word_len = len(word)
        group_len = len(word_dict[word])
        if word_len < 2:
            if not args["single"]:
                continue
            is_blank = False
            min_list = [word_dict[word][0]]
            max_list = [word_dict[word][0]]
            for i in range(1, group_len):
                cur_code = word_dict[word][i]
                is_min_had = False
                for j in range(len(min_list)):
                    if is_start_with(min_list[j], cur_code):
                        is_min_had = True
                        min_list[j] = cur_code if len(cur_code) < len(
                            min_list[j]) else min_list[j]
                if not is_min_had:
                    min_list.append(cur_code)

                is_max_had = False
                for j in range(len(max_list)):
                    if is_start_with(max_list[j], cur_code):
                        is_max_had = True
                        max_list[j] = cur_code if len(cur_code) > len(
                            max_list[j]) else max_list[j]
                if not is_max_had:
                    max_list.append(cur_code)

            for code_item in word_dict[word]:
                if min_list.count(code_item) > 0 or max_list.count(
                        code_item) == 0:
                    for j in range(1, len(code_item)):
                        if not code_item[0:j] in code_dict:
                            is_blank = True
                            break
                        # !可以要求必须是单字
                        # else:
                        #     is_blank = True
                        #     for temp_word in code_dict[code_item[0:j]]:
                        #         if len(temp_word) == 1:
                        #             is_blank = False
                        #             break
                        # if is_blank:
                        #     break
                if is_blank:
                    break
            if is_blank:
                blank_list.append(f"{word}: [{' '.join(word_dict[word])}]")
            continue

        if group_len > 1:
            is_surplus = False
            for i in range(0, group_len):
                for j in range(i + 1, group_len):
                    if is_part(word_dict[word][i], word_dict[word][j]):
                        is_surplus = True
                        break
                if is_surplus:
                    break
            if is_surplus:
                surplus_list.append(f"{word}: [{' '.join(word_dict[word])}]")

        if args["fly"]:
            is_fly_err = False
            for i in range(word_len):
                if i < 3 or i == word_len - 1:
                    index = i if i < 3 else 3
                    if word[i] in fly_dict:
                        fly_count = 0
                        use_code_list = []
                        for code in word_dict[word]:
                            use_code = code[index]
                            if word_len == 2:
                                use_code = code[(index * 2):(index * 2 + 2)]
                            if use_code_list.count(use_code) > 0:
                                continue
                            use_code_list.append(use_code)
                            for fly_code in fly_dict[word[i]]:
                                if fly_code[:(len(use_code))] == use_code:
                                    fly_count += 1
                        if fly_count == 1:
                            is_fly_err = True
                            break
            if is_fly_err:
                log_str = " ".join(word_dict[word])
                fly_list.append(f"{word}: [{log_str}]")

    surplus_count = len(surplus_list)
    blank_count = len(blank_list)
    fly_err_count = len(fly_list)
    if surplus_count > 0:
        xlog.info("================================================")
        xlog.warning("共检测到 " + str(surplus_count) + " 组词条存在编码冗余：")
        for s_item in surplus_list:
            xlog.warning(s_item)
        xlog.info("================================================")
    if blank_count:
        xlog.info("================================================")
        xlog.warning("共检测到 " + str(blank_count) + " 组单字存在编码冗余：")
        for b_item in blank_list:
            xlog.warning(b_item)
        xlog.info("================================================")
    if fly_err_count > 0:
        xlog.info("================================================")
        xlog.warning("共检测到 " + str(fly_err_count) + " 组可能存在飞键编码缺失的词条：")
        for f_item in fly_list:
            xlog.warning(f_item)
        xlog.info("================================================")

    if args["irrational"]:
        xlog.info("开始校验单字编码的编排是否合理...")
        irrational_list = []
        for key in code_dict:
            group_list = code_dict[key]
            single_list = [
                group_list[i] for i in range(len(group_list))
                if len(group_list[i]) == 1
            ]
            if len(single_list) >= 2:
                first_single = single_list[0]
                key_len = len(key) - 1
                while key_len > 0:
                    a_key = key[0:key_len]
                    if a_key in code_dict:
                        if code_dict[a_key][0] == first_single:
                            irrational_list.append(
                                f"{key}: [{' '.join(single_list)}]")
                        break
                    key_len -= 1
        irrational_count = len(irrational_list)
        if irrational_count > 0:
            xlog.info("================================================")
            xlog.warning("共检测到 " + str(irrational_count) + " 组编排不合理的单字编码：")
            for i_item in irrational_list:
                xlog.warning(i_item)
            xlog.info("================================================")

    if args["verify"]:
        xlog.info("开始校验简码所对应的声韵词组...")
        simplified_list = []
        for key in code_dict:
            for item in code_dict[key]:
                if len(item) == 2 and len(key) > 3:
                    if item in second_level_dict:
                        simplified_list.append(
                            f"{item}\t{key}\t({item}\t{second_level_dict[item]})"
                        )
                        continue
                    if (item[0] in first_level_dict) and (item[1]
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
