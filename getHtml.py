# -*-coding:utf-8 -*-
#__Author__:"JimmyLiang"
#__Date__: 2020/4/7

import re
import requests
from bs4 import BeautifulSoup as bs

storageList = []        #用于储存旧的列表

def getHTMLText(url):       #获取网页代码与信息
    header = {
         'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64)'     #反扒标识
                      'AppleWebKit/537.36 (KHTML, like Gecko)'
                      'Chrome/61.0.3163.79 Safari/537.36'}
    try:
        r = requests.get(url,headers=header,timeout=30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        print("Html is Ok")
        return r.text
    except:
        return ""

def beLists(html):      #将获取到的页面信息转换成三维的数据列表
    try:
        Lists = []
        soup = bs(html,"html.parser")
        temp = soup.body.find_all('div',attrs={"class":"conter"})
        #print(type(temp))
        #print(str(temp))
        temp = re.findall(r'<li id="line\S*">([\s\S]*?)</li>',str(temp))
        #print(temp)
        for i in range(len(temp)):
            mess = re.findall(r'title="(\S*?)"',temp[i])[0]
            date = re.findall(r'class="date">\[(\S*?)\]</span>',temp[i])[0]
            path = re.findall(r'href="\.\.(\S*?)"',temp[i])[0]
            Lists.append([mess,date,"http://www.njit.edu.cn"+path])
        return Lists
    except:
       print("解析数据出现问题")
       return ""

def updateMessage(inLists):     #检查信息是否出现变化，如果变化则返回最新信息
    global storageList
    #print(inLists)
    #print((storageList))
    if inLists == storageList:
        return ""
    else:
        newList = []
        conf = False
        for i in range(len(inLists)):
            for j in range(len(storageList)):
                if inLists[i] == storageList[j]:
                    conf = True
                else:
                    continue
            if conf == False:
                newList.append(inLists[i])
            else:
                conf = False
        storageList = inLists
        if len(newList) >= 0:
            return newList
        else:
            return ""

def robotMain(url):        #程序主界面
    html = getHTMLText(url)
    if html == "":
        print("未爬取到任何信息")
        return ""
    else:
        feedback = updateMessage(beLists(html))
        if feedback != "":
            print("通知数据已更新。")
            return feedback
        else:
            print("暂无更新。")
            return ""