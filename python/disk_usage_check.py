#!/usr/bin/python
# -*- coding: UTF-8 -*-
import threading
import time
import queue as Queue
import csv
from fabric import Connection
import logging
logger = logging.getLogger('check disk usage')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('./check_disk_usage.log')
fh.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)


formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)


logger.addHandler(fh)
logger.addHandler(ch)

start = time.time()




def do_check_disk(threadName,q):
    # 从队列里获取目标
    i = q.get(timeout=2)
    c = Connection(host=i[2], user='prtg',connect_timeout=5, connect_kwargs={"key_filename":['/home/devops/.ssh/id_30_rsa']})
    try:
        disk_result = c.run("df -hP / | grep / | awk '{print $(NF -2) $(NF -1)}'", pty=True, hide=True,)
        disk_free,disk_use_percent = disk_result.stdout.split("G")
        disk_free = int(disk_free)
        disk_use_percent=int(disk_use_percent.replace('%',''))
        if disk_free < 30 and disk_use_percent > 95:
            # print(i[0],"\t",i[2],"\t",disk_free)
            logger.error(" {} {} disk usage alert!".format(i[0],i[2]))

    except Exception as e:
        logger.error(" {} {} host disk check fail,since:{}".format(i[0],i[2],e))


class myThread(threading.Thread):
    def __init__(self,name,q):
        threading.Thread.__init__(self)
        self.name = name
        self.q = q
    def run(self):
        print("Starting " + self.name)
        while True:
            try:
                do_check_disk(self.name,self.q)
            except:
                break
        print("Exiting " + self.name)


# url列表，这里是虚构的,现实情况这个列表里有大量的url
with open('dblist_20211024.csv', newline='') as f:
    reader = csv.reader(f)
    link_list = [item for item in reader]

# 创建5个线程名
threadList = ["Thread-1","Thread-2","Thread-3","Thread-4","Thread-5","Thread-6","Thread-7","Thread-8"]

# 设置队列长度
workQueue = Queue.Queue(300)

# 线程池
threads = []

#创建新线程
for tName in threadList:
    thread = myThread(tName,workQueue)
    thread.start()
    threads.append(thread)

#将url填充到队列
for url in link_list:
    workQueue.put(url)

#等待所有线程完成
for t in threads:
    t.join()

end = time.time()
print('数据库磁盘检查总时间为：',end-start)
