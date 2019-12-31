import re
import requests
from lxml import html
import pymysql
import traceback
import threading
from queue import Queue
from aleax_top_extract import get_info, save
from DBUtils.PooledDB import PooledDB

mutex = threading.Lock()
thread_number = 20
db_info ={}
pool = PooledDB(pymysql, thread_number, host=db_info['host'], port=db_info['port'], user=db_info['user'],
                passwd=db_info['passwd'], db=db_info['dbname'])


def get_domain():
    conn = pool.connection()
    c = conn.cursor()
    sql = "select domain from domain_name where flag=0"
    c.execute(sql)
    results = c.fetchall()
    c.close()
    conn.close()
    domain_queue = Queue()
    for i in results:
        domain_queue.put(i[0])
    return domain_queue


def threads(q, pool):
    while 1:
        try:
            mutex.acquire()
            if q.qsize() > 0:
                domain = q.get()
                print("队列还剩" + str(q.qsize()))
                mutex.release()
            else:
                mutex.release()
                return 0
            if "http" not in domain:
                domain = "http://" + domain
            data = get_info(domain)
            print(data['keywords'])
            conn = pool.connection()
            save(data, conn)
        except:
            continue


def main():
    tt = []
    q = get_domain()
    for i in range(thread_number):
        t = threading.Thread(target=threads, args=(q, pool,))
        tt.append(t)
        t.start()
    for t in tt:
        t.join()
    print("任务结束")


main()
