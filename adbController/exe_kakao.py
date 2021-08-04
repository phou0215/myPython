import os
import sys
import re
import subprocess
import re
import time
from time import sleep
from datetime import datetime
from cmds import CMDS

class KAKAOTALK_Test():

    def __init__(self, uuid, divide_window=10):

        super().__init__()
        self.cmd = CMDS(uuid, divide_window)
        self.limit_count = 0
        self.delay_time = 20
        self.dict_result = {}
        self.send_button_pos = None
        # self.display_flag = False
        # self.end_flag = False

    def launch_kakao(self):

        try:
            # check displayOn
            return_status = self.cmd.execute_cmd(self.cmd.getDisplayStatus)
            # displayOn 상태
            if "mholdingdisplaysuspendblocker=true" in return_status[1].lower():
                pass
            # display off 상태
            else:
                self.cmd.cmd_status_powerButton()

            # kakaotalk Run
            self.cmd.cmd_status_launchApp(name="com.kakao.talk")
            # check runing status
            status = self.cmd.cmd_status_currnetActivity(name="com.kakao.talk")
            if status != 1:
                while True:
                    self.cmd.cmd_status_backButton(iter_count=5)
                    self.cmd.cmd_status_launchApp(name="com.kakao.talk")
                    sleep(2)
                    status = self.cmd.cmd_status_currnetActivity(name="com.kakao.talk")
                    if status == 1:
                        self.cmd.save_dump_xml()
                        chat_room_pos = self.cmd.get_pos_elements(attr="resource-id",
                                                                  name="com.kakao.talk:id/chat_room_list_item")
                        self.cmd.cmd_status_click(width=chat_room_pos[0][0], height=chat_room_pos[0][1], pos_type="abs")
                        sleep(1)
                        # get pos 전송 버튼
                        self.cmd.cmd_status_sendKey(message="Find_Pos")
                        self.cmd.save_dump_xml()
                        self.send_button_pos = self.cmd.get_pos_elements(attr="content-desc", name="전송")
                        self.cmd.cmd_status_click(width=chat_room_pos[0][0],
                                                  height=chat_room_pos[0][1],
                                                  pos_type="abs")
                        break
            else:
                self.cmd.save_dump_xml()
                chat_room_pos = self.cmd.get_pos_elements(attr="resource-id",
                                                          name="com.kakao.talk:id/chat_room_list_item")
                self.cmd.cmd_status_click(width=chat_room_pos[0][0], height=chat_room_pos[0][1], pos_type="abs")
                sleep(1)
                # get pos 전송 버튼
                self.cmd.cmd_status_sendKey(message="Find_Pos")
                self.cmd.save_dump_xml()
                self.send_button_pos = self.cmd.get_pos_elements(attr="content-desc", name="전송")
                self.cmd.cmd_status_click(width=self.send_button_pos[0][0],
                                          height=self.send_button_pos[0][1],
                                          pos_type="abs")
            self.cmd.set_print("카카오톡 실행이 완료되었습니다.")
        except:
            self.cmd.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                                sys.exc_info()[1],
                                                                sys.exc_info()[2].tb_lineno))

    def run_script(self):

        try:
            # 필수 setup method 반드시 호출
            self.cmd.setup_test()
            # kakao talk 실행
            self.launch_kakao()
            # limit count 실행 Case
            if self.limit_count != 0:
                i = 0
                while i <= self.limit_count:
                    status = self.cmd.cmd_status_currnetActivity(name="com.kakao.talk")
                    if status != 1:
                        self.launch_kakao()
                    current_time = self.cmd.get_current_time()[1]
                    self.cmd.set_print("==================={} {}번 Test===================".format(current_time, i))
                    self.cmd.cmd_status_sendKey(message="Event_Test_{}_{}".format((i+1), current_time))
                    self.cmd.cmd_status_click(width=self.send_button_pos[0][0], height=self.send_button_pos[0][1])
                    i += 1
                    sleep(self.delay_time)
            # 무제한 실행 Case
            else:
                i = 0
                while True:
                    status = self.cmd.cmd_status_currnetActivity(name="com.kakao.talk")
                    if status != 1:
                        self.launch_kakao()
                    current_time = self.cmd.get_current_time()[1]
                    self.cmd.set_print("==================={} {}번 Test===================".format(current_time, i))
                    self.cmd.cmd_status_sendKey(message="Event_Test_{}_{}".format((i+1), current_time))
                    self.cmd.cmd_status_click(width=self.send_button_pos[0][0], height=self.send_button_pos[0][1])
                    i += 1
                    sleep(self.delay_time)

        except:
            self.cmd.set_print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                                sys.exc_info()[1],
                                                                sys.exc_info()[2].tb_lineno))


if __name__ == "__main__":

    kakao = KAKAOTALK_Test('RF9N604ZM0N', divide_window=10)
    kakao.run_script()