# -*-coding:utf-8 -*-
#__Author__:"JimmyLiang"
#__Date__: 2020/4/7

from twilio.rest import Client
import re

def SendMessage(phonenum,messages):     #此为短信发送设置，请登录twilio获取XXXX与0000部分
    res = re.match(r'^1[35789]\d{9}$',phonenum)
    if res:
        account_sid = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
        auth_token = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
        client = Client(account_sid, auth_token)
        message = client.messages.create(from_='+00000000',body=messages,to='+86' + phonenum)
    else:
        pass