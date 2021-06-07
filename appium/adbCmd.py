# -*- coding: utf-8 -*-
"""
Created on Wed May 29 10:37:12 2019
@author: TestEnC hanrim lee

"""
class CmdText ():

    def __init__(self, uuid, packageName, parent=None):
        self.getDeives = "adb devices"
        self.back = "adb "+uuid+" shell input keyevent 4"
        self.menu = "adb "+uuid+" shell input keyevent 82"
        self.home = "adb "+uuid+" shell input keyevent 3"
        self.power = "adb "+uuid+" shell input keyevent 26"
        self.killApp = "adb "+uuid+" shell am force-stop "
        self.appSwitch = "adb "+uuid+" shell input keyevent 187"
        self.langSwitch = "adb "+uuid+" shell input keyevent 204"
        self.deviceSleep = "adb "+uuid+" shell input keyevent 223"
        self.deviceWakeup = "adb "+uuid+" shell input keyevent 224"
        self.tap = "adb "+uuid+" shell input touchscreen tap "
        self.swipe = "adb "+uuid+" shell input touchscreen swipe "
        self.reboot = "adb reboot-bootloader"
        self.rebootSafe = "adb reboot recovery"
        self.touchScreen = "adb "+uuid+" shell input tap "
        self.cameraExe = "adb "+uuid+" shell am start -a android.media.action.IMAGE_CAPTURE"
        self.googleExe = "adb "+uuid+" shell am start -a android.intent.action.VIEW http://www.google.com"
        self.callExe = "adb "+uuid+" shell input keyevent 5"
        # self.smsExe = "adb shell am start -a android.intent.action.VIEW \"sms:"+phoneNum+"\" exit_on_sent true"

        # youtube function
        self.youtubePlay1 = "adb "+uuid+" shell am start -a android.intent.action.VIEW -d \"https://www.youtube.com/watch?v=IKWw8iZPCzo\""
        self.youtubePlay2 = "adb "+uuid+" shell am start -a android.intent.action.VIEW -d \"https://www.youtube.com/watch?v=dVQWgPYaDSU\""
        self.mediaPlay = "adb "+uuid+" shell input keyevent 126"
        self.mediaPause = "adb "+uuid+" shell input keyevent 127"
        self.mediaPP = "adb "+uuid+" shell input keyevent 85"
        self.mediaPre = "adb "+uuid+" shelll input keyevent 88"
        self.mediaNext = "adb "+uuid+" shell input keyevent 87"
        self.mediaRec = "adb "+uuid+" shell input keyevent 130" # recording keyevent

        # Camera function
        self.cameraCap = "adb "+uuid+" shell input keyevent 27"
        self.cameraFront1 = "adb "+uuid+" shell am start -a android.media.action.IMAGE_CAPTURE --ei android.intent.extras.CAMERA_FACING 1" # Only Android 7.0 under
        self.cameraFront2 = "adb "+uuid+" shell am start -a android.media.action.IMAGE_CAPTURE --ez android.intent.extra.USE_FRONT_CAMERA true" # Only Android 7.0 high
        self.screenRec = "adb "+uuid+" shell screenrecord /sdcard/video.mp4."
        self.videoFront = "adb "+uuid+" shell am start -a android.media.action.VIDEO_CAPTURE --ez android.intent.extra.USE_FRONT_CAMERA true"
        #self.checkFront = "adb "+uuid+" shell \"dumpsys window windows | grep -E mCurrentFocus\""
        # CALL Function
        self.callDial = "adb "+uuid+" shell am start -a android.intent.action.DIAL tel:"
        self.callMake = "adb "+uuid+" shell am start -a android.intent.action.CALL tel:"
        self.callEnd = "adb "+uuid+" shell input keyevent 6"
        self.checkCall = "adb "+uuid+" shell \"dumpsys telephony.registry | grep mCallStat\"" # ==>0 indicates idle, 1 = ringing and, 2 = active call
        # self.videoCall = "adb "+uuid+" shell am start -a android.intent.action.CALL -d tel:" # --ei android.telecom.extra.START_CALL_WITH_VIDEO_STATE 3"
        self.receiveCall = "adb "+uuid+" shell input keyevent 5"

        # SMS Function
        self.smsText = "adb "+uuid+" shell input text "
        self.sendMessage = "adb shell "+uuid+ "am start -a android.intent.action.SENDTO -d sms:'010XXXXXXXX' --es sms_body 'test message!!' --ez exit_on_sent true"
        # smsText 명령어 뒤에 텍스트 내용 넣으면 됨(이런 형식으로 ==> \"When%sWill%syou%scome%sback%shere?%sI%swill%swait%shere\")
        self.smsEnter = "adb "+uuid+" shell input keyevent 66"
        self.smsTab = "adb "+uuid+" shell input keyevent 61"
        # Samsung LG 모두 smsTab 두번 후 smsEnter
        # 영상통화는 call DIAL 이후 삼성은 resourceID = "com.samsung.android.dialer:id/very_left_frame" LG는 resourceID = "com.android.contacts:id/btnVT" 선택

        # Check Status
        self.checkAppProcess = "adb "+uuid+" shell pidof "+packageName # If app package on process returned pid number and unless app package on process returned null
        self.checkAppWindow = "adb "+uuid+" shell \"dumpsys window windows | grep 'Window #{num}'\"" # check assigned package from Window num
        self.checkAppOntop = "adb "+uuid+" shell \"dumpsys activity | grep top-activity\"" # check On top App Activity name ==> returned "Proc # 0: fore  F/A/T  trm: 0 3074:com.android.launcher/u0a8 (top-activity)"
        self.checkCallState = "adb "+uuid+" shell \"dumpsys telephony.registry | grep mCallState\""
        self.checkScreenOnOff = "adb "+uuid+" shell \"dumpsys power | grep mHolding\""
        self.topCpu = "adb "+uuid+" shell top -m 2 -s cpu"
        self.getWinSize = "adb "+uuid+" shell wm size"
        self.getSoundStatus = "adb -s "+num+" shell \"dumpsys audio | grep pack:\"";
		self.getPid = "adb -s "+num+" shell \"ps | grep skplanet.musicmate\"";


        # WIFI/Bluetooth/GPS/screen rotation
        self.gpsOn = "adb "+uuid+" shell settings put secure location_providers_allowed +gps"
        self.gpsOff = "adb "+uuid+" shell settings put secure location_providers_allowed -gps"
        self.gpsNetOn = "adb "+uuid+" shell settings put secure location_providers_allowed +network"
        self.gpsNetOff = "adb "+uuid+" shell settings put  secure location_providers_allowed -network"
        self.blueToothOn = "adb "+uuid+" shell am start -a android.bluetooth.adapter.action.REQUEST_ENABLE"
        self.blueToothOff = "adb "+uuid+" shell am start -a android.bluetooth.adapter.action.REQUEST_DISABLE"
        self.wifiControl = "adb "+uuid+" shell am start -a android.intent.action.MAIN -n com.android.settings/.wifi.WifiSettings"
        self.airControl = "adb "+uuid+" shell am start -a android.settings.AIRPLANE_MODE_SETTINGS"
        self.cellOn = "adb "+uuid+" shell svc data enable"
        self.cellOff = "adb "+uuid+" shell svc data disable"
        self.autoRotateOff = "adb "+uuid+" shell settings put system accelerometer_rotation 0"
        self.autoRotateOn = "adb "+uuid+" shell settings put system accelerometer_rotation 1"

        #Android 9.0 이상
        self.wifiOn = "adb "+uuid+" shell svc wifi enable"
        self.wifiOff = "adb "+uuid+" shell svc wifi disable"


        # key focus moving
        self.keyLeft = "adb "+uuid+" shell input keyevent 21"
        self.keyRight = "adb "+uuid+" shell input keyevent 22"
        self.keyCenter = "adb "+uuid+" shell input keyevent 23"
        self.keyUp = "adb "+uuid+" shell input keyevent 19"
        self.keyDown = "adb "+uuid+" shell input keyevent 20"
        self.keyEnter = "adb "+uuid+" shell input keyevent 66"

        # Bluetooth on 상황 ==> am start -a android.bluetooth.adapter.action.REQUEST_ENABLE -> bluetooth 팝업에서 keyevent 22 -> keyevent 22 -> keyevent 66
        # Bluetooth off 상황 ==> am start -a android.bluetooth.adapter.action.REQUEST_ENABLE -> bluetooth 팝업에서 keyevent 22 -> keyevent 22 -> keyevent 66
        # 와이파이는 팝업이 아닌 Activity가 있음 따라서 아래와 같은 커맨드를 따라야 함
        # 삼성: am start -a android.intent.action.MAIN -n com.android.settings/.wifi.WifiSettings -> keyevent 20 -> keyevent 20 -> keyevent 66 -> keyevent 4
        # LG: am start -a android.intent.action.MAIN -n com.lge.wifisettings/.activity.WifiSettingsActivity -> keyevent 19 -> keyevent 66 -> keyevent 4
        # Wifi Off 상황 ==>  am start -a android.intent.action.MAIN -n com.android.settings/.wifi.WifiSettings -> keyevent 66 -> keyevent 4
        # Airplane On 상황 ==>  am start -a android.settings.AIRPLANE_MODE_SETTINGS -> keyevent 20 -> keyevent 20 -> keyevent 66 -> keyevent 4
        # Airplane Off 상황 ==>  am start -a android.settings.AIRPLANE_MODE_SETTINGS -> keyevent 66 -> keyevent 4

        #volume control
        self.keyVolup = "adb "+uuid+" shell input keyevent 24"
        self.keyVoldown = "adb "+uuid+" shell input keyevent 25"

        # Doze 모드
        self.unplug = "adb "+uuid+" shell dumpsys battery unplug"
        self.deviceIdle = "adb "+uuid+" shell dumpsys deviceidle step"
        self.deviceStatus = "adb "+uuid+" shell \"dumpsys deviceidle | grep mState\""
        self.plugReset = "adb "+uuid+" shell dumpsys battery reset"

        #svc mode control
        # adb shell svc data enable/disable
        # adb shell svc wifi enable/disable
        # adb shell svc nfc enable/disable
        # adb shell svc bluetooth enable/disable
        # adb shell svc usb setFunctions [mtp', 'ptp', 'rndis', 'midi]
        # adb shell svc power stayon [true|false|usb|ac|wireless]

        #brightness
        self.brightSetMode = "adb "+uuid+" shell settings put system screen_brightness_mode 0"
        self.brightSetValue = "adb "+uuid+" shell settings put system screen_brightness "
        self.brightSetBack = "adb "+uuid+" shell settings put system screen_brightness_mode 1"
        self.brightGetCurrent = "adb "+uuid+" shell settings get system screen_brightness" #==> only number return ex) 128
        # # Game Function
        # self.apkInstall = "adb install -r "
        # self.apkInstallOndevice = "adb shell pm install -r /sdcard/Download/"
        # self.apkPush = "adb push "
        self.apkList = "adb shell pm list packages -f "+self.appname
        self.apkRun = "adb "+uuid+" shell monkey -p "+packageName+" -c android.intent.category.LAUNCHER 1"
        # self.downloadApk = "adb shell am start -a android.intent.action.VIEW -d \"https://drive.google.com/uc?id=1stl-3wbkQMmKX9FGy-EAyubJmLiCoCqa&export=download\" --ez create_new_tab false"
        # self.downloadApkVersion = "adb shell am start -a android.intent.action.VIEW -d \"http://121.166.62.161:8080/res/version.txt\" --ez create_new_tab false"
        # self.deleteFile = "adb shell rm /sdcard/Download/"
        # self.checkFile = "adb shell ls /sdcard/Download/"
        #
        # # T map
        # self.tmapExe = "adb shell monkey -p com.skt.skaf.l001mtm091 -c android.intent.category.LAUNCHER 1"
        # self.tmapExe2 = "adb shell am start -n com.skt.skaf.l001mtm091/com.skt.skaf.l001mtm091.TmapMainActivity"
        # self.tmapSearch = "adb shell input touchscreen tap 500 100"
        # self.tampInputText = "adb shell input text \"CJ\""
        # self.koreanText = "adb shell am broadcast -a ADB_INPUT_TEXT --es msg " # You must download adbkeyboard and install. Next You have to change main keyboard "adbkeyboard" on setting > keyboard
        # self.englishText = "adb shell input text "
