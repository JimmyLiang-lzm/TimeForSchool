# -*-coding:utf-8 -*-
#__Author__:"JimmyLiang"
#__Date__: 2020/4/7

import sys
from threading import Thread
from PyQt5.QtWidgets import QApplication,QMessageBox
from PyQt5 import QtWidgets
import sysUI as cui
import sender
import requests
import time
from bs4 import BeautifulSoup as bs
import re

Objective = cui.Ui_MainWindow

webAddress = ""
quitc = False
times = 2
phoneNum = ''
keyword = ""
storageList = []        #用于储存旧的列表

class MainWindow(QtWidgets.QMainWindow,Objective):
    def __init__(self,parent = None):
        super(MainWindow,self).__init__(parent)
        self.setupUi(self)
        self.btn_phoneTest.clicked.connect(self.phoneTest)
        self.btn_start.clicked.connect(self.programStart)
        self.btn_webConfirm.clicked.connect(self.webConfirm)
        self.btn_setphoneNum.clicked.connect(self.setPhone)
        self.btn_kwedit.clicked.connect(self.setKeyword)
        self.btn_timeSet.clicked.connect(self.timeSet)
        self.btn_stop.clicked.connect(self.stopProgram)

    def stopProgram(self):      #停止监视进程运行
        global quitc
        quitc = True

    def timeSet(self):      #设置隔多少秒访问一次网站
        global times
        td = self.lineEdit_time.text()
        if td.isdigit():
            times = int(self.lineEdit_time.text())
            self.view_console.append("信息：成功设置延时"+td)
        else:
            QMessageBox.information(self,"警告","请输入正确的时间")

    def setKeyword(self):       #设置信息关键字
        global keyword
        keyword = self.lineEdit_Keyword.text()
        self.view_console.append("信息：成功设置关键词" + keyword)

    def webConfirm(self):       #确定网站地址信息
        global webAddress
        webAddress = self.lineEdit_address.text()
        self.view_console.append("信息：成功设置网站" + webAddress)

    def setPhone(self):     #设置手机号码
        global phoneNum
        phoneNum = self.lineEdit_phoneNum.text()
        self.view_console.append("信息：成功设置手机号")

    def phoneTest(self):        #进行手机短信号码的测试
        timeText = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        text1 = '如果你收到这条短信则证明你的手机可以正常接收到通知的消息！\n来自开学日期提醒程序。\n日期：'
        try:
            sender.SendMessage(self.lineEdit_phoneNum.text(),text1+timeText)
            QMessageBox.information(self,"发送成功",'已向你的手机发送消息。',QMessageBox.Ok)
        except:
            QMessageBox.Warning(self,'发送错误','发送失败，请检查你输入的号码。',QMessageBox.Ok)

    def getHTMLText(self,url):  # 获取网页代码与信息
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64)'  # 反扒标识
                          'AppleWebKit/537.36 (KHTML, like Gecko)'
                          'Chrome/61.0.3163.79 Safari/537.36'}
        try:
            self.r = requests.get(url, headers=header, timeout=30)
            self.r.raise_for_status()
            self.r.encoding = self.r.apparent_encoding
            #print("Html is Ok")
            return self.r.text
        except:
            return ""

    def beLists(self,html):  # 将获取到的页面信息转换成三维的数据列表
        try:
            self.Lists = []
            soup = bs(html, "html.parser")
            temp = soup.body.find_all('div', attrs={"class": "conter"})
            #print(type(temp))
            # print(str(temp))    这里的信息筛选可以自行更改
            temp = re.findall(r'<li id="line\S*">([\s\S]*?)</li>', str(temp))
            # print(temp)
            for i in range(len(temp)):
                mess = re.findall(r'title="(\S*?)"', temp[i])[0]
                date = re.findall(r'class="date">\[(\S*?)\]</span>', temp[i])[0]
                path = re.findall(r'href="\.\.(\S*?)"', temp[i])[0]
                self.Lists.append([mess, date, "http://www.njit.edu.cn" + path])
            return self.Lists
        except:
            #print("解析数据出现问题")
            return ""

    def updateMessage(self,inLists):  # 检查信息是否出现变化，如果变化则返回最新信息
        global storageList
        # print(inLists)
        # print((storageList))
        if inLists == storageList:
            return ""
        else:
            self.newList = []
            conf = False
            for i in range(len(inLists)):
                for j in range(len(storageList)):
                    if inLists[i] == storageList[j]:
                        conf = True
                    else:
                        continue
                if conf == False:
                    self.newList.append(inLists[i])
                else:
                    conf = False
            storageList = inLists
            if len(self.newList) >= 0:
                return self.newList
            else:
                return ""

    def robotMain(self,url):  # 程序主界面
        self.html = self.getHTMLText(url)
        if self.html == "":
            #print("未爬取到任何信息")
            return ""
        else:
            self.feedback = self.updateMessage(self.beLists(self.html))
            if self.feedback != "":
                #print("通知数据已更新。")
                return self.feedback
            else:
                #print("暂无更新。")
                return ""

    def Started(self):      #开始进程
        global quitc
        while True:
            time.sleep(times)
            if webAddress == "":
                QMessageBox.Warning(self,'警告','请输入完整的网站地址',QMessageBox.Ok)
                break
            elif times == 0:
                QMessageBox.Warning(self, '警告', '请输入间隔时间',QMessageBox.Ok)
                break
            elif phoneNum == "":
                QMessageBox.Warning(self, '警告', '请输入正确的手机号码',QMessageBox.Ok)
                break
            elif quitc == True:
                break
            else:
                self.lists = self.robotMain(webAddress)
                if self.lists == "":
                    self.view_console.append("信息：暂无更新")
                    continue
                else:
                    text1 = '\n抓取到新消息：'
                    text2 = ''
                    timed = '\n发送日期：' + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                    if keyword == "":
                        for i in range(len(self.lists)):
                            self.view_console.append(str(self.lists[i]))
                            temp = str()
                            text1 = text1 + '\n' + self.lists[i][0] +":"+self.lists[i][1]
                            text2 = text2 +"\n"+self.lists[i][2]
                        try:
                            print(text1+timed)
                            sender.SendMessage(phoneNum,text1 + timed)
                            sender.SendMessage(phoneNum,text2)
                            self.view_console.append("已向（"+phoneNum+"）发送信息")
                        except:
                            self.view_console.append("信息：发送失败")
                    else:
                        for i in range(len(self.lists)):
                            t = re.findall(keyword,str(self.lists[i]))
                            if t:
                                text1 = text1 + "\n" + self.lists[i][0]+self.lists[i][1]
                                text2 = text2+"\n"+self.lists[i][2]
                            else:
                                continue
                        try:
                            print(text1 + timed)
                            sender.SendMessage(phoneNum,text1 + timed)
                            sender.SendMessage(phoneNum,text2)
                            self.view_console.append("已向（" + phoneNum + "）发送关键词信息")
                        except:
                            self.view_console.append("信息：发送失败")
        self.view_console.append("信息：进程关闭")
        quitc = False


    def programStart(self):     #多线程执行监视程序
        try:
            self.view_console.append("信息：正在启动进程")
            self.t1 = Thread(target=self.Started)
            self.t1.setDaemon(True)
            self.t1.start()
            self.view_console.append("信息：监控进程已启动")
        except:
            self.view_console.append("信息：进程启动失败")






if __name__ == "__main__":      #主函数
    app = QApplication(sys.argv)
    MainWindow = MainWindow()
    MainWindow.show()
    sys.exit(app.exec_())