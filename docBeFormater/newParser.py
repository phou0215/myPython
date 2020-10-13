import os
import sys
import json
import pkg_resources.py2_warn
# from PyQt5.QtWidgets import *
from os.path import expanduser
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSlot
from newModule import Formater
from newConnectDB import connMyDb
from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5 import QtCore

# from PyQt5.QtCore import *
# from PyQt5.QtCore import QApplication

form_class = uic.loadUiType("main_window5.ui")[0]

# app = None
#Layout => Centralwidget
#QScrollArea = > scrollArea

# tabWidget(analysis tab)

# 	groupBox_2(Viewer)

# 		groupBox
# 			pushButton_clear(button_log clear)
# 			label_count(label_data count)
# 			plainTextEdit_print(plaintext_log display)


# 	groupBox_1(Controller)

# 		groupBox_9(input data)
# 			textEdit_browser(input data file path)
# 			pushButton_browser(input file saerch btn)


# 		groupBox_17(Length Edit)
# 			checkBox_enabled(length adjusting use)
# 			lineEdit_limit(limit adjusting input lineEdit)
# 			lineEdit_mini(minimum adjusting input lineEdit)


# 		groupBox_9(Device Mapping)
# 			radioButton_OpOn(Excel option on optionBtn)
# 			radioButton_OpOff(Excel option off optionBtn)

# 		groupBox_18(model select)
# 			radioButton_f1(Bee optionBtn)
# 			radioButton_f2(Dong optionBtn)

# 		groupBox_6(Control Button)
# 			pushButton_start(start analysis)
# 			pushButton_cancel(abort analysis)
#
# 		progressBar(analysis progress)

# connect tab

# 	groupBox_3(Viewer)

# 		groupBox
# 			pushButton_clear_2(button_log clear)
# 			label_count_2(label_data count)
# 			plainTextEdit_print_2(plaintext_log display)

# 	groupBox_10(Controller)

# 		groupBox_14(update data)
# 			textEdit_browser_2(update Data data file path)
# 			pushButton_browser_2(update file search btn)

# 		groupBox_11(Db Host info)
# 			checkBox_enabled_2(save host info)
# 			lineEdit_address(host ip address)
# 			lineEdit_port(host port)
# 			lineEdit_id(host account id)
# 			lineEdit_pw(host account pw)
# 			lineEdit_db(host db name)
# 			lineEdit_table(host table name)

# 		groupBox_12(command Type)
# 			radioButton_upload(updte data insert to db optionBtn)
# 			radioButton_drop(updte data drop to db optionBtn)

# 		groupBox_13(Control Button)
# 			pushButton_commit(start commit)

