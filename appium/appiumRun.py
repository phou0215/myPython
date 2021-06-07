import os
import sys
import signal
import pandas as pd
import numpy as np
import threading
import multiprocessing
import cv2

# from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtGui import QStandardItem
from http.client import responses

from appiumServer import Server
from appiumClient import Client
from appiumMethods import Method
from appiumReport import Report
from appiumDevices import Device
from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5 import QtCore
# import subprocess
# from uiautomator import Device

# from PyQt5.QtCore import *
# from PyQt5.QtCore import QApplication

# groupBox_list
# 	listWidget_devices
#   pushButton_coreset
#   pushButton_sereset

# groupBox_log
# 	plainTextEdit_log
#   label_status
#   pushButton_clearLog

# groupBox_controller
# 	groupBox_setting
# 		lineEdit_file
# 		lineEdit_delay
# 		lineEdit_loop
# 	groupBox_option
# 		checkBox_data
# 		checkBox_wifi
# 		checkBox_gps
# 		checkBox_blue
# 		checkBox_nfc
#       groupBox_bright
#           lcdNumber_bright
#           horizontalSlider_bright
#        pushButton_options
# 	groupBox_run
# 		pushButton_Srun
#       pushButton_Crun
# 		pushButton_cancel

form_class = uic.loadUiType("main_appium.ui")[0]
class MyWindow(QMainWindow, form_class):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.format = QtGui.QTextCharFormat()
        self.setWindowIcon(QtGui.QIcon('icon.png'))

        #init sub class
        self.server = None
        self.client = None
        self.device = None

        # each flag __init__
        self.started_Cflag = False
        self.started_Sflag = False
        self.started_Dflag = False

        self.data_flag = True
        self.wifi_flag = False
        self.gps_flag = False
        self.nfc_flag = False

        # each variables __init__
        self.inputFile_path = ""

        #server
        self.previous_se_index = 0
        self.buffer_se_size = 0
        #client
        self.previous_cl_index = 0
        self.buffer_cl_size = 0
        #device
        self.previous_de_index = 0
        self.buffer_de_size = 0


        self.serials = []
        self.delay = 0
        self.times = 1

        # self.df_config = None
        self.list_serverInfo = []
        self.cursor = self.plainTextEdit_log.textCursor()
        self.plainTextEdit_log.setReadOnly(True)

        # sub modules __init__
        self.device = Device()
        self.started_Dflag = True
        self.device.print_flag.connect(self.printTextDevice)
        self.device.end_flag.connect(self.endFlag)

        self.setDevices()
        ################################__function button and eventListener init__################################
        self.pushButton_coreset.clicked.connect(self.setDevices)
        self.pushButton_sereset.clicked.connect(self.resetSelect)
        self.pushButton_browser.clicked.connect(self.btn_openFile)
        self.listWidget_devices.itemClicked.connect(self.selectDevices)

        #function device log reset button
        self.pushButton_clearLog.clicked.connect(self.resetLog)

        #Options
        self.checkBox_data.setChecked(True)
        self.checkBox_data.clicked.connect(self.changeCheck)
        self.checkBox_wifi.clicked.connect(self.changeCheck)
        self.checkBox_gps.clicked.connect(self.changeCheck)
        self.checkBox_nfc.clicked.connect(self.changeCheck)
        self.horizontalSlider_bright.setValue(128)
        self.lcdNumber_bright.display(128)
        self.horizontalSlider_bright.valueChanged.connect(self.changeSlider)
        self.pushButton_options.clicked.connect(self.btn_Options)

        #function conroller button
        self.pushButton_Srun.clicked.connect(self.btn_Sstart)
        self.pushButton_Crun.clicked.connect(self.btn_Cstart)
        self.pushButton_cancel.clicked.connect(self.btn_closed)

        #background control
        self.pushButton_cancel.setStyleSheet("background-color:rgba(211,211,211,220);color:rgb(255,255,255);")


    def setDevices(self):
        self.serials = []
        self.list_devices = self.device.getDevicesSerial()
        # self.listItems = self.listWidget_devices.selectedItems()
        self.listWidget_devices.clearSelection()
        self.listWidget_devices.clear()
        for item in self.list_devices:
            self.listWidget_devices.addItem(item)

    def selectDevices(self):

        self.serials = []
        self.temp_list = self.listWidget_devices.selectedItems()
        for item in self.temp_list:
            self.serials.append(str(item.text()))

    def btn_openFile(self):

        openFrame = QFileDialog.getOpenFileName(self)
        # self.lineEdit_text.setText(openFrame[0])
        self.lineEdit_filepath.setText(openFrame[0])

    def resetSelect(self):
        self.listWidget_devices.clearSelection()
        self.serials = []

    def changeCheck(self):
        if self.checkBox_data.isChecked():
            self.data_flag = True
        else:
            self.data_flag = False

        if self.checkBox_wifi.isChecked():
            self.wifi_flag = True
        else:
            self.wifi_flag = False

        if self.checkBox_gps.isChecked():
            self.gps_flag = True
        else:
            self.gps_flag = False

        if self.checkBox_nfc.isChecked():
            self.nfc_flag = True
        else:
            self.nfc_flag = False

    def changeSlider(self):
        self.size = self.horizontalSlider_bright.value()
        self.lcdNumber_bright.display(self.size)

    def set_info(self):
        for idx, item in enumerate(self.device.list_servers):
            if self.device.list_devices[idx] in self.serials:
                self.list_serverInfo.append((item, self.device.list_ports[idx], self.device.list_bootstraps[idx], self.device.list_devices[idx]))

    def btn_Sstart(self):

        #Check about enabled_flag and if enabled_flag is
        self.list_serverInfo = []
        self.set_delay()
        self.set_times()
        self.inputFile_path = self.lineEdit_filepath.text().replace(" ","")
        ##############  Check controller option values  ##############
        self.flag = self.check_values(self.inputFile_path, self.delay, self.times)
        if not self.flag:
            return
        ##############  Check controller option values  ##############
        self.flag = self.device.parse_data(self.inputFile_path)
        if not self.flag:
            return
        ##############  Check mandatory value exist in config_data  ##############
        self.flag = self.check_deviceFlag(self.device.check_config())
        if not self.flag:
            return
        ##############  Check selected serial in config_data  ##############
        self.flag = self.check_uuid()
        if not self.flag:
            return
        ##############  Check action serial sheet in config file ##############
        self.flag = self.check_sheet()
        if not self.flag:
            return

        self.set_info()
        self.server = Server(self.list_serverInfo)
        self.server.print_flag.connect(self.printTextServer)
        self.server.complete_flag.connect(self.completeServer)
        self.server.end_flag.connect(self.endFlag)
        self.server.start()
        self.controlAction_server()

    def btn_Cstart(self):
        if self.started_Sflag:
            #Client execute
            self.device.setSerial(self.serials)
            self.device.generate_data()
            self.device.generate_data_act(self.inputFile_path)
            self.client = Client(self.device.dict_final, self.device.dict_event, self.delay, self.times)
            self.client.print_flag.connect(self.printTextClient)
            self.client.end_flag.connect(self.endFlag)
            self.client.start()
            self.started_Cflag = True
            self.controlAction(False, True)
        else:
            self.showMessageBox('You must start Server first! Please click \"Server run\".')
            return

    def btn_closed(self):

        if not self.started_Cflag:
            buttonReplay = QMessageBox.question(self, "message", "Do you want Appium Server process quit?", QMessageBox.Yes, QMessageBox.Cancel)
            if buttonReplay == QMessageBox.Yes:
                self.endFlag()
                self.controlAction(True, False)
                self.resetSelect()
            else:
                return
        else:
            buttonReplay = QMessageBox.question(self, 'message', "Do you want Appium All process quit?", QMessageBox.Yes, QMessageBox.Cancel)
            if buttonReplay == QMessageBox.Yes:
                self.endFlag()
                self.controlAction(True, False)
                self.resetSelect()
            else:
                return

    def btn_Options(self):
        if len(self.serials) == 0:
            self.showMessageBox('Please select device first!')
        else:
            self.Bvalaue = self.horizontalSlider_bright.value()
            self.device.setOptions(self.serials, [self.data_flag, self.wifi_flag, self.gps_flag, self.nfc_flag], self.Bvalaue)

    def set_delay(self):
        self.delay = self.lineEdit_delay.text().replace(" ","")

    def set_times(self):
        self.times = self.lineEdit_loop.text().replace(" ","")

    def resetLog(self):

        self.plainTextEdit_log.clear()

    def check_values(self, path, delay, times):
        # Check File path validation
        self.iNfileFlag = os.path.isfile(path)
        if path is None or path is "":
            self.showMessageBox("Please selcet \"Setting File Path\" using \"Browser button\".")
            return False
        elif not self.iNfileFlag:
            self.showMessageBox(" Selected file was not existed. Please select file again")
            return False
        # Check delay time value validation
        if not self.check_int(delay):
            self.showMessageBox("Please input only number in \"Delay Time\"")
            return False
        else:
            if delay is "" or delay is None:
                self.delay = 0
            else:
                self.delay = int(delay)
        # Check Repeat times value validation
        if not self.check_int(times):
            self.showMessageBox("Please input only number in \"Repeat Time\"")
            return False
        else:
            if times is "" or times is None:
                self.times = 1
            else:
                self.times = int(times)

        return True

    def check_deviceFlag(self, list_status):
        if not list_status[0]:
            if list_status[1] is 'diff':
                self.showMessageBox('Mandatory values counts must not be same Please Check again')
                return False
            elif list_status[1] is 'Unexpected':
                self.showMessageBox('Unexpected Error is occurred')
                return False
            elif list_status[1] is 'duplicate':
                self.showMessageBox('Duplicated \"uuid\" in config_data file')
                return False
            else:
                self.showMessageBox(list_status[1]+'" mandatory value format error! Please Check again')
                return False
        return True

    def check_uuid(self):
        if len(self.list_devices) is 0:
            self.showMessageBox("Please check connect device or debug mode!")
            return False
        elif len(self.serials) is 0 :
            self.showMessageBox("Please select target serials on list!")
            return False
        else:
            for item in self.serials:
                if item not in self.device.list_devices:
                    self.showMessageBox('Selected serial "'+item+'" is not in config data')
                    return False
        return True

    def check_sheet(self):
        for item in self.serials:
            if item not in self.device.list_sheets:
                self.showMessageBox('Selected serial "'+item+'" action sheet is not in config file')
                return False
        return True

    def showMessageBox(self, message):

        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Critical)
        self.msg.setWindowTitle("경고")
        self.msg.setText(message)
        self.msg.setStandardButtons(QMessageBox.Ok)
        self.msg.show()

    def check_int(self, value):

        try:
            if value is "" or value is None:
                return True
            else:
                self.value_converted = int(value)
                return True
        except:
            return False

    def check_float(self, value):

        try:
            if value is "" or value is None:
                return True
            else:
                self.value_converted = float(value)
                return True
        except:
            return False

    def resetStyle(self):
        #button elements
        self.pushButton_sereset.setStyleSheet('')
        self.pushButton_coreset.setStyleSheet('')
        self.pushButton_Srun.setStyleSheet('')
        self.pushButton_Crun.setStyleSheet('')
        self.pushButton_cancel.setStyleSheet('')
        self.pushButton_browser.setStyleSheet('')

        #input field elements
        self.lineEdit_filepath.setStyleSheet('')
        self.lineEdit_delay.setStyleSheet('')
        self.lineEdit_loop.setStyleSheet('')

    def controlAction(self, flag, flag2):

        self.resetStyle()
        if flag and not flag2:
            #button elements
            self.pushButton_sereset.setStyleSheet("background-color:rgba(95,154,135,220);color:rgb(255,255,255);")
            self.pushButton_coreset.setStyleSheet("background-color:rgba(95,154,135,220);color:rgb(255,255,255);")
            self.pushButton_Srun.setStyleSheet("background-color:rgba(197,255,201,220);color:rgb(255,255,255);")
            self.pushButton_browser.setStyleSheet("background-color:rgba(255,177,20,220);color:rgb(255,255,255);")
            self.pushButton_cancel.setStyleSheet("background-color:rgba(211,211,211,220);color:rgb(255,255,255);")
            self.pushButton_Crun.setStyleSheet("background-color:rgba(157,205,255,220);color:rgb(255,255,255);")

            #input field elements
            self.lineEdit_filepath.setStyleSheet("background-color:rgb(255,255,255);color:rgb(3,3,3);")
            self.lineEdit_delay.setStyleSheet("background-color:rgb(255,255,255);color:rgb(3,3,3);")
            self.lineEdit_loop.setStyleSheet("background-color:rgb(255,255,255);color:rgb(3,3,3);")

        elif not flag and flag2:
            #button elements
            self.pushButton_sereset.setStyleSheet("background-color:rgba(211,211,211,220);color:rgb(255,255,255);")
            self.pushButton_coreset.setStyleSheet("background-color:rgba(211,211,211,220);color:rgb(255,255,255);")
            self.pushButton_Srun.setStyleSheet("background-color:rgba(211,211,211,220);color:rgb(255,255,255);")
            self.pushButton_Crun.setStyleSheet("background-color:rgba(211,211,211,220);color:rgb(255,255,255);")
            self.pushButton_browser.setStyleSheet("background-color: rgba(211,211,211,220);color:rgb(255,255,255);")
            self.pushButton_cancel.setStyleSheet("background-color:rgba(255,152,143,220);color:rgb(255,255,255);")

            #input field elements
            self.lineEdit_filepath.setStyleSheet("background-color:rgb(211,211,211);color:rgb(3,3,3);")
            self.lineEdit_delay.setStyleSheet("background-color:rgb(211,211,211);color:rgb(3,3,3);")
            self.lineEdit_loop.setStyleSheet("background-color:rgb(211,211,211);color:rgb(3,3,3);")

        self.groupBox_list.setEnabled(flag)
        self.pushButton_browser.setEnabled(flag)
        self.groupBox_setting.setEnabled(flag)
        self.groupBox_option.setEnabled(flag)
        self.pushButton_Srun.setEnabled(flag)
        self.pushButton_Crun.setEnabled(flag)
        self.pushButton_cancel.setEnabled(flag2)

    def controlAction_server(self):

        #button elements
        self.resetStyle()
        self.pushButton_sereset.setStyleSheet("background-color:rgba(211,211,211,220);color:rgb(255,255,255);")
        self.pushButton_coreset.setStyleSheet("background-color:rgba(211,211,211,220);color:rgb(255,255,255);")
        self.pushButton_Srun.setStyleSheet("background-color:rgba(211,211,211,220);color:rgb(255,255,255);")
        self.pushButton_Crun.setStyleSheet("background-color:rgba(157,205,255,220);color:rgb(255,255,255);")
        self.pushButton_browser.setStyleSheet("background-color: rgba(211,211,211,220);color:rgb(255,255,255);")
        self.pushButton_cancel.setStyleSheet("background-color:rgba(255,152,143,220);color:rgb(255,255,255);")
        #input field elements
        self.lineEdit_filepath.setStyleSheet("background-color:rgb(211,211,211);color:rgb(3,3,3);")
        self.lineEdit_delay.setStyleSheet("background-color:rgb(211,211,211);color:rgb(3,3,3);")
        self.lineEdit_loop.setStyleSheet("background-color:rgb(211,211,211);color:rgb(3,3,3);")

        self.groupBox_list.setEnabled(False)
        self.pushButton_browser.setEnabled(False)
        self.groupBox_setting.setEnabled(False)
        self.pushButton_Srun.setEnabled(False)
        self.pushButton_Crun.setEnabled(True)
        self.pushButton_cancel.setEnabled(True)

    #####################################__Appium Server slots__#####################################

    @pyqtSlot()
    def printTextServer(self):

        if self.previous_se_index is not 0:
            self.temp_size = len(self.server.buffer_text)
            if self.previous_se_index is not self.temp_size:
                self.temp_list = self.server.buffer_text[self.previous_se_index:]
                for item in self.temp_list:
                    self.plainTextEdit_log.appendPlainText(item)
                self.previous_se_index = self.temp_size
        else:
            self.temp_list = self.server.buffer_text
            for item in self.temp_list:
                self.plainTextEdit_log.appendPlainText(item)
            self.previous_se_index = len(self.temp_list)


    @pyqtSlot()
    def endFlag(self):

        self.started_dflag= False
        self.started_Sflag= False
        self.device.stop()
        self.server.stop()
        if self.started_Cflag:
            self.started_Cflag= False
            self.client.stop()
        self.resetSelect()
        self.controlAction(True, False)

    @pyqtSlot()
    def completeServer(self):

        self.started_Sflag = True

    #####################################__Appium Client slots__#####################################

    @pyqtSlot()
    def printTextClient(self):

        if self.previous_cl_index is not 0:
            self.temp_size = len(self.client.buffer_text)
            if self.previous_cl_index is not self.temp_size:
                self.temp_list = self.client.buffer_text[self.previous_cl_index:]
                for item in self.temp_list:
                    self.plainTextEdit_log.appendPlainText(item)
                self.previous_cl_index = self.temp_size
        else:
            self.temp_list = self.client.buffer_text
            for item in self.temp_list:
                self.plainTextEdit_log.appendPlainText(item)
            self.previous_cl_index = len(self.temp_list)

###################################__Device slot__###################################

    @pyqtSlot()
    def printTextDevice(self):

        if self.previous_de_index is not 0:
            self.temp_size = len(self.device.buffer_text)
            if self.previous_de_index is not self.temp_size:
                self.temp_list = self.device.buffer_text[self.previous_de_index:]
                for item in self.temp_list:
                    self.plainTextEdit_log.appendPlainText(item)
                self.previous_de_index = self.temp_size
        else:
            self.temp_list = self.device.buffer_text
            for item in self.temp_list:
                self.plainTextEdit_log.appendPlainText(item)
            self.previous_de_index = len(self.temp_list)


if __name__ == "__main__":

    app = QApplication(sys.argv)
    myWindow = MyWindow()
    multiprocessing.freeze_support()
    myWindow.show()
    sys.exit(app.exec_())
