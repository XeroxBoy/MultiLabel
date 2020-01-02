import re
import requests
from lxml import html
import pymysql
import traceback

db_info = {'host': '10.0.3.11', 'port': 3306, 'user': 'root', 'passwd': 'Ntci@85418825', 'dbname': 'sx'}
db = pymysql.connect(host=db_info['host'], port=db_info['port'], user=db_info['user'], passwd=db_info['passwd'],
                     db=db_info['dbname'])
c = db.cursor()


def readUnlabeledData():
    sql = """select domain,description,keywords,flag from domain_headers where flag != 0 and keywords !="" """
    c.execute(sql)
    results = c.fetchall()
    data = [i[0] for i in results]
    return data


def readLabeledData():
    sql = """select domain,description,keywords,first_level,second_level,flag from domain_headers where flag != 0 and keywords !="" """
    c.execute(sql)
    results = c.fetchall()
    data = [i[0] for i in results]
    return data


def label404():
    sql = """update domain_headers set flag = 3 where keywords="" """
    c.execute(sql)


def isYGP(text):
    
    pass


def labelUnNormal(data):
    for i in range(len(data)):
        domain = data[i]["domain"]
        description = data[i]["description"]
        keywords = data[i]["keywords"]
        isDescriptionNormal = isYGP(description)
        isKeywordsNormal = isYGP(keywords)
        if isDescriptionNormal == False or isKeywordsNormal == False:
            sql = """update domain_headers set flag = 2 where  domain = "{}" and description = "{}" """ \
                .format(domain, description)
            c.execute(sql)