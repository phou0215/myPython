import os
import subprocess
import sys
from time import sleep
from datetime import datetime

test_time = 50000
delay_time = 20
sleep_time = 2

def execute_cmd(cmd):

    pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdoutdata, stderrdata = pipe.communicate()
    if stderrdata:
        stderrdata = stderrdata.decode('utf-8').strip()
        print("Error!! : " + stderrdata)
    if stdoutdata:
        stdoutdata = stdoutdata.decode('utf-8').strip()
        print(stdoutdata)

    return (stdoutdata, stdoutdata)

def get_currnet_activity(package_name):
    flag = True
    stdoutdata = execute_cmd(currentActi.format(deviceSerial))[0]
    if package_name not in stdoutdata:
        flag = False
    return flag

def get_pid():
    mem_data = execute_cmd(memInfo.format(deviceSerial, "com.kakao.talk"))[0]
    pid = find_between(mem_data, "pid", "[")
    return pid.strip()

def kill_pid(pid):
    execute_cmd(killPid.format(deviceSerial, pid))
    sleep(sleep_time)

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


def return_to_kakako():

    print('return to home and stop Kakao Talk')
    execute_cmd(home.format(deviceSerial))
    execute_cmd(killApp.format(deviceSerial, 'com.kakao.talk'))
    sleep(sleep_time)
    print('retry to executes Kakao Talk')
    execute_cmd(appExecute.format(deviceSerial, 'com.kakao.talk'))
    sleep(sleep_time)
    execute_cmd(click.format(deviceSerial, '500', '600'))
    sleep(sleep_time)


def test_start():

    execute_times = 0
    end_flag =False
    print("Initial App")
    execute_cmd(home.format(deviceSerial))
    execute_cmd(killApp.format(deviceSerial, 'com.kakao.talk'))
    sleep(sleep_time)
    print('Execute Test!')
    execute_cmd(appExecute.format(deviceSerial, 'com.kakao.talk'))
    print('Execute kakao talk')
    sleep(sleep_time)
    execute_cmd(click.format(deviceSerial, '500', '600'))
    sleep(sleep_time)

    while True:
        now = datetime.today().strftime("%H:%M:%S")
        print(now)
        # check text execute times
        # if execute_times > test_time:
        #     print("kakao test is completed!")
        #     break
        # check current package app if not retry launch kakao
        flag_current = get_currnet_activity('com.kakao.talk')
        if not flag_current:
            return_to_kakako()

        print(("============================[SEND_TEXT {} Time]============================").format(execute_times))
        # execute_cmd(click.format(deviceSerial, '650', '2390'))
        sleep(1)
        execute_cmd(sendText.format(deviceSerial, 'event_test_'+ str(execute_times+1) +'_'+ now))
        sleep(1)
        print('Input text')
        execute_cmd(click.format(deviceSerial, '1040', '2390'))
        print('send text')
        execute_times = execute_times + 1
        print("Wait for Delay Time 20's")
        sleep(delay_time)



