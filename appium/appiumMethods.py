import os
import sys
import re
import pandas as pd
import numpy as np
import threading
import signal
import subprocess
import cv2
import re
from datetime import date, time, datetime
from time import sleep
from os.path import expanduser
from PyQt5.QtCore import QThread, pyqtSignal
from appiumReport import Report
from appium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from appium.webdriver.common.mobileby import MobileBy
from appium.webdriver.common.touch_action import TouchAction


# adb", "-s", "YOURDEVICEUUID", "shell", "input", "text", "YOURTEXTASINPUT"
#self.driver.remove_app('com.example.AppName');
#self.driver.install_check('/Users/johndoe/path/to/app.apk')


#Time Check
# import time
# start_time = time.time()
# main()
# print("--- %s seconds ---" % (time.time() - start_time))
class Method(QThread):

    error_flag = pyqtSignal()
    end_flag = pyqtSignal()
    def __init__(self, DEFAULT_DELAY, DEFAULT_TIMES, dict_init, dict_act, parent=None):

        QThread.__init__(self, parent)
        self.home  = expanduser("~")
        self.error_text = ""
        self.drive = None
        self.unlock_break = False
        self.window_height = 0
        self.window_width = 0
        self.cv2_base_line = 0.8
        self.cv2_base_line_per = 90.0
        self.cv2_img_xSize = 224
        self.cv2_img_ySize = 224
        self.desired_caps = {}
        self.dict_result = {}
        self.dict_init = dict_init
        self.dict_act = dict_act
        self.DEFAULT_DELAY = DEFAULT_DELAY
        self.DEFAULT_TIMES = DEFAULT_TIMES
        self.screen_path = ""
        self.record_path = ""
        self.list_result = []
        self.list_eventDesc = []
        self.list_assertDesc = []
        self.list_subprocess = []
        self.list_recordFiles = []
        self.list_elapsed = []
        self.log_output = ""
        self.output_path = ""
        self.screen_path = ""
        self.record_path = ""

        # Excel Config File __init__
        # 'record_stop','pull_files'
        self.list_command = ['click','scroll','swipe','sendKey','wait_ele','back','home', 'wait_app','uninstall_app','install_app',\
        'dropall_app','screenShot','record_start', 'airplane_on', 'airplane_off','act_none', 'launch_app', 'stop_app', 'execute_Cmd']
        self.list_command2 = ['assert_none','logical','exists','text_equal','text_notEqual','attribute_equal','attribute_notEqual','execute_adb', 'image_compare', 'image_in']

        self.dict_method = {'click':self.click_obj, 'scroll':self.scroll_obj, 'sendKey':self.sendKey_obj, \
        'wait_ele':self.waitEle_obj, 'back':self.back_obj, 'home':self.home_obj, 'wait_app':self.waitApp_obj, 'install_app':self.installApp_obj, \
        'uninstall_app':self.uninstallApp_obj,'dropall_app':self.dropAllApp_obj,'back':self.back_obj,'home':self.home_obj,'screenShot':self.screenShot_obj,\
        'record_start':self.screenRecord_start_obj, 'airplane_on':self.airplane_on_obj, 'airplane_off':self.airplane_off_obj, 'act_none':self.act_none_obj,\
        'launch_app':self.launchApp_obj, 'stop_app':self.stopApp_obj, 'execute_Cmd':self.executeCmd_obj}
        # 'record_stop':self.screenRecord_end_obj, 'pull_files':self.pullFiles_obj

        self.dict_method2 = {'assert_none':self.assert_none,'logical':self.assert_logical,'exists':self.assert_exists, 'text_equal':self.assert_text_equal,\
        'text_notEqual':self.assert_text_notEqual,'attribute_equal':self.assert_attribute_equal,'attribute_notEqual':self.assert_attribute_notEqual,\
        'execute_adb':self.assert_execute_adb, "image_compare":self.assert_image_compare, "image_in":self.assert_image_in}


        #Generate desired_caps
        if self.dict_init['directStart'] == 'YES':
            self.desired_caps['appPackage'] = self.dict_init['appPackage']
            self.desired_caps['appActivity'] = self.dict_init['appActivity']
        else:
            self.desired_caps['appPackage'] = 'com.android.settings'
            self.desired_caps['appActivity'] = 'com.android.settings.Settings'

        if self.dict_init['app'] != 'None':
            self.desired_caps['app'] = self.dict_init['app']

        self.desired_caps['platformName'] = self.dict_init['platformName']
        self.desired_caps['systemPort'] = self.dict_init['port']
        self.desired_caps['platformVersion'] = self.dict_init['platformVersion']
        # self.desired_caps['deviceName'] = self.dict_init['deviceName']
        self.desired_caps['deviceName'] = self.dict_init['uuid']
        self.desired_caps['uuid'] = self.dict_init['uuid']
        self.desired_caps['newCommandTimeout'] = 12000
        self.desired_caps['automationName'] = "Appium"
        # self.desired_caps['automationName'] = "UiAutomator2"
        self.desired_caps['unicodeKeyboard'] = "true"
        self.desired_caps['resetKeyboard'] = "true"
        self.desired_caps['autoGrantPermissions'] = "true"
        # self.desired_caps['fullReset'] = "true"
        # print(str(self.desired_caps))
        # print("http://"+self.dict_init['address']+":"+self.dict_init['port']+"/wd/hub")
        self.driver = webdriver.Remote("http://"+self.dict_init['address']+":"+self.dict_init['port']+"/wd/hub", self.desired_caps)
        # self.wait = WebDriverWait(self.driver, 20)
        self.t_action = TouchAction(self.driver)
        self.driver.implicitly_wait(0)

    def log_write(self):
        with open(self.output_path + self.dict_init['uuid']+"_log.txt", "w") as fw:
            fw.write(self.log_output)

    # def keep_unlock(self):
    #     while True:
    #         if self.unlock_break:
    #             break
    #         sleep(60)
    #         self.driver.unlock()

    def tearDown(self):
        self.driver.quit()
        self.drive = None
        self.cmd = None
        self.dict_act = {}
        self.dict_init = {}

    def logPrint(self, text):

        self.log_time = datetime.now()
        self.log_time_text = self.log_time.strftime('%Y-%m-%d %H:%M:%S')
        print(self.log_time_text , text)
        if isinstance(text, list) or isinstance(text, tuple):
            self.log_temp = ""
            for item in text:
                if isinstance(item, list) or isinstance(item, tuple):
                    self.log_temp_child = ""
                    for item2 in item:
                        self.log_temp_child = self.log_temp_child+str(item2)+" "
                    self.log_temp = self.log_temp+self.log_temp_child+" "

                elif isinstance(item, dict):
                    self.log_temp_child = ""
                    self.log_keys = list(item.keys())
                    self.log_values = list(item.values())
                    for idx,item2 in enumerate(self.list_log_keys):
                        self.log_temp_child = self.log_temp+str(item2)+" "+str(self.list_log_values[idx])+" "
                    self.log_temp = self.log_temp+self.log_temp_child+" "
                else:
                    self.log_temp = self.log_temp+str(item)+" "
            self.log_output = self.log_time_text+" : "+self.log_output+self.log_temp+"\r\n"
        elif isinstance(text, dict):
            self.log_temp = ""
            self.list_log_keys = list(text.keys())
            self.list_log_values = list(text.values())
            for idx,item in enumerate(self.list_log_keys):
                self.log_temp = self.log_temp+str(item)+" "+str(self.list_log_values[idx])+" "
            self.log_output = self.log_time_text+" : "+self.log_output+self.log_temp+"\r\n"
        else:
            self.log_output = self.log_time_text+" : "+self.log_output+str(text)+"\r\n"

    def launch_package(self):

        self.driver.execute_script('mobile:shell', {'command':"monkey -p "+self.dict_init['appPackage']+" -c android.intent.category.LAUNCHER 1"})
        sleep(2)
        self.res = self.driver.execute_script('mobile:shell', {'command':'dumpsys activity | grep top-activity'})
        if self.dict_init['appPackage'] in self.res:
            self.log_text = 'Device '+self.dict_init['uuid']+' launched '+self.dict_init['appPackage']+' app'
            self.logPrint(self.log_text)
        else:
            self.log_text = 'Failed device '+self.dict_init['uuid']+' launch '+self.dict_init['appPackage']+' app'
            self.logPrint(self.log_text)
            # self.tearDown()

    def start_test(self):
        try:

            self.returnData = {}
            self.window_size = self.driver.get_window_size()
            self.window_height = self.window_size['height']
            self.window_width = self.window_size['width']
            # self.keep_display = threading.Thread(target=self.keep_unlock, args=())
            # self.keep_display.start()

            # check launched app
            if self.dict_init['directStart'] == 'NO':
                self.launch_package()
            # testing start

            for i in range(self.DEFAULT_TIMES):
                self.total_startTime = datetime.now()
                self.df_result = None
                self.list_result = []
                self.list_eventDesc = []
                self.list_assertDesc = []
                self.list_elapsed = []
                self.nowTime = datetime.today().strftime("%Y-%m-%dT%Hh%Mm%Ss")

                # makes report directory
                os.makedirs(self.home+"\\Desktop\\APPIUM\\report\\"+self.nowTime+"("+self.dict_init['uuid']+")\\")
                #makes screenshot directory
                os.makedirs(self.home+"\\Desktop\\APPIUM\\screenShot\\"+self.nowTime+"("+self.dict_init['uuid']+")\\")
                #makes screenshot directory
                os.makedirs(self.home+"\\Desktop\\APPIUM\\record\\"+self.nowTime+"("+self.dict_init['uuid']+")\\")
                self.output_path = self.home+"\\Desktop\\APPIUM\\report\\"+self.nowTime+"("+self.dict_init['uuid']+")\\"
                self.screen_path = self.home+"\\Desktop\\APPIUM\\screenShot\\"+self.nowTime+"("+self.dict_init['uuid']+")\\"
                self.record_path = self.home+"\\Desktop\\APPIUM\\record\\"+self.nowTime+"("+self.dict_init['uuid']+")\\"


                for idx, key in enumerate(self.dict_act['TestCase']):
                    self.parameters= [self.dict_act['Ele_Type'][idx], self.dict_act['Ele_Value'][idx], self.dict_act['Assert_API'][idx], \
                    self.dict_act['Assert_Type'][idx], self.dict_act['Assert_Value'][idx], self.dict_act['Force_Stop'][idx]]
                    if self.dict_act['Event_API'][idx] not in self.list_command:
                        self.log_text = self.dict_init['uuid']+' : Error: Invalid Event API '+self.dict_act['Event_API'][idx]
                        self.logPrint(self.log_text)
                        self.list_result.append('N/A')
                        self.list_eventDesc.append('Event command is invalid')
                        self.list_assertDesc.append('Event command is invalid')
                    elif self.dict_act['Assert_API'][idx] not in self.list_command2:
                        self.log_text = self.dict_init['uuid']+' : Error: Invalid Assert API '+self.dict_act['Assert_API'][idx]
                        self.logPrint(self.log_text)
                        self.list_result.append('N/A')
                        self.list_eventDesc.append('Assert command is invalid')
                        self.list_assertDesc.append('Assert command is invalid')
                    else:
                        self.log_text = self.dict_init['uuid']+" : "+key+' Executes : Ele==> '+str(self.dict_act['Ele_Value'][idx])+' Event==> '+str(self.dict_act['Event_API'][idx])
                        self.logPrint(self.log_text)
                        # collection of event and assert result
                        self.desc_event = self.dict_method[self.dict_act['Event_API'][idx]](self.parameters)
                        self.desc_assert = self.dict_method2[self.dict_act['Assert_API'][idx]](self.parameters)
                        self.log_text = self.dict_init['uuid']," : ",self.desc_event
                        self.logPrint(self.log_text)
                        self.log_text = self.dict_init['uuid']," : ",self.desc_assert
                        self.logPrint(self.log_text)

                        # collection if total result (if one of collection is NOK result is fail)
                        if self.desc_event[0] == 'OK' and self.desc_assert[0] =='OK':
                            self.list_result.append('PASS')
                            self.list_eventDesc.append(self.desc_event[1])
                            self.list_assertDesc.append(self.desc_assert[1])
                        elif self.desc_event[0] == 'OK' and self.desc_assert[0] == 'NOK':
                            self.list_result.append('FAIL')
                            self.list_eventDesc.append(self.desc_event[1])
                            self.list_assertDesc.append(self.desc_assert[1])
                        elif self.desc_event[0] == 'NOK' and self.desc_assert[0] == 'OK':
                            self.list_result.append('FAIL')
                            self.list_eventDesc.append(self.desc_event[1])
                            self.list_assertDesc.append(self.desc_assert[1])
                        else:
                            self.list_result.append('FAIL')
                            self.list_eventDesc.append(self.desc_event[1])
                            self.list_assertDesc.append(self.desc_assert[1])
                        self.list_elapsed.append(self.desc_event[2])

                        if self.dict_act['Force_Stop'][idx] == 'Y' and (self.desc_event[0] != 'OK' or self.desc_assert[0] !='OK'):
                            self.log_text = 'Force stop condition','NOK occured! Event: {} Assert: {}'.format(self.dict_act['TestCase'][idx],self.desc_event[0], self.desc_assert[0])
                            self.logPrint(self.log_text)
                            self.log_write()
                            self.unlock_break = True
                            sleep(60)
                            self.tearDown()
                            break

                    sleep(self.DEFAULT_DELAY)

                self.elapsed = self.get_takeMilliTime(self.total_startTime)
                self.df_result = pd.DataFrame.from_dict(self.dict_act)
                self.df_result['Result'] = self.list_result
                self.df_result['Event_Desc'] = self.list_eventDesc
                self.df_result['Assert_Desc'] = self.list_assertDesc
                self.df_result['Elapsed'] = self.list_elapsed
                self.list_cols = ['TestCase','Event_API','Ele_Type','Ele_Value','Assert_API','Assert_Type','Assert_Value',\
                'Result','Event_Desc','Assert_Desc','Elapsed']
                #result DataFrame is reindexing
                self.df_result = self.df_result[self.list_cols]
                self.report = Report(self.dict_init['uuid'], self.output_path, self.nowTime, self.df_result, \
                self.total_startTime.strftime('%Y-%m-%d %H:%M:%S'), self.elapsed[1].strftime('%Y-%m-%d %H:%M:%S'), self.elapsed[0])
                self.logPrint(self.dict_init['uuid']+" Started to generate report...")
                self.report.html_report()
                self.report.excel_report()
                self.logPrint(self.dict_init['uuid']+" finished to generate report...")
                self.logPrint(self.dict_init['uuid']+" All test is completed...")
                self.log_write()

            self.unlock_break = True
            sleep(60)
            self.tearDown()
        except:
            self.log_text = 'NOK','Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno)
            self.logPrint(self.log_text)
            self.log_write()
            self.unlock_break = True
            sleep(60)
            self.tearDown()

