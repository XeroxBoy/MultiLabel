# -*- coding:utf-8 -*-

import time

# from pybloomfilter import BloomFilter
import pymysql

time1 = time.time()


# DFA算法
class DFAFilter:
    num_20_count = 0
    num_25_count = 0
    num_15_count = 0
    num_10_count = 0

    def __init__(self):
        self.keyword_chains = {}
        self.delimit = '\x00'

    def add(self, keyword):
        keyword = keyword.lower()
        chars = keyword.strip()
        if not chars:
            return
        level = self.keyword_chains
        for i in range(len(chars)):
            if chars[i] in level:
                level = level[chars[i]]
            else:
                if not isinstance(level, dict):
                    break
                for j in range(i, len(chars)):
                    level[chars[j]] = {}
                    last_level, last_char = level, chars[j]
                    level = level[chars[j]]
                last_level[last_char] = {self.delimit: 0}
                break
        if i == len(chars) - 1:
            level[self.delimit] = 0

    def parse(self, path):
        with open(path, encoding='utf-8') as f:
            for keyword in f:
                self.add(str(keyword).strip())
        f.close()

    def filter(self, message, repl="*"):
        message = message.lower()
        ret = []
        start = 0
        while start < len(message):
            level = self.keyword_chains
            step_ins = 0
            for char in message[start:]:
                if char in level:
                    step_ins += 1
                    if self.delimit not in level[char]:
                        level = level[char]
                    else:
                        ret.append(repl * step_ins)
                        start += step_ins - 1
                        break
                else:
                    ret.append(message[start])
                    break
            else:
                ret.append(message[start])
            start += 1

        return ''.join(ret)

    def isNormalFilter(self, message):
        message = message.lower()
        all_length = len(message)
        un_normal_length = 0
        start = 0
        while start < len(message):
            level = self.keyword_chains
            step_ins = 0
            for char in message[start:]:
                if char in level:
                    step_ins += 1
                    if self.delimit not in level[char]:
                        level = level[char]
                    else:
                        un_normal_length += 1
                        start += step_ins - 1
                else:
                    break
            else:
                pass
            start += 1
        if all_length != 0:
            un_normal_rate = un_normal_length / all_length
        else:
            un_normal_rate = 0
        # if un_normal_rate > 0.1:
        #     self.num_10_count += 1
        # if un_normal_rate > 0.2:
        #     self.num_20_count += 1
        # if un_normal_rate > 0.25:
        #     self.num_25_count += 1
        if un_normal_rate > 0.10:
            self.num_10_count += 1
            return False
        else:
            return True


if __name__ == "__main__":
    db_info = {'host': '10.0.3.11', 'port': 3306, 'user': 'root', 'passwd': 'Ntci@85418825', 'dbname': 'sx'}
    db = pymysql.connect(host=db_info['host'], port=db_info['port'], user=db_info['user'], passwd=db_info['passwd'],
                         db=db_info['dbname'])
    c = db.cursor()
    gfw = DFAFilter()
    path = "../UnNormal.txt"
    gfw.parse(path)
    sql = """select description,keywords from domain_headers where description != "" and keywords != "" """
    c.execute(sql)
    data = c.fetchall()
    data_length = len(data)
    kw_un_normal_count = 0
    des_un_normal_count = 0
    both_un_normal_count = 0
    # for i in range(len(data)):
    #     description = data[i][0]
    #     if description != "":
    #         gfw.isNormalFilter(description)
    for i in range(len(data)):
        description = data[i][0]
        keywords = data[i][1]
        if keywords != "":
            is_kw_normal = gfw.isNormalFilter(keywords)
            is_des_normal = gfw.isNormalFilter(description)
            if not is_kw_normal and not is_des_normal:
                both_un_normal_count += 1
            if not is_kw_normal:
                kw_un_normal_count += 1
            if not is_des_normal:
                des_un_normal_count += 1
    # print("高于0.10的有: " + str(gfw.num_10_count))
    print("高于0.10的有: " + str(gfw.num_15_count))
    # print("高于0.20的有: " + str(gfw.num_20_count))
    # print("高于0.25的有: " + str(gfw.num_25_count))
    print("总数据有:" + str(data_length))
    print("keywords不正常数有: " + str(kw_un_normal_count))
    print("description不正常数有: " + str(kw_un_normal_count))
    print("两样都不正常数有: " + str(both_un_normal_count))
    # print(text)
    # print(result)
