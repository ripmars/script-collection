# coding:utf-8

# python lib
#from subprocess import Popen,PIPE
from threading import Timer
import psutil,platform
import time,datetime
#import threading
import pycurl
#import StringIO
import sys,os,socket
#import ping
import json
#import urllib, urllib2,requests


def write_to_file(fname, message):
    #os.makedirs(os.path.dirname(file_to_write))
    #os.makedirs(os.path.dirname(file_to_write),exist_ok=True)
    fh = open(fname, 'a')
    fh.write(message+'\n')
    fh.close()


class Test:
    def __init__(self):
        self.contents = ''
    def body_callback(self,buf):
        self.contents = self.contents + buf

def http_monitor(monitor_url):
    t = Test()
    #gzip_test = file("gzip_test.txt", 'w')
    c = pycurl.Curl()
    c.setopt(pycurl.WRITEFUNCTION,t.body_callback)
    c.setopt(pycurl.ENCODING, 'gzip')
    c.setopt(pycurl.URL,monitor_url)
    c.perform()
    http_code = c.getinfo(pycurl.HTTP_CODE)
    http_conn_time = c.getinfo(pycurl.CONNECT_TIME)
    http_pre_tran = c.getinfo(pycurl.PRETRANSFER_TIME)
    http_start_tran = c.getinfo(pycurl.STARTTRANSFER_TIME)
    http_total_time = c.getinfo(pycurl.TOTAL_TIME)
    http_size = c.getinfo(pycurl.SIZE_DOWNLOAD)
    http_result = {"time":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"http_code": http_code, "http_conn_time": http_conn_time,"http_total_time": http_total_time, "http_size": http_size}
    return http_result


def get_dmidecode():
    P = Popen(['dmidecode'],stdout=PIPE)
    data = P.stdout.read()
    lines = data.split('\n\n')
    dmidecode_line =  lines[2]
    line = [i.strip() for i in dmidecode_line.split('\n') if i]
    Manufacturer = line[2].split(': ')[-1]
    product = line[3].split(': ')[-1]
#    sn = line[5].split(': ')[-1]
    return Manufacturer,product


def disk_info():
    disk_info_list = []
    disk_info_dict = {}
    disk = psutil.disk_usage('/')
    # 硬盘总量
    disk_info_dict["total"] = disk.total
    # 硬盘使用量
    disk_info_dict["used"] = disk.used
    # 硬盘剩余量
    disk_info_dict["free"] = disk.free
    # 硬盘使用比
    disk_info_dict["percent"] = disk.percent
    disk_info_list.append(disk_info_dict)
    return disk_info_list

def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

#def get_http_status():
#    global _http_monitor_target
#    for http_url in (_http_monitor_target):
#        html = requests.head(http_url)    # 用head方法去请求资源头部
#        print html.status_code  # 状态码
#        print(http_url)


def ping_monitor(ping_target):
    ping_result_lst = ping.quiet_ping(ping_target, timeout=1, count=5, psize=64)
    ping_result={"ping_max_time":ping_result_lst[1],"ping_loss":ping_result_lst[0]}
    return ping_result
#def timer_post(ping_target,http_target,exec_times=1,interval=5):
#def timer_post(http_target,exec_times=1,interval=5):
def timer_post(http_target,interval=10):
#    for count in range(exec_times):
        i = datetime.datetime.now()
        hostname = socket.gethostname()
        disk_percent = str(psutil.disk_usage('/').percent) +'%'
        total_cpu_count=psutil.cpu_count()
        uptime_day=str(psutil.boot_time()/24/60/60/1000) + 'days'
        mem_total =str(psutil.virtual_memory().total/1024/1024)+'MB'
        cpu_percent = str(psutil.cpu_percent(interval=None, percpu=False)) + '%'
        #mem_used = psutil.Process(os.getpid()).memory_info().rss
        mem_used = str(psutil.virtual_memory().percent) +'%'
        myaddr = get_host_ip()
        ver=platform.dist()[0] + platform.dist()[1]
        #dmi=get_dmidecode()
        #ping_result_dict={}
        http_result_dict={}
        host_info={
                      "ip":myaddr,
                      "os":ver,
                      "time":i.strftime("%Y-%m-%d %H:%M:%S"),
                      "hostname": hostname,
                      "disk_usage": disk_percent,
                      "total_cpu_count":total_cpu_count,
                      "cpu_percent":cpu_percent,
                      "mem_total":mem_total,
                      "mem_used_prcent":mem_used,
        }
#        for pt in ping_target:
#            ping_result=ping_monitor(pt)
#            ping_result_dict.update({pt:ping_result})
        for url in http_target:
            http_result=http_monitor(url)
            http_result_dict.update({url:http_result})
        host_info.update({"http_result":http_result_dict})
#        host_info.update({"ping_result":ping_result_dict})
        json_data = json.dumps(host_info,encoding="utf8", ensure_ascii=True,sort_keys=True)
        print 'json_data:\t' + json_data
        log_file = 'monitor.' + i.strftime('%Y.%m.%d') + '.json'
        write_to_file(log_file, json_data)
        #count +=1
        #print 'count=' + str(count+1)
#        time.sleep(interval)
#        break
#    req = urllib2.Request('http://192.168.11.163:20888/hostinfo', json_data,{'Content-Type': 'application/json'})
#    f = urllib2.urlopen(req)
#    response = f.read()
#    print response
#    f.close()
        t = Timer(interval, timer_post, (http_target,interval,))
        t.start()


if __name__ == "__main__":
    _ping_monitor_target=['8.8.8.8','114.114.114.114']
    _http_monitor_target = ['https://www.163.com','https://www.qq.com']
    #timer_post(_ping_monitor_target,_http_monitor_target,exec_times=2,interval=3)
    timer_post(_http_monitor_target)