# 0 -->  "KEYCODE_0"
# 1 -->  "KEYCODE_SOFT_LEFT"
# 2 -->  "KEYCODE_SOFT_RIGHT"
# 3 -->  "KEYCODE_HOME"
# 4 -->  "KEYCODE_BACK"
# 5 -->  "KEYCODE_CALL"
# 6 -->  "KEYCODE_ENDCALL"
# 7 -->  "KEYCODE_0"
# 8 -->  "KEYCODE_1"
# 9 -->  "KEYCODE_2"
# 10 -->  "KEYCODE_3"
# 11 -->  "KEYCODE_4"
# 12 -->  "KEYCODE_5"
# 13 -->  "KEYCODE_6"
# 14 -->  "KEYCODE_7"
# 15 -->  "KEYCODE_8"
# 16 -->  "KEYCODE_9"
# 17 -->  "KEYCODE_STAR"
# 18 -->  "KEYCODE_POUND"
# 19 -->  "KEYCODE_DPAD_UP"
# 20 -->  "KEYCODE_DPAD_DOWN"
# 21 -->  "KEYCODE_DPAD_LEFT"
# 22 -->  "KEYCODE_DPAD_RIGHT"
# 23 -->  "KEYCODE_DPAD_CENTER"
# 24 -->  "KEYCODE_VOLUME_UP"
# 25 -->  "KEYCODE_VOLUME_DOWN"
# 26 -->  "KEYCODE_POWER"
# 27 -->  "KEYCODE_CAMERA"
# 28 -->  "KEYCODE_CLEAR"
# 29 -->  "KEYCODE_A"
# 30 -->  "KEYCODE_B"
# 31 -->  "KEYCODE_C"
# 32 -->  "KEYCODE_D"
# 33 -->  "KEYCODE_E"
# 34 -->  "KEYCODE_F"
# 35 -->  "KEYCODE_G"
# 36 -->  "KEYCODE_H"
# 37 -->  "KEYCODE_I"
# 38 -->  "KEYCODE_J"
# 39 -->  "KEYCODE_K"
# 40 -->  "KEYCODE_L"
# 41 -->  "KEYCODE_M"
# 42 -->  "KEYCODE_N"
# 43 -->  "KEYCODE_O"
# 44 -->  "KEYCODE_P"
# 45 -->  "KEYCODE_Q"
# 46 -->  "KEYCODE_R"
# 47 -->  "KEYCODE_S"
# 48 -->  "KEYCODE_T"
# 49 -->  "KEYCODE_U"
# 50 -->  "KEYCODE_V"
# 51 -->  "KEYCODE_W"
# 52 -->  "KEYCODE_X"
# 53 -->  "KEYCODE_Y"
# 54 -->  "KEYCODE_Z"
# 55 -->  "KEYCODE_COMMA"
# 56 -->  "KEYCODE_PERIOD"
# 57 -->  "KEYCODE_ALT_LEFT"
# 58 -->  "KEYCODE_ALT_RIGHT"
# 59 -->  "KEYCODE_SHIFT_LEFT"
# 60 -->  "KEYCODE_SHIFT_RIGHT"
# 61 -->  "KEYCODE_TAB"
# 62 -->  "KEYCODE_SPACE"
# 63 -->  "KEYCODE_SYM"
# 64 -->  "KEYCODE_EXPLORER"
# 65 -->  "KEYCODE_ENVELOPE"
# 66 -->  "KEYCODE_ENTER"
# 67 -->  "KEYCODE_DEL"
# 68 -->  "KEYCODE_GRAVE"
# 69 -->  "KEYCODE_MINUS"
# 70 -->  "KEYCODE_EQUALS"
# 71 -->  "KEYCODE_LEFT_BRACKET"
# 72 -->  "KEYCODE_RIGHT_BRACKET"
# 73 -->  "KEYCODE_BACKSLASH"
# 74 -->  "KEYCODE_SEMICOLON"
# 75 -->  "KEYCODE_APOSTROPHE"
# 76 -->  "KEYCODE_SLASH"
# 77 -->  "KEYCODE_AT"
# 78 -->  "KEYCODE_NUM"
# 79 -->  "KEYCODE_HEADSETHOOK"
# 80 -->  "KEYCODE_FOCUS"
# 81 -->  "KEYCODE_PLUS"
# 82 -->  "KEYCODE_MENU"
# 83 -->  "KEYCODE_NOTIFICATION"
# 84 -->  "KEYCODE_SEARCH"
# 85 -->  "KEYCODE_MEDIA_PLAY_PAUSE"
# 86 -->  "KEYCODE_MEDIA_STOP"
# 87 -->  "KEYCODE_MEDIA_NEXT"
# 88 -->  "KEYCODE_MEDIA_PREVIOUS"
# 89 -->  "KEYCODE_MEDIA_REWIND"
# 90 -->  "KEYCODE_MEDIA_FAST_FORWARD"
# 91 -->  "KEYCODE_MUTE"
# 92 -->  "KEYCODE_PAGE_UP"
# 93 -->  "KEYCODE_PAGE_DOWN"
# 94 -->  "KEYCODE_PICTSYMBOLS"
# 122 -->  "KEYCODE_MOVE_HOME"
# 123 -->  "KEYCODE_MOVE_END"
# 로그 레벨
# V    Verbose (default for <tag>)
# D    Debug (default for '*')
# I    Info
# W    Warn
# E    Error
# F    Fatal
# S    Silent (suppress all output)

# 모든 로그 사항 adb logcat -v threadtime -d *:v > C:\Users\TestEnC\Desktop\log.txt
# 로그 초기화 adb logcat -c
# 에러만 뽑기 adb logcat -v threadtime -d *:E > C:\Users\TestEnC\Desktop\log.txt