#########################################################################################################################################################################
######################################################################__Event Handler method__###########################################################################

    def click_obj(self, parameters):

        self.start_time = datetime.now()
        try:

            self.ele_type = parameters[0]
            self.ele_values = str(parameters[1]).split("|")

            self.child_nth = 0
            self.waitTime = 0

            if self.ele_type == 'id':
                if len(self.ele_values) == 2:
                    self.waitTime = int(self.ele_values[1])
                sleep(self.waitTime)
                self.object = self.driver.find_element_by_id(self.ele_values[0])
                self.object.click()
            elif self.ele_type == 'Xpath':
                if len(self.ele_values) == 2:
                    self.waitTime = int(self.ele_values[1])
                sleep(self.waitTime)
                self.object = self.driver.find_element_by_xpath(self.ele_values[0])
                self.object.click()
            elif self.ele_type == 'name':
                if len(self.ele_values) == 2:
                    self.waitTime = int(self.ele_values[1])
                sleep(self.waitTime)
                self.object = self.driver.find_element_by_android_uiautomator('new UiSelector().text("'+self.ele_values[0]+'")')
                self.object.click()
            elif self.ele_type == 'class':
            # value size check(wait time and class child_nth)
                if len(self.ele_values) == 2:
                    self.waitTime = int(self.ele_values[1])
                elif len(self.ele_values) == 3:
                    self.waitTime = int(self.ele_values[1])
                    self.child_nth = int(self.ele_values[2])
                sleep(self.waitTime)
                self.objects = self.driver.find_elements_by_class_name(self.ele_values[0])
                self.objects[int(self.child_nth)].click()
            elif self.ele_type == 'access_id':
                if len(self.ele_values) == 2:
                    self.waitTime = int(self.ele_values[1])
                sleep(self.waitTime)
                self.object = self.driver.find_element_by_accessibility_id(self.ele_values[0])
                self.object.click()
            # image click
            elif self.ele_type == 'image':
                self.target_img_obj = None
                self.target_img_path = ""
                self.screen_img_obj = None
                self.screen_img_path = ""
                self.rectangle_flag = ""
                sleep(int(self.ele_values[4]))

                #check file path validation
                if str(self.ele_values[0]).lower() == "true":
                    if not self.check_file(self.ele_values[1]):
                        self.elapsed = self.get_takeMilliTime(self.start_time)
                        return ["NOK","target image file does not exist", self.elapsed[0]]
                    else:
                        #target image obj and path info
                        self.target_result = self.get_imgObject(self.ele_values[1], 0)
                        self.target_img_obj = self.target_result[0]
                        self.target_img_path = self.target_result[1]

                        #screen image obj and path info
                        self.screen_result = self.get_screenshot_obj(self.ele_values[2], 0)
                        self.screen_img_obj = self.screen_result[0]
                        self.screen_img_path = self.screen_result[1]
                        self.rectangle_flag = str(self.ele_values[3].lower())

                else:
                    if not (self.check_file(self.ele_values[1]) and self.check_file(self.ele_values[2])):
                        self.elapsed = self.get_takeMilliTime(self.start_time)
                        return ["NOK","target or screen image file does not exist", self.elapsed[0]]
                    else:
                        #target image obj and path info
                        self.target_result = self.get_imgObject(self.ele_values[1], 0)
                        self.target_img_obj = self.target_result[0]
                        self.target_img_path = self.target_result[1]
                        #screen image obj and path info
                        self.screen_result = self.get_imgObject(self.ele_values[2], 0)
                        self.screen_img_obj = self.screen_result[0]
                        self.screen_img_path = self.screen_result[1]
                        self.rectangle_flag = str(self.ele_values[3].lower())

                self.detect_result = self.detectImage(self.target_img_obj, self.screen_img_obj, self.rectangle_flag, self.screen_img_path)
                #cv2_base_line value check
                if len(self.ele_values) == 6:
                    self.cv2_base_line = float(self.ele_values[5])

                if self.detect_result[0] <= self.cv2_base_line:
                    self.elapsed = self.get_takeMilliTime(self.start_time)
                    return ["NOK","There is no matching target image on screen_shot ==> base line : "+str(self.cv2_base_line)+" but actually : "+str(self.detect_result[0]), self.elapsed[0]]
                else:
                    self.t_action.tap(x=int(self.detect_result[1][0]),y=int(self.detect_result[1][1])).perform()
            # xy position click
            else:
                if len(self.ele_values) == 3:
                    self.waitTime = int(self.ele_values[2])
                sleep(self.waitTime)
                self.point_x = int(self.window_width * float(self.ele_values[0]))
                self.point_y = int(self.window_height * float(self.ele_values[1]))
                self.t_action.tap(x=self.point_x, y=self.point_y).perform()

            self.elapsed = self.get_takeMilliTime(self.start_time)
            sleep(self.DEFAULT_TIMES)
            return ["OK", "OK", self.elapsed[0]]
        except:
            self.elapsed = self.get_takeMilliTime(self.start_time)
            return ['NOK','Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno), self.elapsed[0]]

    def waitEle_obj(self, parameters):

        self.start_time = datetime.now()
        try:
            self.ele_type = parameters[0]
            self.ele_values = str(parameters[1]).split("|")
            self.child_nth = 0
            self.waitTime = 20
            # value size check(wait time and class child_nth)
            if len(self.ele_values) == 2:
                self.waitTime = int(self.ele_values[1])
            elif len(self.ele_values) == 3:
                self.waitTime = int(self.ele_values[1])
                self.child_nth = int(self.ele_values[2])
            #check ele type and fix method of ele existed each type
            #
            # self.wait = WebDriverWait(self.driver, self.waitTime)
            if self.ele_type == 'id':
                # self.wait.until(EC.presence_of_element_located((By.ID, self.ele_values[0])))
                sleep(self.waitTime)
                self.object = self.driver.find_element_by_id(self.ele_values[0])
            elif self.ele_type == 'Xpath':
                # self.wait.until(EC.presence_of_element_located((By.XPATH, self.ele_values[0])))
                sleep(self.waitTime)
                self.object = self.driver.find_element_by_xpath(self.ele_values[0])
            elif self.ele_type == 'class':
                # self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, self.ele_values[0])))
                sleep(self.waitTime)
                self.objects = self.driver.find_elements_by_class_name(self.ele_values[0])[int(self.ele_values[2])]
            else:
                # self.wait.until(EC.presence_of_element_located((By.NAME, self.ele_values[0])))
                sleep(self.waitTime)
                self.object = self.driver.find_element_by_name(self.ele_values[0])

            self.elapsed = self.get_takeMilliTime(self.start_time)
            return ["OK", "OK", self.elapsed[0]]
        except:
            self.elapsed = self.get_takeMilliTime(self.start_time)
            return ['NOK','Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno), self.elapsed[0]]

    def sendKey_obj(self, parameters):

        self.start_time = datetime.now()
        try:
            self.ele_type = parameters[0]
            self.ele_values = str(parameters[1]).split("|")
            self.inputSrting = "검색"
            self.child_nth = 0

            # value size check(wait time and class child_nth)
            if len(self.ele_values) == 2:
                self.inputSrting = self.ele_values[1]
            elif len(self.ele_values) == 3:
                self.inputSrting = self.ele_values[1]
                self.child_nth = int(self.ele_values[2])
            #check ele type and fix method of sending key each type
            if self.ele_type == 'id':
                self.object = self.driver.find_element_by_id(self.ele_values[0])
                self.object.send_keys(self.inputSrting)
                self.driver.press_keycode(66)
            elif self.ele_type == 'Xpath':
                self.object = self.driver.find_element_by_xpath(self.ele_values[0])
                self.object.send_keys(self.inputSrting)
                self.driver.press_keycode(66)
            elif self.ele_type == 'name':
                self.object = self.driver.find_element_by_android_uiautomator('new UiSelector().text("'+self.ele_values[0]+'")')
                self.object.send_keys(self.inputSrting)
                self.driver.press_keycode(66)
            elif self.ele_type == 'class':
                self.objects = self.driver.find_elements_by_class_name(self.ele_values[0])
                self.objects[self.child_nth].send_keys(self.inputSrting)
                self.driver.press_keycode(66)
            elif self.ele_type == 'access_id':
                self.object = self.driver.find_element_by_accessibility_id(self.ele_values[0])
                self.object.send_keys(self.inputSrting)
                self.driver.press_keycode(66)

            self.elapsed = self.get_takeMilliTime(self.start_time)

            sleep(self.DEFAULT_TIMES)
            return ["OK", "OK", self.elapsed[0]]
        except:
            self.elapsed = self.get_takeMilliTime(self.start_time)

            return ['NOK','Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno), self.elapsed[0]]

    def waitApp_obj(self, parameters):

        self.start_time = datetime.now()
        try:
            self.ele_values = str(parameters[1]).split("|")
            self.check_time = 1
            self.check_delay = 50
            self.flag_exist = False
            if len(self.ele_values) == 2:
                self.check_delay = int(self.ele_values[1])
            elif len(self.ele_values) == 3:
                self.check_delay = int(self.ele_values[1])
                self.check_time = int(self.ele_values[2])

            self.cmd_check = "adb -s "+self.dict_init['uuid']+" shell pm list packages"
            self.pipe = subprocess.Popen(self.cmd_check, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.res = self.pipe.communicate()
            self.res = str(self.res[0])
            for i in range(self.check_time):
                if self.ele_values[0] in self.res:
                    self.flag_exist = True
                    break
                else:
                    sleep(self.check_delay)
                    self.pipe = subprocess.Popen(self.cmd_check, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    self.res = self.pipe.communicate()
                    self.res = str(self.res[0])
            self.elapsed = self.get_takeMilliTime(self.start_time)
            if self.flag_exist:
                return ['OK', "OK", self.elapsed[0]]
            else:
                return ['NOK','Error: app package is not installed', self.elapsed[0]]
        except:
            self.elapsed = self.get_takeMilliTime(self.start_time)
            return ['NOK','Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno), self.elapsed[0]]

    def uninstallApp_obj(self, parameters):

        self.start_time = datetime.now()
        try:
            self.ele_values = str(parameters[1]).split("|")
            self.count = len(self.ele_values)
            self.cmd_packages = "adb -s "+self.dict_init['uuid']+" shell pm list packages"
            self.pipe = subprocess.Popen(self.cmd_packages, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.res_packages = self.pipe.communicate()
            #install App
            for i in range(self.count):
                if self.ele_values[i] in str(self.res_packages[0]):
                    self.cmd_check = "adb -s "+self.dict_init['uuid']+" uninstall "+self.ele_values[i]
                    self.pipe = subprocess.Popen(self.cmd_check, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    self.res = self.pipe.communicate()
                    sleep(3)
                else:
                    continue
            self.elapsed = self.get_takeMilliTime(self.start_time)
            return ['OK', "OK", self.elapsed[0]]
        except:
            self.elapsed = self.get_takeMilliTime(self.start_time)
            return ['NOK','Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno), self.elapsed[0]]

    def installApp_obj(self, parameters):

        self.start_time = datetime.now()
        try:
            self.ele_values = str(parameters[1]).split("|")
            self.count = len(self.ele_values)
            self.installing_result = ""
            #install App
            for i in range(self.count):
                self.cmd_check = "adb -s "+self.dict_init['uuid']+" install -r "+self.ele_values[i]
                self.pipe = subprocess.Popen(self.cmd_check, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                self.res = self.pipe.communicate()
                if "Success" in self.res[0]:
                    self.installing_result = self.installing_result+"OK "
                else:
                    self.installing_result = self.installing_result+self.res[0]+" "
            self.elapsed = self.get_takeMilliTime(self.start_time)
            return ['OK', self.installing_result, self.elapsed[0]]
        except:
            self.elapsed = self.get_takeMilliTime(self.start_time)
            return ['NOK','Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno), self.elapsed[0]]

    def scroll_obj(self, parameters):

        self.start_time = datetime.now()
        try:

            self.ele_type = parameters[0]
            self.ele_values = str(parameters[1]).split("|")
            self.find_ele = None
            self.start_x = None
            self.start_y = None
            self.end_x = None
            self.end_y = None
            self.move_times = None
            self.cmd_text = None

            if self.ele_type == 'xy':
                self.start_x = str(int(self.window_width * float(self.ele_values[0])))
                self.start_y = str(int(self.window_height * float(self.ele_values[1])))
                self.end_x = str(int(self.window_width * float(self.ele_values[2])))
                self.end_y = str(int(self.window_height * float(self.ele_values[3])))
                self.move_times = int(self.ele_values[4])
                self.cmd_text = 'adb -s '+self.dict_init['uuid']+' shell input touchscreen swipe '+self.start_x+' '+self.start_y+' '+self.end_x+' '+self.end_y
            else:
                self.find_ele = self.ele_values[0]
                self.start_x = str(int(self.window_width * float(self.ele_values[1])))
                self.start_y = str(int(self.window_height * float(self.ele_values[2])))
                self.end_x = str(int(self.window_width * float(self.ele_values[3])))
                self.end_y = str(int(self.window_height * float(self.ele_values[4])))
                self.move_times = int(self.ele_values[5])
                # fixed end postion xy
                # cal end x position by self.move_dir
                self.cmd_text = 'adb -s '+self.dict_init['uuid']+' shell input touchscreen swipe '+self.start_x+' '+self.start_y+' '+self.end_x+' '+self.end_y


            # fixed end postion xy
            # cal end x position by self.move_dir
            print(self.start_x," ",self.start_y," ",self.end_x," ",self.end_y)
            self.cmd_text = 'adb -s '+self.dict_init['uuid']+' shell input touchscreen swipe '+self.start_x+' '+self.start_y+' '+self.end_x+' '+self.end_y
            if self.ele_type == 'id':
                for i in range(self.move_times):
                    try:
                        self.flag = self.driver.find_element_by_id(self.ele_values[0])
                        break
                    except:
                        self.pipe = subprocess.Popen(self.cmd_text, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                        self.res = self.pipe.communicate()
                        sleep(1.8)
                        # self.driver.execute_script('mobile:shell',{'command':'input touchscreen swipe '+self.start_x+' '+self.start_y+' '+self.end_x+' '+self.end_y})
                        # self.action.press(x=self.start_x, y=self.start_y).wait(ms=400).move_to(x=self.end_x, y=self.end_y).wait(ms=400).release().perform();

            elif self.ele_type == 'Xpath':
                for i in range(self.move_times):
                    try:
                        self.flag = self.driver.find_element_by_xpath(self.ele_values[0])
                        break
                    except:
                        self.pipe = subprocess.Popen(self.cmd_text, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                        self.res = self.pipe.communicate()
                        sleep(1.8)
                        # self.driver.execute_script('mobile:shell',{'command':'input touchscreen swipe '+self.start_x+' '+self.start_y+' '+self.end_x+' '+self.end_y})
                        # self.action.press(x=self.start_x, y=self.start_y).wait(ms=400).move_to(x=self.end_x, y=self.end_y).wait(ms=400).release().perform();

            elif self.ele_type == 'name':
                for i in range(self.move_times):
                    try:
                        self.flag = self.driver.find_element_by_android_uiautomator('new UiSelector().text("'+self.ele_values[0]+'")')
                        break
                    except:
                        self.pipe = subprocess.Popen(self.cmd_text, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                        self.res = self.pipe.communicate()
                        sleep(1.8)
                        # self.driver.execute_script('mobile:shell',{'command':'input touchscreen swipe '+self.start_x+' '+self.start_y+' '+self.end_x+' '+self.end_y})
                        # self.action.press(x=self.start_x, y=self.start_y).wait(ms=400).move_to(x=self.end_x, y=self.end_y).wait(ms=400).release().perform();

            elif self.ele_type == 'access_id':
                for i in range(self.move_times):
                    try:
                        self.flag = self.driver.find_element_by_accessibility_id(self.ele_values[0])
                        break
                    except:
                        self.pipe = subprocess.Popen(self.cmd_text, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                        self.res = self.pipe.communicate()
                        sleep(1.8)
                        # self.driver.execute_script('mobile:shell',{'command':'input touchscreen swipe '+self.start_x+' '+self.start_y+' '+self.end_x+' '+self.end_y})
                        # self.action.press(x=self.start_x, y=self.start_y).wait(ms=400).move_to(x=self.end_x, y=self.end_y).wait(ms=400).release().perform();

            elif self.ele_type == 'image':
                self.target_img_obj = None
                self.target_img_path = ""
                self.screen_img_obj = None
                self.screen_img_path = ""
                self.rectangle_flag = ""
                #check file path validation
                if not self.check_file(self.ele_values[0]):
                    self.elapsed = get_takeMilliTime(self.start_time)
                    return ["NOK","target image file does not exist", self.elapsed[0]]
                else:
                    #target image obj and path info
                    self.target_result = self.get_imgObject(self.find_ele, 0)
                    self.target_img_obj = self.target_result[0]
                    self.target_img_path = self.target_result[1]
                    #cv2_base_line value check
                    if len(self.ele_values) == 9:
                        self.cv2_base_line = float(self.ele_values[8])
                    for i in range(self.move_times):
                        #screen image obj and path info
                        self.screen_result = self.get_screenshot_obj(self.ele_values[6], 0)
                        self.screen_img_obj = self.screen_result[0]
                        self.screen_img_path = self.screen_result[1]
                        self.rectangle_flag = str(self.ele_values[7].lower())
                        self.detect_result = self.detectImage(self.target_img_obj, self.screen_img_obj, self.rectangle_flag, self.screen_img_path)
                        if self.detect_result[0] >= self.cv2_base_line:
                            break
                        elif i == self.move_times-1 and self.detect_result[0] < self.cv2_base_line:
                            self.elapsed = self.get_takeMilliTime(self.start_time)
                            return ["NOK", "There is no matching target image on screen_shot", self.elapsed[0]]
                        else:
                            self.pipe = subprocess.Popen(self.cmd_text, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                            self.res = self.pipe.communicate()
                            sleep(1.8)
                        # self.driver.execute_script('mobile:shell',{'command':'input touchscreen swipe '+self.start_x+' '+self.start_y+' '+self.end_x+' '+self.end_y})
                        # self.action.press(x=self.start_x, y=self.start_y).wait(ms=400).move_to(x=self.end_x, y=self.end_y).wait(ms=400).release().perform();
            #xy position scroll action
            else:
                for i in range(self.move_times):
                    self.pipe = subprocess.Popen(self.cmd_text, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    self.res = self.pipe.communicate()
                    sleep(1.8)

            self.elapsed = self.get_takeMilliTime(self.start_time)

            return ["OK", "OK", self.elapsed[0]]
        except:
            self.elapsed = self.get_takeMilliTime(self.start_time)

            return ['NOK','Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno), self.elapsed[0]]

    def back_obj(self, parameters):

        self.start_time = datetime.now()
        self.rep_times = 1
        self.delays = 0
        self.ele_values = str(parameters[1]).split("|")
        try:
            if str(self.ele_values[0]).lower() != "none":
                self.rep_times = int(self.ele_values[0])
            if len(self.ele_values) == 2:
                self.delays = int(self.ele_values[1])
            if self.delays == 0:
                for time in range(self.rep_times):
                    self.driver.press_keycode(4)
                self.elapsed = self.get_takeMilliTime(self.start_time)
                return ["OK", "OK", self.elapsed[0]]
            else:
                for time in range(self.rep_times):
                    sleep(self.delays)
                    self.driver.press_keycode(4)
                self.elapsed = self.get_takeMilliTime(self.start_time)
                return ["OK", "OK", self.elapsed[0]]
        except:
            self.elapsed = self.get_takeMilliTime(self.start_time)
            return ['NOK','Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno), self.elapsed[0]]

    def home_obj(self, parameters):

        self.start_time = datetime.now()
        try:
            self.driver.press_keycode(3)
            self.elapsed = self.get_takeMilliTime(self.start_time)
            return ["OK", "OK", self.elapsed[0]]
        except:
            self.elapsed = self.get_takeMilliTime(self.start_time)
            return ['NOK','Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno), self.elapsed[0]]

    def screenShot_obj(self, parameters):

        self.start_time = datetime.now()
        try:
            self.start_time = datetime.now()
            self.file_name = parameters[1]
            self.driver.save_screenshot(self.screen_path + self.file_name +".png")
            self.elapsed = self.get_takeMilliTime(self.start_time)
            return ["OK","OK",self.elapsed[0]]
        except:
            self.elapsed = self.get_takeMilliTime(self.start_time)
            return ['NOK','Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno), self.elapsed[0]]

    def launchApp_obj(self, parameters):

        self.start_time = datetime.now()
        try:
            self.ele_values = str(parameters[1]).split("|")
            self.package_name = self.ele_values[0]
            self.res = self.driver.execute_script('mobile:shell', {'command':"monkey -p "+self.package_name+" -c android.intent.category.LAUNCHER 1"})
            if 'No activities found to run, monkey aborted.' in self.res:
                self.take_time = datetime.now() - self.start_time
                self.elapsed = str(self.take_time.seconds)+"."+str(self.take_time.microseconds)
                return ['NOK','Error: launching the app is failed', self.elapsed]

            self.elapsed = self.get_takeMilliTime(self.start_time)
            return ["OK","OK", self.elapsed[0]]
        except:
            self.elapsed = self.get_takeMilliTime(self.start_time)
            return ['NOK','Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno), self.elapsed[0]]

    def stopApp_obj(self, parameters):

        self.start_time = datetime.now()
        try:
            self.ele_values = str(parameters[1]).split("|")
            self.package_name = self.ele_values[0]
            self.driver.execute_script('mobile:shell', {'command':"am force-stop "+self.package_name})
            self.elapsed = self.get_takeMilliTime(self.start_time)
            return ["OK","OK", self.elapsed[0]]
        except:
            self.elapsed = self.get_takeMilliTime(self.start_time)
            return ['NOK','Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno), self.elapsed[0]]

    # def screenRecord_start_obj(self, parameters):
    #     self.start_time = datetime.now()
    #     try:
    #         self.driver.start_recording_screen(filePath=self.record_path + self.file_name + ".mp4",videoSize=,)
    #         self.take_time = datetime.now() - self.start_time
    #         self.elpased = str(self.take_time.seconds)+"."+str(self.take_time.microseconds)
    #         return ["OK","OK",self.elapsed]
    #     except:
    #         self.take_time = datetime.now() - self.start_time
    #         self.elapsed = str(self.take_time.seconds)+"."+str(self.take_time.microseconds)
    #         return ['NOK','Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno), self.elapsed]

    def screenRecord_start_obj(self, parameters):

        self.start_time = datetime.now()
        try:
            self.ele_values = str(parameters[1]).split("|")
            self.thread_video = threading.Thread(target=self.recordVideo, args=(self.ele_values[0], self.ele_values[1], self.ele_values[2]))
            self.thread_video.start()
            # self.driver.execute_script('mobile:shell', {'command':'screenrecord --time-limit '+self.record_time+' /sdcard/'+self.file_name})
            self.elapsed = self.get_takeMilliTime(self.start_time)
            return ["OK","OK", self.elapsed[0]]
        except:
            self.elapsed = self.get_takeMilliTime(self.start_time)
            return ['NOK','Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno), self.elapsed[0]]

        # print("Sending CTRL-C...")
        # proc.send_signal(signal.SIGINT) ## Send interrupt signal
        # ## You can also use one of these two
        # #proc.terminate() ## send terminate signal
        # #proc.kill() ## send kill signal (forcibly kill the process, it cannot be trapped so the process can't exit gracefully, use with caution)

    def airplane_off_obj(self, parameters):

        self.start_time = datetime.now()
        try:

            self.ele_type = parameters[0]
            self.cmd_check = "adb -s "+self.dict_init['uuid']+" shell settings get global airplane_mode_on"
            self.pipe = subprocess.Popen(self.cmd_check, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.res = self.pipe.communicate()
            if "1" in str(self.res[0]):

                # self.ele_values = str(parameters[1]).split("|")
                # self.find_ele = self.ele_values[0]
                self.cmd_air = "adb -s "+self.dict_init['uuid']+" shell am start -a android.settings.AIRPLANE_MODE_SETTINGS"
                self.pipe = subprocess.Popen(self.cmd_air, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                self.res = self.pipe.communicate()
                self.sleep(1)
                # 삼성의 경우 바로 비행기모드 화면 전환 LG는 settings에서 스크롤 다운으로 찾아야
                if self.ele_type == 'samsung':
                    #samsung 엘레먼트 찾고 거기에 맞춰 맞춰 실행
                    #설정 //com.android.settings[@text='사용 안 함'] 확인 //android.widget.Switch[@text='사용 안 함']
                    #해제 //com.android.settings[@text='사용 중'] //android.widget.Switch[@text='사용 중']
                    self.setting_switch = self.driver.find_element_by_id("com.android.settings:id/switch_widget")
                    self.setting_switch.click()
                elif self.ele_type == 'lg':
                    #LG 엘레먼트 찾고 거기에 맞춰 맞춰 실행
                    #//android.widget.TextView[@text='비행기 모드'] 찾고 ==> //android.widget.Switch[@text='해제']를 클릭 ==>popup id android:id/text1 존재 확인 ==> //android.widget.Button[@text='사용'] 클릭
                    #해제 //android.widget.TextView[@text='비행기 모드'] 찾고 ==> //android.widget.Switch[@text='설정']를 클릭

                    self.start_x = str(int(self.window_width * 0.5))
                    self.start_y = str(int(self.window_height * 0.8))
                    self.end_x = str(int(self.window_width * 0.5))
                    self.end_y = str(int(self.window_height * 0.5))
                    self.cmd_text = 'adb -s '+self.dict_init['uuid']+' shell input touchscreen swipe '+self.start_x+' '+self.start_y+' '+self.end_x+' '+self.end_y
                    for i in range(30):
                        try:
                            self.flag = self.driver.find_element_by_xpath('//android.widget.TextView[@text="비행기 모드"]')
                            self.button = self.driver.find_element_by_xpath('//android.widget.Switch[@text="설정"]')
                            self.button.click()
                            break
                        except:
                            self.pipe = subprocess.Popen(self.cmd_text, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                            self.res = self.pipe.communicate()
                            sleep(1)
                elif self.ele_type == "poco":
                    self.setting_switch = self.driver.find_element_by_xpath('//android.widget.CheckBox[@instance="0"]')
                    self.setting_switch.click()
                else:
                    self.setting_switch = self.driver.find_element_by_id('//android:id/switch_widget')
                    self.setting_switch.click()

                self.driver.press_keycode(4)
                self.elapsed = self.get_takeMilliTime(self.start_time)

                return ["OK","OK", self.elapsed[0]]
            else:
                self.elapsed = self.get_takeMilliTime(self.start_time)

                return ["NOK","AIRPLANE_MODE is already off", self.elapsed[0]]
        except:
            self.driver.press_keycode(4)
            self.elapsed = self.get_takeMilliTime(self.start_time)

            return ['NOK','Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno), self.elapsed[0]]

    def airplane_on_obj(self, parameters):

        self.start_time = datetime.now()
        try:

            self.ele_type = parameters[0]
            #airplane mode on/off check
            self.cmd_check = "adb -s "+self.dict_init['uuid']+" shell settings get global airplane_mode_on"
            self.pipe = subprocess.Popen(self.cmd_check, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.res = self.pipe.communicate()
            if "0" in str(self.res[0]):

                # self.ele_values = str(parameters[1]).split("|")
                # self.find_ele = self.ele_values[0]
                self.cmd_air = "adb -s "+self.dict_init['uuid']+" shell am start -a android.settings.AIRPLANE_MODE_SETTINGS"
                self.pipe = subprocess.Popen(self.cmd_air, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                self.res = self.pipe.communicate()
                self.sleep(1)
                # 삼성의 경우 바로 비행기모드 화면 전환 LG는 settings에서 스크롤 다운으로 찾아야
                if self.ele_type == 'samsung':
                    #samsung 엘레먼트 찾고 거기에 맞춰 맞춰 실행
                    #설정 //com.android.settings[@text='사용 안 함'] 확인 //android.widget.Switch[@text='사용 안 함']
                    #해제 //com.android.settings[@text='사용 중'] //android.widget.Switch[@text='사용 중']
                    self.setting_switch = self.driver.find_element_by_id("com.android.settings:id/switch_widget")
                    self.setting_switch.click()
                elif self.ele_type == 'lg':
                    #LG 엘레먼트 찾고 거기에 맞춰 맞춰 실행
                    #//android.widget.TextView[@text='비행기 모드'] 찾고 ==> //android.widget.Switch[@text='해제']를 클릭 ==>popup id android:id/text1 존재 확인 ==> //android.widget.Button[@text='사용'] 클릭
                    #해제 //android.widget.TextView[@text='비행기 모드'] 찾고 ==> //android.widget.Switch[@text='설정']를 클릭

                    self.start_x = str(int(self.window_width * 0.5))
                    self.start_y = str(int(self.window_height * 0.8))
                    self.end_x = str(int(self.window_width * 0.5))
                    self.end_y = str(int(self.window_height * 0.5))
                    self.cmd_text = 'adb -s '+self.dict_init['uuid']+' shell input touchscreen swipe '+self.start_x+' '+self.start_y+' '+self.end_x+' '+self.end_y
                    for i in range(30):
                        try:
                            self.flag = self.driver.find_element_by_xpath('//android.widget.TextView[@text="비행기 모드"]')
                            self.button = self.driver.find_element_by_xpath('//android.widget.Switch[@text="해제"]')
                            self.button.click()
                            sleep(1)
                            self.button2 = self.driver.find_element_by_id('android:id/button1')
                            self.button2.click()
                            break
                        except:
                            self.pipe = subprocess.Popen(self.cmd_text, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                            self.res = self.pipe.communicate()
                            sleep(1)
                elif self.ele_type == 'poco':
                    self.setting_switch = self.driver.find_element_by_xpath('//android.widget.CheckBox[@instance="0"]')
                    self.setting_switch.click()

                else:
                    self.setting_switch = self.driver.find_element_by_id('//android:id/switch_widget')
                    self.setting_switch.click()

                self.driver.press_keycode(4)
                self.elapsed = self.get_takeMilliTime(self.start_time)

                return ["OK","OK", self.elapsed[0]]
            else:
                self.elapsed = self.get_takeMilliTime(self.start_time)

                return ["NOK","AIRPLANE_MODE is already on", self.elapsed[0]]

        except:
            self.driver.press_keycode(4)
            self.take_time = datetime.now() - self.start_time
            self.elapsed = str(self.take_time.seconds)+"."+str(self.take_time.microseconds)

            return ['NOK','Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno), self.elapsed[0]]

    def dropAllApp_obj(self, parameters):

        self.start_time = datetime.now()
        try:
            self.ele_type = parameters[0]

            self.driver.press_keycode(3)
            self.driver.press_keycode(187)
            #check close all recently app kill button depend on device manufacturers
            if self.ele_type == "samsung":
                if self.driver.find_element_by_android_uiautomator('new UiSelector().resourceId("com.android.systemui:id/recents_close_all_button")').is_displayed():
                    self.driver.find_element_by_id('com.android.systemui:id/recents_close_all_button').click()
                else:
                    self.driver.press_keycode(4)
                    pass
            else:
                if self.driver.find_element_by_android_uiautomator('new UiSelector().text("모두 지우기")').is_displayed():
                    self.driver.find_element_by_android_uiautomator('new UiSelector().text("모두 지우기")').click()
                else:
                    self.driver.press_keycode(4)
                    pass

            self.elapsed = self.get_takeMilliTime(self.start_time)

            return ["OK","OK", self.elapsed[0]]
        except:
            self.elapsed = self.get_takeMilliTime(self.start_time)

            return ['NOK','Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno), self.elapsed[0]]

    def act_none_obj(self, parameters):

        self.start_time = datetime.now()
        try:
            self.delay_time = parameters[1]
            sleep(int(self.delay_time))
            self.elapsed = self.get_takeMilliTime(self.start_time)
            return ['OK', "OK", self.elapsed[0]]
        except:
            self.elapsed = self.get_takeMilliTime(self.start_time)
            return ['NOK','Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno), self.elapsed[0]]

    def executeCmd_obj(self, parameters):

        self.start_time = datetime.now()
        try:
            self.type = parameters[0]
            self.expected_returned = ""
            self.delays = 1
            self.ele_values = str(parameters[1]).split("&")
            # 리턴값 비교
            if self.type == "ON":
                if len(self.ele_values) == 2:
                    self.expected_returned = str(self.ele_values[1])
                elif len(self.ele_values) == 3:
                    self.expected_returned = str(self.ele_values[1])
                    self.delays = int(self.ele_values[2])

                self.cmd_text = self.ele_values[0]
                self.pipe = subprocess.Popen(self.cmd_text, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                self.res = self.pipe.communicate()
                self.res_data = str(self.res[0])
                sleep(self.delays)
                if self.expected_returned in self.res_data:
                    self.elapsed = self.get_takeMilliTime(self.start_time)
                    return ['OK', "OK", self.elapsed[0]]
                else:
                    self.elapsed = self.get_takeMilliTime(self.start_time)
                    return ['NOK', "Expected Data is not in real returned data : Expected ==> "+self.expected_returned+" Actucally ==> "+self.res_data, self.elapsed[0]]

            else:
                if len(self.ele_values) == 2:
                    self.delays = int(self.ele_values[1])

                self.cmd_text = self.ele_values[0]
                # args = {"command": "input text", "args": "/sdcard/test.mp4"}
                # output = self.driver.execute_script("mobile: shell", args)
                self.pipe = subprocess.Popen(self.cmd_text, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                self.res = self.pipe.communicate()
                sleep(self.delays)
                self.elapsed = self.get_takeMilliTime(self.start_time)
                return ['OK', "OK", self.elapsed[0]]
        except:
            self.elapsed = self.get_takeMilliTime(self.start_time)
            return ['NOK','Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno), self.elapsed[0]]

    # def generate_folder(self):
    #     self.pipe = subprocess.Popen("adb -s "+self.dict_init['uuid']+" shell mkdir /sdcard/appium_record", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    #     self.pipe.communicate()
#########################################################################################################################################################################
######################################################################__assert Handler method__##########################################################################

    def assert_none(self, parameters):
        return ['OK', "OK"]

    def assert_text_equal(self, parameters):

        try:
            self.ele_type = parameters[3]

            self.ele_values = parameters[4].split("|")
            if len(self.ele_values) != 3:

                return ['NOK','ele_values parameter size must be 3']
            else:
                self.option_flag = self.ele_values[2]
                #check ele type and fix method of sending key each type
                # target string include true case
                if self.option_flag == 'true':
                    if self.ele_type == 'id':
                        self.object = self.driver.find_element_by_id(self.ele_values[0])
                        if str(self.ele_values[1]) not in self.object.text:

                            return ["NOK", "element "+self.ele_values[0]+"'s text is not "+self.ele_values[1]+" but "+self.object.text]

                    elif self.ele_type == 'Xpath':
                        self.object = self.driver.find_element_by_xpath(self.ele_values[0])
                        if str(self.ele_values[1]) not in self.object.text:

                            return ["NOK", "element "+self.ele_values[0]+"'s text is not "+self.ele_values[1]+" but "+self.object.text]

                    elif self.ele_type == 'name':
                        self.object = self.driver.find_element_by_android_uiautomator('new UiSelector().text("'+self.ele_values[0]+'")')
                        if str(self.ele_values[1]) not in self.object.text:

                            return ["NOK", "element "+self.ele_values[0]+"'s text is not "+self.ele_values[1]+" but "+self.object.text]

                    elif self.ele_type == 'access_id':
                        self.object = self.driver.find_element_by_accessibility_id(self.ele_values[0])
                        if str(self.ele_values[1]) not in self.object.text:

                            return ["NOK", "element "+self.ele_values[0]+"'s text is not "+self.ele_values[1]+" but "+self.object.text]
                # target string totally equals case
                else:
                    if self.ele_type == 'id':
                        self.object = self.driver.find_element_by_id(self.ele_values[0])
                        if self.object.text != str(self.ele_values[1]):

                            return ["NOK", "element "+self.ele_values[0]+"'s text is not "+self.ele_values[1]+" but "+self.object.text]

                    elif self.ele_type == 'Xpath':
                        self.object = self.driver.find_element_by_xpath(self.ele_values[0])
                        if self.object.text != str(self.ele_values[1]):

                            return ["NOK", "element "+self.ele_values[0]+"'s text is not "+self.ele_values[1]+" but "+self.object.text]

                    elif self.ele_type == 'name':
                        self.object = self.driver.find_element_by_android_uiautomator('new UiSelector().text("'+self.ele_values[0]+'")')
                        if self.object.text != str(self.ele_values[1]):

                            return ["NOK", "element "+self.ele_values[0]+"'s text is not "+self.ele_values[1]+" but "+self.object.text]

                    elif self.ele_type == 'access_id':
                        self.object = self.driver.find_element_by_accessibility_id(self.ele_values[0])
                        if self.object.text != str(self.ele_values[1]):

                            return ["NOK", "element "+self.ele_values[0]+"'s text is not "+self.ele_values[1]+" but "+self.object.text]


                return ["OK", "OK"]
        except:

            return ['NOK','Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno)]

    def assert_text_notEqual(self, parameters):

        try:
            self.ele_type = parameters[3]

            self.ele_values = parameters[4].split("|")
            if len(self.ele_values) != 3:

                return ['NOK','ele_values parameter size must be 3']
            else:
                self.option_flag = self.ele_values[2]
                #check ele type and fix method of sending key each type
                # target string include true case
                if self.option_flag == 'true':
                    if self.ele_type == 'id':
                        self.object = self.driver.find_element_by_id(self.ele_values[0])
                        if str(self.ele_values[1]) in self.object.text:

                            return ["NOK", "element "+self.ele_values[0]+"'s text is not "+self.ele_values[1]+" but "+self.object.text]

                    elif self.ele_type == 'Xpath':
                        self.object = self.driver.find_element_by_xpath(self.ele_values[0])
                        if str(self.ele_values[1]) in self.object.text:

                            return ["NOK", "element "+self.ele_values[0]+"'s text is not "+self.ele_values[1]+" but "+self.object.text]

                    elif self.ele_type == 'name':
                        self.object = self.driver.find_element_by_android_uiautomator('new UiSelector().text("'+self.ele_values[0]+'")')
                        if str(self.ele_values[1]) in self.object.text:

                            return ["NOK", "element "+self.ele_values[0]+"'s text is not "+self.ele_values[1]+" but "+self.object.text]

                    elif self.ele_type == 'access_id':
                        self.object = self.driver.find_element_by_accessibility_id(self.ele_values[0])
                        if str(self.ele_values[1]) in self.object.text:

                            return ["NOK", "element "+self.ele_values[0]+"'s text is not "+self.ele_values[1]+" but "+self.object.text]
                # target string totally equals case
                else:
                    if self.ele_type == 'id':
                        self.object = self.driver.find_element_by_id(self.ele_values[0])
                        if self.object.text == str(self.ele_values[1]):

                            return ["NOK", "element "+self.ele_values[0]+"'s text is not "+self.ele_values[1]+" but "+self.object.text]

                    elif self.ele_type == 'Xpath':
                        self.object = self.driver.find_element_by_xpath(self.ele_values[0])
                        if self.object.text == str(self.ele_values[1]):

                            return ["NOK", "element "+self.ele_values[0]+"'s text is not "+self.ele_values[1]+" but "+self.object.text]

                    elif self.ele_type == 'name':
                        self.object = self.driver.find_element_by_android_uiautomator('new UiSelector().text("'+self.ele_values[0]+'")')
                        if self.object.text == str(self.ele_values[1]):

                            return ["NOK", "element "+self.ele_values[0]+"'s text is not "+self.ele_values[1]+" but "+self.object.text]

                    elif self.ele_type == 'access_id':
                        self.object = self.driver.find_element_by_accessibility_id(self.ele_values[0])
                        if self.object.text == str(self.ele_values[1]):

                            return ["NOK", "element "+self.ele_values[0]+"'s text is not "+self.ele_values[1]+" but "+self.object.text]


                return ["OK", "OK"]
        except:

            return ['NOK','Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno)]

    def assert_attribute_equal(self, parameters):

        try:

            self.ele_type = parameters[3]
            self.ele_values = parameters[4].split("|")
            if len(self.ele_values) != 4:

                return ['NOK','ele_values parameter size must be 4']
            else:
                self.option_flag = self.ele_values[3]
                #check ele type and fix method of sending key each type
                # target string include true case
                if self.option_flag == 'true':
                    if self.ele_type == 'id':
                        self.object = self.driver.find_element_by_id(self.ele_values[0])
                        if str(self.ele_values[2]) not in self.object.get_attribute(self.ele_values[1]):

                            return ["NOK", "element "+self.ele_values[0]+"'s "+self.ele_values[1]+" attribute text is not "+self.ele_values[2]+" but "+self.object.get_attribute(self.ele_values[1])]
                    elif self.ele_type == 'Xpath':
                        self.object = self.driver.find_element_by_xpath(self.ele_values[0])
                        if str(self.ele_values[2]) not in self.object.get_attribute(self.ele_values[1]):

                            return ["NOK", "element "+self.ele_values[0]+"'s "+self.ele_values[1]+" attribute text is not "+self.ele_values[2]+" but "+self.object.get_attribute(self.ele_values[1])]
                    elif self.ele_type == 'name':
                        self.object = self.driver.find_element_by_android_uiautomator('new UiSelector().text("'+self.ele_values[0]+'")')
                        if str(self.ele_values[2]) not in self.object.get_attribute(self.ele_values[1]):

                            return ["NOK", "element "+self.ele_values[0]+"'s "+self.ele_values[1]+" attribute text is not "+self.ele_values[2]+" but "+self.object.get_attribute(self.ele_values[1])]
                    elif self.ele_type == 'access_id':
                        self.object = self.driver.find_element_by_accessibility_id(self.ele_values[0])
                        if str(self.ele_values[2]) not in self.object.get_attribute(self.ele_values[1]):

                            return ["NOK", "element "+self.ele_values[0]+"'s "+self.ele_values[1]+" attribute text is not "+self.ele_values[2]+" but "+self.object.get_attribute(self.ele_values[1])]
                # target string totally equals case
                else:
                    if self.ele_type == 'id':
                        self.object = self.driver.find_element_by_id(self.ele_values[0])
                        if self.object.get_attribute(self.ele_values[1]) != str(self.ele_values[2]):

                            return ["NOK", "element "+self.ele_values[0]+"'s "+self.ele_values[1]+" attribute text is not "+self.ele_values[2]+" but "+self.object.get_attribute(self.ele_values[1])]
                    elif self.ele_type == 'Xpath':
                        self.object = self.driver.find_element_by_xpath(self.ele_values[0])
                        if self.object.get_attribute(self.ele_values[1]) != str(self.ele_values[2]):

                            return ["NOK", "element "+self.ele_values[0]+"'s "+self.ele_values[1]+" attribute text is not "+self.ele_values[2]+" but "+self.object.get_attribute(self.ele_values[1])]
                    elif self.ele_type == 'name':
                        self.object = self.driver.find_element_by_android_uiautomator('new UiSelector().text("'+self.ele_values[0]+'")')
                        if self.object.get_attribute(self.ele_values[1]) != str(self.ele_values[2]):

                            return ["NOK", "element "+self.ele_values[0]+"'s "+self.ele_values[1]+" attribute text is not "+self.ele_values[2]+" but "+self.object.get_attribute(self.ele_values[1])]
                    elif self.ele_type == 'access_id':
                        self.object = self.driver.find_element_by_accessibility_id(self.ele_values[0])
                        if self.object.get_attribute(self.ele_values[1]) != str(self.ele_values[2]):

                            return ["NOK", "element "+self.ele_values[0]+"'s "+self.ele_values[1]+" attribute text is not "+self.ele_values[2]+" but "+self.object.get_attribute(self.ele_values[1])]


                return ["OK", "OK"]
        except:

            return ['NOK','Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno)]

    def assert_attribute_notEqual(self, parameters):

        try:

            self.ele_type = parameters[3]
            self.ele_values = parameters[4].split("|")
            if len(self.ele_values) != 4:

                return ['NOK','ele_values parameter size must be 4']
            else:
                self.option_flag = self.ele_values[3]
                #check ele type and fix method of sending key each type
                # target string include true case
                if self.option_flag == 'true':
                    if self.ele_type == 'id':
                        self.object = self.driver.find_element_by_id(self.ele_values[0])
                        if str(self.ele_values[2]) in self.object.get_attribute(self.ele_values[1]):

                            return ["NOK", "element "+self.ele_values[0]+"'s "+self.ele_values[1]+" attribute text is not "+self.ele_values[2]+" but "+self.object.get_attribute(self.ele_values[1])]
                    elif self.ele_type == 'Xpath':
                        self.object = self.driver.find_element_by_xpath(self.ele_values[0])
                        if str(self.ele_values[2]) in self.object.get_attribute(self.ele_values[1]):

                            return ["NOK", "element "+self.ele_values[0]+"'s "+self.ele_values[1]+" attribute text is not "+self.ele_values[2]+" but "+self.object.get_attribute(self.ele_values[1])]
                    elif self.ele_type == 'name':
                        self.object = self.driver.find_element_by_android_uiautomator('new UiSelector().text("'+self.ele_values[0]+'")')
                        if str(self.ele_values[2]) in self.object.get_attribute(self.ele_values[1]):

                            return ["NOK", "element "+self.ele_values[0]+"'s "+self.ele_values[1]+" attribute text is not "+self.ele_values[2]+" but "+self.object.get_attribute(self.ele_values[1])]
                    elif self.ele_type == 'access_id':
                        self.object = self.driver.find_element_by_accessibility_id(self.ele_values[0])
                        if str(self.ele_values[2]) in self.object.get_attribute(self.ele_values[1]):

                            return ["NOK", "element "+self.ele_values[0]+"'s "+self.ele_values[1]+" attribute text is not "+self.ele_values[2]+" but "+self.object.get_attribute(self.ele_values[1])]
                # target string totally equals case
                else:
                    if self.ele_type == 'id':
                        self.object = self.driver.find_element_by_id(self.ele_values[0])
                        if self.object.get_attribute(self.ele_values[1]) == str(self.ele_values[2]):

                            return ["NOK", "element "+self.ele_values[0]+"'s "+self.ele_values[1]+" attribute text is not "+self.ele_values[2]+" but "+self.object.get_attribute(self.ele_values[1])]
                    elif self.ele_type == 'Xpath':
                        self.object = self.driver.find_element_by_xpath(self.ele_values[0])
                        if self.object.get_attribute(self.ele_values[1]) == str(self.ele_values[2]):

                            return ["NOK", "element "+self.ele_values[0]+"'s "+self.ele_values[1]+" attribute text is not "+self.ele_values[2]+" but "+self.object.get_attribute(self.ele_values[1])]
                    elif self.ele_type == 'name':
                        self.object = self.driver.find_element_by_android_uiautomator('new UiSelector().text("'+self.ele_values[0]+'")')
                        if self.object.get_attribute(self.ele_values[1]) == str(self.ele_values[2]):

                            return ["NOK", "element "+self.ele_values[0]+"'s "+self.ele_values[1]+" attribute text is not "+self.ele_values[2]+" but "+self.object.get_attribute(self.ele_values[1])]
                    elif self.ele_type == 'access_id':
                        self.object = self.driver.find_element_by_accessibility_id(self.ele_values[0])
                        if self.object.get_attribute(self.ele_values[1]) == str(self.ele_values[2]):

                            return ["NOK", "element "+self.ele_values[0]+"'s "+self.ele_values[1]+" attribute text is not "+self.ele_values[2]+" but "+self.object.get_attribute(self.ele_values[1])]


                return ["OK", "OK"]
        except:

            return ['NOK','Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno)]

    def assert_logical(self, parameters):
        pass

    def assert_exists(self, parameters):

        if parameters[3] == 'exists':
            return self.hasObject(parameters)
        else:
            return self.hasNotObject(parameters)

    def assert_execute_adb(self, parameters):

        try:
            self.type = parameters[3]
            self.ele_values = parameters[4].split("&")
            if self.type == "none":
                if len(self.ele_values) != 1:
                    return ['NOK', 'ele_values parameter size must be 1']
                self.driver.execute_script('mobile:shell', {'command':self.ele_values[0]})
                return ["OK", "OK"]

            elif self.type == "exists":
                if len(self.ele_values) != 2:
                    return ['NOK','ele_values parameter size must be 2']
                self.res = self.driver.execute_script('mobile:shell', {'command':self.ele_values[0]})
                if str(self.ele_values[1]) not in self.res:
                    return ['NOK', str(self.ele_values[1])+" is not in adb response. Actucally response '"+self.res+"'"]
                return ["OK", "OK"]

            else:
                if len(self.ele_values) != 2:
                    return ['NOK','ele_values parameter size must be 2']
                self.res = self.driver.execute_script('mobile:shell', {'command':self.ele_values[0]})
                if str(self.ele_values[1]) in self.res:
                    return ['NOK', str(self.ele_values[1])+" is in adb response. Actucally response '"+self.res+"'"]
                return ["OK", "OK"]
        except:
            return ['NOK', 'Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno)]

    def assert_image_compare(self, parameters):

        try:
            self.type = parameters[3]
            self.ele_values = parameters[4].split("|")
            self.target_result = self.get_imgObject(self.ele_values[0], 0)
            self.target_img_obj = self.target_result[0]
            self.target_img_path = self.target_result[1]
            #screen image obj and path info
            self.screen_result = self.get_screenshot_obj(self.ele_values[1], 0)
            self.screen_img_obj = self.screen_result[0]
            self.screen_img_path = self.screen_result[1]
            self.rectangle_flag = str(self.ele_values[2].lower())
            #check cv2_base_line_per Value
            if len(self.ele_values) == 4:
                self.cv2_base_line_per = float(self.ele_values[3])
            # compare image target and screen shot
            self.detect_result = self.compareImage(self.target_img_obj, self.screen_img_obj, self.rectangle_flag, self.screen_img_path)
            #result value check depend on comparation type
            if self.type == "same":
                if self.detect_result >= self.cv2_base_line_per:
                    return ["OK","OK"]
                else:
                    return["NOK","Target_img and Screen_img is lower than base line \""+str(self.cv2_base_line_per)+"\" Actucally "+str(self.detect_result)]
            else:
                if self.detect_result < self.cv2_base_line_per:
                    return ["OK","OK"]
                else:
                    return["NOK","Target_img and Screen_img is higher than base line \""+str(self.cv2_base_line_per)+"\" Actucally "+str(self.detect_result)]
        except:
            return ['NOK','Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno)]

    def assert_image_in(self, parameters):

        try:
            self.type = parameters[3]
            self.ele_values = parameters[4].split("|")
            self.target_result = self.get_imgObject(self.ele_values[0], 0)
            self.target_img_obj = self.target_result[0]
            self.target_img_path = self.target_result[1]
            #screen image obj and path info
            self.screen_result = self.get_screenshot_obj(self.ele_values[1], 0)
            self.screen_img_obj = self.screen_result[0]
            self.screen_img_path = self.screen_result[1]
            self.rectangle_flag = str(self.ele_values[2].lower())
            #check cv2_base_line_per Value
            if len(self.ele_values) == 4:
                self.cv2_base_line = float(self.ele_values[3])
            # compare image target and screen shot
            self.detect_result = self.detectImage(self.target_img_obj, self.screen_img_obj, self.rectangle_flag, self.screen_img_path)
            #result value check depend on comparation type
            if self.type == "exists":
                if self.detect_result[0] >= self.cv2_base_line:
                    return ["OK","OK"]
                else:
                    return["NOK","Target_img is not in Screen_img ==> base_line: "+str(self.cv2_base_line)+" but actually: "+str(self.detect_result[0])]
            else:
                if self.detect_result[0] < self.cv2_base_line:
                    return ["OK","OK"]
                else:
                    return["NOK","Target_img is in Screen_img ==> base_line: "+str(self.cv2_base_line)+" but actually: "+str(self.detect_result[0])]
        except:
            return ['NOK','Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno)]

#########################################################################################################################################################################
######################################################################__utils Handler method__##########################################################################
    def setErrorText(self, text):

        # self.strToday = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        self.strToday = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        self.error_text = self.strToday+":\n"+text+"\n"
        self.error_flag.emit()
        self.tearDown()
        self.end_flag.emit()

    def hasObject(self, parameters):

        try:

            self.ele_values = parameters[4].split("|")
            self.ele_type = self.ele_values[1]
            self.child_nth = 0
            # value size check(wait time and class child_nth)
            if len(self.ele_values) == 3:
                self.child_nth = int(self.ele_values[2])
            #check ele type and fix method of ele existed each type
            if self.ele_type == 'id':
                self.object = self.driver.find_element_by_id(self.ele_values[0])
            elif self.ele_type == 'Xpath':
                self.object = self.driver.find_element_by_xpath(self.ele_values[0])
            elif self.ele_type == 'name':
                self.object = self.driver.find_element_by_android_uiautomator('new UiSelector().text("'+self.ele_values[0]+'")')
            elif self.ele_type == 'class':
                self.objects = self.driver.find_elements_by_class_name(self.ele_values[0])
                self.objects[self.child_nth]
            elif self.ele_type == 'access_id':
                self.object = self.driver.find_element_by_accessibility_id(self.ele_values[0])


            return ["OK","OK"]
        except:

            return ['NOK','Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno)]

    def hasNotObject(self, parameters):

        try:

            self.ele_values = parameters[4].split("|")
            self.ele_type = self.ele_values[1]
            self.child_nth = 0
            # value size check(wait time and class child_nth)
            if len(self.ele_values) == 3:
                self.child_nth = int(self.ele_values[2])
            #check ele type and fix method of ele existed each type
            if self.ele_type == 'id':
                self.object = self.driver.find_element_by_id(self.ele_values[0])
            elif self.ele_type == 'Xpath':
                self.object = self.driver.find_element_by_xpath(self.ele_values[0])
            elif self.ele_type == 'name':
                self.object = self.driver.find_element_by_android_uiautomator('new UiSelector().text("'+self.ele_values[0]+'")')
            elif self.ele_type == 'class':
                self.objects = self.driver.find_elements_by_class_name(self.ele_values[0])
                self.objects[self.child_nth]
            elif self.ele_type == 'access_id':
                self.object = self.driver.find_element_by_accessibility_id(self.ele_values[0])


            return ["NOK", 'Error: \"'+self.ele_values[0]+'\" exists']
        except:

            return ['OK', "OK"]

    def recordVideo(self, name, time, loop):

        for i in range(int(loop)):
            print("adb -s "+self.dict_init['uuid']+" shell screenrecord --time-limit "+time+" /sdcard/"+name+"_"+str(i+1)+".mp4")
            self.list_recordFiles.append(name+"_"+str(i+1)+".mp4")
            self.pipe = subprocess.Popen("adb -s "+self.dict_init['uuid']+" shell screenrecord --time-limit "+time+" /sdcard/"+name+"_"+str(i+1)+".mp4", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.res = self.pipe.communicate()
            self.list_subprocess.append(self.pipe)
            sleep(float(time))

        for item in self.list_recordFiles:
            print("adb -s "+self.dict_init['uuid']+" pull /sdcard/"+item+" "+self.record_path)
            self.pipe = subprocess.Popen("adb -s "+self.dict_init['uuid']+" pull /sdcard/"+item+" "+self.record_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.res = self.pipe.communicate()

    def check_file(self, path):
        self.flag = os.path.isfile(str(path))
        return self.flag

    def get_takeMilliTime(self, start_time):
        self.endTime = datetime.now()
        self.take_time = self.endTime - start_time
        self.elapsed = str(self.take_time.seconds)+"."+str(self.take_time.microseconds)
        return [self.elapsed, self.endTime]

    def get_imgObject(self, path, type):
        self.img_obj = None
        if int(type) == 1:
            self.img_obj = cv2.imread(path, cv2.IMREAD_COLOR)
        elif int(type) == 0:
            self.img_obj = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        elif int(type) == -1:
            self.img_obj = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        else:
            self.img_obj = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        return [self.img_obj, path]

    def get_screenshot_obj(self, file_name, type):
        self.img_obj = None
        self.driver.save_screenshot(self.screen_path + file_name +".png")
        self.img_obj = self.get_imgObject(self.screen_path + file_name +".png", type)
        return [self.img_obj[0], self.img_obj[1]]

    def detectImage(self, target_obj, screen_obj, out_flag, file_path):
        # 최대값 사용
        # cv.TM_CCOEFF, cv.TM_CCOEFF_NORMED, cv.TM_CCORR, cv.TM_CCORR_NORMED
        # 최소값 사용
        # cv.TM_SQDIFF, cv.TM_SQDIFF_NORMED
        # methods = ['cv.TM_CCOEFF', 'cv.TM_CCOEFF_NORMED', 'cv.TM_CCORR',
        #         'cv.TM_CCORR_NORMED', 'cv.TM_SQDIFF', 'cv.TM_SQDIFF_NORMED']
        self.screen_obj = screen_obj
        self.target_obj = target_obj

        self.w, self.h = self.target_obj.shape[::-1]

        self.method = eval('cv2.TM_CCORR_NORMED')
        self.res_img = cv2.matchTemplate(self.screen_obj, self.target_obj, self.method)
        self.min_val, self.max_val, self.min_loc, self.max_loc = cv2.minMaxLoc(self.res_img)

        self.top_left = self.max_loc
        self.bottom_right = (self.top_left[0] + self.w, self.top_left[1] + self.h)
        self.center = (self.top_left[0] + int(self.w/2), self.top_left[1] + int(self.h/2))

        if out_flag == "true":
            # self.color = (0, 0, 255)
            self.color = (255, 0, 0)
            self.img_tangle = cv2.rectangle(self.screen_obj, self.top_left, self.bottom_right, self.color, thickness=5)
            self.detectshotPath = file_path[:-4] + '-detect.png'
            cv2.imwrite(self.detectshotPath, self.img_tangle)
            return [self.max_val, self.center]
        else:
            return [self.max_val, self.center]

    def compareImage(self, target_obj, screen_obj, out_flag, file_path):

        self.screen_re = cv2.resize(screen_obj, (self.cv2_img_xSize, self.cv2_img_ySize)).astype(np.float32)
        self.target_re = cv2.resize(target_obj, (self.cv2_img_xSize, self.cv2_img_ySize)).astype(np.float32)

        # difference = cv2.subtract(image1, image2)
        self.difference = cv2.absdiff(self.screen_re, self.target_re)
        self.same_per = 100-round((self.difference != 0).sum()/50176*100, 2)
        # result = not np.any(difference)
        # result = np.all(difference)
        if self.rectangle_flag == "true":
            self.diff_path = file_path[:-4] + '-comparation.png'
            cv2.imwrite(self.diff_path, self.difference)
        return self.same_per

# image cv2 comparaion 완전 같은 이미지 비교
# import cv2
# import numpy as np
# original = cv2.imread("imaoriginal_golden_bridge.jpg")
# duplicate = cv2.imread("images/duplicate.jpg")
# if original.shape == duplicate.shape:
# print("The images have same size and channels")
# difference = cv2.subtract(original, duplicate)
# b, g, r = cv2.split(difference)
# if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
# print("The images are completely Equal")
# cv2.imshow("Original", original)
# cv2.imshow("Duplicate", duplicate)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# sift = cv2.xfeatures2d.SIFT_create()
# kp_1, desc_1 = sift.detectAndCompute(original, None)
# kp_2, desc_2 = sift.detectAndCompute(image_to_compare, None)
# index_params = dict(algorithm=0, trees=5)
# search_params = dict()
# flann = cv2.FlannBasedMatcher(index_params, search_params)
# matches = flann.knnMatch(desc_1, desc_2, k=2)

# good_points = []
# ratio = 0.6
# for m, n in matches:
#     if m.distance < ratio*n.distance:
#         good_points.append(m)
#         print(len(good_points))
# result = cv2.drawMatches(original, kp_1, image_to_compare, kp_2, good_points, None)

# number_keypoints = 0
# if len(kp_1) <= len(kp_2):
#     number_keypoints = len(kp_1)
# else:
#     number_keypoints = len(kp_2)
# print("Keypoints 1ST Image: " + str(len(kp_1)))
# print("Keypoints 2ND Image: " + str(len(kp_2)))
#
#
# print("GOOD Matches:", len(good_points))
# print("How good it's the match: ", len(good_points) / number_keypoints * 100, "%")


if __name__ == "__main__":
    pass
