import os
import sys
import re
import pandas as pd
import numpy as np
import subprocess
# import shlex
import re
from time import sleep
from datetime import date, time, datetime
from os.path import expanduser
from PyQt5.QtCore import QThread, pyqtSignal


class Device(QThread):

    print_flag = pyqtSignal()
    end_flag = pyqtSignal()
    buffer_text = []

    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.list_return = []
        self.getDeives = "adb devices"
        self.error_text = ""
        self.p_devices = None
        self.is_terminated = False
        self.list_serial = []

        # Excel Config File __init__
        self.list_keys = ['address', 'port', 'bootstrap', 'uuid', 'platformName', 'deviceName', 'deviceManu', 'platformVersion', 'appPackage', 'appActivity', 'app', 'directStart']
        self.list_keys_act = ['TestCase', 'Event_API', 'Ele_Type', 'Ele_Value', 'Assert_API', 'Assert_Type', 'Assert_Value', 'Force_Stop']
        self.dict_mandatory = {}
        self.dict_final = {}
        self.dict_event = {}
        self.list_sheets = []
        self.list_tot = []
        self.DEFAULT_TIMES = 0.2

        #config mandatory columns
        self.list_servers = []
        self.list_ports = []
        self.list_bootstraps = []
        self.list_devices = []
        self.list_names = []
        self.list_manus = []
        self.list_platforms = []
        self.list_versions = []
        self.list_packageNames = []
        self.list_activities = []
        self.list_directStart = []

        #config optional column
        self.list_files = []


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

    def getDevicesSerial(self):
        try:
            self.list_return = []
            # d = Device("5210f864c0e21415")
            self.p_devices = subprocess.Popen(self.getDeives, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.outText = self.p_devices.communicate()
            self.outText = str(self.outText[0])
            self.outText = self.outText.replace("List of devices attached", "")

            if 'successfully' in self.outText:
                self.outText = re.sub(r"\* daemon not running; starting now at tcp:[0-9]{1,4}","", self.outText)
                self.outText = re.sub(r"\* daemon started successfully","", self.outText)

            self.outText = self.outText.replace("\\r\\n", "", 1)
            self.outText = self.outText.replace("device", "")
            self.outText = self.outText.replace("\\t", "")
            self.outText = self.outText.replace("'","")
            self.temp_list = self.outText.split("\\r\\n")

            for i in range(len(self.temp_list)):
                if len(self.temp_list) == 0:
                    break
                else:
                    self.temp_text = self.temp_list[i].replace("\\r\\n", "")
                    if i == 0:
                        self.temp_text = self.temp_list[i][1:]

                    if "unauthorized" in self.temp_text:
                        continue
                    elif len(self.temp_text) > 6:
                        self.temp_text = self.temp_text.replace("\\p{Z}", "")
                        self.temp_text = self.temp_text.replace("device", "")
                        self.temp_text = self.temp_text.replace("\\t", "")
                        self.list_return.append(self.temp_text)

            return self.list_return
        except:
            self.setPrintText('/s Error: {}. {}, line: {} /e'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno))
            self.setEnd()

    def parse_data(self, file_path):
        try:
            self.df = pd.read_excel(file_path, None)
            self.list_sheets = self.df.keys()
            if 'Config_Data' not in self.list_sheets:
                self.setPrintText('/s There is no "Config_Data" sheet in input Excel File Please Check again /e')
                self.setEnd()
            else:
                #################__mandatory values__#################
                self.df_data = pd.read_excel(file_path, sheet_name="Config_Data")
                self.list_servers = self.df_data['SERVER_ADDRESS'].tolist()
                self.list_ports = self.df_data['PORT'].tolist()
                self.list_bootstraps = self.df_data['BOOTSTRAP'].tolist()
                self.list_devices = self.df_data['UUID'].tolist()
                self.list_names = self.df_data['DEVICE_NAME'].tolist()
                self.list_manus = self.df_data['DEVICE_MANU'].tolist()
                self.list_platforms = self.df_data['PLATFORM'].tolist()
                self.list_versions = self.df_data['VERSION'].tolist()
                self.list_packageNames = self.df_data['PACK_NAME'].tolist()
                self.list_activities = self.df_data['MAIN_ACT'].tolist()
                #################__optional values__#################
                self.list_files = self.df_data['FILE_NAME'].tolist()
                self.list_directStart = self.df_data['DIRECT_START'].tolist()

                #################__mandatory value format check__#################
                self.list_servers = [str(X) for X in self.list_servers if str(X) != 'nan' or str(X) != '']
                self.list_ports = [str(X) for X in self.list_ports if str(X) != 'nan' or str(X) != '']
                self.list_bootstraps = [str(X) for X in self.list_bootstraps if str(X) != 'nan' or str(X) != '']
                self.list_devices = [str(X) for X in self.list_devices if str(X) != 'nan' or str(X) != '']
                self.list_names = [str(X) for X in self.list_names if str(X) != 'nan' or str(X) != '']
                self.list_manus = [str(X) for X in self.list_manus if str(X) != 'nan' or str(X) != '']
                self.list_platforms = [str(X) for X in self.list_platforms if str(X) != 'nan' or str(X) !='']
                self.list_versions = [str(X) for X in self.list_versions if str(X) != 'nan' or str(X) != '']
                self.list_packageNames = [str(X) for X in self.list_packageNames if str(X) != 'nan' or str(X) != '']
                self.list_activities = [str(X) for X in self.list_activities if str(X) != 'nan' or str(X) != '']
                #################__optional value format check__#################
                self.list_files = [str(X) for X in self.list_files]
                self.list_directStart = [str(X) for X in self.list_directStart]
                self.list_tot = [self.list_servers, self.list_ports, self.list_bootstraps, self.list_devices, self.list_platforms, self.list_names, self.list_manus,\
                self.list_versions, self.list_packageNames, self.list_activities, self.list_files, self.list_directStart]
                return True
        except:
            self.setPrintText('/s Error: {}. {}, line: {} /e'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno))
            self.setEnd()

    def setSerial(self, serials):
        self.list_serial = serials

    def setOptions(self, serials, list_flag, value_brightness):
        for item in serials:
            self.setBrightness(item, value_brightness)
            self.setCell(item, list_flag[0])
            self.setWifi(item, list_flag[1])
            self.setGps(item, list_flag[2])
            self.setNfc(item, list_flag[3])

    def stop(self):

        self.setPrintText('/s Device Class is shutting down../e')
        sleep(1.8)
        self.is_terminated = True
        self.terminate()

    def setBrightness(self, uuid, value):

        self.brightSetMode = "adb -s "+uuid+" shell settings put system screen_brightness_mode 0"
        self.brightSetValue = "adb -s "+uuid+" shell settings put system screen_brightness "
        # self.brightSetBack = "adb -s "+uuid+" shell settings put system screen_brightness_mode 1"
        # self.brightGetCurrent = "adb -s "+uuid+" shell settings get system screen_brightness"
        self.back = "adb -s "+uuid+" shell input keyevent 4"
        self.p_devices = subprocess.Popen(self.brightSetMode, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        sleep(self.DEFAULT_TIMES)
        self.p_devices = subprocess.Popen(self.brightSetValue+str(value), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        sleep(self.DEFAULT_TIMES)
        self.p_devices = subprocess.Popen(self.back, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def setGps(self, uuid, flag):

        self.gpsOn = "adb -s "+uuid+" shell settings put secure location_providers_allowed +gps"
        self.gpsOff = "adb -s "+uuid+" shell settings put secure location_providers_allowed -gps"
        self.gpsNetOn = "adb -s "+uuid+" shell settings put secure location_providers_allowed +network"
        self.gpsNetOff = "adb -s "+uuid+" shell settings put  secure location_providers_allowed -network"
        self.gpsGetCurrent = "adb -s "+uuid+" shell settings get secure location_providers_allowed"
        self.back = "adb -s "+uuid+" shell input keyevent 4"
        if flag:
            self.p_devices = subprocess.Popen(self.gpsNetOn, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            sleep(self.DEFAULT_TIMES)
            self.p_devices = subprocess.Popen(self.gpsOn, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            sleep(self.DEFAULT_TIMES)
            self.p_devices = subprocess.Popen(self.back, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            # self.p_devices = subprocess.Popen(self.gpsGetCurrent, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        else:
            self.p_devices = subprocess.Popen(self.gpsNetOff, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            sleep(self.DEFAULT_TIMES)
            self.p_devices = subprocess.Popen(self.gpsOff, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            sleep(self.DEFAULT_TIMES)
            self.p_devices = subprocess.Popen(self.back, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def setWifi(self, uuid, flag):

        self.wifiOn = "adb -s "+uuid+" shell svc wifi enable"
        self.wifiOff = "adb -s "+uuid+" shell svc wifi disable"
        self.back = "adb -s "+uuid+" shell input keyevent 4"
        if flag:
            self.p_devices = subprocess.Popen(self.wifiOn, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            sleep(self.DEFAULT_TIMES)
            self.p_devices = subprocess.Popen(self.back, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        else:
            self.p_devices = subprocess.Popen(self.wifiOff, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            sleep(self.DEFAULT_TIMES)
            self.p_devices = subprocess.Popen(self.back, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def setCell(self, uuid, flag):

        self.cellOn = "adb -s "+uuid+" shell svc data enable"
        self.cellOff = "adb -s "+uuid+" shell svc data disable"
        self.back = "adb -s "+uuid+" shell input keyevent 4"
        if flag:
            self.p_devices = subprocess.Popen(self.cellOn, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            sleep(self.DEFAULT_TIMES)
            self.p_devices = subprocess.Popen(self.back, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        else:
            self.p_devices = subprocess.Popen(self.cellOff, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            sleep(self.DEFAULT_TIMES)
            self.p_devices = subprocess.Popen(self.back, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def setNfc(self, uuid, flag):

        self.nfcOn = "adb -s "+uuid+" shell svc nfc enable"
        self.nfcOff = "adb -s "+uuid+" shell svc nfc disable"
        self.back = "adb -s "+uuid+" shell input keyevent 4"
        if flag:
            self.p_devices = subprocess.Popen(self.nfcOn, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            sleep(self.DEFAULT_TIMES)
            self.p_devices = subprocess.Popen(self.back, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        else:
            self.p_devices = subprocess.Popen(self.nfcOff, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            sleep(self.DEFAULT_TIMES)
            self.p_devices = subprocess.Popen(self.back, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def generate_data(self):

        self.dict_final = {}
        try:
            for uuid in self.list_serial:
                self.dict_values = {}
                if uuid not in self.list_devices:
                    self.setPrintText('/s Device '+uuid+' is not in config data uuid /e')
                    self.setEnd()
                    break
                else:
                    self.idx = self.list_devices.index(uuid)
                    for idx2, value in enumerate(self.list_keys):
                        self.temp_value = self.list_tot[idx2][self.idx]
                        if idx2 is 10:
                            if str(self.temp_value) is 'nan' or str(self.temp_value) is '':
                                self.temp_value = 'None'
                        if idx2 is 11:
                            if str(self.temp_value) is 'nan' or str(self.temp_value) is '' or str(self.temp_value.lower()) != 'yes':
                                self.temp_value = 'NO'
                        self.dict_values[value] = self.temp_value
                    self.dict_final[uuid] = self.dict_values
            self.setPrintText('/s Appium config server data is ready /e')
        except:
            self.setPrintText('/s Error: {}. {}, line: {} /e'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno))
            self.setEnd()

    def generate_data_act(self, file_path):

        self.dict_event = {}
        for item in self.list_serial:
            if item not in self.list_sheets:
                self.setPrintText('/s Device '+item+' event action sheet Error! please check event action sheet /e')
                self.setEnd()
                break
            else:
                self.dict_temp = {}
                self.df_data = pd.read_excel(file_path, sheet_name=item)
                self.list_item1 = self.df_data['TestCase'].tolist()
                self.list_item2 = self.df_data['Event_API'].tolist()
                self.list_item3 = self.df_data['Ele_Type'].tolist()
                self.list_item4 = self.df_data['Ele_Value'].tolist()
                self.list_item5 = self.df_data['Assert_API'].tolist()
                self.list_item6 = self.df_data['Assert_Type'].tolist()
                self.list_item7 = self.df_data['Assert_Value'].tolist()
                self.list_item8 = self.df_data['Force_Stop'].tolist()

                self.list_temp = [self.list_item1, self.list_item2, self.list_item3, self.list_item4, self.list_item5, self.list_item6, self.list_item7, self.list_item8]
                for idx, key in enumerate(self.list_keys_act):
                    self.dict_temp[key] = self.list_temp[idx]
                # self.dict_event[item] = self.dict_temp
                self.flag = self.check_config_act(self.dict_temp)
                if self.flag:
                    self.dict_event[item] = self.dict_temp
                    self.setPrintText('/s Appium action client data is ready /e')
                else:
                    self.setPrintText('/s Device '+item+' mandatory value is empty! Please check action sheet /e')
                    self.setEnd()
                    break

    def check_config_act(self, dict_data):
        try:
            for key in dict_data:
                if key != 'Assert_Type' and key != 'Assert_Value' and key != 'Ele_Value' and key != 'Assert_API':
                    for item in dict_data[key]:
                        if item is np.nan or item is '':
                            return False
                        else:
                            pass
                else:
                    pass
            return True
        except:
            return False

    def check_config(self):
        try:
            self.num = 0
            self.p_server = re.compile("^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
            self.p_port = re.compile("^[0-9]+$")
            self.dict_mandatory = {'server':self.list_servers, 'port':self.list_ports, 'bootstrap':self.list_bootstraps, 'uuid':self.list_devices , 'platformName':self.list_platforms,\
            'name': self.list_names, 'manu': self.list_manus, 'packageName':self.list_packageNames, 'activity':self.list_activities, 'version':self.list_versions}

            for idx, key in enumerate(self.dict_mandatory):
                if idx is 0:
                    self.num = len(self.dict_mandatory[key])
                    pass
                else:
                    if self.num is not len(self.dict_mandatory[key]):
                        return [False, 'diff']
                    else:
                        pass

            self.list_temp = []
            for item in self.list_devices:
                if item not in self.list_temp:
                    self.list_temp.append(item)
                    pass
                else:
                    return [False, 'duplicate']


            for idx, item in enumerate([self.list_servers , self.list_ports]):
                if idx is 0:
                    for item2 in item:
                            if len(self.p_server.findall(item2)) is 0:
                                return [False, 'server_address']
                            else:
                                pass
                else:
                    for item2 in item:
                            if len(self.p_port.findall(item2)) is 0:
                                return [False, 'port']
                            else:
                                pass
            return [True, 'good']
        except:
            return [False, 'Unexpected']


if __name__ == "__main__":

    device = Device()
    list = device.getDevicesSerial()
    flag = device.parse_data('C:/Users/TestEnC/Desktop/APPIUM_TEST/config.xlsx')
    print(list)
    if flag:
        device.setSerial(['5210f864c0e21415'])
        device.generate_data()
        print(device.dict_final)
        device.generate_data_act('C:/Users/TestEnC/Desktop/APPIUM_TEST/config.xlsx')
        print(device.dict_event)
    # sample of dict_final



# {'LGMX600S1f73c4d8': {'address': '127.0.0.1', 'port': '4725', 'uuid': 'LGMX600S1f73c4d8', 'platformName': 'Android', 'deviceN
#     ame': 'LG Q6', 'deviceManu': 'LG', 'platformVersion': '8.1.0', 'appPackage': 'com.android.settings', 'appActivity': '.Setting
#     s', 'app': 'None'}, '5210f864c0e21415': {'address': '127.0.0.1', 'port': '4723', 'uuid': '5210f864c0e21415', 'platformName':
#     'Android', 'deviceName': 'Galaxy S8', 'deviceManu': 'SAMSUNG', 'platformVersion': '8.0.0', 'appPackage': 'com.android.setting
#     s', 'appActivity': '.Settings', 'app': 'None'}}


# {'5210f864c0e21415': {'event': ['click'], 'ele_type': ['ID'], 'ele_value': ['com.google.android.music:id/play_pause_header'],
#  'assert': ['None'], 'assert_type': [None], 'assert_value': [None]}}
