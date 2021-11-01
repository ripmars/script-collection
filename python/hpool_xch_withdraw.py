#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File        : hpool_xch_withdraw.py
@Desc        : 当前仅支持手动输入Google Authenticator验证码，使用`oathtool`生成谷歌验证码，获取code完成自动提现.使用telegram bot发送消息通知.
@Time        : 2021/11/01 16:11:55
@Author      : Chaos
@Version     : 1.3
'''

# here put the import lib

import requests
import re
import time,datetime
import json
# from argparse import ArgumentParser as argm
import subprocess
import logging
logger = logging.getLogger('hpool withdraw helper')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('./hpool_xch_withdraw_helper.log')
fh.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)



header = {
    'cookie':'',
    'user-agent':
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
    'sec-ch-ua-platform': "macOS",
    'sec-fetch-site': 'same-origin',
    'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.hpool.in/center/assets',
    'accept-language': 'zh-CN,zh;q=0.9',
    'sec-ch-ua-mobile': '?0',
    'accept': 'application/json, text/plain, */*'
}

# def send_tg_msg(token,chat_id,data):
def send_tg_msg(text):
    '''
    通过telegram bot发送提现通知。
    amount:金额,
    data:时间,
    结果:成功与否
    '''
    # 需要替换该处`bot token`
    token=''
    chat_id=''
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    dataJson={
        "chat_id":'chat_id',
        "text": "XCH到账啦!",
    }
    now=datetime.datetime.now()
    dataJson['text']=text
    dataJson['chat_id']=chat_id
    try:
        r =requests.post(url, data=dataJson,timeout=5)
        return r.text
    except requests.exceptions.ConnectionError:
        msg='报错了，无法访问telegram.'
        logger.error(f"{msg}")
        
        exit(2)
    except Exception as e:
        logger.error(f"报错了，报错信息是:{e}")
        # print('报错了，报错信息是:',e)
        exit(3)
    


def get_total_assets(url):
    totalassets_url = url
    res = requests.get(url=totalassets_url, headers=header)
    # res=res.text
    # currency_list=res['data']['list'] ## failed
    currency_list = json.loads(res.text).get('data').get('list')
    # print(currency_list)
    for i in currency_list:
        if i['name'] == 'CHIA':
            total_xch = i['total_assets']
            total_xch = float(total_xch)
            break
    if total_xch < 0.01:
        msg = (f'提现失败.不够最低提现额度.当前xch资产金额为：{total_xch} xch')
        logger.error(f"{msg}")
        send_tg_msg(text=msg)
        exit(1)

    return total_xch


def get_token():
    t1=int(time.time() * 1000)
    # 此处有坑，需要先请求`/api/security/requestverify`,再获取session
    requests.get(url=f'https://www.hpool.in/api/security/requestverify?_t={t1}', headers=header)
    t2=int(time.time() * 1000)
    res = requests.get(url=f'https://www.hpool.in/api/security/requestsession?_t={t2}', headers=header)
    session = json.loads(res.text).get('data')
    return session


def get_google_auth_code(path):
    '''
    使用`oathtool`生成谷歌验证码,脚本需要有执行权限,
    脚本内容:`oathtool -b --totp 'key'`.
    非最佳方案，注意保护好`key`谨防泄密，造成财产损失.
    '''
    code = subprocess.getoutput(path)
    # return int(code)
    print(code)
    return code


def xch_withdraw(url, session, code, amount, address, **kwargs):
    '''
    session:请求session接口的返回,
    code:谷歌验证码,
    aomount:剩余全部xch,
    address:提现钱包地址
    
    提现到指定钱包地址payload：
    '{"session":"","code":"","type":"chia","address":"","amount":""}'
    '''
    type = 'chia'
    payload = {
        "session": f"{session}",
        "code": f"{code}",
        "type": "chia",
        "address": f"{address}",
        "amount": f"{amount}"
    }
    payload = json.dumps(payload)

    # print(payload)
    res = requests.post(url=url, headers=header, data=payload)
    result_code = json.loads(res.text).get('code')
    print(res.text)
    if result_code == 200:
        msg=f'提现成功,本次提现金额为:{amount}xch,请注意查收.'
        logger.info(f'{msg}')
        send_tg_msg(text=msg)
        return result_code
    else:
        msg='提现失败,未知错误.'
        logger.error(f"{msg}")
        send_tg_msg(text=msg)
        return None


if __name__ == "__main__":

    # parser = argm(prog='hpool_xch_withdraw',description="hpool xch withdraw helper")
    # parser.add_argument("-K", "--code", dest='code', type=int,help="Google Authenticator Code.")
    # parser.add_argument("-P","--percent", dest='withdraw_percent', default=1,help="Withdraw ratio.")
    # parser.add_argument("-M","--tg",help="Send telegram message.")
    # args = parser.parse_args()

    # code = args.code
    # withdraw_percent = args.withdraw_percent

    # if len(str(code)) == 6:
    #     remain_xch=get_total_assets('https://www.hpool.in/api/assets/totalassets')
    #     #sign_url=f'https://www.hpool.in/api/assets/totalassets'
    #     # print(sign_url)
    #     t = int(time.time() * 1000)
    #     session=get_token(f'https://www.hpool.in/api/security/requestsession?_t={t}')
    #     ## 防止被劫持，强制写死提现address.也可以通过接口获取
    #     xch_withdraw(session=session,code=code,amount=remain_xch,address='')
    # else:
    #     parser.print_help()

    remain_xch = get_total_assets(
        'https://www.hpool.in/api/assets/totalassets')
    # t = int(time.time() * 1000)
    session = get_token()
    code = get_google_auth_code('/home/chaos/lab/scripts/totp.sh')
    withdraw_url = 'https://www.hpool.in/api/assets/withdraw'
    ## 防止被劫持，强制写死提现address.也可以通过接口获取
    pay_address = ''
    xch_withdraw(url=withdraw_url,
                 session=session,
                 code=code,
                 amount=remain_xch,
                 address=pay_address)
