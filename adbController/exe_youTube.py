import os
import sys
import re
import subprocess
import re
import time
from time import sleep
from datetime import datetime
from cmds import CMDS

class YOUTUBE_Test():

    def __init__(self, uuid, divide_window=10):

        super().__init__()
        self.cmd = CMDS(uuid, divide_window)
        self.limit_count = 6
        self.delay_time = 120
        self.item_pos = None
        self.search_pos = None

    def launch_youTube(self):

        try:
            # check displayOn
            return_status = self.cmd.execute_cmd(self.cmd.getDisplayStatus)
            # displayOn 상태
            if "mholdingdisplaysuspendblocker=true" in return_status[1].lower():
                pass
            # display off 상태
            else:
                self.cmd.cmd_status_powerButton()

            # youTube Run
            self.cmd.cmd_status_launchApp(name="com.google.android.youtube")
            # check runing status
            status = self.cmd.cmd_status_currnetActivity(name="com.google.android.youtube")
            if status != 1:
                while True:
                    self.cmd.cmd_status_backButton(iter_count=5)
                    self.cmd.cmd_status_launchApp(name="com.google.android.youtube")
                    sleep(2)
                    status = self.cmd.cmd_status_currnetActivity(name="com.google.android.youtube")
                    if status == 1:
                        if not self.search_pos:
                            self.cmd.save_dump_xml()
                            self.search_pos = self.cmd.get_pos_elements(attr="content-desc", name="검색")

                        self.cmd.cmd_status_click(width=self.search_pos[0][0],
                                                  height=self.search_pos[0][1],
                                                  pos_type="abs")
                        # 검색창에 'ytn 입력'
                        self.cmd.cmd_status_sendKey(message="ytn")
                        # 엔터 입력
                        self.cmd.cmd_status_enterButton()
                        if not self.item_pos:
                            self.cmd.save_dump_xml()
                            self.item_pos = self.cmd.get_pos_elements(attr="content-desc", name="[LIVE]", include=True)
                        sleep(2)
                        self.cmd.cmd_status_click(width=self.item_pos[0][0],
                                                  height=self.item_pos[0][1],
                                                  pos_type="abs")
                        break
            else:
                if not self.search_pos:
                    self.cmd.save_dump_xml()
                    self.search_pos = self.cmd.get_pos_elements(attr="content-desc", name="검색")

                self.cmd.cmd_status_click(width=self.search_pos[0][0],
                                          height=self.search_pos[0][1],
                                          pos_type="abs")
                # 검색창에 'ytn 입력'
                self.cmd.cmd_status_sendKey(message="ytn")
                # 엔터 입력
                self.cmd.cmd_status_enterButton()
                if not self.item_pos:
                    self.cmd.save_dump_xml()
                    self.item_pos = self.cmd.get_pos_elements(attr="content-desc", name="[LIVE]", include=True)
                sleep(2)
                self.cmd.cmd_status_click(width=self.item_pos[0][0],
                                          height=self.item_pos[0][1],
                                          pos_type="abs")

            self.cmd.set_print("YouTube YTN 실행이 완료되었습니다.")
        except:
            self.cmd.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                                sys.exc_info()[1],
                                                                sys.exc_info()[2].tb_lineno))

    def run_script(self):

        try:
            # 필수 setup method 반드시 호출
            self.cmd.setup_test()
            self.cmd.cmd_status_backButton(iter_count=5)
            # limit count 실행 Case
            if self.limit_count != 0:
                i = 0
                while i <= self.limit_count:
                    self.launch_youTube()
                    current_time = self.cmd.get_current_time()[1]
                    self.cmd.set_print("==================={} {}번 Delay_Time {} Test===================".
                                       format(current_time, i, self.delay_time))
                    i += 1
                    # vol UP
                    self.cmd.cmd_status_volumeUpDown(exe_type=1, iter_count=3, delay=1)
                    sleep(1)
                    # col Down
                    self.cmd.cmd_status_volumeUpDown(exe_type=0, iter_count=3, delay=1)
                    # 동영상 재생 시간
                    sleep(self.delay_time)
                    # TearDown
                    self.cmd.cmd_status_backButton(iter_count=5)
            # 무제한 실행 Case
            else:
                i = 0
                while True:
                    self.launch_youTube()
                    current_time = self.cmd.get_current_time()[1]
                    self.cmd.set_print("==================={} {}번 Delay_Time {} Test===================".
                                       format(current_time, i, self.delay_time))
                    i += 1
                    # vol UP
                    self.cmd.cmd_status_volumeUpDown(exe_type=1, iter_count=3, delay=1)
                    sleep(1)
                    # Vol Down
                    self.cmd.cmd_status_volumeUpDown(exe_type=0, iter_count=3, delay=1)
                    # 동영상 재생 시간
                    sleep(self.delay_time)
                    # TearDown
                    self.cmd.cmd_status_backButton(iter_count=5)

        except:
            self.cmd.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                                sys.exc_info()[1],
                                                                sys.exc_info()[2].tb_lineno))
if __name__ == "__main__":

    g960 = YOUTUBE_Test('1c25c664460c7ece', divide_window=20)
    g960.run_script()




