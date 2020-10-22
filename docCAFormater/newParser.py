import os
import sys
import json

# from PyQt5.QtWidgets import *
from os.path import expanduser
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSlot
from newModule import Formater
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

# 		groupBox_6(Control Button)
# 			pushButton_start(start analysis)
# 			pushButton_cancel(abort analysis)
#
# 		progressBar(analysis progress)

class MyWindow(QMainWindow, form_class):

    def __init__(self):

        super().__init__()
        self.setupUi(self)
        self.home = expanduser('~')

        #####################################__VOC Parser class__#####################################
        self.started_flag = "n"
        self.search_flag = "n"
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

        #####################################__VOC Parser Events__#####################################
        self.pushButton_browser.clicked.connect(self.btn_openFiles)
        self.pushButton_start.clicked.connect(self.btn_start)
        self.pushButton_cancel.clicked.connect(self.btn_closed)
        self.pushButton_cancel.setEnabled(False)

        #Clear button
        self.pushButton_clear.clicked.connect(self.btn_clear)

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
            self.controlAction(False, True)
            self.moduler = None
            self.moduler = Formater(self.inputFile_path)
            self.moduler.print_flag.connect(self.printText)
            self.moduler.end_flag.connect(self.endFlag)
            self.moduler.progress_flag.connect(self.progressFlag)
            self.moduler.count_flag.connect(self.countText)
            self.moduler.start()

    def controlAction(self, flag, flag2):

        self.groupBox_9.setEnabled(flag)
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
                self.controlAction(True, False)
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
