import re
import os
import sys
import pandas as pd
import numpy as np
# import nltk
import pickle
import joblib

from konlpy.tag import Okt
from konlpy.tag import Komoran

#
# # twitter = Komoran()
# list_sample_text = '특정 사이트에서 멈춤이 발생 카카오 톡 할 때 정상적으로 채팅이 안됨'
#
# text_data = re.sub(r'((특장|특정).?사이트|(특정|특장).?(어플|app|앱)|카카.?오.?톡?|(페이스|보이스|카|페|보).?톡|'
#                    r'kakao.?talk|tmap|(티|t).?맵|후후.?어?플?|페이스.?타임)', 'app', list_sample_text)
#
# # for idx, item in enumerate(list_sample_text):
# #     print('{} 테스트 입니다.'.format(list_sample_text[i]))
# print(text_data)
# #
# # print(twitter.pos(list_sample_text))

test = 0.0
convert = int(test)
print(convert)