class MyWindow(QMainWindow, form_class):

    def __init__(self):

        super().__init__()
        self.setupUi(self)
        self.home = expanduser('~')

        #####################################__VOC Parser class__#####################################
        self.started_flag = "n"
        self.search_flag = "n"
        self.op_flag = True
        self.mode_flag = "f1"
        self.moduler = None
        self.inputFile_path = ""
        self.file_size = 1

        self.progressValue = 0
        self.tabWidget.setCurrentIndex(0)
        self.posList = []
        #text_diplay set Type
        self.plainTextEdit_print.setReadOnly(True)
        #init progressBar Value
        self.progressBar.setValue(0)

        self.format = QtGui.QTextCharFormat()
        self.setWindowIcon(QtGui.QIcon('icon.png'))

        #####################################__DB Commit class__#####################################
        # settings
        self.committed_flag = "n"
        self.acSave_flag = "y"
        self.updateFile_path = ""
        self.connector = None
        #print text
        self.plainTextEdit_print_2.setReadOnly(True)
        self.cursor_connect = self.plainTextEdit_print_2.textCursor()
        #host info
        self.host_ip = ""
        self.host_port = ""
        self.host_id = ""
        self.host_pw = ""
        self.host_dbName = ""
        self.host_tableName = ""
        self.update_mode = "upload"

        #####################################__VOC Parser Events__#####################################
        self.pushButton_browser.clicked.connect(self.btn_openFiles)
        self.pushButton_start.clicked.connect(self.btn_start)
        self.pushButton_cancel.clicked.connect(self.btn_closed)
        self.pushButton_cancel.setEnabled(False)

        #Device Mapping  radio button event
        self.radioButton_OpOn.setChecked(True)
        self.radioButton_OpOn.clicked.connect(self.radio_option1)
        self.radioButton_OpOff.clicked.connect(self.radio_option1)

        #Parser model select radio button event
        self.radioButton_f1.setChecked(True)
        self.radioButton_f1.clicked.connect(self.radio_option2)
        self.radioButton_f2.clicked.connect(self.radio_option2)

        #Clear button
        self.pushButton_clear.clicked.connect(self.btn_clear)

        #####################################__DB Commit Events__#####################################
        self.pushButton_commit.clicked.connect(self.btn_start_conn)
        self.pushButton_stop.clicked.connect(self.btn_stop)
        # radioButton_upload defualt checkbox
        self.radioButton_upload.setChecked(True)
        # Stop button defualt False Enable
        self.pushButton_stop.setEnabled(False)
        #checkbox "DB Host Account info save"
        #Set checkBox_enabled_2 default true
        self.checkBox_enabled_2.setChecked(True)
        self.checkBox_enabled_2.stateChanged.connect(self.set_hostflag)
        #checkbox "DB Host Account info load"
        self.checkBox_enabled_3.stateChanged.connect(self.get_hostInfo)
        #Open update files
        self.pushButton_browser_2.clicked.connect(self.btn_openFile_conn)
        #De  radio button event
        self.radioButton_upload.clicked.connect(self.radio_option_conn)
        self.radioButton_drop.clicked.connect(self.radio_option_conn)
        #Clear button
        self.pushButton_clear_2.clicked.connect(self.btn_clear_conn)

    #####################################__VOC Parser slots__#####################################
    @pyqtSlot(str)
    def printText(self, item):
        self.plainTextEdit_print.appendPlainText(item)

    @pyqtSlot()
    def countText(self):

        self.label_count.clear()
        self.label_count.setText(str(self.moduler.currentRow)+" / "+str(self.moduler.totalRows))

    @pyqtSlot()
    def endFlag(self):

        self.started_flag = "n"
        self.moduler.stop()
        self.tabWidget.setTabEnabled(0, True)
        self.tabWidget.setTabEnabled(1, True)
        self.controlAction(True, False)
        self.progressValue = 0
        self.progressBar.setValue(0)

    @pyqtSlot()
    def progressFlag(self):
        if self.mode_flag == 'f1':
            self.progressValue = self.progressValue + int(100/12)
            self.progressBar.setValue(self.progressValue)
        else:
            self.progressValue = self.progressValue + int(100/self.file_size)
            self.progressBar.setValue(self.progressValue)

    #####################################__DB Commit slots__#####################################

    @pyqtSlot(str)
    def printTextConn(self, item):
        self.plainTextEdit_print_2.appendPlainText(item)

    @pyqtSlot()
    def endFlagConn(self):

        self.committed_flag = "n"
        self.connector.stop()
        self.tabWidget.setTabEnabled(0, True)
        self.tabWidget.setTabEnabled(1, True)
        self.controlAction_conn(True, False)

    @pyqtSlot()
    def countTextConn(self):

        self.label_count_2.clear()
        self.label_count_2.setText(str(self.connector.currentRow)+" / "+str(self.connector.totalRows))


    #####################################__VOC Parser method__#####################################

    def btn_openFile(self):

        openFrame = QFileDialog.getOpenFileName(self)
        # self.lineEdit_text.setText(openFrame[0])
        self.textEdit_browser.setText(openFrame[0])

    def btn_openFiles(self):

        tuple_data = QFileDialog.getOpenFileNames(self, "파일선택", self.home+"\\Desktop", "EXCEL (*.xlsx *.xls)")
        list_names = tuple_data[0]
        file_names = ",".join(list_names)
        self.textEdit_browser.setText(file_names)


    def radio_option1(self):

        if self.radioButton_OpOn.isChecked():
            self.op_flag = True
        elif self.radioButton_OpOff.isChecked():
            self.op_flag = False

    def radio_option2(self):

        if self.radioButton_f1.isChecked():
            self.mode_flag = "f1"
        elif self.radioButton_f2.isChecked():
            self.mode_flag = "f2"

    def btn_start(self):

        self.inputFile_path = self.textEdit_browser.toPlainText()
        self.flag = self.check_values(self.inputFile_path)

        if not self.flag:
            return
        else:
            self.tabWidget.setTabEnabled(1, False)
            self.started_flag = "y"
            self.progressValue = 0
            self.progressBar.setValue(0)
            self.radio_option1()
            self.radio_option2()
            self.controlAction(False, True)
            self.moduler = None
            self.moduler = Formater(self.inputFile_path, self.op_flag, self.mode_flag)
            self.moduler.print_flag.connect(self.printText)
            self.moduler.end_flag.connect(self.endFlag)
            self.moduler.progress_flag.connect(self.progressFlag)
            self.moduler.count_flag.connect(self.countText)
            self.moduler.start()

    def controlAction(self, flag, flag2):

        self.groupBox_9.setEnabled(flag)
        self.groupBox_17.setEnabled(flag)
        self.groupBox_18.setEnabled(flag)
        self.pushButton_start.setEnabled(flag)
        self.pushButton_cancel.setEnabled(flag2)

    def btn_clear(self):

        self.plainTextEdit_print.clear()
        self.label_count.clear()


    def check_values(self, path):

        list_file = path.split(",")
        self.file_size = len(list_file)
        if len(list_file) < 1:
            self.showMessageBox("Please selcet \"INPUT_DATA PATH\" using \"Browser button\".")
            return False
        elif len(list_file) == 1:
            exist_flag = os.path.isfile(list_file[0])
            if not exist_flag:
                self.showMessageBox("There is no file what your selected. Please select \"Input data\" file again")
                return False
            else:
                return True
        else:
            exist_flag =True
            for item in list_file:
                exist_flag = os.path.isfile(item)
                if not exist_flag:
                    self.showMessageBox("\"{}\" file does not exist. please check again".format(item))
                    exist_flag = False
                    break
            return exist_flag

    def display_text(self):

        self.label_main.setText(self.lineEdit_text.text())
        self.inputFile_path = self.lineEdit_text.text()

    def btn_closed(self):

        if self.started_flag is "y":
            self.buttonReplay = QMessageBox.question(self, "message", "Do you want all process quit?", QMessageBox.Yes, QMessageBox.Cancel)
            if self.buttonReplay == QMessageBox.Yes:
                self.moduler.stop()
                self.started_flag = "n"
                self.tabWidget.setTabEnabled(0, True)
                self.tabWidget.setTabEnabled(1, True)
                self.controlAction(True, False)
                # self.plainTextEdit_print.clear()
            else:
                return

    #####################################__DB Commit method__#####################################
    def set_hostflag(self):

        if self.checkBox_enabled.isChecked():
            self.acSave_flag = 'y'
        else:
            self.acSave_flag = 'n'

    def btn_start_conn(self):
        # set host db info
        self.host_ip = self.lineEdit_address.text().replace(" ","")
        self.host_port = self.lineEdit_port.text().replace(" ","")
        self.host_id = self.lineEdit_id.text().replace(" ","")
        self.host_pw = self.lineEdit_pw.text().replace(" ","")
        self.updateFile_path = self.textEdit_browser_2.toPlainText().replace(" ","")

        self.flag = self.check_host(self.updateFile_path, self.host_ip, self.host_port, self.host_id, self.host_pw)
        if not self.flag:
            return
        else:
            # Check messagebox about sure of executes commit
            self.confirm = self.check_commit()
            if self.confirm:
                if self.acSave_flag is "y":
                    self.set_hostInfo()
                self.tabWidget.setTabEnabled(0, False)
                self.controlAction_conn(False, True)
                self.connector = connMyDb(self.updateFile_path, "통품전체VOC", "불만성유형VOC", "전체가입자", "모델명매칭", "모델명매칭2", self.host_ip, self.host_port, self.host_id, self.host_pw, self.update_mode)
                self.connector.print_conn_flag.connect(self.printTextConn)
                self.connector.end_conn_flag.connect(self.endFlagConn)
                self.connector.count_conn_flag.connect(self.countTextConn)
                self.committed_flag = "y"
                self.connector.start()
            else:
                return

    def btn_openFile_conn(self):

        openFrame_conn = QFileDialog.getOpenFileName(self)
        # self.lineEdit_text.setText(openFrame[0])
        self.textEdit_browser_2.setText(openFrame_conn[0])

    def get_hostInfo(self):
        try:
            if self.checkBox_enabled_3.isChecked():
                self.current_path = os.getcwd()
                if os.path.isfile(self.current_path+"\\host\\hostInfo.txt"):
                    self.r1 = open(self.current_path+"\\host\\hostInfo.txt", mode='rt')
                    self.host_strings = self.r1.read()
                    self.dict_host = json.loads(self.host_strings)
                    self.lineEdit_address.setText(self.dict_host['address'])
                    self.lineEdit_port.setText(self.dict_host['port'])
                    self.lineEdit_id.setText(self.dict_host['id'])
                    self.lineEdit_pw.setText(self.dict_host['pw'])
                    self.r1.close()
            else:
                self.lineEdit_address.clear()
                self.lineEdit_port.clear()
                self.lineEdit_id.clear()
                self.lineEdit_pw.clear()
        except:
            self.lineEdit_address.clear()
            self.lineEdit_port.clear()
            self.lineEdit_id.clear()
            self.lineEdit_pw.clear()

    def set_hostInfo(self):

        self.current_path = os.getcwd()
        if not os.path.isdir(self.current_path+"\\host\\") :
            os.makedirs(self.current_path+"\\host\\", exist_ok=True)

        self.dict_host = {}
        self.dict_host['address'] = self.host_ip
        self.dict_host['port'] = self.host_port
        self.dict_host['id'] = self.host_id
        self.dict_host['pw'] = self.host_pw
        self.text_host = json.dumps(self.dict_host)
        with open(self.current_path+"\\host\\hostInfo.txt", "wt") as f:
            f.write(self.text_host)

    def radio_option_conn(self):

        if self.radioButton_upload.isChecked():
            self.update_mode = "upload"
        elif self.radioButton_drop.isChecked():
            self.update_mode = "drop"

    def controlAction_conn(self, flag, flag2):

        self.textEdit_browser_2.setEnabled(flag)
        self.pushButton_browser_2.setEnabled(flag)
        self.pushButton_commit.setEnabled(flag)
        self.groupBox_11.setEnabled(flag)
        self.groupBox_12.setEnabled(flag)
        self.pushButton_stop.setEnabled(flag2)

    def check_host(self, path, ip, port, id, pw):

        self.iNfileFlag = os.path.isfile(path)
        if ip is None or ip is "":
            self.showMessageBox("Please input \"DB HOST IP address\".")
            return False
        elif port is None or port is "":
            self.showMessageBox("Please input \"DB HOST PORT number\"")
            return False
        elif id is None or id is "":
            self.showMessageBox("Please input \"DB HOST ID for access\"")
            return False
        elif pw is None or pw is "":
            self.showMessageBox("Please input \"DB HOST PW for access\"")
            return False
        elif not self.iNfileFlag:
                self.showMessageBox("There is no file what your selected. Please select \"Upadte data\" file again")
        else:
            return True

    def check_commit(self):

        self.buttonCheck = QMessageBox.question(self, "message", "Do you want update to server?", QMessageBox.Yes, QMessageBox.Cancel)
        if self.buttonCheck == QMessageBox.Yes:
            return True
        elif self.buttonCheck == QMessageBox.Cancel:
            return False

    def btn_clear_conn(self):

        self.plainTextEdit_print_2.clear()
        self.label_count_2.clear()

    def btn_stop(self):

        if self.committed_flag is "y":
            self.confirm = QMessageBox.question(self, "message", "Do you want to stop update working?", QMessageBox.Yes, QMessageBox.Cancel)
            if self.confirm == QMessageBox.Yes:
                self.connector.stop()
                self.committed_flag = "n"
                self.tabWidget.setTabEnabled(0, True)
                self.tabWidget.setTabEnabled(1, True)
                self.controlAction_conn(True, False)
                # self.plainTextEdit_print_2.clear()
            else:
                return

    #####################################__Public method__#####################################
    def showMessageBox(self, message):

        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Critical)
        self.msg.setWindowTitle("경고")
        self.msg.setText(message)
        self.msg.setStandardButtons(QMessageBox.Ok)
        self.msg.show()

    def showMessageBox_info(self, message):

        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Information)
        self.msg.setWindowTitle("알림")
        self.msg.setText(message)
        self.msg.setStandardButtons(QMessageBox.Ok)
        self.msg.show()

    def check_int(self, value):

        try:
            self.value_converted = int(value)
            return "PASS"
        except:
            return "ERROR"

#####################################__Main Executes__#####################################
if __name__ == "__main__":

    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    sys.exit(app.exec_())
