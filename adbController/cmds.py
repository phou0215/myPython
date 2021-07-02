import os
import subprocess
import sys
import re
from time import sleep
from datetime import datetime

# 각 void 함수의 경우 status code => 'adb cmd 정상동작 조건일치' => '1',
#                         'adb cmd 정상동작 조건 불일치' => '2',
#                         'adb cmd 비정상 동작' => '0'
class CMDS():

    def __init__(self, uuid):

        super().__init__()

        self.serial_num = uuid
        self.wm_divide_count = 10
        self.width = 0
        self.height = 0

        self.windowSize = "adb -s "+self.serial_num+" shell wm size"
        self.appExecute = "adb -s "+self.serial_num+" shell monkey -p {} -c android.intent.category.LAUNCHER 1"
        self.killApp = "adb -s "+self.serial_num+" shell am force-stop {}"
        self.killPid = "adb -s "+self.serial_num+" shell kill {}"
        self.currentActi = "adb -s "+self.serial_num+" shell dumpsys activity recents | find \"Recent #0\""
        self.click = "adb -s "+self.serial_num+" shell input touchscreen tap {} {}"
        self.memInfo = "adb -s "+self.serial_num+" shell dumpsys meminfo {}"
        self.getDeives = "adb devices"
        self.back = "adb -s "+self.serial_num+" shell input keyevent 4"
        self.menu = "adb -s "+self.serial_num+" shell input keyeve  nt 82"
        self.home = "adb -s "+self.serial_num+" shell input keyevent 3"
        self.power = "adb -s "+self.serial_num+" shell input keyevent 26"
        self.killApp = "adb -s "+self.serial_num+" shell am force-stop "
        self.appSwitch = "adb -s "+self.serial_num+" shell input keyevent 187"
        self.langSwitch = "adb -s "+self.serial_num+" shell input keyevent 204"
        self.deviceSleep = "adb -s "+self.serial_num+" shell input keyevent 223"
        self.deviceWakeup = "adb -s "+self.serial_num+" shell input keyevent 224"
        self.tap = "adb -s "+self.serial_num+" shell input touchscreen tap "
        self.swipe = "adb -s "+self.serial_num+" shell input touchscreen swipe "
        self.reboot = "adb reboot-bootloader"
        self.rebootSafe = "adb reboot recovery"
        self.touchScreen = "adb -s "+self.serial_num+" shell input tap "
        self.cameraExe = "adb -s "+self.serial_num+" shell am start -a android.media.action.IMAGE_CAPTURE"
        self.googleExe = "adb -s "+self.serial_num+" shell am start -a android.intent.action.VIEW http://www.google.com"
        self.callExe = "adb -s "+self.serial_num+" shell input keyevent 5"
        self.sendText = "adb -s "+self.serial_num+" shell input text {}"

    # Function of console print
    def set_print(self, text):

        current = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        print("{}:\n{}".format(current, text) + "\n")

    # 특정 문자 구간 Parsing 함수(앞에서부터)
    def find_between(self, s, first, last):

        try:
            start = s.index(first) + len(first)
            end = s.index(last, start)
            return s[start:end]
        except ValueError:
            return ""

    # 특정 문자 구간 Parsing 함수(뒤에서부터)
    def find_between_r(self, s, first, last):

        try:
            start = s.rindex(first) + len(first)
            end = s.rindex(last, start)
            return s[start:end]
        except ValueError:
            return ""

    # Function of executing ADB command
    def execute_cmd(self, cmd=None):

        return_data = [True, '']
        try:
            pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            stdout_text, stderr_text = pipe.communicate()

            if stderr_text:
                stderr_text = stderr_text.decode('utf-8').strip()
                return_data[0] = False
                return_data[1] = stderr_text

            if stdout_text:
                stdout_text = stdout_text.decode('utf-8').strip()
                return_data[1] = stdout_text

            return return_data
        except:
            self.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                            sys.exc_info()[1],
                                                            sys.exc_info()[2].tb_lineno))
            return None

    # get mobile window size
    def get_window_size(self):
        try:
            returns = self.execute_cmd(self.windowSize)
            list_sizes = re.split(r'[0-9]]{3,4}', returns[1])

            if len(list_sizes) > 3:
                self.width = list_sizes[2]
                self.height = list_sizes[3]
            else:
                self.width = list_sizes[0]
                self.height = list_sizes[1]
                print(self.width, self.height)

        except:
            self.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                            sys.exc_info()[1],
                                                            sys.exc_info()[2].tb_lineno))

    # ###########################################__function of cmd send__############################################

    # Function of Check on Forward
    def cmd_status_currnetActivity(self, name=None):

        # status 정상동작 조건일치 => '1' 정상동작 조건 불일치 => '2' 비정상 동작 => '0'
        try:
            status = 1
            function_name = self.cmd_status_currnetActivity.__name__
            returns = self.execute_cmd(self.currentActi)
            # cmd 정상 실행 case
            if returns[0]:
                if name not in returns[1]:
                    status = 2
                    self.set_print("Activate \"{}\" but {} is not on top".format(function_name, name))
                else:
                    self.set_print("Activate \"{}\" and {} is on top".format(function_name, name))
            # cmd 비정상 실행 case
            else:
                status = 0
                self.set_print("ADB Occurred \"{}\" and cause by : {}".format(function_name, returns[1]))

            return status

        except:
            self.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                            sys.exc_info()[1],
                                                            sys.exc_info()[2].tb_lineno))
            return None

    def cmd_return_getPid(self, name=None):

        try:
            pid = ''
            function_name = self.cmd_return_getPid.__name__
            returns = self.execute_cmd(self.memInfo.format(name))
            if returns[0]:
                if 'No process found' not in  returns[1]:
                    pid = find_between(returns[1], "pid", "[")
                    self.set_print("Activate \"{}\" and get pid {}".format(function_name, pid))
                else:
                    self.set_print("Activate \"{}\" but No process found".format(function_name))
            else:
                self.set_print("ADB Occurred \"{}\" and cause by : {}".format(function_name, returns[1]))

            return pid.strip()
        except:
            self.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                            sys.exc_info()[1],
                                                            sys.exc_info()[2].tb_lineno))
            return None

    def cmd_status_killApp(self, name=None):

        # status 정상동작 조건일치 => '1' 정상동작 조건 불일치 => '2' 비정상 동작 => '0'
        try:
            status = 1
            function_name = self.cmd_status_killApp.__name__
            returns = self.execute_cmd(self.killApp.format(name))
            # cmd 정상 실행 case
            if returns[0]:
                if 'No process found' not in returns[1]:
                    status = 2
                    self.set_print("Activate \"{}\" and {} But no process found".format(function_name, name))
                else:
                    self.set_print("Activate \"{}\" and {}".format(function_name, name))
            # cmd 비정상 실행 case
            else:
                status = 0
                self.set_print("ADB Occurred \"{}\" and cause by : {}".format(function_name, returns[1]))

            return status

        except:
            self.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                            sys.exc_info()[1],
                                                            sys.exc_info()[2].tb_lineno))
            return None

    def cmd_status_click(self, width=None, height=None, width_rate=None, height_rate=None):

        # status 정상동작 조건일치 => '1' 정상동작 조건 불일치 => '2' 비정상 동작 => '0'
        try:
            status = 1
            function_name = self.cmd_status_click.__name__
            returns = self.execute_cmd(self.click.format(name))
            # cmd 정상 실행 case
            if returns[0]:
                if 'No process found' not in returns[1]:
                    status = 2
                    self.set_print("Activate \"{}\" and {} But no process found".format(function_name, name))
                else:
                    self.set_print("Activate \"{}\" and {}".format(function_name, name))
            # cmd 비정상 실행 case
            else:
                status = 0
                self.set_print("ADB Occurred \"{}\" and cause by : {}".format(function_name, returns[1]))

            return status

        except:
            self.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                            sys.exc_info()[1],
                                                            sys.exc_info()[2].tb_lineno))
            return None

    def cmd_scroll(self):
        pass

    def cmd_sendkey(self):
        pass

    def cmd_script(self):
        pass

    def cmd_topActivity(self):
        pass

    def cmd_backward(self):
        pass

    def cmd_powerButton(self):
        pass

    def cmd_killApp(self):
        pass

    def cmd_installApp(self):
        pass

    def cmd_deleteApp(self):
        pass

    def cmd_sendCall(self):
        pass

    def cmd_endCall(self):
        pass

    def cmd_menu(self):
        pass

    def cmd_power(self):
        pass
