from pywinauto.application import Application
import pywinauto.mouse as mouse
import pywinauto.keyboard as keyboard
from time import sleep
from pywinauto.keyboard import send_keys, KeySequenceError
import re
# app = Application(backend="uia").connect(path="notepad.exe")
# app['Dialog']['Edit'].set_text("Sample")
# send_keys('some text{ENTER 2}some more textt{BACKSPACE}')
#

reportDate_str = '\u200e09-24-2020'
reportDate_str = re.findall('[0-9]{2}-[0-9]{2}-[0-9]{4}', reportDate_str)
print(reportDate_str[0])

# from pywinauto.application import Application
#
# #app = Application.start("C:\Program Files (x86)\Google\Chrome\Application\chrome.exe")
# app = Application.start("C:\Program Files (x86)\Internet Explorer\iexplore.exe")
# app.window_().TypeKeys('{F11}')
# app.window_().TypeKeys('https://www.yogiyo.co.kr')
# sleep(5)


# from pywinauto import Application
#
# app = Application(backend="uia").connect(title='Web page title - Google Chrome')
# main_win = app.window(title='Web page title - Google Chrome')
# main_win_wrapper = main_win.set_focus() # not needed if this is already in focus (needed during debug)
#
# sign_in = main_win.child_window(title="Sign in", depth=2) # search only for 1 level below
#
# # visible_only=False is a workaround for bug I discovered while writing this script
# username = sign_in.child_window(title="Username", control_type="Edit", visible_only=False)
# password = sign_in.child_window(title="Password", control_type="Edit", visible_only=False)
# sign_in_button = sign_in.child_window(title="Sign in", control_type="Button", visible_only=False)
#
# # commented methods are not implemented for EditWrapper
# # this is also area for improvement
# username.iface_value.SetValue("username") # .set_value("user name")
# password.iface_value.SetValue("password") # .set_value("password")
# sign_in_button.invoke()