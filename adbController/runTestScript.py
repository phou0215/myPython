import os
import subprocess
import sys
from time import sleep
from datetime import datetime

test_time = 50000
delay_time = 20
sleep_time = 2


# 특정 문자 구간 Parsing 함수(앞에서부터)
def find_between(s, first, last):
    try:
        start = s.index(first)+len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""

# 특정 문자 구간 Parsing 함수(뒤에서부터)
def find_between_r(s, first, last ):
    try:
        start = s.rindex(first) + len(first)
        end = s.rindex(last, start)
        return s[start:end]
    except ValueError:
        return ""


def test_start():
    print("test start!")

    while True:
        pass



