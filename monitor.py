#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   monitor.py
@Time    :   2020/01/14 22:37:39
@Author  :   Chaos
@Version :   1.0
@Desc    :   None
'''

# here put the import lib

# import requests post
from requests import post,exceptions
from psutil import disk_usage
import time,datetime
from argparse import ArgumentParser as argm
from os import path,popen,statvfs,listdir,remove
from socket import gethostname
import re
import fnmatch

# import socket
def sendWX(key,title,json):
    """发送方糖告警"""
    url = 'http://sc.ftqq.com/{}.send'.format(key)
    dataJson={
  "text": "Disk Monitor Alarm by Script",
  "desp": "Disk Monitor Alarm by Script"
}
    dataJson['desp']=json
    dataJson['text']=title
    # r = requests.post(url, data=dataJson)
    try:
        r = post(url, data=dataJson,timeout=5)
        return r.text
    except exceptions.ConnectionError:
        print('报错了，无法访问方糖.')
    except Exception as e:
        print('报错了，报错信息是:',e)
    # return r.text

def testFS(testFile,item):
    """测试文件系统是否为只读"""
    try:
        with open('{}'.format(testFile), 'w') as fp:
            fp.write(item)
        return True
    except (OSError,IOError) as err:
        if err.errno == 30:
            return False
        else:
            return True
class zibao():
    """
    get/post
    """
    def __init__(self,lp):
        self.lp = lp
    def delta(self):
        # oldest_date = popen('ls /logs/' + gethostname() + '*.tar.gz |  grep -oE "20[0-9]+-[0-9]+-[0-9]+" | sort -n | head -1').read().strip() #.readlines()
        oldest_date = popen('ls '+ self.lp + '/*bklog*.tar.gz |  grep -oE "20[0-9]+-[0-9]+-[0-9]+" | sort -n | head -1').read().strip() #.readlines()

        # oldest_date = oldest_date[0]
        print(oldest_date)
        last_three_month = (datetime.datetime.now() + datetime.timedelta(days=-180)).strftime('%Y-%m-%d')
        datestart = datetime.datetime.strptime(oldest_date,'%Y-%m-%d')
        dateend = datetime.datetime.strptime(last_three_month,'%Y-%m-%d')
        date_list = []
        while datestart <= dateend:
            date_list.append(datestart.strftime('%Y-%m-%d'))
            datestart += datetime.timedelta(days=1)
            # date_list.append(dateend.strftime('%Y-%m-%d'))
            # dateend += datetime.timedelta(days=-1)
        # file_reg = gethostname() + "*.tar.gz"
        # filenames=showDir('/logs')
        # filenames = fnmatch.filter(filenames, file_reg)
        # print(filenames)
        return date_list

    def showDir(self):
        ls=listdir(self.lp) #.sort(key=lambda x:str(x[:-7]))
        return ls
    def rmlogtar(self,file):
        pass

if __name__ == "__main__":
    # import argparse
    parser = argm(prog='serverjo',description="Host Monitor")
    parser.add_argument("-K", "--auth-key", dest='authKey', help="Server jo auth key.")
    parser.add_argument("-l", dest='logpath', default='/logs',help="log dir path.")
    # parse arguments
    args = parser.parse_args()
    authKey = args.authKey
    logpath = args.logpath
    print(logpath)
    st = statvfs('/')
    freeDisk= st.f_bavail * st.f_frsize/1024
    freeDisk_G=freeDisk/1024/1024
    df_percent=disk_usage('/').percent

    IdFilePath='/home/tomcat/war/var/web-online/webapps/ROOT/WEB-INF/classes/common.properties'
    hisId = None
    file_reg = "*bklog*.tar.gz"
    docleanlog = zibao(logpath)
    filenames=docleanlog.showDir()
    print(filenames)

    filenames = fnmatch.filter(filenames, file_reg)
    # for f in showDir('/tmp'):
    #     print(re.match(ft, f).group())
    to_be_deleted = []  # 保存筛选出来dog的列表
    frange = docleanlog.delta()
    if len(frange) == 0:
        print('没啥好删的')
    else:
        for data in filenames:  # 遍历列表
            for t in frange:
                # if  re.match('.*2019-10-01.*', data) != None:
                # print(t,data)
                if  re.search(t, data) != None:
                    to_be_deleted.append(data)
    # for k in to_be_deleted:
    #     print(k)
        # print(f.endswith('.tar.gz'))
    if path.exists(IdFilePath) is True:
        hisId = popen('grep hisId '+ IdFilePath + ' | cut -d= -f2').readlines()
        hisId='hisId为:' + hisId[0]


    if hisId is None:
        hisId = '未获取到hisId信息'

    hname = '主机名为:' + gethostname()
    Rtime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    testfile = '/tmp/testfilesystem'

    if authKey is not None:
        try:
            if  df_percent >= float(85) and df_percent < float(90):
                title = '[warnning]前置机空间告警,{}'.format(hisId)
                alertMessage = '当前时间为:{},{},{}前置机空间使用率告警.目前使用率为{},剩余空间为{}G,请及时处理。'.format(Rtime,hisId,hname,df_percent,int(freeDisk_G))
                print(alertMessage)
                sendWX(authKey,title,alertMessage)
            elif df_percent >= float(90):
                title = '[critical]前置机空间告警,{}'.format(hisId)
                alertMessage = '当前时间为:{},{},{}前置机空间使用率告警.目前使用率为{},剩余空间为{}G,请及时处理。'.format(Rtime,hisId,hname,df_percent,int(freeDisk_G))
                print(alertMessage)
                sendWX(authKey,title,alertMessage)
            else:
                print('没毛病.当前时间为:{},目前空间使用率为{},剩余空间为{}G'.format(Rtime,df_percent,int(freeDisk_G)))

            isWriteable=testFS(testfile,Rtime)
            if isWriteable == False:
                fserr_title = '前置机文件系统只读告警,{}'.format(hisId)
                fserr_message = '当前时间为:{},{},{}前置机文件系统只读,请及时处理。'.format(Rtime,hisId,hname)
                sendWX(authKey,fserr_title,fserr_message)
        except Exception as e:
                print('报错了，报错信息是:',e)
    else:
            print('The auth key is empty.Please Check the input').com','https://www.qq.com']
    timer_post(_http_monitor_target)
