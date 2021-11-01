#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File        : hpool_xch_withdraw.py
@Desc        : 当前仅支持手动输入Google Authenticator验证码，计划后续将从bitwarden获取code完成自动提现.
@Time        : 2021/11/01 16:11:55
@Author      : Chaos
@Version     : 1.0
'''

# here put the import lib
import requests
import re
import time
import json
from argparse import ArgumentParser as argm

header = {
            'cookie': '',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
            'sec-ch-ua-platform': "macOS",
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://www.hpool.in/center/assets',
            'accept-language': 'zh-CN,zh;q=0.9',
            'sec-ch-ua-mobile': '?0',
            'accept':'application/json, text/plain, */*'
        }

def get_total_assets(url):
    # totalassets_url='https://www.hpool.in/api/assets/totalassets'
    totalassets_url=url
    res = requests.get(url=totalassets_url,headers=header)
    # res=res.text
    # currency_list=res['data']['list'] ## failed
    currency_list=json.loads(res.text).get('data').get('list')
    # print(currency_list)
    for i in currency_list:
        if i['name'] == 'CHIA':
            total_xch=i['total_assets']
            break
    if total_xch < 0.01:
        print('不够最低提现额度。当前xch资产金额为：'+ total_xch)
    else:
        exit(1)

    return total_xch

def get_token(url):
    res = requests.get(url=url,headers=header)
    session=json.loads(res.text).get('data')
    return session

def get_google_auth_code():
    pass

def tg_bot():
    pass

def xch_withdraw(session,code,amount,address,**kwargs):
    '''
    session:请求session接口的返回,
    code:谷歌验证码,
    aomount:剩余全部xch,
    address:提现钱包地址
    
    提现到指定钱包地址payload：
    '{"session":"","code":"","type":"chia","address":"","amount":""}'
    '''
    type='chia'
    url='https://www.hpool.in/api/assets/withdraw'

    #payload='{"session":"{session}","code":"248807","type":"chia","address":"{address}","amount":"{amount}"}'
    payload={"session":f"{session}","code":f"{code}","type":"chia","address":f"{address}","amount":f"{amount}"}
    payload=json.dumps(payload)

    print(payload)
    res = requests.post(url=url,headers=header,data=payload)
    result_code =json.loads(res.text).get('code')
    if result_code == 200:
        print('提现成功')
    else:
        print('出现未知错误')
    
    

if __name__=="__main__":
 
    parser = argm(prog='hpool_xch_withdraw',description="hpool xch withdraw helper")
    parser.add_argument("-K", "--code", dest='code', type=int,help="Google Authenticator Code.")
    parser.add_argument("-P","--percent", dest='withdraw_percent', default=1,help="Withdraw ratio.")
    parser.add_argument("-M","--tg",help="Send telegram message.")
    args = parser.parse_args()

    code = args.code
    withdraw_percent = args.withdraw_percent
    if len(str(code)) == 6:
        remain_xch=get_total_assets('https://www.hpool.in/api/assets/totalassets')
        t = int(time.time() * 1000)
        session=get_token(f'https://www.hpool.in/api/security/requestsession?_t={t}')
        ## 防止被劫持，强制写死提现address.也可以通过接口获取
        xch_withdraw(session=session,code=code,amount=remain_xch,address='')
    else:
        parser.print_help()
