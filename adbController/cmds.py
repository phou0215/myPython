import os
import subprocess
import sys
import re
import time
from time import sleep
from datetime import datetime

# 각 void 함수의 경우 status code => 'adb cmd 정상동작 조건일치' => '1',
#                         'adb cmd 정상동작 조건 불일치' => '2',
#                         'adb cmd 비정상 동작' => '0'
class CMDS():

    def __init__(self, uuid=None, divide_window=10):

        super().__init__()

        self.serial_num = uuid
        self.wm_divide_count = divide_window
        # self.adbkeyboard_name = 'com.android.adbkeyboard/.AdbIME'
        self.width = 0
        self.height = 0
        self.divided_width = 0
        self.divided_height = 0
        self.usedAdbKeyboard = False
        self.current_path = os.getcwd()

        # ##########################__Device Control__##########################
        self.deviceSleep = "adb -s "+self.serial_num+" shell input keyevent 223"
        self.deviceWakeup = "adb -s "+self.serial_num+" shell input keyevent 224"
        self.reboot = "adb -s "+self.serial_num+" reboot"
        self.rebootSafe = "adb -s "+self.serial_num+" reboot recovery"
        # %USERPROFILE%\Desktop\파일명(확장자 포함) => 바탕화면 경로
        # pull 1st 값은 디바이스 경로 2nd 값은 저장할 PC 장소
        # (adb -s RF9N604ZM0N pull /sdcard/tmp_uiauto.xml %USERPROFILE%\Desktop\tmp_uiauto.xml)
        self.pullFile = "adb -s "+self.serial_num+" pull {} {}"
        # push 1st 값은 PC 파일 경로 2nd 값은 저장할 device 경로
        # (adb -s RF9N604ZM0N push %USERPROFILE%\Desktop\tmp_uiauto.xml /sdcard/tmp_uiauto.xml)
        self.pushFile = "adb -s "+self.serial_num+" push {} {}"
        # change default keyboard
        self.changeKeyboard = "adb -s "+self.serial_num+" shell ime set {}"
        # recent app button press
        self.langSwitch = "adb -s "+self.serial_num+" shell input keyevent 204"
        # launch app
        self.appExecute = "adb -s "+self.serial_num+" shell monkey -p {} -c android.intent.category.LAUNCHER 1"
        # if success return "Success and you have to input package name"
        self.forceStop = "adb -s "+self.serial_num+" shell am force-stop {}"
        # you have to input pid number
        self.killPid = "adb -s "+self.serial_num+" shell kill {}"
        # install apk(apk 경로 입력)
        self.installApk = "adb -s "+self.serial_num+" install {}"
        # uninstall apk(package name 입력)
        self.uninstallApk = "adb -s "+self.serial_num+" uninstall --user 0 {}"

        # #########################__Get adb data__##########################
        self.getDeives = "adb devices"
        self.windowSize = "adb -s "+self.serial_num+" shell wm size"
        self.currentActi = "adb -s "+self.serial_num+" shell dumpsys activity recents | find \"Recent #0\""
        self.memInfo = "adb -s "+self.serial_num+" shell dumpsys meminfo {}"
        self.getXmlDump = "adb -s "+self.serial_num+" shell uiautomator dump /sdcard/tmp_uiauto.xml"
        # check default keyboard
        self.getDefaultKeyboard = "adb -s "+self.serial_num+" shell settings get secure default_input_method"
        self.getPackageList = "adb -s "+self.serial_num+" shell pm list packages"

        # #########################__Action control__##########################
        self.back = "adb -s "+self.serial_num+" shell input keyevent 4"
        self.menu = "adb -s "+self.serial_num+" shell input keyeve 82"
        self.home = "adb -s "+self.serial_num+" shell input keyevent 3"
        self.power = "adb -s "+self.serial_num+" shell input keyevent 26"
        self.killApp = "adb -s "+self.serial_num+" shell am force-stop "
        self.appSwitch = "adb -s "+self.serial_num+" shell input keyevent 187"
        self.click = "adb -s "+self.serial_num+" shell input touchscreen tap {} {}"
        self.swipe = "adb -s "+self.serial_num+" shell input touchscreen swipe {} {} {} {} {}"
        self.normalInput = "adb -s "+self.serial_num+" shell input text '{}'"
        self.adbKeyInput = "adb -s "+self.serial_num+" shell am broadcast -a ADB_INPUT_TEXT --es msg '{}'"

        # #########################__Executes accessories control__##########################
        self.cameraExe = "adb -s "+self.serial_num+" shell am start -a android.media.action.IMAGE_CAPTURE"
        self.googleExe = "adb -s "+self.serial_num+" shell am start -a android.intent.action.VIEW http://www.google.com"
        self.callExe = "adb -s "+self.serial_num+" shell input keyevent 5"


    # #######################################__function of utility__##########################################

    # 테스트 시작 전에 반드시 호출되어야 하는 Setup method
    def setup_test(self):
        try:
            keyboard_flag = False
            default_flag = False

            # adbkeyboard installed check
            # adbkeyboard package name 'com.android.adbkeyboard'
            check_returns = self.execute_cmd(self.getPackageList)
            if 'com.android.adbkeyboard' in check_returns[1]:
                keyboard_flag = True
                # check default keyboard is adbkeyboard or not
                check_returns = self.execute_cmd(self.getDefaultKeyboard)
                if "com.android.adbkeyboard/.AdbIME" in check_returns[1]:
                    default_flag = True
                    self.usedAdbKeyboard = True

            # adbkeyboard 미설치의 Case 분기처리
            if not keyboard_flag:
                # install keyboard adb
                self.set_print("AdbKeyboard 설치를 진행합니다.")
                status = self.cmd_status_install(path=self.current_path+'\\adbkeyboard.apk')

                # 설치가 정상적이지 않은 경우 무시 절차 유무 진행
                if status != 1:
                    ignore_flag = input("AdbKeyboard를 정상적으로 설치하지 않았습니다. 이 절차를 무시합니까?(y/n): ")
                    ignore_flag.lower()
                    # check ignore_flag
                    if ignore_flag == 'y':
                        self.set_print("AdbKeyboard 설치 과정을 skip 처리합니다. text 입력에서 영문 이외에는 입력하실 수 없습니다.")
                        pass
                    elif ignore_flag == 'n':
                        self.setPrint("수동으로 AdbKeyboard apk를 설치 후에 프로그램 재실행을 부탁드립니다. 프로그램을 종료합니다.")
                        sys.exit(0)
                    else:
                        while ignore_flag != "y" and ignore_flag != "n":
                            ignore_flag = input("잘못입력하셨습니다. \"y\" 또는 \"n\"을 입력하여 주세요: ")
                            ignore_flag.lower()
                            if ignore_flag == 'n':
                                self.set_print("메뉴얼로 AdbKeyboard apk 설치 후에 프로그램 재실행을 부탁드립니다. 프로그램을 종료합니다.")
                                sys.exit(0)
                            elif ignore_flag == 'y':
                                self.set_print("AdbKeyboard 설치 과정을 skip 처리합니다. text 입력에서 영문 이외에는 입력하실 수 없습니다.")
                                break
                            else:
                                continue

                # 설치가 정상인 경우
                else:
                    # 설치가 정상적으로 된 경우 sequence 절차 진행
                    input("설정 > 일반 > 키보드 설정에서 AdbKeyboard를 기본 "
                          "키보드로 설정해주신 후 아무키나 입력하세요.(설정 후 디바이스 다시 시작 진행해주세요): ")
                    # 기본 키보드에 AdbKeyboard로 되어 있는지 확인
                    while not default_flag:
                        # adb driver reconnect
                        self.execute_cmd(self.getDeives)
                        # check default keyboard is adbkeyboard or not
                        check_returns = self.execute_cmd(self.getDefaultKeyboard)
                        if "com.android.adbkeyboard/.AdbIME" in check_returns[1]:
                            default_flag = True
                            self.set_print("AdbKeyboard가 정상적으로 기본 키보드로 설정되었습니다.")
                        else:
                            input("아직 기본 키보드로 설정되지 않았습니다. 키보드 설정에서 AdbKeyboard를 "
                                  "기본 키보드로 설정해주신 후 아무키나 입력하세요(설정 후 디바이스 reboot 진행): ")

            # adbkeyboard 설치의 Case 분기처리
            else:
                # 기본 키보드에 AdbKeyboard로 되어 있지 않는 경우
                if not default_flag:
                    # 설치가 정상적으로 된 경우 sequence 절차 진행
                    input("설정 > 일반 > 키보드 설정에서 AdbKeyboard를 기본 "
                          "키보드로 설정해주신 후 아무키나 입력하세요.(설정 후 디바이스 다시 시작 진행해주세요): ")
                    # 기본 키보드에 AdbKeyboard로 되어 있는지 확인
                    while not default_flag:
                        # adb driver reconnect
                        self.execute_cmd(self.getDeives)
                        # check default keyboard is adbkeyboard or not
                        check_returns = self.execute_cmd(self.getDefaultKeyboard)
                        if "com.android.adbkeyboard/.AdbIME" in check_returns[1]:
                            default_flag = True
                            self.set_print("AdbKeyboard가 정상적으로 기본 키보드로 설정되었습니다.")
                        else:
                            input("아직 기본 키보드로 설정되지 않았습니다. 키보드 설정에서 AdbKeyboard를 "
                                  "기본 키보드로 설정해주신 후 아무키나 입력하세요.(설정 후 디바이스 reboot 진행): ")

                # 기본 키보드가 AdbKeyboard인 경우
                else:
                    pass
            self.set_print('ADBKeyboard: 설치완료(OK)\r\n기본키보드: AdbKeyboard(OK)')
            self.usedAdbKeyboard = True
            # check device size
            self.get_window_size()
        except:
            self.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                            sys.exc_info()[1],
                                                            sys.exc_info()[2].tb_lineno))
            sys.exit(-1)

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
            self.set_print('Failed to execute CMD {}'.format(cmd))
            self.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                            sys.exc_info()[1],
                                                            sys.exc_info()[2].tb_lineno))
            return None

    # get mobile window size => This is mandatory method You have to call this before testing start!!!
    def get_window_size(self):

        try:
            returns = self.execute_cmd(self.windowSize)
            list_sizes = re.findall(r'[0-9]{3,4}', returns[1])

            if len(list_sizes) > 3:
                self.width = int(list_sizes[2])
                self.height = int(list_sizes[3])
            else:
                self.width = int(list_sizes[0])
                self.height = int(list_sizes[1])

            self.divided_width = int(self.width/self.wm_divide_count)
            self.divided_height = int(self.height/self.wm_divide_count)
            self.set_print('Device Window Size {} X {}'.format(self.width, self.height))
            self.set_print('Divided Window Size X={}, Y={} by count {}'.format(self.divided_width,
                                                                               self.divided_height,
                                                                               self.wm_divide_count))
        except:
            self.set_print('Failed to get windows size of device({})!'.format(self.serial_num))
            self.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                            sys.exc_info()[1],
                                                            sys.exc_info()[2].tb_lineno))

    # get device x,y position of rate values
    def get_divided_size(self, x=0, y=0):

        try:
            selected_x = 0
            selected_y = 0

            initiation_area_x = self.divided_width * (x - 1)
            initiation_area_y = self.divided_height * (y - 1)

            mid_area_x = int(self.divided_width / 2)
            mid_area_y = int(self.divided_height / 2)

            # width count
            if x == 0:
                selected_x = 0
            elif x == -1:
                selected_x = self.width
            else:
                selected_x = initiation_area_x + mid_area_x

            # height count
            if y == 0:
                selected_y = 0
            elif y == -1:
                selected_y = self.height
            else:
                selected_y = initiation_area_y + mid_area_y

            return selected_x, selected_y

        except:
            self.set_print('Failed to count divided_x and divided_y!')
            self.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                            sys.exc_info()[1],
                                                            sys.exc_info()[2].tb_lineno))

    # ####################################__function of device control__######################################

    # 현재 화면에 노출되고 있는 currnetActivity 확인
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
                self.set_print("ADB Occurred error \"{}\" and cause by : {}".format(function_name, returns[1]))

            return status

        except:
            self.set_print('Failed to check Top Activity \"{}\"'.format(name))
            self.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                            sys.exc_info()[1],
                                                            sys.exc_info()[2].tb_lineno))
            return None

    # package name에 해당하는 process id 반환
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
                self.set_print("ADB Occurred error \"{}\" and cause by : {}".format(function_name, returns[1]))

            return pid.strip()
        except:
            self.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                            sys.exc_info()[1],
                                                            sys.exc_info()[2].tb_lineno))
            return None

    # package name에 해당하는 process kill
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
                self.set_print("ADB Occurred error \"{}\" and cause by : {}".format(function_name, returns[1]))

            return status

        except:
            self.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                            sys.exc_info()[1],
                                                            sys.exc_info()[2].tb_lineno))
            return None

    # click event
    def cmd_status_click(self, width=0, height=0, pos_type='abs'):

        # type 'abs' => 절대 좌표 값 'rate' => self.wm_winodw_count에 의해서 분리된 좌표의 중간 표지션
        # status 정상동작 조건일치 => '1' 비정상 동작 => '0'
        try:
            status = 1
            function_name = self.cmd_status_click.__name__
            target_x = width
            target_y = height

            # count x/y position
            if pos_type == 'rate':
                target_x, target_y = self.get_divided_size(target_x, target_y)
            returns = self.execute_cmd(self.click.format(target_x, target_y))

            # cmd 정상 실행 case
            if returns[0]:
                self.set_print("Activate \"{}\" and click type={}, X={}, Y={}".format(function_name,
                                                                                      pos_type,
                                                                                      target_x,
                                                                                      target_y))
            # cmd 비정상 실행 case
            else:
                status = 0
                self.set_print("ADB Occurred error \"{}\" and cause by : {}".format(function_name, returns[1]))
            return status
        except:
            self.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                            sys.exc_info()[1],
                                                            sys.exc_info()[2].tb_lineno))
            return None

    # swipe or scroll event
    def cmd_status_swipe(self, s_width=0, s_height=0, e_width=0, e_height=0, duration=300, pos_type="abs"):

        # s_width => 터치 시작 x width, s_height => 터치 시작 y height,
        # e_width => 터치 종료 x width, e_height => 터치 종료 y height
        # duration => swipe action 실행 시간 단위 ms
        # type 'abs' => 절대 좌표 값 'rate' => self.wm_winodw_count에 의해서 분리된 좌표의 중간 표지션
        # status 정상동작 조건일치 => '1' 비정상 동작 => '0'
        try:
            status = 1
            function_name = self.cmd_status_swipe.__name__
            from_x = s_width
            from_y = s_height
            to_x = e_width
            to_y = e_height

            # count start and end x/y position
            if pos_type == 'rate':
                from_x, from_y = self.get_divided_size(from_x, from_y)
                to_x, to_y = self.get_divided_size(to_x, to_y)

            returns = self.execute_cmd(self.swipe.format(from_x, from_y, to_x, to_y, duration))
            # cmd 정상 실행 case
            if returns[0]:
                self.set_print("Activate \"{}\" and swipe type={}, "
                               "from_X={}, from_Y={}, to_X={}, to_Y={}, duration={}".format(function_name,
                                                                                            pos_type,
                                                                                            from_x,
                                                                                            from_y,
                                                                                            to_x,
                                                                                            to_y,
                                                                                            duration))
            # cmd 비정상 실행 case
            else:
                status = 0
                self.set_print("ADB Occurred error \"{}\" and cause by : {}".format(function_name, returns[1]))
            return status
        except:
            self.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                            sys.exc_info()[1],
                                                            sys.exc_info()[2].tb_lineno))
            return None

    # input text event
    def cmd_status_sendkey(self, message=''):

        # type 'abs' => 절대 좌표 값 'rate' => self.wm_winodw_count에 의해서 분리된 좌표의 중간 표지션
        # status 정상동작 조건일치 => '1' 비정상 동작 => '0'
        try:
            status = 1
            returns = None
            function_name = self.cmd_status_sendkey.__name__
            # check keyboard whether used adbkeyboard or not
            if self.usedAdbKeyboard:
                returns = self.execute_cmd(self.adbKeyInput.format(message))
            else:
                returns = self.execute_cmd(self.normalInput.format(message))
            # cmd 정상 실행 case
            if returns[0]:
                self.set_print("Activate \"{}\" and send text: {}".format(function_name, message))
            # cmd 비정상 실행 case
            else:
                status = 0
                self.set_print("ADB Occurred error \"{}\" and cause by : {}".format(function_name, returns[1]))
            return status
        except:
            self.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                            sys.exc_info()[1],
                                                            sys.exc_info()[2].tb_lineno))
            return None

    # install apk with path
    def cmd_status_install(self, path="/"):

        # path=> apk 파일 경로 parameter
        # status 정상동작 조건일치 => '1' 비정상 동작 => '0', 설치 실패 => '2'
        try:
            status = 1
            function_name = self.cmd_status_install.__name__
            returns = self.execute_cmd(self.installApk.format(path))
            # cmd 정상 실행 case
            if returns[0]:
                if 'success' in returns[1].lower():
                    self.set_print("Activate \"{}\" and install apk path={}".format(function_name, path))
                else:
                    status = 2
                    self.set_print("Activate \"{}\" and try to install apk But failed!({})".format(function_name,
                                                                                                   returns[1]))
            # cmd 비정상 실행 case
            else:
                status = 0
                self.set_print("ADB Occurred error \"{}\" and cause by : {}".format(function_name, returns[1]))
            return status
        except:
            self.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                            sys.exc_info()[1],
                                                            sys.exc_info()[2].tb_lineno))
            return None

    # device back button press event
    def cmd_status_backward(self, iter_count=1, delay=0):

        # iter_count 는 뒤로 가기 버튼 반복 실행 수 delay는 다음 back button 실행 delay 시간
        # status 정상동작 조건일치 => '1' 비정상 동작 => '0'
        try:
            status = 1
            returns = None
            function_name = self.cmd_status_backward.__name__
            # check keyboard whether used adbkeyboard or not
            for i in range(iter_count):
                returns = self.execute_cmd(self.back.format(message))
                sleep(delay)
            # cmd 정상 실행 case
            if returns[0]:
                self.set_print("Activate \"{}\" and send text: {}".format(function_name, message))
            # cmd 비정상 실행 case
            else:
                status = 0
                self.set_print("ADB Occurred error \"{}\" and cause by : {}".format(function_name, returns[1]))
            return status
        except:
            self.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                            sys.exc_info()[1],
                                                            sys.exc_info()[2].tb_lineno))
            return None

    #  deivece power button press event
    def cmd_powerButton(self):

        # status 정상동작 조건일치 => '1' 비정상 동작 => '0'
        try:
            status = 1
            function_name = self.cmd_powerButton.__name__
            # check keyboard whether used adbkeyboard or not
            returns = self.execute_cmd(self.power)
            # cmd 정상 실행 case
            if returns[0]:
                self.set_print("Activate \"{}\" and send text: {}".format(function_name, message))
            # cmd 비정상 실행 case
            else:
                status = 0
                self.set_print("ADB Occurred error \"{}\" and cause by : {}".format(function_name, returns[1]))
            return status
        except:
            self.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                            sys.exc_info()[1],
                                                            sys.exc_info()[2].tb_lineno))
            return None

    # uninstall apk with package name
    def cmd_status_uninstall(self, name=''):

        # name=> 삭제 대상 package name parameter
        # status 정상동작 조건일치 => '1' 비정상 동작 => '0', 삭제 실패 => '2'
        try:
            status = 1
            function_name = self.cmd_status_uninstall.__name__
            returns = self.execute_cmd(self.uninstallApk.format(name))
            # cmd 정상 실행 case
            if returns[0]:
                if 'success' in returns[1].lower():
                    self.set_print("Activate \"{}\" and delete package name {}".format(function_name, path))
                else:
                    status = 2
                    self.set_print("Activate \"{}\" and try to delete app But failed!({})".format(function_name,
                                                                                                  returns[1]))
            # cmd 비정상 실행 case
            else:
                status = 0
                self.set_print("ADB Occurred error \"{}\" and cause by : {}".format(function_name, returns[1]))
            return status
        except:
            self.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                            sys.exc_info()[1],
                                                            sys.exc_info()[2].tb_lineno))
            return None

    def cmd_sendCall(self):
        pass

    def cmd_endCall(self):
        pass

    def cmd_menu(self):
        pass

    def cmd_power(self):
        pass

    def run_script(self):
        pass


if __name__ == "__main__":
    cmd = CMDS('R39KA0CN92', 20)
    cmd.setup_test()
    status = cmd.cmd_status_click(10, 16, pos_type='rate')
    cmd.set_print("Status Click: {}".format(status))
    sleep(5)
    status = cmd.cmd_status_swipe(7, 5, 5, 5, 300, pos_type="rate")
    cmd.set_print("Status Swipe: {}".format(status))