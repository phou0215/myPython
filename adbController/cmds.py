import os
import subprocess
import sys
import xml.etree.cElementTree as et
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

        # self.adbkeyboard_name = 'com.android.adbkeyboard/.AdbIME'
        self.serial_num = uuid
        self.modelName = ''
        self.wm_divide_count = divide_window

        self.width = 0
        self.height = 0
        self.divided_width = 0
        self.divided_height = 0
        self.manufacturer = ''
        self.wifi_address = ''
        self.usedAdbKeyboard = False
        self.pattern = re.compile(r"\d+")
        self.current_path = os.getcwd()
        self.xml_device_path = '/sdcard/tmp_uiauto.xml'
        self.xml_local_path = self.current_path + '\\xmlDump(' + self.serial_num + ')\\tmp_uiauto.xml'
        self.capture_path = ''
        # ##########################__Device Control__##########################
        self.deviceSleep = ""
        self.deviceWakeup = ""
        self.reboot = ""
        self.rebootSafe = ""
        self.pullFile = ""
        self.pushFile = ""
        self.changeKeyboard = ""
        self.langSwitch = ""
        self.appExecute = ""
        self.forceStop = ""
        self.killPid = ""
        self.installApk = ""
        self.uninstallApk = ""
        self.keepDisplayOn = ""
        self.screen_shot = ""
        self.delete_path = ""
        self.setPort = ""
        self.setConnect = ""
        self.wifiOn = ""
        self.wifiOff = ""
        self.cellOn = ""
        self.cellOff = ""
        self.gpsOn = ""
        self.gpsOff = ""
        self.gpsNetOn = ""
        self.gpsNetOff = ""
        self.autoRotateOff = ""
        self.autoRotateOn = ""
        # #########################__Get adb data__##########################
        self.getDeives = "adb devices"
        self.getManuInfo = ""
        self.getModelInfo = ""
        self.windowSize = ""
        self.currentActi = ""
        self.memInfo = ""
        self.getXmlDump = ""
        self.getDefaultKeyboard = ""
        self.getPackageList = ""
        self.getCallState = ""
        self.getWifiAddress = ""
        self.getWifiStatus = ""
        self.getCellStatus = ""
        self.getGpsStatus = ""
        self.getAirplaneStatus = ""
        self.getRotateStatus = ""
        self.getBlueToothStatus = ""
        self.getBatteryStatus = ""
        # #########################__Action control__##########################
        self.back = ""
        self.menu = ""
        self.home = ""
        self.enter = ""
        self.power = ""
        self.killApp = ""
        self.appSwitch = ""
        self.click = ""
        self.swipe = ""
        self.normalInput = ""
        self.adbKeyInput = ""
        self.makeCall = ""
        self.dialCall = ""
        self.makeVideoCall = ""
        self.endCall = ""
        self.receiveCall = ""
        self.makeSMS = ""
        # #########################__Executes accessories control__##########################
        self.cameraExe = ""
        self.googleExe = ""
        self.callExe = ""
        self.callAirplaneMode = ""
        self.callBlueToothMode = ""
        # setting cmds
        self.set_serial_cmd()

    # #######################################__function of utility__##########################################
    # cmds setting
    def set_serial_cmd(self):

        # ##########################__Device Control__##########################
        self.deviceSleep = "adb -s " + self.serial_num + " shell input keyevent 223"
        self.deviceWakeup = "adb -s " + self.serial_num + " shell input keyevent 224"
        self.reboot = "adb -s " + self.serial_num + " reboot"
        self.rebootSafe = "adb -s " + self.serial_num + " reboot recovery"
        # %USERPROFILE%\Desktop\파일명(확장자 포함) => 바탕화면 경로
        # pull 1st 값은 디바이스 경로 2nd 값은 저장할 PC 장소
        # (adb -s RF9N604ZM0N pull /sdcard/tmp_uiauto.xml %USERPROFILE%\Desktop\tmp_uiauto.xml)
        self.pullFile = "adb -s " + self.serial_num + " pull {} {}"
        # push 1st 값은 PC 파일 경로 2nd 값은 저장할 device 경로
        # (adb -s RF9N604ZM0N push %USERPROFILE%\Desktop\tmp_uiauto.xml /sdcard/tmp_uiauto.xml)
        self.pushFile = "adb -s " + self.serial_num + " push {} {}"
        # change default keyboard
        self.changeKeyboard = "adb -s " + self.serial_num + " shell ime set {}"
        # recent app button press
        self.langSwitch = "adb -s " + self.serial_num + " shell input keyevent 204"
        # launch app
        self.appExecute = "adb -s " + self.serial_num + " shell monkey -p {} -c android.intent.category.LAUNCHER 1"
        # if success return "Success and you have to input package name"
        self.forceStop = "adb -s " + self.serial_num + " shell am force-stop {}"
        # you have to input pid number
        self.killPid = "adb -s " + self.serial_num + " shell kill {}"
        # install apk(apk 경로 입력)
        self.installApk = "adb -s " + self.serial_num + " install -r {}"
        # uninstall apk(package name 입력)
        self.uninstallApk = "adb -s " + self.serial_num + " uninstall --user 0 {}"
        # keep display on
        self.keepDisplayOn = "adb -s " + self.serial_num + " shell svc power stayon true"
        # capture screen shot(only png)
        self.screen_shot = "adb -s " + self.serial_num + " shell screencap -p /sdcard/{}"
        # delete file or dir
        self.delete_path = "adb -s " + self.serial_num + " shell rm {}"
        # wireless tcpip connect
        # set port
        # 정상의 경우 restarting in TCP mode port: 5555 response 됨
        self.setPort = "adb -s " + self.serial_num + " tcpip 5555"
        # set connect tcpip
        # 정상 연결의 경우 connected to 192.168.1.32:5555 response 됨
        # 비정상 연결 실패의 경우 annot connect to 192.168.1.31:5555: 대상 컴퓨터에서 연결을 거부했으므로 연결하지 못했습니다. (10061)
        self.setConnect = "adb -s " + self.serial_num + " connect {}:5555"

        self.wifiOn = "adb -s " + self.serial_num + " shell svc wifi enable"
        self.wifiOff = "adb -s " + self.serial_num + " shell svc wifi disable"
        self.cellOn = "adb -s " + self.serial_num + " shell svc data enable"
        self.cellOff = "adb -s " + self.serial_num + " shell svc data disable"
        self.gpsOn = "adb -s " + self.serial_num + " shell settings put secure location_providers_allowed +gps"
        self.gpsOff = "adb -s " + self.serial_num + " shell settings put secure location_providers_allowed -gps"
        self.gpsNetOn = "adb -s " + self.serial_num + " shell settings put secure location_providers_allowed +network"
        self.gpsNetOff = "adb -s " + self.serial_num + " shell settings put  secure location_providers_allowed -network"
        self.autoRotateOff = "adb -s " + self.serial_num + " shell settings put system accelerometer_rotation 0"
        self.autoRotateOn = "adb -s " + self.serial_num + " shell settings put system accelerometer_rotation 1"

        # #########################__Get adb data__##########################
        self.getDeives = "adb devices"
        self.getManuInfo = "adb -s " + self.serial_num + " shell \"getprop | grep -e ro.product.manufacturer\""
        self.getModelInfo = "adb -s " + self.serial_num + " shell getprop ro.product.model"
        self.windowSize = "adb -s " + self.serial_num + " shell wm size"
        self.currentActi = "adb -s " + self.serial_num + " shell dumpsys activity recents | find \"Recent #0\""
        self.memInfo = "adb -s " + self.serial_num + " shell dumpsys meminfo {}"
        # get elements Xpath node tree with xml data
        self.getXmlDump = "adb -s " + self.serial_num + " shell uiautomator dump {}"
        # check default keyboard
        self.getDefaultKeyboard = "adb -s " + self.serial_num + " shell settings get secure default_input_method"
        self.getPackageList = "adb -s " + self.serial_num + " shell pm list packages"
        # mCallState=0 indicates idle, mCallState=1 = ringing, mCallState=2 = active call
        self.getCallState = "adb -s " + self.serial_num + " shell \"dumpsys telephony.registry | grep mCallStat\""
        # wifi ipv4 주소 get
        # wifi 정상적 연결 상태라면 "192.168.1.0/24 dev wlan0 proto kernel scope link src 192.168.1.32" 값 노출
        self.getWifiAddress = "adb -s " + self.serial_num + " shell ip route"
        # get wifi status
        # 만약 wifi off 상태이면 return 값이 없음
        # 만약 wifi on 상태이면 return 값이
        # iface=wlan0 ident=[{type=WIFI, subType=COMBINED, networkId="TESTENCM25G", metered=false, defaultNetwork=true}]
        # 들어옴
        self.getWifiStatus = "adb -s " + self.serial_num + " shell \"dumpsys netstats | grep -E iface=wlan.*networkId\""
        self.getCellStatus = "adb -s " + self.serial_num + " shell telephony.registry"
        # get gps status
        # 만약 gps on 상태인 경우 gps,network로 노출되며 그렇지 않은 경우(둘다 없거나 하나만 있는 경우)는 gps off 상태임
        self.getGpsStatus = "adb -s " + self.serial_num + " shell settings get secure location_providers_allowed"
        # get airplane status
        # 만약 켜진 경우 'mAirplaneModeOn true'
        # 만약 꺼진 경우 'mAirplaneModeOn false'
        self.getAirplaneStatus = "adb -s " + self.serial_num + " shell \"dumpsys wifi | grep mAirplaneModeOn\""
        # get window auto rotate mode status
        # on의 경우 1 off의 경우 0으로 출력
        self.getRotateStatus = "adb -s " + self.serial_num + " shell settings get system accelerometer_rotation"
        # get bluetooth status
        # on의 경우 1 off의 경우 0으로 출력
        self.getBlueToothStatus = "adb -s " + self.serial_num + " shell settings get global bluetooth_on"
        # get battery status
        # AC 충전 여부 AC powered: false/true
        # USB 충전 여부 USB powered: true
        # Wireless 충전 여부 Wireless powered: false
        self.getBatteryStatus = "adb -s " + self.serial_num + " shell dumpsys battery"
        # display 전원 On Off status 체크
        self.getDisplayStatus = "adb -s " + self.serial_num + " shell \"dumpsys power | grep mHolding\""

        # #########################__Action control__##########################
        self.back = "adb -s " + self.serial_num + " shell input keyevent 4"
        self.menu = "adb -s " + self.serial_num + " shell input keyeve 82"
        self.home = "adb -s " + self.serial_num + " shell input keyevent 3"
        self.enter = "adb -s " + self.serial_num + " shell input keyevent 66"
        self.power = "adb -s " + self.serial_num + " shell input keyevent 26"
        self.clear = "adb -s " + self.serial_num + " shell input keyevent 28"
        self.killApp = "adb -s " + self.serial_num + " shell am force-stop"
        self.appSwitch = "adb -s " + self.serial_num + " shell input keyevent 187"
        self.click = "adb -s " + self.serial_num + " shell input touchscreen tap {} {}"
        self.swipe = "adb -s " + self.serial_num + " shell input touchscreen swipe {} {} {} {} {}"
        self.normalInput = "adb -s " + self.serial_num + " shell input text '{}'"
        self.adbKeyInput = "adb -s " + self.serial_num + " shell am broadcast -a ADB_INPUT_TEXT --es msg '{}'"
        self.makeCall = "adb -s " + self.serial_num + " shell am start -a android.intent.action.CALL tel:{}"
        self.dialCall = "adb -s " + self.serial_num + " shell am start -a android.intent.action.DIAL tel:{}"
        self.makeVideoCall = "adb -s " + self.serial_num + " shell am start -a android.intent.action.CALL -d tel:{} " \
                                                           "--ei android.telecom.extra.START_CALL_WITH_VIDEO_STATE 3"
        self.endCall = "adb -s " + self.serial_num + " shell input keyevent 6"
        self.receiveCall = "adb -s " + self.serial_num + " shell input keyevent 5"
        self.makeSMS = "adb shell -s " + self.serial_num + " am start -a android.intent.action.SENDTO -d sms:'{}' " \
                                                           "--es sms_body '{}' --ez exit_on_sent true"

        # #########################__Executes accessories control__##########################
        self.cameraExe = "adb -s " + self.serial_num + " shell am start -a android.media.action.STILL_IMAGE_CAMERA"
        self.googleExe = "adb -s " + self.serial_num + " shell am start -a android.intent.action.VIEW http://www.google.com"
        self.callExe = "adb -s " + self.serial_num + " shell input keyevent 5"
        self.callAirplaneMode = "adb -s " + self.serial_num + " shell am start -a android.settings.AIRPLANE_MODE_SETTINGS"
        self.callBlueToothMode = "adb -s " + self.serial_num + " shell am start -a android.settings.BLUETOOTH_SETTINGS"

    # 테스트 시작 전에 반드시 호출되어야 하는 Setup method
    def setup_test(self):

        try:

            keyboard_flag = False
            default_flag = False
            installed_status = 'Ok'
            connect_type = 'USB'
            # check device serial number
            self.check_device_serial()
            # check device model name info
            self.check_device_modelName()
            # check manufacturer device(Only support LGE or SAMSUNG)
            self.check_device_manuInfo()
            # keep display on
            self.check_device_displayOn()

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
                status = self.cmd_status_install(path=self.current_path + '\\adbkeyboard.apk')

                # 설치가 정상적이지 않은 경우 무시 절차 유무 진행
                if status != 1:
                    ignore_flag = input("AdbKeyboard를 정상적으로 설치하지 않았습니다. 이 절차를 무시합니까?(y/n): ")
                    ignore_flag.lower()
                    # check ignore_flag
                    if ignore_flag == 'y':
                        self.set_print("AdbKeyboard 설치 과정을 skip 처리합니다. text 입력에서 영문 이외에는 입력하실 수 없습니다.")
                        installed_status = "Skip"
                        pass
                    elif ignore_flag == 'n':
                        self.set_print("수동으로 AdbKeyboard apk를 설치 후에 프로그램 재실행을 부탁드립니다. 프로그램을 종료합니다.")
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
                            self.usedAdbKeyboard = True
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
                            self.usedAdbKeyboard = True
                            self.set_print("AdbKeyboard가 정상적으로 기본 키보드로 설정되었습니다.")
                        else:
                            input("아직 기본 키보드로 설정되지 않았습니다. 키보드 설정에서 AdbKeyboard를 "
                                  "기본 키보드로 설정해주신 후 아무키나 입력하세요.(설정 후 디바이스 reboot 진행): ")

                # 기본 키보드가 AdbKeyboard인 경우
                else:
                    self.usedAdbKeyboard = True
                    pass

            # check device size
            self.get_window_size()
            # check xml dump file directory
            dir_flag = os.path.isdir(self.current_path + '\\xmlDump(' + self.serial_num + ')')
            if not dir_flag:
                os.makedirs(self.current_path + '\\xmlDump(' + self.serial_num + ')')
            dir_flag = os.path.isdir(self.current_path + '\\capture(' + self.serial_num + ')')
            if not dir_flag:
                os.makedirs(self.current_path + '\\capture(' + self.serial_num + ')')
            current_time_dir = self.get_current_time()[2]
            self.capture_path = self.current_path + '\\capture(' + self.serial_num + ')\\' + current_time_dir + '\\'

            # Wireless Connection check
            wireless_flag = input("ADB를 무선으로 연결하시겠습니까? (y/n): ")
            wireless_flag.lower()
            # check ignore_flag

            if wireless_flag == 'y':
                self.set_print("ADB 무선 연결 절차를 시작합니다.")
                connect_type = 'Wifi'
                self.setup_wireless()
            elif wireless_flag == 'n':
                pass
            else:
                while wireless_flag != "y" and wireless_flag != "n":
                    wireless_flag = input("잘못입력하셨습니다. \"y\" 또는 \"n\"을 입력하여 주세요: ")
                    wireless_flag.lower()
                    if wireless_flag == 'n':
                        pass
                    elif wireless_flag == 'y':
                        self.set_print("ADB 무선 연결 절차를 시작합니다.")
                        connect_type = 'Wifi'
                        self.setup_wireless()
                    else:
                        continue
            self.set_print('ADBKeyboard: 설치완료({})\r\n기본키보드: AdbKeyboard({})'.format(installed_status, installed_status))
            self.set_print("ADB 연결 상태 : {}".format(connect_type))

        except:
            self.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                            sys.exc_info()[1],
                                                            sys.exc_info()[2].tb_lineno))
            sys.exit(-1)

    # wifi wireless adb connect
    def setup_wireless(self):
        try:
            input("무선 연결 절차를 시작합니다. 단말기 Local PC를 동일한 Wifi로 연결 진행한 후 아무키나 입력하세요.")
            # check device wifi connect
            return_wifiInfo = self.execute_cmd(self.getWifiAddress)

            while return_wifiInfo[1] == '':
                return_wifiInfo = self.execute_cmd(self.getWifiAddress)
                if return_wifiInfo[1] == '':
                    input("단말기의 Wifi 연결 상태가 아닙니다. 다시 확인하시고 아무키나 입력하세요.")
                else:
                    break

            raw_data = return_wifiInfo[1] + "/e"
            self.wifi_address = self.find_between(raw_data, 'src', '/e').strip()
            self.set_print("wifi 연결 확인 완료(wifi IPv4 address {})".format(self.wifi_address))

            # adb set up tcpip connect
            for i in range(3):
                return_setPort = self.execute_cmd(self.setPort)
                if 'restarting' not in return_setPort[1].lower() and i != 2:
                    self.set_print('ADB wifi TCP 연결 대기 실패! 연결 재시도')
                    sleep(1)
                    continue
                elif 'restarting' not in return_setPort[1].lower() and i == 2:
                    self.set_print('ADB wifi TCP 연결 대기 실패 디바이스 wifi 연결 상태를 다시 확인하시고 재실행 해주세요!: {}'.
                                   format(return_setPort[1]))
                    sys.exit(-1)
                else:
                    self.set_print('ADB tcpip IPv4 {} port {} 연결 대기'.format(self.wifi_address, '5555'))
                    break

            # try to connect wireless adb protocol
            for i in range(3):
                return_wireless = self.execute_cmd(self.setConnect.format(self.wifi_address))
                if 'connected' not in return_wireless[1].lower() and i != 2:
                    self.set_print('ADB wifi wireless 연결 실패! 연결 재시도')
                    sleep(1)
                    continue
                elif 'connected' not in return_wireless[1].lower() and i == 2:
                    self.set_print('ADB wifi wireless 연결 최종 실패 디바이스 wifi 연결 상태를 다시 확인하시고 재실행 해주세요!: {}'.
                                   format(return_wireless[1]))
                    sys.exit(-1)
                else:
                    self.set_print('ADB wireless 연결 완료!')
                    self.serial_num = self.wifi_address+":5555"
                    # serial 변경으로 cmd도 모두 변경
                    self.set_serial_cmd()
                    break

            # wait for disconnect usb cable
            input("무선 연결 protocol 설정 완료. 이제 USB 케이블을 해제한 후 아무키나 입력하세요.")
            # check device wifi connect
            return_usbStatus = self.execute_cmd(self.getBatteryStatus)
            while 'usb powered: true' in return_usbStatus[1].lower():
                return_usbStatus = self.execute_cmd(self.getBatteryStatus)
                if 'usb powered: false' in return_usbStatus[1].lower():
                    pass
                else:
                    input("단말기의 USB 연결 상태 입니다. USB 연결을 해제한 후 아무키나 입력하세요.")
        except:
            self.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                            sys.exc_info()[1],
                                                            sys.exc_info()[2].tb_lineno))
            sys.exit(-1)

    # check device_serial number
    def check_device_serial(self):

        # check device manufacture
        devices_info = self.execute_cmd(self.getDeives)

        if self.serial_num + "\tdevice" in devices_info[1]:
            self.set_print('Device Serial Number({}) is connected'.format(self.serial_num))
        else:
            self.set_print('Device Serial Number({}) is not in connected device list'.format(self.serial_num))
            sys.exit(-1)

    # check device manufacturer
    def check_device_manuInfo(self):

        # check device manufacture
        manu_info = self.execute_cmd(self.getManuInfo)

        if 'lg' in manu_info[1].lower():
            self.manufacturer = 'LGE'
            self.set_print('Device Manufacturer : {}'.format(self.manufacturer))
        elif 'samsung' in manu_info[1].lower():
            self.manufacturer = 'SAMSUNG'
            self.set_print('Device Manufacturer : {}'.format(self.manufacturer))
        else:
            self.set_print('ADB Controller 프로그램은 삼성 또는 LG 디바이스만 지원합니다.')
            sys.exit(-1)

    # check device manufacturer
    def check_device_modelName(self):

        # check device manufacture
        model_info = self.execute_cmd(self.getModelInfo)
        self.modelName = model_info[1].strip()

    # check device keep display on
    def check_device_displayOn(self):

        # check device manufacture
        self.execute_cmd(self.keepDisplayOn)
        self.set_print('Device Keep Display On Enabled')

    # Function of console print
    def set_print(self, text):

        current = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        if self.serial_num != "" and self.modelName != "":
            print("[{}({})]{}:\n{}".format(self.modelName, self.serial_num, current, text) + "\n")
        else:
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

            self.divided_width = int(self.width / self.wm_divide_count)
            self.divided_height = int(self.height / self.wm_divide_count)
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

    # get activity elements xpath node format xml file
    def save_dump_xml(self):

        try:
            # save dump
            returns = self.execute_cmd(self.getXmlDump.format(self.xml_device_path))
            if 'dumped to' not in returns[1]:
                raise Exception('Failed to get xml dump file cause by {}'.format(returns[1]))
            sleep(1)
            returns = self.execute_cmd(self.pullFile.format(self.xml_device_path, self.xml_local_path))
            if 'pulled' not in returns[1]:
                raise Exception('Failed to pull xml dump file casue by {}'.format(returns[1]))
            self.set_print('Extract and Save Activity xml dump file')
        except Exception as e:
            self.set_print('Error occured : {}'.format(e))

    # get list X and Y positions selected elements
    def get_pos_elements(self, attr='', name='', include=False):
        # attr type = (text, class, resource-id, content-desc)
        try:
            # get xml dump file
            self.save_dump_xml()
            list_pos = []
            list_target = name.split('|')
            tree = et.ElementTree(file=self.xml_local_path)
            list_elements = tree.iter(tag="node")
            if not include:
                for elem in list_elements:
                    attr_value = elem.attrib[attr]
                    if attr_value in list_target:
                        bounds = elem.attrib["bounds"]
                        coord = self.pattern.findall(bounds)
                        x = (int(coord[2]) - int(coord[0])) / 2.0 + int(coord[0])
                        y = (int(coord[3]) - int(coord[1])) / 2.0 + int(coord[1])
                        list_pos.append((x, y))
            else:
                for elem in list_elements:
                    attr_value = elem.attrib[attr]
                    for item in list_target:
                        if item in attr_value:
                            bounds = elem.attrib["bounds"]
                            coord = self.pattern.findall(bounds)
                            x = (int(coord[2]) - int(coord[0])) / 2.0 + int(coord[0])
                            y = (int(coord[3]) - int(coord[1])) / 2.0 + int(coord[1])
                            list_pos.append((x, y))
            return list_pos
        except:
            self.set_print('Failed to get position selected elements attr:{}, name:{}'.format(attr, name))
            self.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                            sys.exc_info()[1],
                                                            sys.exc_info()[2].tb_lineno))
            return None

    # 현재 시간 구하여 3가지 타입으로 list return
    def get_current_time(self):

        nowTime = datetime.now()
        now_datetime_str = nowTime.strftime('%Y-%m-%d %H:%M:%S')
        now_datetime_str2 = nowTime.strftime('%Y-%m-%d_%H%M%S')
        return [nowTime, now_datetime_str, now_datetime_str2]

    # ####################################__function of device control__######################################

    # ####################################__return function__####################################
    # package name에 해당하는 process id 반환
    def cmd_return_getPid(self, name=None):

        try:
            pid = ''
            function_name = self.cmd_return_getPid.__name__
            returns = self.execute_cmd(self.memInfo.format(name))
            if returns[0]:
                if 'No process found' not in returns[1]:
                    pid = find_between(returns[1], "pid", "[")
                    self.set_print("Activate \"{}\" : get pid {}".format(function_name, pid))
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

    # package name에 해당하는 process id 반환
    def cmd_return_getCallState(self):

        try:
            mCallState = ''
            dict_state = {"0": "idle", "1": "ringing", "2": "activate call"}
            function_name = self.cmd_return_getCallState.__name__
            returns = self.execute_cmd(self.getCallState)

            if returns[0]:
                if 'mCallState' in returns[1]:
                    mCallState = find_between(returns[1] + "/e", "mCallState=", "/e").strip()
                    self.set_print("Activate \"{}\" : get mCallState: {}({})".format(function_name,
                                                                                     mCallState,
                                                                                     dict_state[mCallState]))
                else:
                    self.set_print("Activate \"{}\" but no call state returns".format(function_name))
            else:
                self.set_print("ADB Occurred error \"{}\" and cause by : {}".format(function_name, returns[1]))

            return mCallState
        except:
            self.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                            sys.exc_info()[1],
                                                            sys.exc_info()[2].tb_lineno))
            return None

    # ####################################__status function__####################################
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
                    self.set_print("Activate \"{}\" : {} is on top".format(function_name, name))
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
                    self.set_print("Activate \"{}\" : {} But no process found".format(function_name, name))
                else:
                    self.set_print("Activate \"{}\" : {}".format(function_name, name))
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

    # launch APP
    def cmd_status_launchApp(self, name=''):

        # status 정상동작 조건일치 => '1' 비정상 동작 => '0' App 실행 실패 => '2'
        try:
            status = 1
            function_name = self.cmd_status_launchApp.__name__
            returns = self.execute_cmd(self.appExecute.format(name))
            # cmd 정상 실행 case
            if returns[0]:
                if 'events injected: 1' in returns[1].lower():
                    self.set_print("Activate \"{}\" : app launched package name ={}".format(function_name, name))
                else:
                    status = 2
                    self.set_print("Activate \"{}\" : try to launch app But failed!({})".format(function_name,
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
                self.set_print("Activate \"{}\" : click type={}, X={}, Y={}".format(function_name,
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
                self.set_print("Activate \"{}\" : swipe type={}, "
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
    def cmd_status_sendKey(self, message=''):

        # type 'abs' => 절대 좌표 값 'rate' => self.wm_winodw_count에 의해서 분리된 좌표의 중간 표지션
        # status 정상동작 조건일치 => '1' 비정상 동작 => '0'
        try:
            status = 1
            returns = None
            function_name = self.cmd_status_sendKey.__name__
            # check keyboard whether used adbkeyboard or not
            if self.usedAdbKeyboard:
                # returns = self.execute_cmd(self.adbKeyInput.format(message))
                returns = self.execute_cmd(self.normalInput.format(message))
            else:
                returns = self.execute_cmd(self.normalInput.format(message))
            # cmd 정상 실행 case
            if returns[0]:
                self.set_print("Activate \"{}\" : send text: {}".format(function_name, message))
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
                    self.set_print("Activate \"{}\" : install apk path={}".format(function_name, path))
                else:
                    status = 2
                    self.set_print("Activate \"{}\" : try to install apk But failed!({})".format(function_name,
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
                    self.set_print("Activate \"{}\" : delete package name {}".format(function_name, name))
                else:
                    status = 2
                    self.set_print("Activate \"{}\" : try to delete app But failed!({})".format(function_name,
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
    def cmd_status_backButton(self, iter_count=1, delay=0):

        # iter_count 는 뒤로 가기 버튼 반복 실행 수 delay는 다음 back button 실행 delay 시간
        # status 정상동작 조건일치 => '1' 비정상 동작 => '0'
        try:
            status = 1
            returns = None
            function_name = self.cmd_status_backButton.__name__
            for i in range(iter_count):
                returns = self.execute_cmd(self.back)
                sleep(delay)
            # cmd 정상 실행 case
            if returns[0]:
                self.set_print("Activate \"{}\" : executes back button : {} delay: {}".format(function_name,
                                                                                              iter_count,
                                                                                              delay))
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

    #  device power button press event
    def cmd_status_powerButton(self):

        # status 정상동작 조건일치 => '1' 비정상 동작 => '0'
        try:
            status = 1
            function_name = self.cmd_status_powerButton.__name__
            returns = self.execute_cmd(self.menu)
            # cmd 정상 실행 case
            if returns[0]:
                self.set_print("Activate \"{}\" : press power button".format(function_name))
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

    #  device home button press event
    def cmd_status_homeButton(self):

        # status 정상동작 조건일치 => '1' 비정상 동작 => '0'
        try:
            status = 1
            function_name = self.cmd_status_homeButton.__name__
            returns = self.execute_cmd(self.home)
            # cmd 정상 실행 case
            if returns[0]:
                self.set_print("Activate \"{}\" : press home button".format(function_name))
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

    #  device enter button press event
    def cmd_status_enterButton(self):

        # status 정상동작 조건일치 => '1' 비정상 동작 => '0'
        try:
            status = 1
            function_name = self.cmd_status_enterButton.__name__
            returns = self.execute_cmd(self.enter)
            # cmd 정상 실행 case
            if returns[0]:
                self.set_print("Activate \"{}\" : press enter button".format(function_name))
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

    # make a phone call event
    def cmd_status_sendCall(self, phone_num=''):

        # status 정상동작 조건일치 => '1' 비정상 동작 => '0' 전화 발신 실패 => '2'
        try:
            status = 1
            function_name = self.cmd_status_sendCall.__name__
            returns = self.execute_cmd(self.makeCall.format(phone_num))
            # cmd 정상 실행 case
            if returns[0]:
                if 'act=android.intent.action.call' in returns[1].lower():
                    self.set_print("Activate \"{}\" : make phone call number ={}".format(function_name, phone_num))
                else:
                    status = 2
                    self.set_print("Activate \"{}\" : try to make phone call But failed!({})".format(function_name,
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

    # make a video phone call event
    def cmd_status_sendVideoCall(self, phone_num=''):

        # status 정상동작 조건일치 => '1' 비정상 동작 => '0' 전화 발신 실패 => '2'
        try:
            status = 1
            function_name = self.cmd_status_sendVideoCall.__name__
            returns = self.execute_cmd(self.makeVideoCall.format(phone_num))
            # cmd 정상 실행 case
            if returns[0]:
                if 'act=android.intent.action.call' in returns[1].lower():
                    self.set_print("Activate \"{}\" : make video phone call number ={}".format(function_name,
                                                                                               phone_num))
                else:
                    status = 2
                    self.set_print(
                        "Activate \"{}\" : try to make video phone call But failed!({})".format(function_name,
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

    # end of phone call event
    def cmd_status_endCall(self):

        # status 정상동작 조건일치 => '1' 비정상 동작 => '0'
        try:
            status = 1
            function_name = self.cmd_status_endCall.__name__
            returns = self.execute_cmd(self.endCall)
            # cmd 정상 실행 case
            if returns[0]:
                self.set_print("Activate \"{}\" : end of phone call".format(function_name))
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

    # receive of phone call event
    def cmd_status_receiveCall(self):

        # status 정상동작 조건일치 => '1' 비정상 동작 => '0'
        try:
            status = 1
            function_name = self.cmd_status_receiveCall.__name__
            returns = self.execute_cmd(self.receiveCall)
            # cmd 정상 실행 case
            if returns[0]:
                self.set_print("Activate \"{}\" : receive of phone call".format(function_name))
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

    # send sms message event
    def cmd_status_sendSMS(self, phone_num='', message=''):

        # type 'abs' => 절대 좌표 값 'rate' => self.wm_winodw_count에 의해서 분리된 좌표의 중간 표지션
        # status 정상동작 조건일치 => '1' 비정상 동작 => '0'
        try:
            function_name = self.cmd_status_sendSMS.__name__
            # input sms text
            self.execute_cmd(self.makeSMS.format(phone_num, message))
            # get location(X/Y)
            location = self.get_pos_elements(attr='content-desc', name='전송')
            sleep(1)
            status = self.cmd_status_click(width=location[0][0], height=location[0][1], pos_type='abs')

            # cmd 정상 실행 case
            if status == 1:
                self.set_print("Activate \"{}\" : SMS text: {}".format(function_name, message))
            # cmd 비정상 실행 case
            else:
                status = 0
                self.set_print("ADB Occurred error \"{}\" and Failed to click send button".format(function_name))
            return status
        except:
            self.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                            sys.exc_info()[1],
                                                            sys.exc_info()[2].tb_lineno))
            return None

    # menu button press event
    def cmd_status_menuButton(self):

        # status 정상동작 조건일치 => '1' 비정상 동작 => '0'
        try:
            status = 1
            function_name = self.cmd_status_menuButton.__name__
            returns = self.execute_cmd(self.menu)
            # cmd 정상 실행 case
            if returns[0]:
                self.set_print("Activate \"{}\" : press menu button".format(function_name))
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

    # capture screen shot activity
    def cmd_status_screenShot(self, delay=1, name=''):

        # status 정상동작 조건일치 => '1' 비정상 동작 => '0'
        try:
            # check image capture folder is exist
            dir_flag = os.path.isdir(self.capture_path)
            if not dir_flag:
                os.makedirs(self.capture_path)

            status = 1
            function_name = self.cmd_status_screenShot.__name__
            sleep(delay)
            # executes screen capture
            current_time = self.get_current_time()[2]
            file_name = name + '_' + current_time + '.png'
            returns = self.execute_cmd(self.screen_shot.format(file_name))
            # cmd 정상 실행 case
            if returns[0]:
                # pull capture file to local PC
                returns_pull = self.execute_cmd(
                    self.pullFile.format('/sdcard/' + file_name, self.capture_path + file_name))
                # capture image delete on device
                self.execute_cmd(self.delete_path.format('/sdcard/' + file_name))
                if returns_pull[0]:
                    self.set_print("Activate \"{}\" : success to take screen shot: {}".format(function_name,
                                                                                              self.capture_path + file_name))
                # pull file error
                else:
                    status = 0
                    self.set_print("ADB Occurred error \"{}\" and pull file failed : {}".format(function_name,
                                                                                                returns_pull[1]))
            # cmd 비정상 실행 case
            else:
                status = 0
                self.set_print("ADB Occurred error \"{}\" and screen capture failed : {}".format(function_name,
                                                                                                 returns[1]))
            return status
        except:
            self.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                            sys.exc_info()[1],
                                                            sys.exc_info()[2].tb_lineno))
            return None

    # wifi on or off
    def cmd_status_wifiOnOff(self, exe_type=1, delay=1):

        # status 정상동작 조건일치 => '1' 비정상 동작 => '0' wifi control 실패 => '2'
        try:
            # check wifi status whether turn on or turn off
            function_name = self.cmd_status_wifiOnOff.__name__
            status = 1
            # turn on wifi case
            if exe_type == 1:
                returns = self.execute_cmd(self.wifiOn)
                # cmd 정상 실행 case
                if returns[0]:
                    self.set_print("Activate \"{}\" : enable wifi is success".format(function_name))
                # cmd 비정상 실행 case
                else:
                    status = 0
                    self.set_print("ADB Occurred error \"{}\" cause by can't turn on wifi: {}".format(function_name,
                                                                                                      returns[1]))
            # turn off wifi case
            else:
                returns = self.execute_cmd(self.wifiOff)
                # cmd 정상 실행 case
                if returns[0]:
                    self.set_print("Activate \"{}\" : disable wifi is success".format(function_name))
                # cmd 비정상 실행 case
                else:
                    status = 0
                    self.set_print("ADB Occurred error \"{}\" cause by can't turn off wifi: {}".format(function_name,
                                                                                                       returns[1]))
            # check wifi status
            sleep(delay)
            returns = self.execute_cmd(self.getWifiStatus)
            # turn on wifi case
            if exe_type == 1:
                if returns[0] and 'type=wifi' in returns[1].lower():
                    self.set_print("Current wifi status is \"Enabled\"")
                else:
                    status = 2
                    self.set_print(
                        "Current wifi status is not yet \"Enabled\"\nreturned message :\n{}".format(returns[1]))
            # turn off wifi case
            else:
                if returns[0] and 'type=wifi' not in returns[1].lower():
                    self.set_print("Current wifi status is \"Disabled\"")
                else:
                    status = 2
                    self.set_print(
                        "Current wifi status is not yet \"Disabled\"\nreturned message :\n{}".format(returns[1]))
            return status

        except:
            self.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                            sys.exc_info()[1],
                                                            sys.exc_info()[2].tb_lineno))
            return None

    # cellular on or off
    def cmd_status_cellOnOff(self, exe_type=1, delay=1):

        # status 정상동작 조건일치 => '1' 비정상 동작 => '0' wifi control 실패 => '2'
        try:
            # check cellular status whether turn on or turn off
            function_name = self.cmd_status_cellOnOff.__name__
            status = 1
            # turn on cellular case
            if exe_type == 1:
                returns = self.execute_cmd(self.cellOn)
                # cmd 정상 실행 case
                if returns[0]:
                    self.set_print("Activate \"{}\" : enable cellular is success".format(function_name))
                # cmd 비정상 실행 case
                else:
                    status = 0
                    self.set_print("ADB Occurred error \"{}\" cause by can't turn on cellular: {}".format(function_name,
                                                                                                          returns[1]))
            # turn off cellular case
            else:
                returns = self.execute_cmd(self.cellOff)
                # cmd 정상 실행 case
                if returns[0]:
                    self.set_print("Activate \"{}\" : disable cellular is success".format(function_name))
                # cmd 비정상 실행 case
                else:
                    status = 0
                    self.set_print(
                        "ADB Occurred error \"{}\" cause by can't turn off cellular: {}".format(function_name,
                                                                                                returns[1]))
            # check cellular status
            sleep(delay)
            returns = self.execute_cmd(self.getCellStatus)
            # turn on cellular case
            if exe_type == 1:
                if returns[0] and 'mDataConnectionState=2' in returns[1]:
                    self.set_print("Current cellular status is \"Enabled\"")
                else:
                    status = 2
                    self.set_print(
                        "Current cellular status is not yet \"Enabled\"\nreturned message :\n{}".format(returns[1]))
            # turn off cellular case
            else:
                if returns[0] and 'mDataConnectionState=2' not in returns[1]:
                    self.set_print("Current cellular status is \"Disabled\"")
                else:
                    status = 2
                    self.set_print(
                        "Current cellular status is not yet \"Disabled\"\nreturned message :\n{}".format(returns[1]))
            return status

        except:
            self.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                            sys.exc_info()[1],
                                                            sys.exc_info()[2].tb_lineno))
            return None

    # gps on or off
    def cmd_status_gpsOnOff(self, exe_type=1, delay=1):

        # status 정상동작 조건일치 => '1' 비정상 동작 => '0' wifi control 실패 => '2'
        try:
            # check gps status whether turn on or turn off
            function_name = self.cmd_status_gpsOnOff.__name__
            status = 1
            # turn on gps case
            if exe_type == 1:
                self.execute_cmd(self.gpsNetOn)
                returns = self.execute_cmd(self.gpsOn)
                # cmd 정상 실행 case
                if returns[0]:
                    self.set_print("Activate \"{}\" : enable gnss service is success".format(function_name))
                # cmd 비정상 실행 case
                else:
                    status = 0
                    self.set_print(
                        "ADB Occurred error \"{}\" cause by can't turn on gnss service: {}".format(function_name,
                                                                                                   returns[1]))
            # turn off gps case
            else:
                self.execute_cmd(self.gpsNetOff)
                returns = self.execute_cmd(self.gpsOff)
                # cmd 정상 실행 case
                if returns[0]:
                    self.set_print("Activate \"{}\" : disable gnss service is success".format(function_name))
                # cmd 비정상 실행 case
                else:
                    status = 0
                    self.set_print(
                        "ADB Occurred error \"{}\" cause by can't turn off gnss service: {}".format(function_name,
                                                                                                    returns[1]))
            # check gps status
            sleep(delay)
            returns = self.execute_cmd(self.getGpsStatus)
            # turn on gps case
            if exe_type == 1:
                if returns[0] and 'gps,network' in returns[1]:
                    self.set_print("Current gnss status is \"Enabled\"")
                else:
                    status = 2
                    self.set_print(
                        "Current gnss status is not yet \"Enabled\"\nreturned message :\n{}".format(returns[1]))
            # turn off gps case
            else:
                if returns[0] and 'gps,network' not in returns[1]:
                    self.set_print("Current gnss status is \"Disabled\"")
                else:
                    status = 2
                    self.set_print(
                        "Current gnss status is not yet \"Disabled\"\nreturned message :\n{}".format(returns[1]))
            return status

        except:
            self.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                            sys.exc_info()[1],
                                                            sys.exc_info()[2].tb_lineno))
            return None

    # auto rotate mode on or off
    def cmd_status_autoRotateOnOff(self, exe_type=1, delay=1):

        # status 정상동작 조건일치 => '1' 비정상 동작 => '0' auto rotate control 실패 => '2'
        try:
            function_name = self.cmd_status_autoRotateOnOff.__name__
            status = 1
            # turn on auto rotate case
            if exe_type == 1:
                returns = self.execute_cmd(self.autoRotateOn)
                # cmd 정상 실행 case
                if returns[0]:
                    self.set_print("Activate \"{}\" : enable auto rotate window is success".format(function_name))
                # cmd 비정상 실행 case
                else:
                    status = 0
                    self.set_print(
                        "ADB Occurred error \"{}\" cause by can't enable auto rotate window : {}".format(function_name,
                                                                                                         returns[1]))
            # turn off auto rotate case
            else:
                returns = self.execute_cmd(self.autoRotateOff)
                # cmd 정상 실행 case
                if returns[0]:
                    self.set_print("Activate \"{}\" : disable wifi is success".format(function_name))
                # cmd 비정상 실행 case
                else:
                    status = 0
                    self.set_print(
                        "ADB Occurred error \"{}\" cause by can't disable auto rotate window : {}".format(function_name,
                                                                                                          returns[1]))
            # check auto rotate status
            sleep(delay)
            returns = self.execute_cmd(self.getRotateStatus)
            # turn on auto rotate case
            if exe_type == 1:
                if returns[0] and '1' in returns[1]:
                    self.set_print("Current auto rotate status is \"Enabled\"")
                else:
                    status = 2
                    self.set_print(
                        "Current  auto rotate status is not yet \"Enabled\"\nreturned message :\n{}".format(returns[1]))
            # turn off auto rotate case
            else:
                if returns[0] and '0' in returns[1]:
                    self.set_print("Current auto rotate status is \"Disabled\"")
                else:
                    status = 2
                    self.set_print(
                        "Current auto rotate status is not yet \"Disabled\"\nreturned message :\n{}".format(returns[1]))
            return status

        except:
            self.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                            sys.exc_info()[1],
                                                            sys.exc_info()[2].tb_lineno))
            return None

    # blueTooth on or off
    def cmd_status_blueToothOnOff(self, exe_type=1, delay=1):

        # status 정상동작 조건일치 => '1' 비정상 동작 => '0' bluetooth control 실패 => '2'
        try:
            # check blueTooth status whether turn on or turn off
            function_name = self.cmd_status_blueToothOnOff.__name__
            status = 1
            execute_flag = True

            # execute_flag는 현재 디바이스 blueTooth mode 상태 켜져 있는지 확인 후 exe_type 에 맞춰서 함수가 실행되어야 할지 않지 결정함
            # check current blueTooth status
            returns = self.execute_cmd(self.getBlueToothStatus)
            # 실행타입이 On인데 이미 blueTooth 모드가 켜져 있는 경우
            if exe_type == 1 and "1" in returns[1]:
                execute_flag = False
            # 실행타입이 Off인데 이미 blueTooth 모드가 꺼져 있는 경우
            if exe_type == 0 and "0" in returns[1]:
                execute_flag = False

            # execute function depend on execute_flag
            # executes case
            if execute_flag:
                # turn on bluetooth mode case
                if exe_type == 1:
                    # 먼저 blueTooth mode activity call
                    self.execute_cmd(self.callBlueToothMode)
                    sleep(1)
                    # android.widget.TextView[@text='사용 안 함'] location 얻고 클릭하기
                    pos = self.get_pos_elements(attr='text', name='사용 안 함')
                    self.cmd_status_click(width=pos[0][0], height=pos[0][1], pos_type='abs')
                    sleep(1)
                    self.set_print("Activate \"{}\" : enable blueTooth mode is success".format(function_name))

                # turn off bluetooth mode case
                else:
                    # 먼저 airplane mode activity call
                    self.execute_cmd(self.callBlueToothMode)
                    sleep(1)
                    # android.widget.TextView[@text='사용 중'] location 얻고 클릭하기
                    pos = self.get_pos_elements(attr='text', name='사용 중|사용')
                    self.cmd_status_click(width=pos[0][0], height=pos[0][1], pos_type='abs')
                    sleep(1)
                    self.set_print("Activate \"{}\" : disable blueTooth mode is success".format(function_name))

                # check blueTooth status
                sleep(delay)
                returns = self.execute_cmd(self.getBlueToothStatus)
                # turn on blueTooth case
                if exe_type == 1:
                    if returns[0] and '1' in returns[1]:
                        self.set_print("Current blueTooth mode is \"Enabled\"")
                    else:
                        status = 2
                        self.set_print(
                            "Current blueTooth mode is not yet \"Enabled\"\nreturned message :\n{}".format(returns[1]))
                # turn off blueTooth case
                else:
                    if returns[0] and '0' in returns[1]:
                        self.set_print("Current blueTooth mode is \"Disabled\"")
                    else:
                        status = 2
                        self.set_print(
                            "Current blueTooth mode is not yet \"Disabled\"\nreturned message :\n{}".format(returns[1]))
            # skip case
            else:
                if exe_type == 1:
                    self.set_print("Activate \"{}\" : blueTooth mode already enabled. skip func".format(function_name))
                else:
                    self.set_print("Activate \"{}\" : blueTooth mode already disabled. skip func".format(function_name))

            return status

        except:
            self.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                            sys.exc_info()[1],
                                                            sys.exc_info()[2].tb_lineno))
            return None

    # airplane mode on of off(only samsung or lg)
    # 제조사마다 해당 airplane mode 각기 다름
    def cmd_status_airplaneOnOff(self, exe_type=1, delay=1):

        # status 정상동작 조건일치 => '1' 비정상 동작 => '0' airplane control 실패 => '2'
        try:
            # check airplane status whether turn on or turn off
            function_name = self.cmd_status_airplaneOnOff.__name__
            status = 1
            execute_flag = True

            # execute_flag는 현재 디바이스 airplane mode 상태 켜져 있는지 확인 후 exe_type 에 맞춰서 함수가 실행되어야 할지 않지 결정함
            # check current airplane status
            returns = self.execute_cmd(self.getAirplaneStatus)
            # 실행타입이 On인데 이미 비행기 모드가 켜져 있는 경우
            if exe_type == 1 and "mAirplaneModeOn true" in returns[1]:
                execute_flag = False
            # 실행타입이 Off인데 이미 비행기 모드가 꺼져 있는 경우
            if exe_type == 0 and "mAirplaneModeOn false" in returns[1]:
                execute_flag = False

            # execute function depend on execute_flag
            # execute case
            if execute_flag:
                # device LG case
                if self.manufacturer == "LGE":
                    # turn on airplane mode case
                    if exe_type == 1:
                        # 먼저 airplane mode activity call
                        self.execute_cmd(self.callAirplaneMode)
                        sleep(1)
                        # //android.widget.TextView[@text="비행기 모드"] location 얻고 클릭하기
                        pos = self.get_pos_elements(attr='text', name='비행기 모드|비행기모드')
                        self.cmd_status_click(width=pos[0][0], height=pos[0][1], pos_type='abs')
                        sleep(1)
                        # 설정 팝업에서 //android.widget.Button[@text="사용"|@text="설정"] location 얻고 클릭하기
                        pos = self.get_pos_elements(attr='text', name='사용|설정')
                        self.cmd_status_click(width=pos[0][0], height=pos[0][1], pos_type='abs')
                        self.set_print(
                            "Activate \"{}\" : LGE device enable airplane mode is success".format(function_name))

                    # turn off airplane mode case
                    else:
                        # 먼저 airplane mode activity call
                        self.execute_cmd(self.callAirplaneMode)
                        sleep(1)
                        # //android.widget.TextView[@text="비행기 모드"] location 얻고 클릭하기
                        pos = self.get_pos_elements(attr='text', name='비행기 모드|비행기모드')
                        self.cmd_status_click(width=pos[0][0], height=pos[0][1], pos_type='abs')
                        sleep(1)
                        self.set_print(
                            "Activate \"{}\" : LGE device disable airplane mode is success".format(function_name))

                # device samsung case
                elif self.manufacturer == "SAMSUNG":
                    # turn on airplane mode case
                    if exe_type == 1:
                        # 먼저 airplane mode activity call
                        self.execute_cmd(self.callAirplaneMode)
                        sleep(1)
                        # android.widget.Switch[@text='사용 안 함'] location 얻고 클릭하기
                        pos = self.get_pos_elements(attr='text', name='사용 안 함')
                        self.cmd_status_click(width=pos[0][0], height=pos[0][1], pos_type='abs')
                        sleep(1)
                        self.set_print(
                            "Activate \"{}\" : samsung device enable airplane mode is success".format(function_name))

                    # turn off airplane mode case
                    else:
                        # 먼저 airplane mode activity call
                        self.execute_cmd(self.callAirplaneMode)
                        sleep(1)
                        # android.widget.Switch[@text='사용 중'] location 얻고 클릭하기
                        pos = self.get_pos_elements(attr='text', name='사용 중')
                        self.cmd_status_click(width=pos[0][0], height=pos[0][1], pos_type='abs')
                        sleep(1)
                        self.set_print(
                            "Activate \"{}\" : samsung device disable airplane mode is success".format(function_name))
                # device not samsung or not lg stauts return 2
                else:
                    self.set_print("Activate \"{}\" : device's manufacturer is not in Samsung or not in LGE ".format(
                        function_name))
                    status = 0
                    return status
                # check airplane mode status
                sleep(delay)
                returns = self.execute_cmd(self.getAirplaneStatus)
                # turn on airplane mode case
                if exe_type == 1:
                    if returns[0] and 'mAirplaneModeOn true' in returns[1]:
                        self.set_print("Current airplane mode is \"Enabled\"")
                    else:
                        status = 2
                        self.set_print(
                            "Current airplane mode is not yet \"Enabled\"\nreturned message :\n{}".format(returns[1]))
                # turn off airplane mode case
                else:
                    if returns[0] and 'mAirplaneModeOn false' in returns[1]:
                        self.set_print("Current airplane mode is \"Disabled\"")
                    else:
                        status = 2
                        self.set_print(
                            "Current airplane mode is not yet \"Disabled\"\nreturned message :\n{}".format(returns[1]))
            # skip case
            else:
                if exe_type == 1:
                    self.set_print("Activate \"{}\" : airplane mode already enabled. skip func".format(function_name))
                else:
                    self.set_print("Activate \"{}\" : airplane mode already disabled. skip func".format(function_name))

            return status

        except:
            self.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                            sys.exc_info()[1],
                                                            sys.exc_info()[2].tb_lineno))
            return None


