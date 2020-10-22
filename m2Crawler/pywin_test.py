from pywinauto import application
import json
from pywinauto.findwindows import WindowAmbiguousError, WindowNotFoundError

# app = application.Application(backend='win32').connect(path="")
#
#
# list_test = ['texst']
# list_body = list_test[0]
# list_rest = list_test[1:]
# print(len(list_body))
# print(len(list_rest))
# print(list_body)
# print(list_rest)
# string_data = '2020.09.10. 08:45'
# list_temp = string_data.split()
# list_temp[0] = list_temp[0][0:len(list_temp[0])-1]
# list_temp[0] = list_temp[0].replace('.', '-')
# print(list_temp)

# data = '{"type":"v2_video", "id" :"SE-e96b7a4a-9c11-4a71-992a-4899954d8f84", "data" : { "videoType" : "player", "vid" : "945D3BF5B3F93C16B57E463C2458197E492A", "inkey" : "V12120ddb2edef313531d3e18cecaae499f65d37b46b6c89ef8c5b6bc77824cb9b82c3e18cecaae499f65", "originalWidth": "1280", "originalHeight": "720", "width": "800", "height": "450", "contentMode": "fit", "format": "normal", "mediaMeta": {"@ctype":"mediaMeta","title":"밑에 터치 불량 동영상 입니다~ (1)","tags":[],"description":null} }}'
# dict = json.loads(data)
# print(dict['data']['vid'])
# print(dict['data']['inkey'])

# import pandas as pd
#
# list_cols = ['가진','자는']
# list_cols_2 = []
# dict_empty = {}
# df_test = None
# for item in list_cols:
#     dict_empty[item] = [1,2,3]
#
# df_test = pd.DataFrame(dict_empty, index=None)
# df_test.rename(columns = {'가진': '너를', '자는': '위해'}, inplace = True)
# print(df_test.head())

string_text = 'https://www.clien.net/service/board/cm_andro(안드로메당)'
list_text = string_text.split('(')
url = list_text[0]
nav_name = list_text[1]
nav_name = nav_name[:len(nav_name)-1]
print(url, nav_name)

num = 5
print(num % 10)

