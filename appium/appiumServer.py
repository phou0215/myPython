from time import sleep
from datetime import datetime
import os
import json
import urllib3
import threading
from http.client import responses
import pandas as pd
from PyQt5.QtCore import QThread, pyqtSignal
import subprocess
import sys
import time

class Server(QThread):

    print_flag = pyqtSignal()
    complete_flag = pyqtSignal()
    end_flag = pyqtSignal()
    buffer_text = []

    def __init__(self, list_server, parent=None):
        QThread.__init__(self, parent)
        self.is_terminated = False
        self.list_process = []
        self.list_servers = list_server
        self.DEFAULT_HOST = '127.0.0.1'
        self.DEFAULT_PORT = '4723'
        self.STARTUP_TIMEOUT = 60
    # 프로세스 종료는 self._process.terminate() list_process =[]

    def setPrintText(self, text):

        self.strToday = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        self.text = self.find_between(text, "/s", "/e")
        self.print_text = self.strToday+":\n"+self.text+"\n"
        self.buffer_text.append(self.print_text)

    def setEnd(self):

        self.end_flag.emit()

    def getPrintText(self):
        while True:
            if not self.is_terminated:
                sleep(0.5)
                self.print_flag.emit()
            else:
                break

    def find_between(self, s, first, last):
        try:
            self.returnData = ""
            self.start = s.index(first)+len(first)
            self.end = s.index(last, self.start)
            self.returnData = s[self.start:self.end]
            return self.returnData
        except ValueError:
            return self.returnData

    def find_between_r(self, s, first, last ):
        try:
            self.returnData = ""
            self.start = s.rindex(first)+len(first)
            self.end = s.rindex(last, self.start)
            self.returnData = s[self.start:self.end]
            return self.returnData
        except ValueError:
            return self.returnData

    def is_listening(self, address, port):
        self.returns = self.check_status(address, port, 1.0)
        return self.returns

    def check_status(self, address, port, timeout):
        # http://127.0.0.1:4723/wd/hub/status
        try:
            self.url = 'http://'+address+':'+port+'/wd/hub/status'
            self.req = urllib3.PoolManager(timeout=timeout)
            self.res = self.req.request('GET', self.url)
            self.status_code = self.res.status
            self.status_des = responses[self.status_code]
            if self.status_code is 200 and self.status_des is 'OK':
                return [True, self.status_code, self.status_des]
            else:
                return [False, self.status_code, self.status_des]
        except:
            return [False, 500, 'terminated']

    def run(self):
        try:
            self.thread_print = threading.Thread(target=self.getPrintText, args=())
            self.thread_print.daemon = True
            self.thread_print.start()
            self.setPrintText('/s Appium Server is Started.../e')
            if len(self.list_servers) is 0:
                self.setPrintText('/s No Config server info. appium have been started DEFAULT(127.0.0.1 / 4723) /e')
                self.setEnd()
            else:
                self.setPrintText('/s Total '+str(len(self.list_servers))+' Appium servers are starting now.../e')
                for item in self.list_servers:
                    self.cmdText = "start /B start cmd.exe @cmd /k appium -a "+item[0]+" -p "+item[1]+" -U "+item[3]+" -bp "+item[2]+" --relaxed-security --session-override"
                    self.setPrintText('/s '+self.cmdText+' /e')
                    os.system(self.cmdText)
            #wait appium remote server's starting maxium 15 second
            sleep(19)
            for item in self.list_servers:
                self.list_status = self.is_listening(item[0], item[1])
                if (self.list_status[0]) and (self.list_status[1] is 200) and (self.list_status[2] is 'OK'):
                    self.setPrintText('/s HOST: '+item[0]+' PORT: '+item[1]+'==> Started OK/e')
                    self.complete_flag.emit()
                else:
                    self.setPrintText('/s HOST: '+item[0]+' PORT: '+item[1]+'==> Started NOK (RES_CODE: '+str(self.list_status[1])+', RES_DES: '+self.list_status[2]+') /e')
                    self.setEnd()
        except:
            self.setPrintText('/s HOST: '+item[0]+' PORT: '+item[1]+'==> Started NOK (RES_CODE: 500, RES_DES: Unexpected Error) /e')
            self.setEnd()

    def stop(self):
        self.setPrintText("/s All Appium Server is shutting down../e")
        self.process = subprocess.Popen('taskkill /im node.exe /F', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr= subprocess.PIPE)
        self.setPrintText('/s All Appium Server is terminated../e')
        sleep(1.8)
        self.is_terminated = True
        self.terminate()

if __name__ == "__main__":
    nowTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("<Start Time> : ",nowTime)
    server = Server([('127.0.0.1','4723')])
    server.run()
    sleep(10)
    for idx, item in enumerate(server.list_process):
        list_status = server.is_listening(item, server.list_servers[idx][0], server.list_servers[idx][1])
        assert(list_status[0])
        assert(list_status[1] is 200)
        assert(list_status[2] is 'OK')
    sleep(10)
    server.stop()
    sleep(60)
    for idx, item in enumerate(server.list_process):
        list_status = server.is_listening(item, server.list_servers[idx][0], server.list_servers[idx][1])
        assert(not list_status[0])
        assert(list_status[1] is 500)
        assert(list_status[2] is 'terminated')
