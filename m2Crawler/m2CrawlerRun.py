#-*- coding:utf-8 -*-

import os
import sys
import signal
import pandas as pd
import numpy as np
import threading
# import tkfilebrowser

from time import sleep
from os.path import expanduser
from datetime import datetime
from tkinter import *
# from tqdm import tqdm
from m2CrawlerSpider import SearchCrawl
from Check_Chromedriver import Check_Chromedriver
from apscheduler.schedulers.background import BackgroundScheduler

class ScrapRun():

    # 클레스 초기화
    def __init__(self):
        # self.dict_login = {"클리앙":["https://www.clien.net/service/", "glory019", "Qwer1234!"],
        # "뽐뿌":["https://www.ppomppu.co.kr/zboard/login.php?r_url=http%3A%2F%2Fwww.ppomppu.co.kr%2Fzboard%2Fzboard.php%3Fid%3Dphone", "glory019", "Qwer1234!"],
        # "네이버":["https://nid.naver.com/nidlogin.login?mode=form&url=https%3A%2F%2Fwww.naver.com", "testenc2018", "Qwer1234!"]}

        # self.df_default_sources = {'클리앙':'https://www.clien.net/service/', '뽐뿌':'http://www.ppomppu.co.kr/zboard/zboard.php?id=phone',
        # '디벨로이드':'https://cafe.naver.com/develoid/827731', '삼성스마트폰 커뮤니티':'https://cafe.naver.com/anycallusershow/'}
        # self.df_default_login = {'클리앙':['glory019','Qwer1234!'], '뽐뿌':['glory019','Qwer1234!'], '네이버':['testenc2018','Qwer1234!']}
        super().__init__()
        self.home = expanduser("~")
        self.df_general = None
        self.df_time = None
        self.df_mail = None
        self.df_login = None
        self.m2Spider = None
        self.sched_module = None

        self.dict_sources = {}
        self.dict_navigation = {}
        self.dict_findKey = {}
        self.dict_primary = {}
        self.dict_secondary = {}
        self.dict_exclude = {}
        self.dict_type = {}
        self.dict_crawl = {}
        self.dict_mail = {}

        self.naver_id = ""
        self.naver_pw = ""
        self.type = None
        self.cron_time = None
        self.interval = None
        self.job_size = 1
        self.sender_account = None
        self.sender_password = None
        self.recievers = None

        # self.root = Tk()
        # self.root.withdraw()

        # self.current_path = os.getcwd()
        self.home = expanduser("~")
        self.dir_pathes = None
        self.config_path = self.home+"\\Desktop\\Crawler\\config\\SearchForm.xlsx"
        self.driver_root_path = self.home+"\\Desktop\\Crawler\\driver\\"


    # 시간 정보와 함께 Console에 Print 하는 함수
    def setPrint(self, text):

        current = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        print("{}:\n{}\n".format(current, text))

    # 현재 시간 구하여 3가지 타입으로 list return
    def getCurrent_time(self):

        nowTime = datetime.now()
        nowtime_str = nowTime.strftime('%Y-%m-%d %H:%M:%S')
        nowtime_str_2 = nowTime.strftime('%Y-%m-%d %H %M %S')
        return [nowTime, nowtime_str, nowtime_str_2]

    # 구분자 포함을 확인한 후 배열로 리턴
    def setValue(self, value):

        check_value = str(value).strip()
        if check_value == 'nan' or check_value == '':
            return 'Null'
        else:
            if '|' in check_value:
                list_data = check_value.split('|')
                list_data = [x.strip() for x in list_data]
                return list_data
            else:
                return [check_value.strip()]

    # Config Excel 파일 read 함수
    def getConfigFile(self):

        # self.start_time = self.getCurrent_time()[2]
        self.df_general = pd.read_excel(self.config_path, sheet_name="General", engine="openpyxl")
        self.df_time = pd.read_excel(self.config_path, sheet_name="Time", engine="openpyxl")
        self.df_mail = pd.read_excel(self.config_path, sheet_name="Mail", engine="openpyxl")
        self.df_login = pd.read_excel(self.config_path, sheet_name="NaverLogin", engine="openpyxl")

        # naver login info
        self.naver_id = str(self.df_login.at[0, "아이디"]).strip()
        self.naver_pw = str(self.df_login.at[0, "비밀번호"]).strip()

        #General config data parsing
        for i in range(self.df_general.shape[0]):
            if pd.isnull(self.df_general.at[i,"도메인"]) and not pd.isnull(self.df_general.at[i,"URL"]):
                self.setPrint('도메인 이름을 비워둘 수 없습니다. Config 파일 "General" 시트를 확인해 주세요.')
                sys.exit(0)
            elif not pd.isnull(self.df_general.at[i,"도메인"]) and pd.isnull(self.df_general.at[i,"URL"]):
                self.setPrint('URL은 비워둘 수 없습니다. Config 파일 "General" 시트를 확인해 주세요.')
                sys.exit(0)
            else:
                dict_temp = {}
                key = str(self.df_general.at[i, "도메인"]).strip()

                dict_temp["URL"] = self.setValue(self.df_general.at[i, "URL"])

                dict_temp["타입"] = self.setValue(self.df_general.at[i, "타입"])
                dict_temp["검색어"] = self.setValue(self.df_general.at[i, "검색어"])
                dict_temp["네비게이션"] = self.setValue(self.df_general.at[i, "네비게이션"])
                dict_temp["PRIMARY_KEYS"] = self.setValue(self.df_general.at[i, "PRIMARY_KEYS"])
                dict_temp["SECONDARY_KEYS"] = self.setValue(self.df_general.at[i, "SECONDARY_KEYS"])
                dict_temp["EXCLUDE_KEYS"] = self.setValue(self.df_general.at[i, "EXCLUDE_KEYS"])
                self.dict_crawl[key] = dict_temp

        #Time config data parsing
        if pd.isnull(self.df_time.at[0, "타입"]):
            self.setPrint('시간 타입을 비워둘 수 없습니다. Config 파일 "Time" 시트를 확인해 주세요.')
            sys.exit(0)
        else:
            self.type = self.setValue(self.df_time.at[0, "타입"])
            self.cron_time = self.setValue(self.df_time.at[0, "시간(cron)"])
            self.interval = self.setValue(self.df_time.at[0, "간격(interval)"])

        #Mail config data parsing
        self.dict_mail["계정"] = self.setValue(self.df_mail.at[0, "계정"])
        self.dict_mail["아이디"] = self.setValue(self.df_mail.at[0, "아이디"])
        self.dict_mail["비밀번호"] = self.setValue(self.df_mail.at[0, "비밀번호"])
        self.dict_mail["수신처"] = self.setValue(self.df_mail.at[0, "수신처"])

    # 생성자 초기화
    def reset_config(self):

        self.df_general = None
        self.df_time = None
        self.df_mail = None
        self.df_data = None
        self.dict_sources = {}
        self.dict_navigation = {}
        self.dict_findKey = {}
        self.dict_primary = {}
        self.dict_secondary = {}
        self.dict_exclude = {}
        self.start_time = ""
        self.end_time = ""
        self.terms = 30
        self.sender_account = ""
        self.sender_password = ""
        self.recievers = []

    # 설치된 Chrome 버전 확인 후 전용 Driver 자동 Download
    def set_driver(self):

        if not os.path.isdir(self.driver_root_path):
            os.makedirs(self.driver_root_path)

        Check_Chromedriver.driver_mother_path = self.driver_root_path
        Check_Chromedriver.main()

    # BackgroundScheduler에 타입(cron / interval)에 따른 스케쥴 등록
    def setting_jod(self, type, parameters):

        if type[0] == 'cron':
            if parameters[0] == "Null":
                self.sched_module.add_job(self.m2Spider.activate_spider, 'cron', hour="0-23", minute="0", id=str(self.job_size))
            else:
                self.job_size = len(parameters[0])
                for idx, item in enumerate(parameters[0]):
                    temp_time = str(item).split(":")
                    temp_hour = temp_time[0]
                    temp_minute = temp_time[1]

                    if temp_minute == '00':
                        temp_minute = '0'
                    elif temp_minute[0] == '0':
                        temp_minute = temp_minute[1:]

                    self.sched_module.add_job(self.m2Spider.activate_spider, 'cron', hour=temp_hour, minute=temp_minute, id=str(idx))

        else:
            if parameters[1] == "Null":
                self.sched_module.add_job(self.m2Spider.activate_spider, 'interval', hours=1, id=str(self.job_size))
            else:
                temp_minute = int(parameters[1][0])
                self.sched_module.add_job(self.m2Spider.activate_spider, 'interval', minutes=temp_minute, id=str(self.job_size))


    def start(self):

        self.introText = """
        #################################################-WEB CRAWLER-#############################################

            1. 웹 모니터링 자동 Crawler 프로그램 입니다.
            2. 해당 프로그램은 Google Chrome이 설치되어 있어야 합니다.
            3. 시간 및 간격 Config 정보 파일을(SearchForm.xlsx) 바탕화면/Crawler 폴더에 준비하셔야 합니다.
            4. Config 파일의 'General'에 소스명과 URL이 명시되어 있어야 합니다.
            5. 디벨로이드 경우 검색어에 검색해야 할 키워드를 명시하셔야 합니다.
            6. Naver Cafe인 경우 네이버 네비게이션에 메뉴명 키워드 일부를 명시해야 합니다.
            7. Config 파일의 'Time'에 '시작시간'과 '종료시간'을 명시하면 특정 시간에 동작하게 됩니다.(Optional)
            8. 간격은 분단위로 입력해주시고 해당 간격으로 소스를 순회하며 모니터링 합니다.(Report 주기)
            9. Config 파일의 'Time'에 보내는 계정/비밀번호와 메일 수신처에 대해 명시해야 합니다.

        ##########################################################################################################\n\n
        """

        print(self.introText)
        #Check File exists
        self.config_flag = os.path.isfile(self.config_path)


        #프로그램 진행 Process logic
        if self.config_flag:
            self.flag = input("Crawling을 진행 하시겠습니까?(y|n) : ")
            self.flag.lower()
            #check intro flag
            if self.flag == 'y':
                pass
            elif self.flag == 'n':
                self.setPrint("프로그램을 종료합니다.")
                sys.exit(0)
            else:
                while self.flag is not "y" and self.flag is not "n":
                    self.flag = input("잘못입력하셨습니다. \"y\" 또는 \"n\"을 입력하여 주세요. : ")
                    self.flag.lower()
                    if self.flag == 'n':
                        self.setPrint("프로그램을 종료합니다.")
                        sys.exit(0)
                    elif self.flag == 'y':
                        break
                    else:
                        pass
        else:
            self.setPrint("바탕화면의 'Crawler' 폴더 안에 'SearchForm.xlsx' 설정 엑셀 파일을 위치해 주시고 다시 시작해주세요.")
            sys.exit(0)

        # Chrome driver setting
        self.set_driver()
        # scheduler start
        self.sched_module = BackgroundScheduler()
        self.sched_module.start()
        # Config Data setting
        self.setPrint("설정 파일 경로: {}".format(self.config_path))
        self.getConfigFile()
        # Generate instance of spider
        self.m2Spider = SearchCrawl(self.dict_crawl, self.dict_mail, self.driver_root_path + "chromedriver.exe", self.naver_id, self.naver_pw)
        # Set scheduler job
        self.setting_jod(self.type, [self.cron_time, self.interval])

        # batch start
        while True:
            if not self.m2Spider.process_flag:
                self.setPrint("System error shut down program...")
                self.m2Spider.stop()
                self.sched_module.shutdown()
                sys.exit(0)
            elif not self.m2Spider.hold_flag:
                self.setPrint("Running crawling process..")
            sleep(120)

            # count += 1
            # if count == 10:
            #     scheduler.kill_scheduler("1")
            #     print("Kill cron Scheduler")
            # elif count == 15:
            #     scheduler.kill_scheduler("2")
            #     print("Kill interval Scheduler")
        # self.thread_crawl = threading.Thread(target=self.getCrawlData, args=())
        # self.thread_crawl.daemon = True
        # self.thread_crawl.start()
        # self.thread_crawl.join()


if __name__ == "__main__":

    scrap = ScrapRun()
    scrap.start()