if __name__ == "__main__":
    # RF9N604ZM0N
    serial_num = 'RF9N604ZM0N'
    window_count = 20
    cmd = CMDS(serial_num, 20)
    # 필수 setup method 반드시 호출
    cmd.setup_test()
    cmd.save_dump_xml()
    # ########################__비행기 모드 테스트__########################
    # cmd.cmd_status_airplaneOnOff(exe_type=1, delay=1)
    # cmd.cmd_status_backButton(iter_count=2)
    # sleep(2)
    # cmd.cmd_status_airplaneOnOff(exe_type=0, delay=1)
    # cmd.cmd_status_backButton(iter_count=2)
    # sleep(2)
    # cmd.cmd_status_airplaneOnOff(exe_type=0,delay=1)
    # cmd.cmd_status_backButton(iter_count=2)

    # cmd.cmd_status_autoRotateOnOff(exe_type=1, delay=2)
    # sleep(3)
    # cmd.cmd_status_autoRotateOnOff(exe_type=0, delay=2)
    # sleep(3)
    # cmd.cmd_status_backButton(iter_count=2)

    # ########################__BlueTooth 모드 테스트__########################
    # cmd.cmd_status_blueToothOnOff(exe_type=1, delay=1)
    # cmd.cmd_status_backButton(iter_count=2)
    # sleep(2)
    # cmd.cmd_status_blueToothOnOff(exe_type=0, delay=1)
    # cmd.cmd_status_backButton(iter_count=2)
    # sleep(2)
    # cmd.cmd_status_blueToothOnOff(exe_type=0, delay=1)
    # cmd.cmd_status_backButton(iter_count=2)

    # # ########################__화면 회전 모드 테스트__########################
    # cmd.cmd_status_autoRotateOnOff(exe_type=1, delay=2)
    # sleep(3)
    # cmd.cmd_status_autoRotateOnOff(exe_type=0, delay=2)
    # sleep(3)
    # cmd.cmd_status_backButton(iter_count=2)

    # cmd.cmd_status_wifiOnOff(delay=1)
    # sleep(3)
    # cmd.cmd_status_wifiOnOff(delay=1)
    # status = cmd.cmd_status_click(10, 16, pos_type='rate')
    # cmd.set_print("Status Click: {}".format(status))
    # sleep(5)
    # status = cmd.cmd_status_swipe(7, 5, 5, 5, 300, pos_type="rate")
    # cmd.set_print("Status Swipe: {}".format(status))
    # list_pos = cmd.get_pos_elements(attr='content-desc', name='공유하기 버튼')
    # cmd.set_print(list_pos)
    # cmd.cmd_status_screenShot(delay=2, name="f1")

    # cmd.execute_cmd(cmd.cameraExe)
    # sleep(2)
    # cmd.execute_cmd('adb -s '+serial_num+' shell input keyevent 27')
    # # 카메라 전환
    # pos = cmd.get_pos_elements(attr='text', name='전면 카메라로 전환')
    # cmd.cmd_status_click(width=pos[0][0], height=pos[0][1], pos_type='abs')
    # sleep(2)
    # cmd.execute_cmd('adb -s '+serial_num+' shell input keyevent 27')
    # sleep(2)
    # # 동영상 전환
    # pos = cmd.get_pos_elements(attr='text', name='동영상')
    # cmd.cmd_status_click(width=pos[0][0], height=pos[0][1], pos_type='abs')
    # sleep(1)
    # # 녹화 시작
    # pos = cmd.get_pos_elements(attr='content-desc', name='녹화 시작')
    # cmd.cmd_status_click(width=pos[0][0], height=pos[0][1], pos_type='abs')
    # sleep(2)
    # # 녹화 정지
    # pos = cmd.get_pos_elements(attr='content-desc', name='일시정지')
    # cmd.cmd_status_click(width=pos[0][0], height=pos[0][1], pos_type='abs')
    # sleep(1)
    # # 계속 촬영
    # pos = cmd.get_pos_elements(attr='content-desc', name='계속')
    # cmd.cmd_status_click(width=pos[0][0], height=pos[0][1], pos_type='abs')
    # sleep(2)
    # # 녹화 중지
    # pos = cmd.get_pos_elements(attr='content-desc', name='녹화 중지')
    # cmd.cmd_status_click(width=pos[0][0], height=pos[0][1], pos_type='abs')
    # sleep(2)
    # # 뒤로 가기
    # cmd.cmd_status_backButton(iter_count=2)
    # cmd.save_dump_xml()
    # # switch app 지우기
    # cmd.execute_cmd(cmd.appSwitch)
    # pos = cmd.get_pos_elements(attr='text', name='모두 닫기')
    # cmd.cmd_status_click(width=pos[0][0], height=pos[0][1], pos_type='abs')
    # cmd.set_print('Sample Test 종료!')
