import re
import requests
from DBUtils.PooledDB import PooledDB
from lxml import html
import pymysql
import traceback

from PreProcess.DFAFilter import DFAFilter

db_info = {}
# db = pymysql.connect(host=db_info['host'], port=db_info['port'], user=db_info['user'], passwd=db_info['passwd'],
#                      db=db_info['dbname'])
thread_number = 20
pool = PooledDB(pymysql, thread_number, host=db_info['host'], port=db_info['port'], user=db_info['user'],
                passwd=db_info['passwd'], db=db_info['dbname'])
# c = db.cursor()

gfw = DFAFilter()
path = "../UnNormal.txt"
gfw.parse(path)


def readUnlabeledData():
    try:
        conn = pool.connection()
        c = conn.cursor()
        sql = """select domain,description,keywords,flag from domain_headers where flag != 0 and keywords !="" """
        c.execute(sql)
        conn.commit()
        results = c.fetchall()
        data = [
            {"domain": i[0], "description": i[1], "keywords": i[2], "flag": i[3]}
            for i in results]
        c.close()
        conn.close()
        return data
    except Exception as e:
        print(e)
        c.close()
        conn.close()
        return


def readLabeledData():
    try:
        conn = pool.connection()
        c = conn.cursor()
        sql = """select domain,description,keywords,first_level,second_level,flag from domain_headers where flag != 0 and keywords !="" """
        c.execute(sql)
        conn.commit()
        results = c.fetchall()
        data = [
            {"domain": i[0], "description": i[1], "keywords": i[2], "first_level": i[3], "second_level": i[4],
             "flag": i[5]}
            for i in results]
        c.close()
        conn.close()
        return data
    except Exception as e:
        print(e)
        c.close()
        conn.close()
        return


def label404():
    try:
        conn = pool.connection()
        c = conn.cursor()
        readySql = "set SQL_SAFE_UPDATES=0"
        c.execute(readySql)
        conn.commit()
        sql = """update domain_headers set flag=3 where keywords='' and id>=1 """
        print(sql)
        c.execute(sql)
        conn.commit()
        c.close()
        conn.close()
        print("运行完成")
    except Exception as e:
        print(e)
        c.close()
        conn.close()


def isYGP(text):
    return gfw.isNormalFilter(text)


def labelUnNormal(data):
    try:
        conn = pool.connection()
        c = conn.cursor()
        ready_sql = "SET SQL_SAFE_UPDATES = 0"
        c.execute(ready_sql)
        count = 0
        for i in range(len(data)):
            domain = data[i]["domain"]
            description = data[i]["description"]
            keywords = data[i]["keywords"]
            is_description_normal = isYGP(description)
            is_keywords_normal = isYGP(keywords)
            if is_description_normal == False and is_keywords_normal == False:
                # print("网址: " + domain + " 描述:" + description + " 关键词: " + keywords)
                count += 1
            if is_description_normal == False or is_keywords_normal == False:
                sql = """update domain_headers set flag = 2 where id<>0 and domain = "{}" and description = "{}" """ \
                    .format(domain, description)
                print(sql)
                c.execute(sql)
        print(count)
        conn.commit()
        c.close()
        conn.close()
    except Exception as e:
        print(e)
        c.close()
        conn.close()


data = readLabeledData()
# print(len(data))
# for i in range(len(data)):
#     print("域名: " + data[i]['domain'] + " 关键词: " + data[i]['keywords'] + " 描述: " + data[i]['description'])
# label404()
labelUnNormal(data)
