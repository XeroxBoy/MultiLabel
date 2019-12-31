import re
import requests
from lxml import html
import pymysql
import traceback

PROXIES = {
    'http': '127.0.0.1:1080',
    'https': '127.0.0.1:1080'
}  # 代理翻墙，爬国外网站用的
db_info = {}
db = pymysql.connect(host=db_info['host'], port=db_info['port'], user=db_info['user'], passwd=db_info['passwd'],
                     db=db_info['dbname'])


# c = db.cursor()
# task_table = "domain_name"  # 要爬取的表名


#
# def get_domain():
#     sql = "select domain from " + task_table
#     c.execute(sql)
#     results = c.fetchall()
#     data = [i[0] for i in results]
#     return data
#
#
# def already_done():
#     sql = "select domain from domain_key_word"
#     c.execute(sql)
#     results = c.fetchall()
#     data = [i[0] for i in results]
#     return data


def save(data, conn):
    c = conn.cursor()
    sql = """insert into domain_key_word (domain,description,keywords) values("{}","{}","{}")""".format(
        data['domain'],
        data['description'].replace(
            '"', "'"),
        data['keywords'].replace(
            '"', "'"))
    try:
        print(sql)
        # print(data['domain'])
        c.execute(sql)
        conn.commit()
        if data['description'] != '':
            print(data['domain'] + " 保存成功")
        data['domain'] = data['domain'].replace('http://', "")
        # print(data['domain'])
        new_sql = """update domain_name set flag = 1 where domain = "{}" """.format(data['domain'])
        c.execute(new_sql)
        conn.commit()
        return 0
    except Exception as e:
        conn.rollback()
        sql = """insert into domain_key_word (domain,description,keywords) values("{}","{}","{}")""".format(
            data['domain'], '', '')
        c.execute(sql)
        conn.commit()
        print(e)
        print(data['domain'] + " have save error")
        # traceback.print_exc()
        return -1


def get_info(url):
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1'}
    data = {'domain': url, 'keywords': '', 'description': ''}
    try:
        response = requests.get(url, headers=header, timeout=2)
        charsetx = charset(response.text)
        response.encoding = charsetx
    except:
        try:
            response = requests.get(url, headers=header, timeout=7, proxies=PROXIES, allow_redirects=True)
        except Exception as e:
            # traceback.print_exc()
            print(e)
            print(url + " have requests error")
            return data
    try:
        tree = html.fromstring(response.text)
        head = tree.xpath('head')[0]
        # code_type = head.xpath('./meta[@http-equiv="Content-Type"]/@content')[0].split('=')[-1]
        metas = head.xpath('.//meta')
        for i in metas:
            name = i.xpath('./@name')
            if len(name) == 0:
                continue
            value = i.xpath('./@content')
            if name[0].lower() == "keywords":
                data['keywords'] = value[0]
            elif name[0].lower() == "description":
                data['description'] = value[0]
        return data
    except Exception as e:
        print(e)
        # traceback.print_exc()
        print(url + ' have extract error')
        return data


def charset(html):
    charset = None
    m = re.compile('<meta .*(http-equiv="?Content-Type"?.*)?charset="?([a-zA-Z0-9_-]+)"?', re.I).search(html)
    if m and m.lastindex == 2:
        charset = m.group(2).lower()
    return charset

#
# def main():
#     task = get_domain()
#     ad = already_done()
#     lens = len(task)
#     for url in task:
#         if "http" not in url:
#             url = "http://"+url
#         if url in ad:
#             lens -= 1
#             continue
#         print("还剩" + str(lens))
#         data = get_info(url)
#         save(data)
#         lens -= 1
#
#
# main()
