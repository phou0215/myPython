#
# class samples():
#
#     def __init__(self):
#         pass
#     def sample_function(self):
#         print('han')
#         print(self.sample_function.__name__)
#
#
# if __name__ == "__main__":
#     sm = samples()
#     sm.sample_function()

import subprocess
import os

# cmd = "adb shell dumpsys activity recents | find \"Recent #0\""
# cmd = "adb shell dumpsys meminfo com.android.adbkeyboard"
# cmd = "adb shell uninstall com.android.adbkeyboard"
cmd = "adb uninstall --user 0 com.android.adbkeyboard"
current_path = os.getcwd()
# cmd = 'adb shell pm list packages'
# cmd = 'adb install '+current_path+'\\adbkeyboard.apk'
cmd = 'adb pull /sdcard/tmp_uiauto.xml '+current_path+"\\xmlDump\\tmp_uiauto.xml"
# cmd = "adb shell am force-stop com.kakao.talk"
# cmd = "adb shell settings get secure default_input_method"
# cmd = "adb shell am broadcast -a ADB_INPUT_TEXT --es msg '안녕하세요? Hello?'"
pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
stdout_text, stderr_text = pipe.communicate()

return_data = [True, '']
if stderr_text:
    stderr_text = stderr_text.                                    decode('utf-8').strip()
    return_data[0] = False
    return_data[1] = stderr_text

if stdout_text:
    stdout_text = stdout_text.decode('utf-8').strip()
    return_data[1] = stdout_text

print(return_data)

# w = 1050
# h = 2500
# d = 20
#
# d_w = int(w/d)
# d_h = int(h/d)
#
# print(d_w, d_h)