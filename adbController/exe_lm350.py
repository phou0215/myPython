import os
import sys
import re
import subprocess
import re
import time
from time import sleep
from datetime import datetime
from cmds import CMDS

class SAMPLE_Test():

    def __init__(self, uuid, divide_window=10):

        super().__init__()
        self.cmd = CMDS(uuid, divide_window)
        # self.display_flag = False
        # self.end_flag = False


    def run_script(self):

        # 필수 setup method 반드시 호출
        self.cmd.setup_test()
        # ########################__비행기 모드 테스트__########################
        # self.cmd.cmd_status_airplaneOnOff(exe_type=1, delay=1)
        # self.cmd.cmd_status_backButton(iter_count=2)
        # sleep(2)
        # self.cmd.cmd_status_airplaneOnOff(exe_type=0, delay=1)
        # self.cmd.cmd_status_backButton(iter_count=2)
        # sleep(2)
        # self.cmd.cmd_status_airplaneOnOff(exe_type=0,delay=1)
        # self.cmd.cmd_status_backButton(iter_count=2)
        #
        # self.cmd.cmd_status_autoRotateOnOff(exe_type=1, delay=2)
        # sleep(3)
        # self.cmd.cmd_status_autoRotateOnOff(exe_type=0, delay=2)
        # sleep(3)
        # self.cmd.cmd_status_backButton(iter_count=2)

        for i in range(3):
        # ########################__BlueTooth 모드 테스트__########################
            self.cmd.cmd_status_blueToothOnOff(exe_type=1, delay=1)
            self.cmd.cmd_status_backButton(iter_count=2)
            sleep(2)
            self.cmd.cmd_status_blueToothOnOff(exe_type=0, delay=1)
            self.cmd.cmd_status_backButton(iter_count=2)
            sleep(2)
            self.cmd.cmd_status_blueToothOnOff(exe_type=0, delay=1)
            self.cmd.cmd_status_backButton(iter_count=2)

            # # ########################__화면 회전 모드 테스트__########################
            self.cmd.cmd_status_autoRotateOnOff(exe_type=1, delay=2)
            sleep(3)
            self.cmd.cmd_status_autoRotateOnOff(exe_type=0, delay=2)
            sleep(3)
            self.cmd.cmd_status_backButton(iter_count=2)
            self.cmd.cmd_status_screenShot(delay=2, name='sample_test1')


if __name__ == "__main__":

    lm350 = SAMPLE_Test('LMV350N7a33ed5c', divide_window=20)
    lm350.run_script()




