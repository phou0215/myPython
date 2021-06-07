import os
import sys
import re
import pandas as pd
import numpy as np
import threading
import subprocess

import multiprocessing
from multiprocessing import Process
from appiumMethods import Method
from datetime import date, time, datetime
from appium import webdriver
from time import sleep
from PyQt5.QtCore import QThread, pyqtSignal

# buffer_text = multiprocessing.Array()

def execute_test(DEFAULT_DELAY, DEFAULT_TIMES, dict_init, dict_act, idx):

    print(str(dict_init['uuid']+' device thread is started'))
    check_display(str(dict_init['uuid']))
    method = Method(DEFAULT_DELAY, DEFAULT_TIMES, dict_init, dict_act)
    method.start_test()

def check_display(uuid):

    cmd_checkDs = "adb -s "+uuid+" shell \"dumpsys power | grep mHolding\""
    cmd_power = "adb -s "+uuid+" shell input keyevent 26"
    cmd_unlock = "adb -s "+uuid+" shell input keyevent 82"
    cmd_swipe = "adb -s "+uuid+" shell input touch 380 880 830 880"

    try:
        pipe = subprocess.Popen(cmd_checkDs, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        res = pipe.communicate()
        res_data = str(res[0])

        ##########################################################-Check Display Status-##############################################################
        while True:
            sleep(1.8)
            if "mHoldingDisplaySuspendBlocker=true" in res_data:
                # self.setPrintText('Device '+uuid+' Power On')
                print('Device '+uuid+' Screen On')
                break
            else:
                #device power on
                pipe = subprocess.Popen(cmd_power, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                print('Try to Screen On '+uuid+' \' device')
                #device display check
                sleep(1.8)
                pipe = subprocess.Popen(cmd_checkDs, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                #retry get status value
                res = pipe.communicate()
                res_data = str(res[0])

        print('Device '+uuid+' Unlock')
        pipe = subprocess.Popen(cmd_unlock, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        sleep(1.8)
    except:
        print('/s Error: {}. {}, line: {} /e'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno))

class Client(QThread):

    print_flag = pyqtSignal()
    end_flag = pyqtSignal()
    buffer_text = []
    is_terminated = False

    def __init__(self, dict_init, dict_event, delay, times, parent=None):
        QThread.__init__(self, parent)
        self.device_count = 0
        self.fota_start = 0
        self.dict_init = dict_init
        self.dict_event = dict_event
        self.DEFAULT_DELAY = delay
        self.DEFAULT_TIMES = times

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
                sleep(0.2)
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

    def removeString(self, text):

        self.tempText = self.text.replace("[","")
        self.tempText = self.tempText.replace("]","")
        self.tempText = self.tempText.replace("-","")
        self.tempText = self.tempText.replace("/","")
        self.tempText = self.tempText.replace("=","")
        self.tempText = self.tempText.replace("<","")
        self.tempText = self.tempText.replace(">","")
        self.tempText = self.tempText.replace("#","")
        self.tempText = self.tempText.replace("*","")
        return self.tempText


    # def setPrintText(self, text):
    #
    #     self.strToday = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    #     self.text = self.find_between(text, "/s", "/e")
    #     self.print_text = self.strToday+":\n"+self.text+"\n"
    #     self.buffer_text.append(self.print_text)
    #
    # def setEnd(self):
    #
    #     self.end_flag.emit()
    #
    # def getPrintText(self):
    #     while True:
    #         if not self.is_terminated:
    #             sleep(0.2)
    #             self.print_flag.emit()
    #         else:
    #             break
    def stop(self):
        self.setPrintText("/s All Client Process is finished../e")
        sleep(1.8)
        for proc in self.procs:
            proc.terminate()
        self.is_terminated = True
        self.terminate()

    def run(self):

        try:
            ##########################################################-ADB CMD COLLECTION-##############################################################
            self.thread_print = threading.Thread(target=self.getPrintText, args=())
            self.thread_print.daemon=True
            self.thread_print.start()
            self.setPrintText('/s Appium Client is Started.../e')
            multiprocessing.freeze_support()
            self.procs = []
            for idx, uuid in enumerate(self.dict_init):
                self.data_init = self.dict_init[uuid]
                self.data_action = self.dict_event[uuid]
                self.proc = Process(target=execute_test, args=(self.DEFAULT_DELAY, self.DEFAULT_TIMES, self.data_init, self.data_action, idx,), daemon=True)
                self.procs.append(self.proc)
                self.proc.start()

            for item in self.procs:
                item.join()

            self.setEnd()

        except:
            self.setPrintText('/s Error: {}. {}, line: {} /e'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno))
            sleep(1)
            self.setEnd()


if __name__ == "__main__":
    pass
