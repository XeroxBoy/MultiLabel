# -*- coding:utf-8 -*-

import time

# from pybloomfilter import BloomFilter

time1 = time.time()


# DFA算法
class DFAFilter:
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
                        start += step_ins - 1
                        return False
                else:
                    break
            else:
                return True
            start += 1
        return True


if __name__ == "__main__":
    gfw = DFAFilter()
    path = "../UnNormal.txt"
    gfw.parse(path)
    text = '曰本真人性做爰在线观看_免费人做人爱的视频_免费观看-女人天堂'
    result = gfw.isNormalFilter(text)

    print(text)
    print(result)
    time2 = time.time()
    print('总共耗时：' + str(time2 - time1) + 's')
