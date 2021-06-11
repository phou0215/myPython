#-*- coding:utf-8 -*-

import os
import sys
import os
import urllib
import keyB as kb
import string
import json
import re
import pywinauto
import threading
import pyperclip
import keyB as kb
import random
import pandas as pd

#utils
from pywinauto import application
from bs4 import BeautifulSoup
from Check_Chromedriver import Check_Chromedriver
from os.path import expanduser
from m2CrawlerMongoDB import ConnDB

from m2CrawlerSender import SendMail
from m2CrawlerReporter import ResultReport
from pywinauto.keyboard import send_keys, KeySequenceError
from datetime import date, time, datetime
from time import sleep
from urllib import parse

# Selenium library
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from pywinauto.application import Application
from selenium.common.exceptions import UnexpectedAlertPresentException


class SearchCrawl():

    # 클래스 초기화
    def __init__(self, dict_crawl, dict_mail, driver_path, naver_id, naver_pw):

        super().__init__()
        self.home = expanduser("~")
        self.process_flag = True
        self.hold_flag = False
        self.focus_flag = False
        self.start_time = ""
        self.end_time = ""
        # 각 카페에서 얻어진 dict 데이터를 해당 배열에 저장
        self.list_result = []
        self.list_upload_status = []
        self.wait_time = 15
        self.paging_num = 0
        self.delay_time = 2
        self.naver_id = naver_id
        self.naver_pw = naver_pw
        self.list_cols = ['bo_no', 'cafeName', 'nav', 'type', 'deviceName', 'reportDate', 'reportTime', 'regiDate', 'title',
                          'story', 'reply', 'cate', 'status', 'reply_num', 'view_num', 'story_url', 'img_url', 'video_url', 'uniqueId']

        self.dict_result = {}
        self.dict_crawl = dict_crawl
        self.dict_email = dict_mail
        self.chrome_driver_path = driver_path
        self.report_path = self.home+"\\Desktop\\Crawler\\report\\"
        self.image_path = self.home+"\\Desktop\\Crawler\\image\\"
        self.driver = None
        self.chrome_option = None
        self.wait = None
        self.myDB = ConnDB("localhost", 27017, None, None, "crawler")
        self.driver_app = None
        self.on_top_thread = None

    ############################################################################__공용 함수__############################################################################

    # 각종 산출물 폴더 생성
    def set_directory(self):

        now_time = self.getCurrent_time()[2]
        dir_report_name = 'report_'+now_time
        dir_image_name = 'images_'+now_time

        if not os.path.isdir(self.report_path):
            os.makedirs(self.report_path)
        if not os.path.isdir(self.image_path):
            os.makedirs(self.image_path)

        os.makedirs(self.report_path + dir_report_name)
        os.makedirs(self.image_path + dir_image_name)
        self.report_path = self.report_path + dir_report_name
        self.image_path = self.image_path + dir_image_name
        self.setPrint("Check and Generate Directory path...")

    # Chrome GUI Driver 생성
    def setDriver(self):
        try:
            self.chrome_option = webdriver.ChromeOptions()
            # self.chrome_option.add_argument('headless') 네이버 로그인 때문에 사용할 수 없음
            # applicable to windows os only
            self.chrome_option.add_argument('disable-gpu')
            # do not use extensions
            self.chrome_option.add_argument('disable-extensions')
            # do not use info-bar
            self.chrome_option.add_argument('disable-infobars')
            # security virtual space do not use
            self.chrome_option.add_argument('no-sandbox')
            # overcome limited resource problem
            self.chrome_option.add_argument('disable-dev-shm-usage')
            # self.chrome_option.add_argument('window-size=1920x1080')
            self.chrome_option.add_argument("start-maximized")
            self.chrome_option.add_argument('lang=ko_KR')
            self.chrome_option.add_argument('user-agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36')
            self.driver = webdriver.Chrome(self.chrome_driver_path, options=self.chrome_option)
            self.driver.implicitly_wait(10)
            self.wait = WebDriverWait(self.driver, self.wait_time)
            self.driver_app = None
            self.setPrint("Generated Chrome Driver is Success...")
        except:
            self.setPrint('Occurred Error at generate chrome driver spot!')
            self.setPrint('Error Occurred : {}. {}, line: {}'.format(sys.exc_info()[0],
                                                                     sys.exc_info()[1],
                                                                     sys.exc_info()[2].tb_lineno))
            self.process_flag = False
    # 설치된 Chrome 버전 확인 후 전용 Driver 자동 Download

    def set_driver(self):

        if not os.path.isdir(self.driver_root_path):
            os.makedirs(self.driver_root_path)

        Check_Chromedriver.driver_mother_path = self.driver_root_path
        Check_Chromedriver.main()
        self.chrome_driver_path = self.driver_root_path + "chromedriver.exe"
    # always fixed chrome driver browser until finished crwaling

    # set focus fixed on the remote chrome window
    def set_on_focus(self):

        # self.driver_app.top_window().set_focus()
        # self.driver.execute_script("window.focus();")

        while True:
            if not self.focus_flag:
                break
            w_handle = pywinauto.findwindows.find_windows(title_re=r'.*Chrome.*')[0]
            window = self.driver_app.window(handle=w_handle)
            window.set_focus()
            sleep(0.5)

    # Connect DB
    def set_connDB(self):

        conn_flag = self.myDB.set_connect()
        if not conn_flag:
            self.stop()
            self.process_flag = False

    # clear storage cache and sessions
    def clear_storage(self):
        self.driver.execute_script('window.localStorage.clear()')
        self.driver.execute_script('window.sessionStorage.clear()')
        self.driver.delete_all_cookies()

    # spider 함수 종료 시 Teardown
    def stop(self):

        self.focus_flag = False
        self.hold_flag = False
        sleep(2)
        self.driver.quit()
        self.setPrint("Stop the Chrome Browser")
        self.myDB.stop()
        self.setPrint("Disconnect MongoDB server")
        self.report_path = self.home+"\\Desktop\\Crawler\\report\\"
        self.image_path = self.home+"\\Desktop\\Crawler\\image\\"
        self.list_result = []
        self.list_upload_status = []
        self.driver = None
        self.chrome_option = None

    # ConnMyDB Teardown
    def conn_teardown(self):

        self.conn.stop()
        self.conn = None

    # 시간 정보와 함께 Console에 Print 하는 함수
    def setPrint(self, text):

        current = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        print("{}:\n{}".format(current, text)+"\n")

    # 문장 맨앞에서부터 서치하여 특이 지점까지 문자열 parsing
    def find_between(self, s, first, last):
        try:
            start = s.index(first)+len(first)
            end = s.index(last, start)
            return_data = s[start:end]
            return return_data
        except ValueError:
            return return_data

    # 문장 맨뒤에서부터 서치하여 특이 지점까지 문자열 parsing
    def find_between_r(self, s, first, last ):
        try:
            start = s.rindex(first)+len(first)
            end = s.rindex(last, start)
            return_data = s[start:end]
            return return_data
        except ValueError:
            return return_data

    # 특수문자 제거
    def removeString(self, text):

        try:
            text_data = re.sub('[-=+,_#/\?^$@*\"※~&%ㆍ!』\‘|\(\)\[\]\<\>\{\}`><\']', '', text)
            # text_data = text_data.lower()
            text_data = text_data.strip()
            # temp_text = temp_text.encode('utf-8').decode('utf-8')
            return text_data
        except:
            self.setPrint('Error occurred : {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno))
            return text

    # ctrl+v 구현 붙여넣기 함수
    def clipboard_input(self, user_xpath, user_input):
            # self.temp_user_input = pyperclip.paste()  # 사용자 클립보드를 따로 저장
            pyperclip.copy(user_input)
            self.driver.find_element_by_xpath(user_xpath).click()
            sleep(2)
            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()

            # pyperclip.copy(self.temp_user_input)  # 사용자 클립보드에 저장 된 내용을 다시 가져 옴
            sleep(1)

    # 현재 시간 구하여 3가지 타입으로 list return
    def getCurrent_time(self):

        nowTime = datetime.now()
        now_datetime_str = nowTime.strftime('%Y-%m-%d %H:%M:%S')
        now_datetime_str2 = nowTime.strftime('%Y-%m-%d %H %M %S')
        return [nowTime, now_datetime_str, now_datetime_str2]

    # date format check
    def date_validate(self, text, type):
        try:
            return_date = None
            if type == 'date':
                return_date = datetime.strptime(text, '%Y-%m-%d')
            else:
                return_date = datetime.strptime(text, '%Y-%m-%d %H:%M:%S')
            return [True, return_date]
        except ValueError:
            return [False, return_date]

    # time format check
    def time_validate(self, text):
        try:
            return_time = datetime.strptime(text, '%H:%M:%S')
            return [True, return_time]
        except ValueError:
            return [False, None]

    # unique 아이디 생성 함수
    def generate_id(self):

        charset = string.ascii_uppercase + string.digits
        uniqueId = ''.join(random.sample(charset * 15, 15))
        return uniqueId

    # ##########################################################################__URL 인코더__############################################################################

    # URL 페이지 값 인코딩 값
    def encoding_url(self, path):

        return_path = path
        if 'http:' in return_path or 'https:' in return_path:
            pass
        else:
            finder = re.findall('^/{2}', return_path)
            if finder:
                return_path = 'http:' + return_path
            else:
                return_path = 'http://' + return_path
        return return_path

    #Save image 파일
    def img_downloader(self, type, url, path, filename):

        try:
            # img = self.driver.find_element_by_xpath('//div[@id="recaptcha_image"]/img')
            # file name example "captcha.png"
            img = None
            if type == 'css':
                img = self.driver.find_element_by_css_selector(url)
            else:
                img = self.driver.find_element_by_xpath(url)

            src = img.get_attribute('src')
            # download the image
            urllib.urlretrieve(src, path+"\\"+filename)
            return True
        except:
            self.setPrint('Occurred Error at saving image')
            self.setPrint('Error Occurred : {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno))
            return False

    # ##########################################################################__Naver 로그인__###########################################################################

    # 네이버 로그인 retry
    def retry_login(self):

        # find elements needs
        # self.driver.switch_to.frame(element)
        login_url1 = "https://nid.naver.com/nidlogin.login"
        login_url2 = "https://nid.naver.com/nidlogin.login?mode=form&url=https%3A%2F%2Fwww.naver.com"
        home_url = "https://www.naver.com/"
        flag_status = False

        for i in range(3):
            current_home = self.driver.current_url
            self.setPrint('현재위치: {}'.format(current_home))
            if current_home == home_url:
                self.setPrint("Naver Login Success!")
                flag_status = True
                break

            elif current_home == login_url1 or current_home == login_url2:

                ele_id = self.driver.find_element_by_css_selector('#id')
                ele_pw = self.driver.find_element_by_css_selector('#pw')
                ele_summit = self.driver.find_element_by_css_selector('#log\.login')
                self.action_wait(mode='id', ele_val='id')
                ele_id.clear()
                ele_id.click()
                sleep(self.delay_time)
                kb.typer(self.naver_id)
                sleep(self.delay_time)
                ele_pw.clear()
                ele_pw.click()
                # self.driver.execute_script("arguments[0].click();", self.ele_pw)
                kb.typer(self.naver_pw)
                sleep(self.delay_time)

                # login id and password print values
                self.setPrint('{} 회 로그인 시도'.format(i+1))
                self.setPrint('로그인 아이디 : {}'.format(ele_id.get_attribute('value')))
                self.setPrint('로그인 비밀번호 : {}'.format(ele_pw.get_attribute('value')))
                self.driver.execute_script("arguments[0].click();", ele_summit)
                sleep(self.delay_time)

            else:
                break

        return flag_status

    # 네이버 로그인 함수(activate_crawler 실행 시 앞서 먼저 실행됨)
    def naver_login(self):

        try:
            self.driver.get("https://nid.naver.com/nidlogin.login")
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#id')))
            #clear storage
            self.clear_storage()
            # chrome on top Thread
            self.driver_app = application.Application(backend='uia').connect(path=self.chrome_driver_path)
            self.on_top_thread = threading.Thread(target=self.set_on_focus, args=())
            self.on_top_thread.setDaemon(True)
            self.on_top_thread.start()

            flag = self.retry_login()
            if not flag:
                self.process_flag = False
        except:
            self.setPrint('Occurred Error at naver login spot!')
            self.setPrint('Error Occurred : {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno))
            self.process_flag = False

    # ########################################################################_Selenium action__##########################################################################
    # window switch handler 함수
    def switch_window(self, index):

        # window_before = driver.window_handles[0]
        # window_after = driver.window_handles[1]
        # driver.switch_to_window(window_after)
        try:
            temp_windows = self.driver.window_handles[index]
            self.driver.switch_to.window(temp_windows)
            self.setPrint('Success windows switching to {}'.format(index))
            return True
        except:
            self.setPrint("Occurred Error at window switch spot!")
            return False

    # 현재 페이지 이외 페이지 닫기 함수
    def close_window(self, mode=1, idx=[1]):

        # every windows
        list_windows = self.driver.window_handles
        # main_window = self.driver.current_window_handle
        if mode == 1:
            windows_size = len(list_windows)
            for i in range(windows_size):
                if i != 0:
                    self.driver.switch_to.window(list_windows[i])
                    list_windows[i].close()
        else:
            for item in idx:
                self.driver.switch_to.window(list_windows[item])
                list_windows[item].close()
        self.driver.switch_to.window(list_windows[0])
        self.driver.switch_to.frame(0)

    # click event 함수
    def action_click(self, mode='css', ele_val='', ele_parent=None, idx=0):
        # object 결정
        obj = self.driver
        if ele_parent:
            obj = ele_parent

        if mode == 'css':
            target_element = obj.find_elements_by_css_selector(ele_val)
            target_element[idx].click()
        elif mode == 'id':
            target_element = obj.find_elements_by_id(ele_val)
            target_element[idx].click()
        elif mode == 'class':
            target_element = obj.find_elements_by_class_name(ele_val)
            target_element[idx].click()
        else:
            target_element = obj.find_elements_by_xpath(ele_val)
            target_element[idx].click()

    # scroll event 함수
    def action_scroll(self, direction='down', mode='css', ele_val='', ele_parent=None, idx=0):

        # object 결정
        obj = self.driver
        if ele_parent:
            obj = ele_parent

        if ele_val == '':
            if direction == 'down':
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            else:
                self.driver.execute_script("window.scrollTo(0,0);")
        else:
            if direction == 'down':
                if mode == 'css':
                    target_element = obj.find_elements_by_css_selector(ele_val)
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({behavior: 'smooth', block: 'end', inline: 'nearest'});",
                        target_element[idx])
                elif mode == 'id':
                    target_element = obj.find_elements_by_id(ele_val)
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({behavior: 'smooth', block: 'end', inline: 'nearest'});",
                        target_element[idx])
                elif mode == 'class':
                    target_element = obj.find_elements_by_class_name(ele_val)
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({behavior: 'smooth', block: 'end', inline: 'nearest'});",
                        target_element[idx])
                else:
                    target_element = obj.find_elements_by_xpath(ele_val)
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({behavior: 'smooth', block: 'end', inline: 'nearest'});",
                        target_element[idx])
            else:
                if mode == 'css':
                    target_element = obj.find_elements_by_css_selector(ele_val)
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({behavior: 'smooth', block: 'start', inline: 'nearest'});",
                        target_element[idx])
                elif mode == 'id':
                    target_element = obj.find_elements_by_id(ele_val)
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({behavior: 'smooth', block: 'start', inline: 'nearest'});",
                        target_element[idx])
                elif mode == 'class':
                    target_element = obj.find_elements_by_class_name(ele_val)
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({behavior: 'smooth', block: 'start', inline: 'nearest'});",
                        target_element[idx])
                else:
                    target_element = obj.find_elements_by_xpath(ele_val)
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({behavior: 'smooth', block: 'start', inline: 'nearest'});",
                        target_element[idx])

    # page move 함수
    def action_page_move(self, mode='back'):
        # driver.execute_script("window.history.go(-1)")
        if mode == 'back':
            self.driver.back()
        else:
            self.driver.forward()

    # wait element 함수
    def action_wait(self, mode='css', ele_val=''):

        try:
            # self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#btn_logout > span')))
            if mode == 'css':
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ele_val)))
            elif mode == 'id':
                self.wait.until(EC.presence_of_element_located((By.ID, ele_val)))
            elif mode == 'class':
                self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, ele_val)))
            else:
                self.wait.until(EC.presence_of_element_located((By.XPATH, ele_val)))
        except:
            self.setPrint('Error Occurred : {}. {}, line: {}'.format(sys.exc_info()[0],
                                                                     sys.exc_info()[1],
                                                                     sys.exc_info()[2].tb_lineno))

    # elements 검사 함수
    def is_element(self, mode='css', ele_val='', ele_parent=None):

        # object 결정
        target_element = []
        obj = self.driver
        if ele_parent:
            obj = ele_parent
        try:
            if mode == 'css':
                target_element = obj.find_elements_by_css_selector(ele_val)
            elif mode == 'id':
                target_element = obj.find_elements_by_id(ele_val)
            elif mode == 'class':
                target_element = obj.find_elements_by_class_name(ele_val)
            else:
                target_element = obj.find_elements_by_xpath(ele_val)
            # elements length 확인
            if len(target_element) == 0:
                return False
            else:
                return True
        except:
            return False

    # element 추출 함수
    def get_elements(self, mode='css', ele_val='', ele_parent=None):

        # object 결정
        obj = self.driver
        if ele_parent:
            obj = ele_parent

        return_ele = None
        try:
            if mode == 'css':
                return_ele = obj.find_elements_by_css_selector(ele_val)
            elif mode == 'id':
                return_ele = obj.find_elements_by_id(ele_val)
            elif mode == 'class':
                return_ele = obj.find_elements_by_class_name(ele_val)
            else:
                return_ele = obj.find_elements_by_xpath(ele_val)
            return return_ele
        except:
            return return_ele

    # page tile 추출 함수
    def get_title(self):

        title = self.driver.title
        return title

    # 이미지 스크린샷 생성 함수
    def get_screenshot_obj(self, file_name):

        try:
            self.driver.save_screenshot(self.image_path + "\\" + file_name + ".png")
            self.setPrint("Capture Screen Shot and Save file at {}".format(file_name + ".png"))
            return True
        except:
            self.setPrint('Error Occurred : {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1],
                                                                     sys.exc_info()[2].tb_lineno))
            return False

    # inner text 값 check
    def equal_text(self, mode='css', ele_val='', ele_parent=None, val='', idx=0):

        # object 결정
        obj = self.driver
        if ele_parent:
            obj = ele_parent

        origin_val = ''
        if mode == 'css':
            target_element = obj.find_elements_by_css_selector(ele_val)
            origin_val = target_element[idx].text
        elif mode == 'id':
            target_element = obj.find_elements_by_id(ele_val)
            origin_val = target_element[idx].text
        elif mode == 'class':
            target_element = obj.find_elements_by_class_name(ele_val)
            origin_val = target_element[idx].text
        else:
            target_element = obj.find_elements_by_xpath(ele_val)
            origin_val = target_element[idx].text

        if origin_val.strip() == val.strip():
            return True
        else:
            return False

    # check attribute value equal
    def equal_attribute(self, mode='css', ele_val='', ele_parent=None, attr_name='', val='', idx=0):

        # object 결정
        obj = self.driver
        if ele_parent:
            obj = ele_parent

        origin_val = ''
        if mode == 'css':
            target_element = obj.find_elements_by_css_selector(ele_val)
            origin_val = target_element[idx].get_attribute(attr_name)
        elif mode == 'id':
            target_element = obj.find_elements_by_id(ele_val)
            origin_val = target_element[idx].get_attribute(attr_name)
        elif mode == 'class':
            target_element = obj.find_elements_by_class_name(ele_val)
            origin_val = target_element[idx].get_attribute(attr_name)
        else:
            target_element = obj.find_elements_by_xpath(ele_val)
            origin_val = target_element[idx].get_attribute(attr_name)

        if origin_val.strip() == val.strip():
            return True
        else:
            return False

    # iframe 변경 함수
    def change_frame(self, element=None, mode=1):

        if mode == 1:
            self.driver.switch_to.frame(element)
        else:
            self.driver.switch_to.default_content()

    # boarder num compare
    def compared_num(self, base_num, boarder_num):

        if base_num < boarder_num:
            return False
        else:
            return True

    # reportDate 및 reportTime 생성 함수
    def get_date_sc(self, text):

        list_return = text.split()
        list_return[0] = list_return[0][0:len(list_return[0]) - 1]
        list_return[0] = list_return[0].replace('.', '-')
        return list_return

    # 당일인지 확인
    def check_today(self, text):

        if ":" in text:
            return False
        else:
            return True

    # ##########################################################################_본문 Parsing__###########################################################################

    # 삼성커뮤니티 본문 글 정리 함수
    def get_main_article_sc(self):

        sleep(self.delay_time)
        html_source = self.driver.page_source
        soup = BeautifulSoup(html_source, "html.parser")
        story_text = ''
        img_url_text = ''
        video_url_text = ''
        reply_text = ''
        nhn_video_url = 'https://serviceapi.nmv.naver.com/view/ugcPlayer.nhn?vid={}&inkey={}&wmode=opaque&hasLink=0&autoPlay=false&beginTime=0'

        # get_attribute('attribute name')
        # 게시글 타입이 두개로 나뉨
        #   1. div.article_container > div.article_viewer > div.ContentRenderer 이게 존재하면
        #       - div.article_container > div.article_viewer > div.ContentRenderer > div > p ==> 게시글
        #       - div.article_container > div.article_viewer > div.ContentRenderer > div > img ==> 이미지(attribute => src)
        #       - div.article_container > div.article_viewer > div.ContentRenderer > div > iframe ==> video(attribute => src)
        #       - div.article_container > div.article_viewer > div.ContentRenderer > div > div.NHN_Writeform_Main 이면
        #         하단의 div 또는 p 테그들의 text 값을 추출
        #         하단에 img는 src 추출 image url
        #         하단에 iframe이면 src 추출 video_url

        #   2. div.article_container > div.article_viewer > div.se-viewer 이게 존재하면
        #      - text elements
        #        div.article_container > div.article_viewer > div:nth-child(2) > div.content.CafeViewer > div > div > div.se-text
        #        그 하위에 div > div > div > p Tag들 밑에 각각의 span tag의 text이며 만약 값이 비어 있으면 줄바꿈으로 변경
        #      - img elements
        #        div.article_container > div.article_viewer > div:nth-child(2) > div.content.CafeViewer > div > div > div.se-image
        #        그 하위에 div > div > div > a > img의 src 값
        #      - video elements
        #        div.article_container > div.article_viewer > div:nth-child(2) > div.content.CafeViewer > div > div > div.se-video
        #        그 하위의 div > script tag에서 attribute => data-module의 값을 json.load를 통해 dict로 변환한 후 data의 'vid'와 'inkey'를 획득한 후
        #        'https://serviceapi.nmv.naver.com/view/ugcPlayer.nhn?vid={}&inkey={}&wmode=opaque&hasLink=0&autoPlay=false&beginTime=0'에
        #        대입하여 url를 만들고 저장

        try:
            render = soup.select('div.ContentRenderer')
            se_viewer = soup.select('div.se-viewer')
            #########################################################__ContentRenderer 타입__###################################################
            if render:
                self.setPrint('분석결과: ContentRender 타입')

                # text 값이 있으면 값을 모두 획득
                p_tags = render[0].select('div > p')
                img_tag = render[0].select('div > img')
                iframe_tag = render[0].select('div > iframe')
                nhn_tag = render[0].select('div.NHN_Writeform_Main')

                if p_tags:

                    for ele in p_tags:
                        line = ele.text
                        if line == '':
                            story_text = story_text+'\n'
                        else:
                            story_text = story_text + line.strip()

                # 이미지가 있으면 src url 모두 획득
                if img_tag:

                    for idx, ele in enumerate(img_tag):
                        try:
                            url = ele['src']
                            url = self.encoding_url(url)
                            img_url_text = img_url_text + str(idx+1) + '. ' + str(url) + '\n'
                        except:
                            continue

                # 동영상이 있으면 src url 모두 획득
                if iframe_tag:

                    for idx, ele in enumerate(iframe_tag):
                        try:
                            url = ele['src']
                            url = self.encoding_url(url)
                            video_url_text = video_url_text + str(idx+1) + '. ' + str(url) + '\n'
                        except:
                            continue

                # NHN_Writeform이면 해당 로직 실행
                if nhn_tag:

                    # p tag 있다면 text 합
                    if nhn_tag[0].select('p'):
                        p_tags = nhn_tag[0].select('p')
                        for ele in p_tags:
                            line = ele.text
                            if line == '':
                                story_text = story_text+'\n'
                            else:
                                story_text = story_text + line.strip()

                    # div tag 있다면 text 합
                    if nhn_tag[0].select('div'):
                        div_tags = nhn_tag[0].select('div')
                        for ele in div_tags:
                            line = ele.text
                            if line == '':
                                story_text = story_text+'\n'
                            else:
                                story_text = story_text + line.strip()

                    # img tag 있다면 src url 모두 획득
                    if nhn_tag[0].select('img'):
                        img_tags = nhn_tag.select('img')
                        for idx, ele in enumerate(img_tags):
                            try:
                                url = ele['src']
                                url = self.encoding_url(url)
                                img_url_text = img_url_text + str(idx+1) + '. ' + str(url) + '\n'
                            except:
                                continue

                    # 동영상이 있으면 src url 모두 획득
                    if nhn_tag[0].select('iframe'):
                        iframe_tags = nhn_tag[0].select('iframe')
                        for idx, ele in enumerate(iframe_tags):
                            try:
                                url = ele['src']
                                url = self.encoding_url(url)
                                video_url_text = video_url_text + str(idx+1) + '. ' + str(url) + '\n'
                            except:
                                continue
            #########################################################__se viewer 타입__#########################################################
            elif se_viewer:

                self.setPrint('분석결과: SE_Viewer 타입')
                # get se-viewer element
                span_tags = se_viewer[0].select('div.se-main-container div.se-text p > span')
                img_tags = se_viewer[0].select('div.se-main-container div.se-image img')
                script_tags = se_viewer[0].select('div.se-main-container div.se-video script')
                # text 값이 있으면 값을 모두 획득
                if span_tags:
                    for ele in span_tags:
                        line = ele.text
                        if line == '':
                            story_text = story_text+'\n'
                        else:
                            story_text = story_text + line.strip() + '\n'

                # 이미지가 있으면 src url 모두 획득
                if img_tags:
                    for idx, ele in enumerate(img_tags):
                        try:
                            url = ele['src']
                            url = self.encoding_url(url)
                            img_url_text = img_url_text + str(idx+1) + '. ' + str(url) + '\n'
                        except:
                            continue

                # 동영상이 있으면 src url 모두 획득
                if script_tags:
                    for idx, ele in enumerate(script_tags):
                        data_module = ele['data-module']
                        if data_module == '':
                            continue
                        else:
                            try:
                                dict_module = json.loads(data_module)
                                vid = dict_module['data']['vid']
                                inkey = dict_module['data']['inkey']
                                video_url_text = video_url_text + str(idx+1) + '. ' + str(nhn_video_url.format(vid, inkey)) + '\n'
                            except:
                                continue
            #######################################################__해당사항 없음 타입__#########################################################
            else:
                self.setPrint('분석결과: Unknown 타입 Parsing Pass')
                pass

            ############################################################__댓글 값 추출__#########################################################
            reply = soup.select('div.CommentBox')
            # 댓글 값 확인
            if reply:
                list_items = reply[0].select('li.CommentItem')

                for idx, item in enumerate(list_items):
                    try:
                        list_reply_comment = item.select('span.text_comment')
                        list_reply_img = item.select('a.comment_image_link > img')
                        reply_info = item.select('span.comment_info_date')

                        # text만 있을 경우
                        if list_reply_comment and not list_reply_img:
                            reply_text = reply_text + str(idx+1) + ". " + list_reply_comment[0].text + "(" + reply_info[0].text + ")\n"
                        # 첨부 img만 있을 경우
                        elif list_reply_img and not list_reply_comment:
                            reply_text = reply_text + str(idx+1) + ". 첨부 이미지 : " + list_reply_img[0]['src'] + "(" + reply_info[0].text + ")\n"
                        # 이미지 text 모두 있을 경우
                        elif list_reply_img and list_reply_comment:
                            reply_text = reply_text + str(idx+1) + ". " + list_reply_comment[0].text + "\n"
                            reply_text = reply_text + '첨부 이미지 : ' + list_reply_img[0]['src'] + "(" + reply_info[0].text + ")\n"
                        else:
                            continue
                    except:
                        continue
            # 페이지 대기
            sleep(self.delay_time)
            # return values
            return [story_text, img_url_text, video_url_text, reply_text]
        except:
            error_message = '본문 내용 정리 중 에러 발생 : {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno)
            return [error_message, '', '', '']

    # 삼성메인커뮤니티 본문 글 정리 함수
    def get_main_article_sm(self):

        try:
            sleep(self.delay_time)
            html_source = self.driver.page_source
            soup = BeautifulSoup(html_source, "html.parser")
            story_text = ''
            img_url_text = ''
            video_url_text = ''
            reply_text = ''
            # get_attribute('attribute name')
            # div.lia-quilt-layout-custom-message의 elements에서 첫 엘레먼트가 본문내용
            # 나머지는 댓글 엘러먼트로 추출
            # 본문 내용 lia-message-body-content에서
            # 이미지의 경우 span.lia-inline-image-display-wrapper > span > img의 src 값
            # 본문의 경우 p tag에 있는 경우와 div tag에 있는 경우가 있어 이를 두개 모두 가져와야 함
            # 동영상의 경우 a tag video-embed-link가 있는 경우 해당 href attr 값 추출
            # 기본적으로 beautifulsoup '.text'를 쓸 경우 child 노드에 있는 text 까지 모두 얻어옴 만약 해당 레벨에서만 얻고자 하면 find_all(text=True, recursive=False)로 만들어 쓰면 list로 반환 됨

            renders = soup.select('div.lia-linear-display-message-view')
            main = renders[0].select('div.lia-message-body-content')
            replys = renders[1:]
            # 본문내용 정리(lia-message-body-content 값 Text 물론 모든 div tag 값 text 붙이기)
            # div_tags = main[0].select('div')
            # p_tags = main[0].select('p')
            img_tag = main[0].select('span.lia-inline-image-display-wrapper > span > img')
            video_tag = main[0].select('a.video-embed-link')
            # text가 있으면 모두 추출(div tag and p tag 포함)
            story_text = story_text + main[0].text.strip()
            # if div_tags:
            #     for ele in div_tags:
            #         line = ele.text
            #         if line == '':
            #             story_text = story_text+'\n'
            #         else:
            #             story_text = story_text + line.strip()
            # if p_tags:
            #     for ele in p_tags:
            #         line = ele.text
            #         if line == '':
            #             story_text = story_text+'\n'
            #         else:
            #             story_text = story_text + line.strip()

            # 이미지가 있으면 src url 모두 획득
            if img_tag:
                for idx, ele in enumerate(img_tag):
                    try:
                        url = ele['src']
                        url = self.encoding_url(url)
                        img_url_text = img_url_text + str(idx+1) + '. ' + str(url) + '\n'
                    except:
                        continue
            # 동영상이 있으면 src url 모두 획득
            if video_tag:
                for idx, ele in enumerate(video_tag):
                    try:
                        url = ele['href']
                        url = self.encoding_url(url)
                        video_url_text = video_url_text + str(idx+1) + '. ' + str(url) + '\n'
                    except:
                        continue

            ############################################################__댓글 값 추출__#########################################################

            # 댓글 값 확인
            if replys:
                for idx, item in enumerate(replys):

                    # reply 날짜 형식 변경
                    reportDate_str = item.select('span.local-date')[1].text
                    reportDate_str = re.findall('[0-9]{2}-[0-9]{2}-[0-9]{4}', reportDate_str)
                    reportDate_date = datetime.strptime(reportDate_str[0], "%m-%d-%Y")
                    # reply 시간 형식 변경
                    reportTime_str = item.select('span.local-time')[1].text
                    reportTime_str = re.sub('(AM|PM|am|pm)', '', reportTime_str)
                    # 최종 값
                    reply_info = reportDate_date.strftime("%Y-%m-%d") + ' ' + reportTime_str
                    reply_main = item.select('div.lia-message-body-content')
                    reply_text = reply_text + str(idx+1) + ". " + reply_main[0].text.strip() + "(" + reply_info + ")\n"
            # 페이지 대기
            sleep(self.delay_time)
            # return values
            return [story_text, img_url_text, video_url_text, reply_text]
        except:
            error_message = '본문 내용 정리 중 에러 발생 : {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1],
                                                                         sys.exc_info()[2].tb_lineno)
            return [error_message, '', '', '']

    # 뽐뿌 본문 글 정리 함수
    def get_main_article_pp(self):

        html_source = self.driver.page_source
        soup = BeautifulSoup(html_source, "html.parser")
        story_text = ''
        img_url_text = ''
        video_url_text = ''
        reply_text = ''
        # get_attribute('attribute name')
        # div.lia-quilt-layout-custom-message의 elements에서 첫 엘레먼트가 본문내용
        # 나머지는 댓글 엘러먼트로 추출
        # 본문 내용 lia-message-body-content에서
        # 이미지의 경우 span.lia-inline-image-display-wrapper > span > img의 src 값
        # 본문의 경우 p tag에 있는 경우와 div tag에 있는 경우가 있어 이를 두개 모두 가져와야 함
        # 동영상의 경우 a tag video-embed-link가 있는 경우 해당 href attr 값 추출
        # 기본적으로 beautifulsoup '.text'를 쓸 경우 child 노드에 있는 text 까지 모두 얻어옴 만약 해당 레벨에서만 얻고자 하면 find_all(text=True, recursive=False)로 만들어 쓰면 list로 반환 됨

        renders = soup.select('td.board-contents')
        # 본문 내용이 있는 경우
        if renders:
            try:
                stories = renders[0].text
                replys = soup.select('div.comment_wrapper')
                img_tag = renders[0].select('img')
                video_tag = renders[0].select('iframe')
                # text가 있으면 모두 추출(div tag and p tag 포함)
                story_text = stories.strip()

                # 이미지가 있으면 src url 모두 획득
                if img_tag:
                    for idx, ele in enumerate(img_tag):
                        try:
                            url = ele['src']
                            url = self.encoding_url(url)
                            img_url_text = img_url_text + str(idx+1) + '. ' + str(url) + '\n'
                        # except KeyError:
                        except:
                            continue

                # 동영상이 있으면 src url 모두 획득
                if video_tag:
                    for idx, ele in enumerate(video_tag):
                        try:
                            url = ele['src']
                            url = self.encoding_url(url)
                            video_url_text = video_url_text + str(idx+1) + '. ' + str(url) + '\n'
                        # except KeyError:
                        except:
                            continue

                ############################################################__댓글 값 추출__#########################################################
                # soup.select('a[href*=london]')  # contains "london"
                # soup.select('a[href$=d12]')  # ends with "d12"
                # soup.select('a[href^=/city/london]')  # starts with "city/london"
                # 댓글 값 확인
                if replys:
                    for idx, item in enumerate(replys):
                        reply_item = item.select('div.comment_line')
                        for idx2, item2 in enumerate(reply_item):
                            # reply 날짜 형식 변경
                            date_str = ''
                            time_str = ''
                            reportDate_raw = item2.select('font.eng-day')[0].text.strip()
                            reportDate_str = re.findall('[0-9]{4}-[0-9]{2}-[0-9]{2}', reportDate_raw)
                            reportTime_str = re.findall('[0-9]{2}:[0-9]{2}:[0-9]{2}', reportDate_raw)
                            # date value check null
                            if len(reportDate_str) == 0:
                                date_str = ''
                            else:
                                date_str = reportDate_str[0]
                            # time value check null
                            if len(reportTime_str) == 0:
                                time_str = ''
                            else:
                                time_str = reportTime_str[0]
                            # 최종 값

                            reply_info = date_str + ' ' + time_str
                            reply_main = item2.select('div[id*=commentContent_]')[0].text.strip()
                            reply_text = reply_text + str(idx+1) + '-' + str(idx2+1) + ". " + reply_main + "(" + reply_info + ")\n"
                # 페이지 대기
                sleep(self.delay_time)
                # return values
                return [story_text, img_url_text, video_url_text, reply_text]
            except:
                error_message = '본문 내용 정리 중 에러 발생 : {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno)
                return [error_message, '', '', '']

        # 회원 전용 글의 경우
        else:
            return ['회원전용 글 내용 무', img_url_text, video_url_text, reply_text]

    # 클리앙 본문 글 정리 함수
    def get_main_article_cl(self):

        html_source = self.driver.page_source
        soup = BeautifulSoup(html_source, "html.parser")
        story_text = ''
        img_url_text = ''
        video_url_text = ''
        reply_text = ''
        # get_attribute('attribute name')
        # div.post_view 본문 내용
        # div.post_comment 댓글 내용
        # 본문 내용 div.post_view > article > div.post_article 에서 'p' 테그의 모든 text 긁어 오기
        # 이미지의 경우 div.post_view > article > div.post_articled에서 img.fr-dib fr-fil 의 src attr 값
        # 동영상의 경우 div.post_view > article > div.post_articled에서 iframe 있는 경우 해당 src attr 값 추출
        # 댓글의 경우 div.post_comment div.comment_row(여러개) span.timestamp 가 시간으로 노출(2020-10-04 23:38:02) 내용은  div.comment_row(여러개) div.comment_view에 텍스트
        # 기본적으로 beautifulsoup '.text'를 쓸 경우 child 노드에 있는 text 까지 모두 얻어옴 만약 해당 레벨에서만 얻고자 하면 find_all(text=True, recursive=False)로 만들어 쓰면 list로 반환 됨

        renders = soup.select('div.post_view')
        # 본문 내용이 있는 경우
        if renders:
            try:
                stories = renders[0].select('div.post_article p')
                for item in stories:
                    line_text = item.text
                    story_text = story_text + line_text + "\n"

                replys = soup.select('div.comment_row')
                img_tag = renders[0].select('div.post_article img.fr-dib')
                video_tag = renders[0].select('div.post_article iframe')

                # text가 있으면 모두 추출(p tag text)
                story_text = story_text.strip()

                # 이미지가 있으면 src url 모두 획득
                if img_tag:
                    for idx, ele in enumerate(img_tag):
                        try:
                            # url = 'http:' + ele['src']
                            url = ele['src']
                            url = self.encoding_url(url)
                            img_url_text = img_url_text + str(idx+1) + '. ' + str(url) + '\n'
                        except:
                            continue
                # 동영상이 있으면 src url 모두 획득
                if video_tag:
                    for idx, ele in enumerate(video_tag):
                        try:
                            url = ele['src']
                            url = self.encoding_url(url)
                            video_url_text = video_url_text + str(idx+1) + '. ' + str(url) + '\n'
                        except:
                            continue

                ############################################################__댓글 값 추출__#########################################################
                # soup.select('a[href*=london]')  # contains "london"
                # soup.select('a[href$=d12]')  # ends with "d12"
                # soup.select('a[href^=/city/london]')  # starts with "city/london"
                # 댓글 값 확인
                if replys:
                    for idx, item in enumerate(replys):

                        item_attr = item['class']
                        if 'blocked' in item_attr:
                            reply_text = reply_text + str(idx + 1) + ". 삭제 처리됨\n"
                            continue

                        # reply 날짜 형식 변경
                        reportDate_raw = item.select('span.timestamp')[0].text.strip()
                        reportDate_str = re.findall('[0-9]{4}-[0-9]{2}-[0-9]{2}', reportDate_raw)
                        reportTime_str = re.findall('[0-9]{2}:[0-9]{2}:[0-9]{2}', reportDate_raw)
                        # 최종 값
                        reply_info = reportDate_str[0] + ' ' + reportTime_str[0]
                        reply_main = item.select('div.comment_view')[0].text.strip()
                        reply_text = reply_text + str(idx+1) + ". " + reply_main + "(" + reply_info + ")\n"
                # 페이지 대기
                sleep(self.delay_time)
                # return values
                return [story_text, img_url_text, video_url_text, reply_text]
            except:
                error_message = '본문 내용 정리 중 에러 발생 : {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1],
                                                                             sys.exc_info()[2].tb_lineno)
                return [error_message, '', '', '']
        # 회원 전용 글의 경우
        else:
            return ['내용 무', img_url_text, video_url_text, reply_text]

    # 엘지모바일 본문 글 정리 함수
    def get_main_article_lg(self):

        sleep(self.delay_time)
        html_source = self.driver.page_source
        soup = BeautifulSoup(html_source, "html.parser")
        story_text = ''
        img_url_text = ''
        video_url_text = ''
        reply_text = ''
        nhn_video_url = 'https://serviceapi.nmv.naver.com/view/ugcPlayer.nhn?vid={}&inkey={}&wmode=opaque&hasLink=0&autoPlay=false&beginTime=0'

        # get_attribute('attribute name')
        # 게시글 타입이 두개로 나뉨
        #   1. div.article_container > div.article_viewer > div.ContentRenderer 이게 존재하면
        #       - div.article_container > div.article_viewer > div.ContentRenderer > div > p ==> 게시글
        #       - div.article_container > div.article_viewer > div.ContentRenderer > div > img ==> 이미지(attribute => src)
        #       - div.article_container > div.article_viewer > div.ContentRenderer > div > iframe ==> video(attribute => src)
        #       - div.article_container > div.article_viewer > div.ContentRenderer > div > div.NHN_Writeform_Main 이면
        #         하단의 div 또는 p 테그들의 text 값을 추출
        #         하단에 img는 src 추출 image url
        #         하단에 iframe이면 src 추출 video_url

        #   2. div.article_container > div.article_viewer > div.se-viewer 이게 존재하면
        #      - text elements
        #        div.article_container > div.article_viewer > div:nth-child(2) > div.content.CafeViewer > div > div > div.se-text
        #        그 하위에 div > div > div > p Tag들 밑에 각각의 span tag의 text이며 만약 값이 비어 있으면 줄바꿈으로 변경
        #      - img elements
        #        div.article_container > div.article_viewer > div:nth-child(2) > div.content.CafeViewer > div > div > div.se-image
        #        그 하위에 div > div > div > a > img의 src 값
        #      - video elements
        #        div.article_container > div.article_viewer > div:nth-child(2) > div.content.CafeViewer > div > div > div.se-video
        #        그 하위의 div > script tag에서 attribute => data-module의 값을 json.load를 통해 dict로 변환한 후 data의 'vid'와 'inkey'를 획득한 후
        #        'https://serviceapi.nmv.naver.com/view/ugcPlayer.nhn?vid={}&inkey={}&wmode=opaque&hasLink=0&autoPlay=false&beginTime=0'에
        #        대입하여 url를 만들고 저장

        render = soup.select('div.ContentRenderer')
        se_viewer = soup.select('div.se-viewer')
        #########################################################__ContentRenderer 타입__###################################################
        if render:
            self.setPrint('분석결과: ContentRender 타입')

            # text 값이 있으면 값을 모두 획득
            p_tags = render[0].select('div > p')
            img_tag = render[0].select('div > img')
            iframe_tag = render[0].select('div > iframe')
            nhn_tag = render[0].select('div.NHN_Writeform_Main')

            if p_tags:

                for ele in p_tags:
                    line = ele.text
                    if line == '':
                        story_text = story_text+'\n'
                    else:
                        story_text = story_text + line.strip()

            # 이미지가 있으면 src url 모두 획득
            if img_tag:

                for idx, ele in enumerate(img_tag):
                    try:
                        url = ele['src']
                        url = self.encoding_url(url)
                        img_url_text = img_url_text + str(idx+1) + '. ' + str(url) + '\n'
                    except:
                        continue

            # 동영상이 있으면 src url 모두 획득
            if iframe_tag:

                for idx, ele in enumerate(iframe_tag):
                    try:
                        url = ele['src']
                        url = self.encoding_url(url)
                        video_url_text = video_url_text + str(idx+1) + '. ' + str(url) + '\n'
                    except:
                        continue

            # NHN_Writeform이면 해당 로직 실행
            if nhn_tag:

                # p tag 있다면 text 합
                if nhn_tag[0].select('p'):
                    p_tags = nhn_tag[0].select('p')
                    for ele in p_tags:
                        line = ele.text
                        if line == '':
                            story_text = story_text+'\n'
                        else:
                            story_text = story_text + line.strip()

                # div tag 있다면 text 합
                if nhn_tag[0].select('div'):
                    div_tags = nhn_tag[0].select('div')
                    for ele in div_tags:
                        line = ele.text
                        if line == '':
                            story_text = story_text+'\n'
                        else:
                            story_text = story_text + line.strip()

                # img tag 있다면 src url 모두 획득
                if nhn_tag[0].select('img'):
                    img_tags = nhn_tag.select('img')
                    for idx, ele in enumerate(img_tags):
                        try:
                            url = ele['src']
                            url = self.encoding_url(url)
                            img_url_text = img_url_text + str(idx+1) + '. ' + str(url) + '\n'
                        except:
                            continue

                # 동영상이 있으면 src url 모두 획득
                if nhn_tag[0].select('iframe'):
                    iframe_tags = nhn_tag[0].select('iframe')
                    for idx, ele in enumerate(iframe_tags):
                        try:
                            url = ele['src']
                            url = self.encoding_url(url)
                            video_url_text = video_url_text + str(idx+1) + '. ' + str(url) + '\n'
                        except:
                            continue

        #########################################################__se viewer 타입__#########################################################
        elif se_viewer:

            self.setPrint('분석결과: SE_Viewer 타입')
            # get se-viewer element
            span_tags = se_viewer[0].select('div.se-main-container div.se-text p > span')
            img_tags = se_viewer[0].select('div.se-main-container div.se-image img')
            script_tags = se_viewer[0].select('div.se-main-container div.se-video script')
            # text 값이 있으면 값을 모두 획득
            if span_tags:
                for ele in span_tags:
                    line = ele.text
                    if line == '':
                        story_text = story_text+'\n'
                    else:
                        story_text = story_text + line.strip() + '\n'

            # 이미지가 있으면 src url 모두 획득
            if img_tags:
                for idx, ele in enumerate(img_tags):
                    try:
                        url = ele['src']
                        url = self.encoding_url(url)
                        img_url_text = img_url_text + str(idx+1) + '. ' + str(url) + '\n'
                    except:
                        continue

            # 동영상이 있으면 src url 모두 획득
            if script_tags:
                for idx, ele in enumerate(script_tags):
                    data_module = ele['data-module']
                    if data_module == '':
                        continue
                    else:
                        try:
                            dict_module = json.loads(data_module)
                            vid = dict_module['data']['vid']
                            inkey = dict_module['data']['inkey']
                            video_url_text = video_url_text + str(idx+1) + '. ' + str(nhn_video_url.format(vid, inkey)) + '\n'
                        except:
                            continue
        #######################################################__해당사항 없음 타입__#########################################################
        else:
            self.setPrint('분석결과: Unknown 타입 Parsing Pass')
            pass

        ############################################################__댓글 값 추출__#########################################################
        reply = soup.select('div.CommentBox')
        # 댓글 값 확인
        if reply:
            list_items = reply[0].select('li.CommentItem')

            for idx, item in enumerate(list_items):
                try:
                    list_reply_comment = item.select('span.text_comment')
                    list_reply_img = item.select('a.comment_image_link > img')
                    reply_info = item.select('span.comment_info_date')

                    # text만 있을 경우
                    if list_reply_comment and not list_reply_img:
                        reply_text = reply_text + str(idx+1) + ". " + list_reply_comment[0].text + "(" + reply_info[0].text + ")\n"
                    # 첨부 img만 있을 경우
                    elif list_reply_img and not list_reply_comment:
                        reply_text = reply_text + str(idx+1) + ". 첨부 이미지 : " + list_reply_img[0]['src'] + "(" + reply_info[0].text + ")\n"
                    # 이미지 text 모두 있을 경우
                    elif list_reply_img and list_reply_comment:
                        reply_text = reply_text + str(idx+1) + ". " + list_reply_comment[0].text + "\n"
                        reply_text = reply_text + '첨부 이미지 : ' + list_reply_img[0]['src'] + "(" + reply_info[0].text + ")\n"
                    else:
                        continue
                except:
                    continue
        # 페이지 대기
        sleep(self.delay_time)
        # return values
        return [story_text, img_url_text, video_url_text, reply_text]

    # ##########################################################################_각 구역 컨트롤러__###########################################################################

    # 뽐뿌 실행 함수
    def activate_ppopm(self, dict_object, name):

        cafeName = name
        try:
            # config values
            url = dict_object['URL'][0]
            execute_mode = dict_object['EXECUTES_MODE'][0]
            work_mode = dict_object['WORK_MODE'][0]
            # ON/OFF 설정 값에서 'OFF'일 경우
            if work_mode == 'OFF':
                self.setPrint('{} 구역 페이지 설정에 의해 크롤링 Skip 처리'.format(cafeName))
                self.list_result.append({cafeName: {}})
                self.list_upload_status.append('설정에 의해 {} 크롤링 Skip 처리'.format(cafeName))
                pass

            # ON/OFF 설정 값에서 'ON'일 경우
            else:
                dict_result = {}
                # data groups
                list_bo_no = []
                list_cafeName = []
                list_navi = []
                list_type = []
                list_device = []
                list_report_date = []
                list_report_time = []
                list_regiDate = []
                list_title = []
                list_stroy = []
                list_reply = []
                list_cate = []
                list_status = []
                list_reply_num = []
                list_view_num = []
                list_story_url = []
                list_img_url = []
                list_video_url = []
                list_uniqueID = []

                # 메인 페이지 이외 팝업 삭제
                self.driver.get(url)
                # self.close_window(mode=1)
                sleep(self.delay_time)
                self.action_wait(mode='id', ele_val='revolution_main_table')

                recent_num = 0
                page_num = 1
                extract_num = 0
                flag_end = False
                self.setPrint('{} 구역 페이지 크롤링 시작'.format(cafeName))
                flag_search_mode = 'today'
                # DB에 최신 값을 조회한 후 DB가 비어 있다면 오늘 데이터만 찾는 방식이고 있다면 최신 보드 번호를 기록 후 이를 기준으로 이후 데이터만 크롤링이 실행된다
                list_recent = self.myDB.check_recent(cafeName, '공통', '공통', 3)

                # 조회모드 선택
                if len(list_recent) != 0 and execute_mode.lower() != 'today' and execute_mode != 'Null':
                    flag_search_mode = 'recent'
                    recent_num = int(list_recent[0]['bo_no'])
                    self.setPrint("최근 {} 게시글 번호: {}".format(cafeName, recent_num))
                self.setPrint('조회방법 : {}'.format(flag_search_mode))

                # 순회 크롤링 시작
                # 서버에 데이터가 하나도 없는 경우 당일 데이터만 추출
                if flag_search_mode == 'today':
                    nowDate = datetime.now()
                    basic_date = nowDate.strftime('%m-%d-%Y')
                    # 먼저 board number, title, reply_num, view_num, story_url을 추출하여 list에 입력
                    while True:
                        if flag_end:
                            break
                        else:
                            self.action_wait(mode='css', ele_val='#revolution_main_table > tbody')
                            # article 데이터들
                            text_xpath_node = '//*[@id="revolution_main_table"]/tbody/tr[@class="list0" or @class="list1" or @class="list0 " or @class="list1 "]'
                            list_rows = self.get_elements(mode='xpath', ele_val=text_xpath_node)
                            article_size = len(list_rows)
                            # //article 값이 없으면
                            if article_size == 0:
                                self.setPrint('뽐뿌 계시글 엘러먼트 미 존재 종료')
                                flag_end = True
                            else:
                                # 테이블 리스트 each tr 조회
                                for idx, row in enumerate(list_rows):
                                    # article 값 추출
                                    link_ele = row.find_element_by_css_selector('td:nth-child(4) > a')
                                    # story_url = link_ele.get_attribute('href').strip()
                                    board_ele = row.find_element_by_css_selector('td:nth-child(1)')
                                    board_num = board_ele.text.strip()
                                    story_url = 'https://www.ppomppu.co.kr/zboard/view.php?id=phone&no='+board_num
                                    board_num = int(board_num)
                                    board_date = row.find_element_by_css_selector('td:nth-child(5) > nobr').text.strip()
                                    # 게시물 타입(번호놀이 제외)
                                    board_type = row.find_element_by_css_selector('td:nth-child(2) > nobr').text.strip()
                                    # 당일 데이터만 획득
                                    flag_end = self.check_today(board_date)
                                    if flag_end:
                                        break
                                    else:
                                        # self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, )))
                                        # 번호 놀이 맴버쉽은 제외
                                        # if board_type in ['번호놀이', '맴버쉽']:
                                        #     # 데이터 테이블의 마지막 행인 경우
                                        #     if idx == article_size - 1:
                                        #         list_pages = self.driver.find_element_by_css_selector('#page_list')
                                        #         action = ActionChains(self.driver)
                                        #         action.move_to_element(list_pages).perform()
                                        #         if page_num % 10 == 0:
                                        #             page_num = page_num + 1
                                        #             page_ele = self.get_elements(mode='xpath', ele_val='//a[text()="다음"]', ele_parent=list_pages)
                                        #             page_ele[0].click()
                                        #         else:
                                        #             page_num = page_num + 1
                                        #             page_ele = self.get_elements(mode='xpath', ele_val='//a[text()="'+str(page_num)+'"]', ele_parent=list_pages)
                                        #             page_ele[0].click()
                                        #
                                        #         self.setPrint('{} Page 페이지로 이동'.format(page_num))
                                        #         break
                                        #     # 데이터 마지막 행이 아닌 경우
                                        #     else:
                                        #         continue
                                        if board_num in list_bo_no:
                                            # 데이터 테이블의 마지막 행인 경우
                                            if idx == article_size - 1:
                                                list_pages = self.driver.find_element_by_css_selector('#page_list')
                                                self.driver.execute_script('arguments[0].scrollIntoView();', list_pages)
                                                # action = ActionChains(self.driver)
                                                # action.move_to_element(list_pages).perform()
                                                if page_num % 10 == 0:
                                                    page_num = page_num + 1
                                                    page_ele = self.get_elements(mode='xpath', ele_val='//a[text()="다음"]',
                                                                                 ele_parent=list_pages)
                                                    page_ele[0].click()
                                                else:
                                                    page_num = page_num + 1
                                                    page_ele = self.get_elements(mode='xpath', ele_val='//a[text()="' + str(
                                                        page_num) + '"]', ele_parent=list_pages)
                                                    page_ele[0].click()

                                                self.setPrint('{} Page 페이지로 이동'.format(page_num))
                                                break
                                            # 데이터 마지막 행이 아닌 경우
                                            else:
                                                continue
                                        title = link_ele.text.strip()
                                        # view_num 부분

                                        view_num = int(row.find_element_by_css_selector('td:nth-child(7)').text.strip().replace(",", ""))
                                        # reply_num 부분
                                        reply_num = 0
                                        reply_flag = self.is_element(mode='css', ele_val='td:nth-child(4) > span > span', ele_parent=row)
                                        if reply_flag:
                                            reply_num = int(row.find_element_by_css_selector('td:nth-child(4) > span > span').text.strip().replace(",", ""))
                                        # 등록일 추출
                                        reportDate_raw = row.find_element_by_css_selector('td:nth-child(5)').get_attribute('title').strip()
                                        list_temp = reportDate_raw.split()

                                        # 날짜 형식 변경
                                        reportDate_str = list_temp[0]
                                        reportDate_date = datetime.strptime(reportDate_str, "%y.%m.%d")
                                        # 시간 형식 변경
                                        reportTime_str = list_temp[1]
                                        list_temp_time = reportTime_str.split(':')
                                        reportTime_str = list_temp_time[0]+':'+list_temp_time[1]
                                        # 최종 값
                                        reportDate = reportDate_date.strftime("%Y-%m-%d")
                                        reportTime = reportTime_str

                                        # 추출된 값 각 list에 입력
                                        list_bo_no.append(board_num)
                                        list_navi.append('공통')
                                        list_type.append('공통')
                                        list_device.append('공통')
                                        list_cate.append('Unknown')
                                        list_status.append('Unknown')
                                        list_reply_num.append(reply_num)
                                        list_view_num.append(view_num)
                                        list_title.append(title)
                                        list_story_url.append(story_url)
                                        list_report_date.append(reportDate)
                                        list_report_time.append(reportTime)
                                        self.setPrint('순번: {}\n게시번호: {}\n제목: {}\nURL: {}'.format(idx, board_num, title, story_url))

                                        # 데이터 테이블의 마지막 행인 경우
                                        if idx == article_size - 1:
                                            list_pages = self.driver.find_element_by_css_selector('#page_list')
                                            self.driver.execute_script('arguments[0].scrollIntoView();', list_pages)
                                            # action = ActionChains(self.driver)
                                            # action.move_to_element(list_pages).perform()
                                            if page_num % 10 == 0:
                                                page_num = page_num + 1
                                                page_ele = self.get_elements(mode='xpath', ele_val='//a[text()="다음"]', ele_parent=list_pages)
                                                page_ele[0].click()
                                            else:
                                                page_num = page_num + 1
                                                page_ele = self.get_elements(mode='xpath', ele_val='//a[text()="'+str(page_num)+'"]', ele_parent=list_pages)
                                                page_ele[0].click()

                                            self.setPrint('{} Page 페이지로 이동'.format(page_num))
                                            break

                    # 해당 본문 페이지 이동
                    if len(list_bo_no) != 0:
                        for idx, item in enumerate(list_story_url):
                            self.driver.get(item)
                            sleep(self.delay_time)
                            ############################################본문 페이지 메인 엘러먼트##########################################
                            self.action_wait(mode='css', ele_val='.sub-nav')
                            # story 또는 image_url 또는 video_url 또는 댓글 부분
                            list_main_article = self.get_main_article_pp()
                            # set each list value
                            list_stroy.append(list_main_article[0])
                            list_reply.append(list_main_article[3])
                            list_img_url.append(list_main_article[1])
                            list_video_url.append(list_main_article[2])

                            self.setPrint(
                                        '게시번호: {}\n카페이름: {}\n타입: {}\n디바이스: {}\n제목: {}\nDate: {} {}\n조회수: {}\n댓글수: {}\n내용:\n{}\n이미지:\n{}\n비디오:\n{}\n댓글:\n{}'.format
                                        (list_bo_no[idx], cafeName, '공통', '공통', list_title[idx], list_report_date[idx], list_report_time[idx], list_view_num[idx], list_reply_num[idx],
                                        list_main_article[0], list_main_article[1], list_main_article[2], list_main_article[3]))

                            # 추출 데이터 count 기록
                            extract_num = extract_num + 1
                            sleep(1)

                # mongoDB에 최근 record가 있는 경우
                else:
                    # 먼저 board number, title, reply_num, view_num, story_url을 추출하여 list에 입력
                    while True:
                        if flag_end:
                            break
                        else:
                            self.action_wait(mode='css', ele_val='#revolution_main_table > tbody')
                            # article 데이터들
                            text_xpath_node = '//*[@id="revolution_main_table"]/tbody/tr[@class="list0" or @class="list1" or @class="list0 " or @class="list1 "]'
                            list_rows = self.get_elements(mode='xpath', ele_val=text_xpath_node)
                            article_size = len(list_rows)
                            # 테이블 리스트 each tr 조회
                            if article_size == 0:
                                self.setPrint('뽐뿌 계시글 엘러먼트 미 존재 종료')
                                flag_end = True
                            else:
                                for idx, row in enumerate(list_rows):
                                    link_ele = row.find_element_by_css_selector('td:nth-child(4) > a')
                                    # story_url = link_ele.get_attribute('href').strip()
                                    board_ele = row.find_element_by_css_selector('td:nth-child(1)')
                                    board_num = board_ele.text.strip()
                                    story_url = 'https://www.ppomppu.co.kr/zboard/view.php?id=phone&no='+board_num
                                    board_num = int(board_num)
                                    board_date = row.find_element_by_css_selector('td:nth-child(5) > nobr').text.strip()
                                    # 게시물 타입(번호놀이 제외)
                                    board_type = row.find_element_by_css_selector('td:nth-child(2) > nobr').text.strip()
                                    # 당일 데이터만 획득
                                    flag_end = self.compared_num(recent_num, board_num)
                                    if flag_end:
                                        break
                                    else:
                                        # self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, )))
                                        # 번호 놀이 맴버쉽은 제외
                                        # if board_type in ['번호놀이', '맴버쉽']:
                                        #     # 데이터 테이블의 마지막 행인 경우
                                        #     if idx == article_size - 1:
                                        #         list_pages = self.driver.find_element_by_css_selector('#page_list')
                                        #         action = ActionChains(self.driver)
                                        #         action.move_to_element(list_pages).perform()
                                        #         if page_num % 10 == 0:
                                        #             page_num = page_num + 1
                                        #             page_ele = self.get_elements(mode='xpath', ele_val='//a[text()="다음"]', ele_parent=list_pages)
                                        #             page_ele[0].click()
                                        #         else:
                                        #             page_num = page_num + 1
                                        #             page_ele = self.get_elements(mode='xpath', ele_val='//a[text()="'+str(page_num)+'"]', ele_parent=list_pages)
                                        #             page_ele[0].click()
                                        #
                                        #         self.setPrint('{} Page 페이지로 이동'.format(page_num))
                                        #         break
                                        #     # 데이터 마지막 행이 아닌 경우
                                        #     else:
                                        #         continue
                                        if board_num in list_bo_no:
                                            # 데이터 테이블의 마지막 행인 경우
                                            if idx == article_size - 1:
                                                list_pages = self.driver.find_element_by_css_selector('#page_list')
                                                self.driver.execute_script('arguments[0].scrollIntoView();', list_pages)
                                                # action = ActionChains(self.driver)
                                                # action.move_to_element(list_pages).perform()
                                                if page_num % 10 == 0:
                                                    page_num = page_num + 1
                                                    page_ele = self.get_elements(mode='xpath', ele_val='//a[text()="다음"]',
                                                                                 ele_parent=list_pages)
                                                    page_ele[0].click()
                                                else:
                                                    page_num = page_num + 1
                                                    page_ele = self.get_elements(mode='xpath', ele_val='//a[text()="' + str(
                                                        page_num) + '"]', ele_parent=list_pages)
                                                    page_ele[0].click()

                                                self.setPrint('{} Page 페이지로 이동'.format(page_num))
                                                break
                                            # 데이터 마지막 행이 아닌 경우
                                            else:
                                                continue
                                        title = link_ele.text.strip()
                                        # view_num 부분
                                        view_num = int(row.find_element_by_css_selector('td:nth-child(7)').text.strip().replace(",", ""))
                                        # reply_num 부분
                                        reply_num = 0
                                        reply_flag = self.is_element(mode='css', ele_val='td:nth-child(4) > span > span',
                                                                     ele_parent=row)
                                        if reply_flag:
                                            reply_num = int(row.find_element_by_css_selector('td:nth-child(4) > span > span').text.strip().replace(",", ""))
                                        # 등록일 추출
                                        reportDate_raw = row.find_element_by_css_selector('td:nth-child(5)').get_attribute(
                                            'title').strip()
                                        list_temp = reportDate_raw.split()

                                        # 날짜 형식 변경
                                        reportDate_str = list_temp[0]
                                        reportDate_date = datetime.strptime(reportDate_str, "%y.%m.%d")
                                        # 시간 형식 변경
                                        reportTime_str = list_temp[1]
                                        list_temp_time = reportTime_str.split(':')
                                        reportTime_str = list_temp_time[0] + ':' + list_temp_time[1]
                                        # 최종 값
                                        reportDate = reportDate_date.strftime("%Y-%m-%d")
                                        reportTime = reportTime_str

                                        # 추출된 값 각 list에 입력
                                        list_bo_no.append(board_num)
                                        list_navi.append('공통')
                                        list_type.append('공통')
                                        list_device.append('공통')
                                        list_cate.append('Unknown')
                                        list_status.append('Unknown')
                                        list_reply_num.append(reply_num)
                                        list_view_num.append(view_num)
                                        list_title.append(title)
                                        list_story_url.append(story_url)
                                        list_report_date.append(reportDate)
                                        list_report_time.append(reportTime)
                                        self.setPrint('순번: {}\n게시번호: {}\n제목: {}\nURL: {}'.format(idx, board_num, title, story_url))

                                        # 데이터 테이블의 마지막 행인 경우
                                        if idx == article_size - 1:
                                            list_pages = self.driver.find_element_by_css_selector('#page_list')
                                            self.driver.execute_script('arguments[0].scrollIntoView();', list_pages)
                                            # action = ActionChains(self.driver)
                                            # action.move_to_element(list_pages).perform()
                                            if page_num % 10 == 0:
                                                page_num = page_num + 1
                                                page_ele = self.get_elements(mode='xpath', ele_val='//a[text()="다음"]', ele_parent=list_pages)
                                                page_ele[0].click()
                                            else:
                                                page_num = page_num + 1
                                                page_ele = self.get_elements(mode='xpath',
                                                                             ele_val='//a[text()="' + str(page_num) + '"]',
                                                                             ele_parent=list_pages)
                                                page_ele[0].click()
                                            self.setPrint('{} Page 페이지로 이동'.format(page_num))
                                            break
                    # 해당 본문 페이지 이동
                    if len(list_bo_no) != 0:

                        for idx, item in enumerate(list_story_url):
                            self.driver.get(item)
                            sleep(self.delay_time)
                            ############################################본문 페이지 메인 엘러먼트##########################################
                            self.action_wait(mode='css', ele_val='.sub-nav')
                            # story 또는 image_url 또는 video_url 또는 댓글 부분
                            list_main_article = self.get_main_article_pp()
                            # set each list value
                            list_stroy.append(list_main_article[0])
                            list_reply.append(list_main_article[3])
                            list_img_url.append(list_main_article[1])
                            list_video_url.append(list_main_article[2])

                            self.setPrint(
                                '게시번호: {}\n카페이름: {}\n타입: {}\n디바이스: {}\n제목: {}\nDate: {} {}\n조회수: {}\n댓글수: {}\n내용:\n{}\n이미지:\n{}\n비디오:\n{}\n댓글:\n{}'.format
                                (list_bo_no[idx], cafeName, '공통', '공통', list_title[idx], list_report_date[idx],
                                 list_report_time[idx], list_view_num[idx], list_reply_num[idx],
                                 list_main_article[0], list_main_article[1], list_main_article[2], list_main_article[3]))

                            # 추출 데이터 count 기록
                            extract_num = extract_num + 1
                            sleep(1)

                # frame main content로 변경
                self.setPrint('뽐뿌 페이지 크롤링 종료 총 {} Data 추출 완료'.format(extract_num))

                # Upload data가 있다면
                if len(list_bo_no) != 0:
                    # generate dict_result
                    # generate cafe name list
                    regiDate = self.getCurrent_time()[1]

                    for idx in range(len(list_bo_no)):

                        list_cafeName.append(cafeName)
                        unique_id = self.generate_id()
                        list_uniqueID.append(unique_id)
                        list_regiDate.append(regiDate)

                    # grouping each list values
                    list_group = [list_bo_no, list_cafeName, list_navi, list_type, list_device, list_report_date, list_report_time, list_regiDate,
                                  list_title, list_stroy, list_reply, list_cate, list_status, list_reply_num, list_view_num, list_story_url,
                                  list_img_url, list_video_url, list_uniqueID]

                    # generate dict_result
                    for idx, item in enumerate(list_group):
                        dict_result[self.list_cols[idx]] = item
                    # append dict_result to total result list array
                    self.list_result.append({'뽐뿌 커뮤니티': dict_result})
                    # insert data to mongoDB server
                    upload_stauts = self.myDB.insertData(dict_result, 3)
                    self.list_upload_status.append(upload_stauts)

                # Upload Data가 없다면
                else:
                    # append empty dict to total result
                    self.list_result.append({'뽐뿌 커뮤니티': {}})
                    self.list_upload_status.append('Data None')

                sleep(self.delay_time)
                self.setPrint('{} 사이트 크롤링 작업 완료'.format(cafeName))
        except:
            self.setPrint('Error Occurred : {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno))
            self.list_result.append({cafeName: {}})
            self.list_upload_status.append('Error Occurred : {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno))
            # self.process_flag = False

    # 클리앙 실행 함수
    def activate_clien(self, dict_object, name):

        cafeName = name
        try:
            # config values
            url = dict_object['URL'][0]
            list_search = dict_object['검색어']
            list_nav = dict_object['네비게이션']
            list_primary = dict_object['PRIMARY_KEYS']
            list_secondary = dict_object['SECONDARY_KEYS']
            list_exclude = dict_object['EXCLUDE_KEYS']
            execute_mode = dict_object['EXECUTES_MODE'][0]
            dict_result = {}
            work_mode = dict_object['WORK_MODE'][0]
            # ON/OFF 설정 값에서 'OFF'일 경우
            if work_mode == 'OFF':
                self.setPrint('{} 구역 페이지 설정에 의해 크롤링 Skip 처리'.format(cafeName))
                self.list_result.append({cafeName: {}})
                self.list_upload_status.append('설정에 의해 {} 크롤링 Skip 처리'.format(cafeName))
                pass
            # ON/OFF 설정 값에서 'ON'일 경우
            else:
                # data groups
                list_bo_no = []
                list_cafeName = []
                list_navi = []
                list_type = []
                list_device = []
                list_report_date = []
                list_report_time = []
                list_regiDate = []
                list_title = []
                list_stroy = []
                list_reply = []
                list_cate = []
                list_status = []
                list_reply_num = []
                list_view_num = []
                list_story_url = []
                list_img_url = []
                list_video_url = []
                list_uniqueID = []

                # 메인 페이지 이외 팝업 삭제
                self.driver.get(url)
                # self.close_window(mode=1)
                sleep(self.delay_time)
                self.action_wait(mode='id', ele_val='menuTop')
                self.action_click(mode='id', ele_val='more')
                sleep(1)

                for item in list_nav:

                    recent_num = 0
                    page_num = 0
                    extract_num = 0
                    flag_end = False

                    # nav_url parsing
                    list_text = item.split('(')
                    nav_url = list_text[0]
                    nav_name = list_text[1]
                    nav_name = nav_name[:len(nav_name) - 1]

                    self.setPrint('{} {} 구역 페이지 크롤링 시작'.format(cafeName, nav_name))
                    # 해당 페이지로 이동
                    self.driver.get(nav_url)

                    # title 대기
                    self.action_wait(mode='css', ele_val='body > nav > div > h1')
                    # device_name , type_name 값 추출
                    device_name = '공통'
                    type_name = '공통'
                    flag_search_mode = 'today'
                    sleep(self.delay_time)

                    # DB에 최신 값을 조회한 후 DB가 비어 있다면 오늘 데이터만 찾는 방식이고 있다면 최신 보드 번호를 기록 후 이를 기준으로 이후 데이터만 크롤링이 실행된다
                    list_recent = self.myDB.check_recent(cafeName, nav_name, type_name, 3)
                    if len(list_recent) != 0 and execute_mode.lower() != 'today' and execute_mode != 'Null':
                        flag_search_mode = 'recent'
                        recent_num = int(list_recent[0]['bo_no'])
                        self.setPrint("최근 {} 게시글 번호: {}".format(nav_name, recent_num))

                    self.setPrint('조회방법 : {}'.format(flag_search_mode))
                    # 순회 크롤링 시작
                    # 서버에 데이터가 하나도 없는 경우 당일 데이터만 추출
                    if flag_search_mode == 'today':
                        while True:
                            if flag_end:
                                break
                            else:
                                self.action_wait(mode='css', ele_val='#div_content > div.list_content')
                                # 테이블 리스트 each tr 조회
                                data_size = len(self.get_elements(mode='css', ele_val='div.symph_row'))
                                for idx in range(1, data_size+1):
                                    # tr값 추출
                                    sleep(self.delay_time)
                                    self.action_wait(mode='css', ele_val='#div_content > div.list_content > div:nth-child(' + str(idx) + ')')
                                    tr_ele = self.get_elements(mode='css', ele_val='#div_content > div.list_content > div:nth-child(' + str(idx) + ')')
                                    board_num = int(tr_ele[0].get_attribute('data-board-sn').strip())
                                    time_value = tr_ele[0].find_element_by_css_selector('span.popover').text.strip()
                                    # 당일 데이터만 획득
                                    flag_end = self.check_today(time_value)
                                    if flag_end:
                                        break
                                    else:
                                        if board_num in list_bo_no:
                                            continue
                                        # self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, )))
                                        title_ele = tr_ele[0].find_element_by_css_selector('div.list_title > a.list_subject > span.subject_fixed')
                                        title = title_ele.text.strip()
                                        story_url = tr_ele[0].find_element_by_css_selector('div.list_title > a.list_subject').get_attribute('href')
                                        view_str = tr_ele[0].find_element_by_css_selector('div.list_hit > span').text.strip().replace(",", "")
                                        view_num = 0
                                        if 'k' in view_str:
                                            view_num = int(float(view_str.replace('k', '')) * 1000)
                                        else:
                                            view_num = int(view_str)
                                        # 해당 본문 페이지 이동
                                        title_ele.click()
                                        sleep(self.delay_time)
                                        ############################################본문 페이지 메인 엘러먼트##########################################
                                        self.action_wait(mode='css', ele_val='div.content_view')
                                        article_main_ele = self.driver.find_element_by_css_selector('div.content_view')
                                        # main article header Date 부분
                                        reportDate_ele = self.get_elements(mode='css',
                                                                           ele_val='div.post_view > div.post_author > span:nth-child(1)',
                                                                           ele_parent=article_main_ele)
                                        reportDate_str = reportDate_ele[0].text.strip()
                                        list_reportDate = reportDate_str.split()
                                        reportDate = list_reportDate[0]
                                        reportTime = list_reportDate[1]
                                        # main article header reply_num 부분
                                        reply_num_ele = self.get_elements(mode='css',
                                                                          ele_val='div.post_title.symph_row > h3 > a > span:nth-child(1)',
                                                                          ele_parent=article_main_ele)
                                        reply_num = 0
                                        if reply_num_ele:
                                            reply_num = int(reply_num_ele[0].text.strip().replace(",", ""))

                                        # story 또는 image_url 또는 video_url 또는 댓글 부분
                                        list_main_article = self.get_main_article_cl()

                                        self.setPrint(
                                            '게시번호: {}\n카페이름: {}\nnav: {}\n타입: {}\n디바이스: {}\n제목: {}\nDate: {} {}\n조회수: {}\n댓글수: {}\n내용:\n{}\n이미지:\n{}\n비디오:\n{}\n댓글:\n{}'.format
                                            (board_num, cafeName, nav_name, type_name, device_name, title, reportDate, reportTime,
                                             view_num, reply_num,
                                             list_main_article[0], list_main_article[1], list_main_article[2],
                                             list_main_article[3]))

                                        # set each list value
                                        list_bo_no.append(board_num)
                                        list_navi.append(nav_name)
                                        list_type.append(type_name)
                                        list_device.append(device_name)
                                        list_report_date.append(reportDate)
                                        list_report_time.append(reportTime)
                                        list_title.append(title)
                                        list_stroy.append(list_main_article[0])
                                        list_reply.append(list_main_article[3])
                                        list_cate.append('Unknown')
                                        list_status.append('Unknown')
                                        list_reply_num.append(reply_num)
                                        list_view_num.append(view_num)
                                        list_story_url.append(story_url)
                                        list_img_url.append(list_main_article[1])
                                        list_video_url.append(list_main_article[2])

                                        extract_num = extract_num + 1
                                        # tr 리스트로 이동
                                        self.action_page_move(mode='back')

                                        # 데이터 테이블의 마지막 행인 경우
                                        if idx == data_size:
                                            if page_num % 10 == 0:
                                                page_num = page_num + 1
                                                page_ele = self.get_elements(mode='css', ele_val='a.board-nav-next')
                                                self.driver.execute_script('arguments[0].scrollIntoView();', page_ele[0])
                                                # action = ActionChains(self.driver)
                                                # action.move_to_element(page_ele[0]).perform()
                                                page_ele[0].click()
                                            else:
                                                page_num = page_num + 1
                                                page_ele = self.get_elements(mode='css', ele_val='#pagingActiveId_'+str(page_num))
                                                self.driver.execute_script('arguments[0].scrollIntoView();', page_ele[0])
                                                # action = ActionChains(self.driver)
                                                # action.move_to_element(page_ele[0]).perform()
                                                page_ele[0].click()

                                            self.setPrint('{} Page 페이지로 이동'.format(page_num))
                                            break
                    # mongoDB에 최근 record가 있는 경우
                    else:
                        while True:
                            if flag_end:
                                break
                            else:
                                self.action_wait(mode='css', ele_val='#div_content > div.list_content')
                                # 테이블 리스트 each tr 조회
                                data_size = len(self.get_elements(mode='css', ele_val='div.symph_row'))
                                for idx in range(1, data_size+1):
                                    # tr값 추출
                                    sleep(self.delay_time)
                                    self.action_wait(mode='css', ele_val='#div_content > div.list_content > div:nth-child(' + str(idx) + ')')
                                    tr_ele = self.get_elements(mode='css', ele_val='#div_content > div.list_content > div:nth-child(' + str(idx) + ')')
                                    board_num = int(tr_ele[0].get_attribute('data-board-sn').strip())
                                    # 서버에 있는 보더 넘버를 현재 번호와 비교하여 flag_end 결정
                                    flag_end = self.compared_num(recent_num, board_num)
                                    if flag_end:
                                        break
                                    else:
                                        if board_num in list_bo_no:
                                            continue
                                        # self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, )))
                                        title_ele = tr_ele[0].find_element_by_css_selector('div.list_title > a.list_subject > span.subject_fixed')
                                        title = title_ele.text.strip()
                                        story_url = tr_ele[0].find_element_by_css_selector('div.list_title > a.list_subject').get_attribute('href')
                                        view_num = 0
                                        view_str = tr_ele[0].find_element_by_css_selector('div.list_hit > span').text.strip().replace(",", "")
                                        if 'k' in view_str:
                                            view_num = int(float(view_str.replace('k', '')) * 1000)
                                        else:
                                            view_num = int(view_str)
                                        # 해당 본문 페이지 이동
                                        title_ele.click()
                                        sleep(self.delay_time)
                                        ############################################본문 페이지 메인 엘러먼트##########################################
                                        self.action_wait(mode='css', ele_val='div.content_view')
                                        article_main_ele = self.driver.find_element_by_css_selector('div.content_view')
                                        # main article header Date 부분
                                        reportDate_ele = self.get_elements(mode='css',
                                                                           ele_val='div.post_view > div.post_author > span:nth-child(1)',
                                                                           ele_parent=article_main_ele)

                                        reportDate_str = reportDate_ele[0].text.strip()
                                        list_reportDate = reportDate_str.split()
                                        reportDate = list_reportDate[0]
                                        reportTime = list_reportDate[1]
                                        # main article header reply_num 부분
                                        reply_num_ele = self.get_elements(mode='css',
                                                                          ele_val='div.post_title.symph_row > h3 > a > span:nth-child(1)',
                                                                          ele_parent=article_main_ele)
                                        reply_num = 0
                                        if reply_num_ele:
                                            reply_num = int(reply_num_ele[0].text.strip().replace(",", ""))

                                        # story 또는 image_url 또는 video_url 또는 댓글 부분
                                        list_main_article = self.get_main_article_cl()

                                        self.setPrint(
                                            '게시번호: {}\n카페이름: {}\nnav: {}\n타입: {}\n디바이스: {}\n제목: {}\nDate: {} {}\n조회수: {}\n댓글수: {}\n내용:\n{}\n이미지:\n{}\n비디오:\n{}\n댓글:\n{}'.format
                                            (board_num, cafeName, nav_name, type_name, device_name, title, reportDate, reportTime,
                                             view_num, reply_num,
                                             list_main_article[0], list_main_article[1], list_main_article[2],
                                             list_main_article[3]))

                                        # set each list value
                                        list_bo_no.append(board_num)
                                        list_navi.append(nav_name)
                                        list_type.append(type_name)
                                        list_device.append(device_name)
                                        list_report_date.append(reportDate)
                                        list_report_time.append(reportTime)
                                        list_title.append(title)
                                        list_stroy.append(list_main_article[0])
                                        list_reply.append(list_main_article[3])
                                        list_cate.append('Unknown')
                                        list_status.append('Unknown')
                                        list_reply_num.append(reply_num)
                                        list_view_num.append(view_num)
                                        list_story_url.append(story_url)
                                        list_img_url.append(list_main_article[1])
                                        list_video_url.append(list_main_article[2])

                                        extract_num = extract_num + 1
                                        # tr 리스트로 이동
                                        self.action_page_move(mode='back')

                                        # 데이터 테이블의 마지막 행인 경우
                                        if idx == data_size:
                                            if page_num % 10 == 0:
                                                page_num = page_num + 1
                                                page_ele = self.get_elements(mode='css', ele_val='a.board-nav-next')
                                                self.driver.execute_script('arguments[0].scrollIntoView();', page_ele[0])
                                                # action = ActionChains(self.driver)
                                                # action.move_to_element(page_ele[0]).perform()
                                                page_ele[0].click()
                                            else:
                                                page_num = page_num + 1
                                                page_ele = self.get_elements(mode='css', ele_val='#pagingActiveId_'+str(page_num))
                                                self.driver.execute_script('arguments[0].scrollIntoView();', page_ele[0])
                                                # action = ActionChains(self.driver)
                                                # action.move_to_element(page_ele[0]).perform()
                                                page_ele[0].click()
                                            self.setPrint('{} Page 페이지로 이동'.format(page_num))
                                            break
                    # frame main content로 변경
                    self.setPrint('클리앙 커뮤니티 {} 구역 페이지 크롤링 종료 총 {} Data 추출 완료'.format(nav_name, extract_num))
                # Upload data가 있다면
                if len(list_bo_no) != 0:
                    # generate dict_result
                    # generate cafe name list
                    regiDate = self.getCurrent_time()[1]

                    for idx in range(len(list_bo_no)):
                        list_cafeName.append(cafeName)
                        unique_id = self.generate_id()
                        list_uniqueID.append(unique_id)
                        list_regiDate.append(regiDate)

                    # grouping each list values
                    list_group = [list_bo_no, list_cafeName, list_navi, list_type, list_device, list_report_date,
                                  list_report_time, list_regiDate,
                                  list_title, list_stroy, list_reply, list_cate, list_status, list_reply_num, list_view_num,
                                  list_story_url,
                                  list_img_url, list_video_url, list_uniqueID]

                    # generate dict_result
                    for idx, item in enumerate(list_group):
                        dict_result[self.list_cols[idx]] = item
                    # append dict_result to total result list array
                    self.list_result.append({'클리앙 커뮤니티': dict_result})
                    # insert data to mongoDB server
                    upload_stauts = self.myDB.insertData(dict_result, 3)
                    self.list_upload_status.append(upload_stauts)

                # Upload Data가 없다면
                else:
                    # append empty dict to total result
                    self.list_result.append({'클리앙 커뮤니티': {}})
                    self.list_upload_status.append('Data None')

                sleep(self.delay_time)
                self.setPrint('{} 사이트 크롤링 작업 완료'.format(cafeName))
        except:
            self.setPrint('Error Occurred : {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno))
            # append empty dict to total result
            self.list_result.append({cafeName: {}})
            self.list_upload_status.append('Error Occurred : {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno))
            # self.process_flag = False

    # 삼성맴버스 실행 함수
    def activate_samsungHome(self, dict_object, name):

        cafeName = name
        try:
            # config values
            url = dict_object['URL'][0]
            list_search = dict_object['검색어']
            list_nav = dict_object['네비게이션']
            list_primary = dict_object['PRIMARY_KEYS']
            list_secondary = dict_object['SECONDARY_KEYS']
            list_exclude = dict_object['EXCLUDE_KEYS']
            execute_mode = dict_object['EXECUTES_MODE'][0]
            work_mode = dict_object['WORK_MODE'][0]
            dict_result = {}
            # ON/OFF 설정 값에서 'OFF'일 경우
            if work_mode == 'OFF':
                self.setPrint('{} 구역 페이지 설정에 의해 크롤링 Skip 처리'.format(cafeName))
                self.list_result.append({cafeName: {}})
                self.list_upload_status.append('설정에 의해 {} 크롤링 Skip 처리'.format(cafeName))
                pass
            # ON/OFF 설정 값에서 'ON'일 경우
            else:
                # data groups
                list_bo_no = []
                list_cafeName = []
                list_navi = []
                list_type = []
                list_device = []
                list_report_date = []
                list_report_time = []
                list_regiDate = []
                list_title = []
                list_stroy = []
                list_reply = []
                list_cate = []
                list_status = []
                list_reply_num = []
                list_view_num = []
                list_story_url = []
                list_img_url = []
                list_video_url = []
                list_uniqueID = []

                # 메인 페이지 이외 팝업 삭제
                self.driver.get(url)
                # self.close_window(mode=1)
                sleep(self.delay_time)
                self.action_wait(mode='css', ele_val='div.samsung-hero-content')

                for item in list_nav:

                    recent_num = 0
                    page_num = 1
                    extract_num = 0
                    flag_end = False

                    # nav_url parsing
                    list_text = item.split('(')
                    nav_url = list_text[0]
                    nav_name = list_text[1]
                    nav_name = nav_name[:len(nav_name) - 1]

                    self.setPrint('{} {} 구역 페이지 크롤링 시작'.format(cafeName, nav_name))
                    # 해당 페이지로 이동
                    self.driver.get(nav_url)

                    flag_search_mode = 'today'
                    # DB에 최신 값을 조회한 후 DB가 비어 있다면 오늘 데이터만 찾는 방식이고 있다면 최신 보드 번호를 기록 후 이를 기준으로 이후 데이터만 크롤링이 실행된다
                    list_recent = self.myDB.check_recent(cafeName, nav_name, '공통', 1)

                    # 조회모드 선택
                    if len(list_recent) != 0 and execute_mode.lower() != 'today' and execute_mode != 'Null':
                        flag_search_mode = 'recent'
                        recent_num = int(list_recent[0]['bo_no'])
                        self.setPrint("최근 {} 게시글 번호: {}".format(nav_name, recent_num))
                    self.setPrint('조회방법 : {}'.format(flag_search_mode))

                    # 순회 크롤링 시작
                    # 서버에 데이터가 하나도 없는 경우 당일 데이터만 추출
                    if flag_search_mode == 'today':
                        nowDate = datetime.now()
                        basic_date = nowDate.strftime('%m-%d-%Y')
                        while True:
                            if flag_end:
                                break
                            else:
                                self.action_wait(mode='css', ele_val='h1.split-carousel')
                                # article 데이터들
                                list_articles = self.get_elements(mode='css', ele_val='article.custom-message-tile')
                                article_size = len(list_articles)
                                # 테이블 리스트 each tr 조회
                                for idx in range(1, article_size + 1):
                                    # article 값 추출
                                    sleep(self.delay_time)
                                    self.action_wait(mode='css', ele_val='#initial-content article:nth-child('+str(idx)+')')
                                    row = self.driver.find_element_by_css_selector('#initial-content article:nth-child('+str(idx)+')')
                                    row_attr = row.get_attribute('class')

                                    # 고정 float article이 있으면 continue
                                    if 'custom-thread-floated' in row_attr:
                                        continue
                                    link_ele = row.find_element_by_css_selector('header > div.subject-bar > div.subject > h3 > a')
                                    story_url = link_ele.get_attribute('href').strip()
                                    board_num = story_url+'/e'
                                    board_num = self.find_between(board_num, 'td-p/', '/e')
                                    board_num = int(board_num)
                                    board_date = row.find_element_by_css_selector('header > div.author > time').text.strip()
                                    # 당일 데이터만 획득
                                    flag_end = basic_date != board_date[:10]
                                    if flag_end:
                                        break
                                    else:
                                        if board_num in list_bo_no:
                                            continue
                                        title = link_ele.text.strip()
                                        # main article header view_num 부분
                                        view_num = int(
                                            row.find_element_by_css_selector(
                                                'div.content-wrapper > div.content > aside > ul > li.samsung-tile-views > b'
                                            ).text.strip().replace(",", ""))
                                        # main article header reply_num 부분
                                        reply_num = int(
                                            row.find_element_by_css_selector(
                                            'div.content-wrapper > div.content > aside > ul > li.samsung-tile-replies > b'
                                            ).text.strip().replace(",", ""))

                                         # 해당 본문 페이지 이동
                                        link_ele.click()
                                        sleep(self.delay_time)
                                        ############################################본문 페이지 메인 엘러먼트##########################################
                                        self.action_wait(mode='css', ele_val='div.lia-message-body-content')
                                        main_body_ele = self.driver.find_elements_by_css_selector('div.lia-quilt-row lia-quilt-row-main')
                                        article_main_ele = main_body_ele[0]
                                        # main article header Date 부분
                                        reportDate_ele = self.get_elements(mode='css',
                                                                           ele_val='span.local-date',
                                                                           ele_parent=article_main_ele)
                                        reportTime_ele = self.get_elements(mode='css',
                                                                           ele_val='span.local-time',
                                                                           ele_parent=article_main_ele)
                                        # 날짜 형식 변경
                                        reportDate_str = reportDate_ele[0].text
                                        reportDate_str = re.findall('[0-9]{2}-[0-9]{2}-[0-9]{4}', reportDate_str)
                                        reportDate_date = datetime.strptime(reportDate_str[0], "%m-%d-%Y")
                                        # 시간 형식 변경
                                        reportTime_str = reportTime_ele[0].text
                                        reportTime_str = re.sub('(AM|PM|am|pm)', '', reportTime_str)
                                        # 최종 값
                                        reportDate = reportDate_date.strftime("%Y-%m-%d").strip()
                                        reportTime = reportTime_str.strip()

                                        # story 또는 image_url 또는 video_url 또는 댓글 부분
                                        list_main_article = self.get_main_article_sm()

                                        self.setPrint(
                                            '게시번호: {}\n카페이름: {}\nnav: {}\n타입: {}\n디바이스: {}\n제목: {}\nDate: {} {}\n조회수: {}\n댓글수: {}\n내용:\n{}\n이미지:\n{}\n비디오:\n{}\n댓글:\n{}'.format
                                            (board_num, cafeName, nav_name, '공통', '공통', title, reportDate, reportTime,
                                             view_num, reply_num,
                                             list_main_article[0], list_main_article[1], list_main_article[2],
                                             list_main_article[3]))

                                        # set each list value
                                        list_bo_no.append(board_num)
                                        list_navi.append(nav_name)
                                        list_type.append('공통')
                                        list_device.append('공통')
                                        list_report_date.append(reportDate)
                                        list_report_time.append(reportTime)
                                        list_title.append(title)
                                        list_stroy.append(list_main_article[0])
                                        list_reply.append(list_main_article[3])
                                        list_cate.append('Unknown')
                                        list_status.append('Unknown')
                                        list_reply_num.append(reply_num)
                                        list_view_num.append(view_num)
                                        list_story_url.append(story_url)
                                        list_img_url.append(list_main_article[1])
                                        list_video_url.append(list_main_article[2])
                                        # 추출 데이터 count 기록
                                        extract_num = extract_num + 1
                                        # tr 리스트로 이동
                                        self.action_page_move(mode='back')

                                        # wait element
                                        self.action_wait(mode='css', ele_val='article.custom-message-tile')
                                        # 데이터 테이블의 마지막 행인 경우
                                        if idx == article_size:
                                            page_num = page_num + 1
                                            page_ele = self.get_elements(mode='xpath', ele_val='//a[@aria-label="' + str(page_num) + '페이지"]')
                                            self.driver.execute_script('arguments[0].scrollIntoView();', page_ele[0])
                                            # action = ActionChains(self.driver)
                                            # action.move_to_element(page_ele[0]).perform()
                                            page_ele[0].click()
                                            self.setPrint('{} Page 페이지로 이동'.format(page_num))
                                            break
                    # mongoDB에 최근 record가 있는 경우
                    else:
                        while True:
                            if flag_end:
                                break
                            else:
                                self.action_wait(mode='css', ele_val='article.custom-message-tile')
                                # article 데이터들
                                list_articles = self.get_elements(mode='css', ele_val='article.custom-message-tile')
                                article_size = len(list_articles)
                                # 테이블 리스트 each tr 조회
                                for idx in range(2, article_size + 1):
                                    # article 값 추출
                                    sleep(self.delay_time)
                                    self.action_wait(mode='css', ele_val='section > article:nth-child('+ str(idx) +')')
                                    row = self.driver.find_element_by_css_selector('section > article:nth-child('+ str(idx) +')')
                                    row_attr = row.get_attribute('class')
                                    # 고정 float article이 있으면 continue
                                    if 'custom-thread-floated' in row_attr:
                                        continue
                                    link_ele = row.find_element_by_css_selector('div > h3 > a')
                                    story_url = link_ele.get_attribute('href').strip()
                                    board_num = story_url+'/e'
                                    board_num = self.find_between(board_num, 'td-p/', '/e')
                                    board_num = int(board_num)
                                    # 서버에 있는 보더 넘버를 현재 번호와 비교하여 flag_end 결정
                                    flag_end = self.compared_num(recent_num, board_num)
                                    if flag_end:
                                        break
                                    else:
                                        if board_num in list_bo_no:
                                            continue
                                        # self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, )))
                                        title = link_ele.text.strip()
                                        # main article header view_num 부분
                                        view_num = int(row.find_element_by_css_selector('li.custom-tile-views > b').text.strip().replace(",", ""))
                                        # main article header reply_num 부분
                                        reply_num = int(row.find_element_by_css_selector('li.custom-tile-replies > b').text.strip().replace(",", ""))

                                         # 해당 본문 페이지 이동
                                        link_ele.click()
                                        ############################################본문 페이지 메인 엘러먼트##########################################
                                        self.action_wait(mode='css', ele_val='div.lia-quilt-layout-custom-message')
                                        main_body_ele = self.driver.find_elements_by_css_selector('div.lia-quilt-layout-custom-message')
                                        article_main_ele = main_body_ele[0]
                                        sleep(self.delay_time)
                                        # main article header Date 부분
                                        reportDate_ele = self.get_elements(mode='css',
                                                                           ele_val='span.local-date',
                                                                           ele_parent=article_main_ele)
                                        reportTime_ele = self.get_elements(mode='css',
                                                                           ele_val='span.local-time',
                                                                           ele_parent=article_main_ele)
                                        # 날짜 형식 변경
                                        reportDate_str = reportDate_ele[1].text
                                        reportDate_str = re.findall('[0-9]{2}-[0-9]{2}-[0-9]{4}', reportDate_str)
                                        reportDate_date = datetime.strptime(reportDate_str[0], "%m-%d-%Y")
                                        # 시간 형식 변경
                                        reportTime_str = reportTime_ele[1].text
                                        reportTime_str = re.sub('(AM|PM|am|pm)', '', reportTime_str)
                                        # 최종 값
                                        reportDate = reportDate_date.strftime("%Y-%m-%d")
                                        reportTime = reportTime_str

                                        # story 또는 image_url 또는 video_url 또는 댓글 부분
                                        list_main_article = self.get_main_article_sm()

                                        self.setPrint(
                                            '게시번호: {}\n카페이름: {}\nnav: {}\n타입: {}\n디바이스: {}\n제목: {}\nDate: {} {}\n조회수: {}\n댓글수: {}\n내용:\n{}\n이미지:\n{}\n비디오:\n{}\n댓글:\n{}'.format
                                            (board_num, cafeName, nav_name, '공통', '공통', title, reportDate, reportTime,
                                             view_num, reply_num,
                                             list_main_article[0], list_main_article[1], list_main_article[2],
                                             list_main_article[3]))

                                        # set each list value
                                        list_bo_no.append(board_num)
                                        list_navi.append(nav_name)
                                        list_type.append('공통')
                                        list_device.append('공통')
                                        list_report_date.append(reportDate)
                                        list_report_time.append(reportTime)
                                        list_title.append(title)
                                        list_stroy.append(list_main_article[0])
                                        list_reply.append(list_main_article[3])
                                        list_cate.append('Unknown')
                                        list_status.append('Unknown')
                                        list_reply_num.append(reply_num)
                                        list_view_num.append(view_num)
                                        list_story_url.append(story_url)
                                        list_img_url.append(list_main_article[1])
                                        list_video_url.append(list_main_article[2])
                                        # 추출 데이터 count 기록
                                        extract_num = extract_num + 1
                                        # tr 리스트로 이동
                                        self.action_page_move(mode='back')

                                        # wait element
                                        self.action_wait(mode='css', ele_val='article.custom-message-tile')
                                        # 데이터 테이블의 마지막 행인 경우
                                        if idx == article_size:
                                            page_num = page_num + 1
                                            page_ele = self.get_elements(mode='xpath', ele_val='//a[@aria-label="' + str(page_num) + '페이지"]')
                                            self.driver.execute_script('arguments[0].scrollIntoView();', page_ele[0])
                                            # action = ActionChains(self.driver)
                                            # action.move_to_element(page_ele[0]).perform()
                                            page_ele[0].click()
                                            self.setPrint('{} Page 페이지로 이동'.format(page_num))
                                            break

                    # frame main content로 변경
                    self.setPrint('삼성 커뮤니티 {} 구역 페이지 크롤링 종료 총 {} Data 추출 완료'.format(nav_name, extract_num))

                # Upload data가 있다면
                if len(list_bo_no) != 0:
                    # generate dict_result
                    # generate cafe name list
                    regiDate = self.getCurrent_time()[1]

                    for idx in range(len(list_bo_no)):

                        list_cafeName.append(cafeName)
                        unique_id = self.generate_id()
                        list_uniqueID.append(unique_id)
                        list_regiDate.append(regiDate)

                    # grouping each list values
                    list_group = [list_bo_no, list_cafeName, list_navi, list_type, list_device, list_report_date, list_report_time, list_regiDate,
                                  list_title, list_stroy, list_reply, list_cate, list_status, list_reply_num, list_view_num, list_story_url,
                                  list_img_url, list_video_url, list_uniqueID]

                    # generate dict_result
                    for idx, item in enumerate(list_group):
                        dict_result[self.list_cols[idx]] = item
                    # append dict_result to total result list array
                    self.list_result.append({'삼성 커뮤니티': dict_result})
                    # insert data to mongoDB server
                    upload_stauts = self.myDB.insertData(dict_result, 1)
                    self.list_upload_status.append(upload_stauts)

                # Upload Data가 없다면
                else:
                    # append empty dict to total result
                    self.list_result.append({'삼성 커뮤니티': {}})
                    self.list_upload_status.append('Data None')

                sleep(self.delay_time)
                self.setPrint('{} 사이트 크롤링 작업 완료'.format(cafeName))
        except:
            self.setPrint('Error Occurred : {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno))
            self.list_result.append({cafeName: {}})
            self.list_upload_status.append('Error Occurred : {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno))
            # self.process_flag = False

    # 삼성스마트폰 커뮤니티 실행 함수
    def activate_samsungComm(self, dict_object, name):

        cafeName = name
        try:
            # config values
            url = dict_object['URL'][0]
            list_search = dict_object['검색어']
            list_nav = dict_object['네비게이션']
            list_primary = dict_object['PRIMARY_KEYS']
            list_secondary = dict_object['SECONDARY_KEYS']
            list_exclude = dict_object['EXCLUDE_KEYS']
            execute_mode = dict_object['EXECUTES_MODE'][0]
            work_mode = dict_object['WORK_MODE'][0]
            dict_result = {}

            # ON/OFF 설정 값에서 'OFF'일 경우
            if work_mode == 'OFF':
                self.setPrint('{} 구역 페이지 설정에 의해 크롤링 Skip 처리'.format(cafeName))
                self.list_result.append({cafeName: {}})
                self.list_upload_status.append('설정에 의해 {} 크롤링 Skip 처리'.format(cafeName))
                pass

            # ON/OFF 설정 값에서 'ON'일 경우
            else:
                # data groups
                list_bo_no = []
                list_cafeName = []
                list_navi = []
                list_type = []
                list_device = []
                list_report_date = []
                list_report_time = []
                list_regiDate = []
                list_title = []
                list_stroy = []
                list_reply = []
                list_cate = []
                list_status = []
                list_reply_num = []
                list_view_num = []
                list_story_url = []
                list_img_url = []
                list_video_url = []
                list_uniqueID = []


                # 메인 페이지 이외 팝업 삭제
                self.driver.get(url)
                # self.close_window(mode=1)
                sleep(self.delay_time)
                self.action_wait(mode='id', ele_val='front-cafe')

                for item in list_nav:

                    recent_num = 0
                    page_num = 1
                    extract_num = 0
                    flag_end = False

                    # nav_url parsing
                    list_text = item.split('(')
                    nav_url = list_text[0]
                    nav_name = list_text[1]
                    nav_name = nav_name[:len(nav_name) - 1]

                    self.setPrint('{} {} 구역 페이지 크롤링 시작'.format(cafeName, nav_name))
                    # main 프레임으로 변경
                    self.change_frame(mode=2)
                    # 해당 페이지로 이동
                    self.driver.get(nav_url)
                    sleep(0.5)

                    # iframe으로 변경
                    frame_ele = self.get_elements(mode='id', ele_val='cafe_main')
                    self.change_frame(element=frame_ele[0], mode=1)

                    # title 대기
                    self.action_wait(mode='css', ele_val='#sub-tit > div.title_area > div > h3')
                    # device_name , type_name 값 추출
                    title_raw = self.get_elements(mode='css', ele_val='#sub-tit > div.title_area > div > h3')[0].text
                    titles = title_raw.split()
                    device_name = titles[0]
                    type_name = titles[1]
                    flag_search_mode = 'today'
                    sleep(self.delay_time)

                    # DB에 최신 값을 조회한 후 DB가 비어 있다면 오늘 데이터만 찾는 방식이고 있다면 최신 보드 번호를 기록 후 이를 기준으로 이후 데이터만 크롤링이 실행된다
                    list_recent = self.myDB.check_recent(cafeName, nav_name, type_name, 1)
                    if len(list_recent) != 0 and execute_mode.lower() != 'today' and execute_mode != 'Null':
                        flag_search_mode = 'recent'
                        recent_num = int(list_recent[0]['bo_no'])
                        self.setPrint("최근 {} 게시글 번호: {}".format(nav_name, recent_num))

                    self.setPrint('조회방법 : {}'.format(flag_search_mode))

                    # 15개 보기를 50개 보는 방식으로 변경
                    self.action_wait(mode='css', ele_val='#main-area > div:nth-child(6) > table > tbody')
                    self.action_click(mode='css', ele_val='#listSizeSelectDiv > a')
                    sleep(self.delay_time)
                    self.action_click(mode='css', ele_val='#listSizeSelectDiv > ul > li:nth-child(7) > a')
                    sleep(self.delay_time)

                    # 순회 크롤링 시작
                    # 서버에 데이터가 하나도 없는 경우 당일 데이터만 추출
                    if flag_search_mode == 'today':
                        while True:
                            if flag_end:
                                break
                            else:
                                self.action_wait(mode='css', ele_val='#main-area > div:nth-child(6) > table > tbody')
                                # 테이블 리스트 each tr 조회
                                for idx in range(1, 50):
                                    # tr element 대기
                                    sleep(self.delay_time)
                                    self.action_wait(mode='css', ele_val='#main-area')
                                    div_parents = self.driver.find_elements_by_css_selector('div.article-board')
                                    # tr 값 추출
                                    tr_ele = self.get_elements(mode='css', ele_val='table > tbody > tr:nth-child(' + str(idx) + ')', ele_parent=div_parents[1])
                                    board_num = tr_ele[0].find_element_by_css_selector('td.td_article > div.board-number > div').text.strip()
                                    board_num = int(board_num.strip())
                                    time_value = tr_ele[0].find_element_by_css_selector('td.td_date').text.strip()
                                    # 당일 데이터만 획득
                                    flag_end = self.check_today(time_value)
                                    if flag_end:
                                        break
                                    else:
                                        # 중복 데이터일 경우
                                        if board_num in list_bo_no:
                                            # 데이터 테이블의 마지막 행인 경우
                                            if idx == 49:
                                                if page_num % 10 == 0:
                                                    page_num = page_num + 1
                                                    list_pages = self.driver.find_elements_by_css_selector('div.prev-next')
                                                    page_ele = self.get_elements(mode='css',
                                                                                 ele_val='a.pgR',
                                                                                 ele_parent=list_pages[0])
                                                    self.driver.execute_script('arguments[0].scrollIntoView();', page_ele[0])
                                                    page_ele[0].click()
                                                else:
                                                    page_num = page_num + 1
                                                    list_pages = self.driver.find_elements_by_css_selector('div.prev-next')
                                                    page_ele = self.get_elements(mode='xpath',
                                                                                 ele_val='//a[text()="' + str(page_num) + '"]',
                                                                                 ele_parent=list_pages[0])
                                                    self.driver.execute_script('arguments[0].scrollIntoView();', page_ele[0])
                                                    page_ele[0].click()
                                                self.setPrint('{} Page 페이지로 이동'.format(page_num))
                                                break
                                            continue

                                        # self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, )))
                                        title_ele = tr_ele[0].find_element_by_css_selector('td.td_article > div.board-list > div > a.article')
                                        title = title_ele.text.strip()
                                        # story_url = title_ele.get_attribute('href').strip()
                                        story_url = 'https://cafe.naver.com/anycallusershow/'+str(board_num)
                                        view_num = int(tr_ele[0].find_element_by_css_selector('td.td_view').text.strip().replace(",", ""))

                                        # 해당 본문 페이지 이동
                                        try:
                                            title_ele.click()
                                            sleep(self.delay_time)
                                            ############################################본문 페이지 메인 엘러먼트##########################################
                                            self.action_wait(mode='css', ele_val='#app > div > div > div.ArticleContentBox')
                                            article_main_ele = self.driver.find_element_by_css_selector('#app > div > div > div.ArticleContentBox')
                                            # main article header Date 부분
                                            reportDate_ele = self.get_elements(mode='css',
                                                                               ele_val='div.article_header > div.WriterInfo > div > div.article_info > span.date',
                                                                               ele_parent=article_main_ele)
                                            reportDate_str = reportDate_ele[0].text.strip()
                                            list_reportDate = self.get_date_sc(reportDate_str)
                                            reportDate = list_reportDate[0]
                                            reportTime = list_reportDate[1]

                                            # main article header reply_num 부분
                                            reply_num_ele = self.get_elements(mode='css',
                                                                              ele_val='div.article_header > div.ArticleTool > a.button_comment > strong',
                                                                              ele_parent=article_main_ele)
                                            reply_num = int(reply_num_ele[0].text.strip().replace(",", ""))

                                            # story 또는 image_url 또는 video_url 또는 댓글 부분
                                            list_main_article = self.get_main_article_sc()

                                            self.setPrint(
                                                '게시번호: {}\n카페이름: {}\nnav: {}\n타입: {}\n디바이스: {}\n제목: {}\nDate: {} {}\n조회수: {}\n댓글수: {}\n내용:\n{}\n이미지:\n{}\n비디오:\n{}\n댓글:\n{}'.format
                                                (board_num, cafeName, nav_name, type_name, device_name, title, reportDate, reportTime,
                                                 view_num, reply_num, list_main_article[0], list_main_article[1], list_main_article[2],
                                                 list_main_article[3]))

                                            # set each list value
                                            list_bo_no.append(board_num)
                                            list_navi.append(nav_name)
                                            list_type.append(type_name)
                                            list_device.append(device_name)
                                            list_report_date.append(reportDate)
                                            list_report_time.append(reportTime)
                                            list_title.append(title)
                                            list_stroy.append(list_main_article[0])
                                            list_reply.append(list_main_article[3])
                                            list_cate.append('Unknown')
                                            list_status.append('Unknown')
                                            list_reply_num.append(reply_num)
                                            list_view_num.append(view_num)
                                            list_story_url.append(story_url)
                                            list_img_url.append(list_main_article[1])
                                            list_video_url.append(list_main_article[2])

                                            extract_num = extract_num + 1
                                            # tr 리스트로 이동
                                            self.action_page_move(mode='back')

                                            # iframe으로 변경
                                            self.change_frame(mode=2)
                                            frame_ele = self.get_elements(mode='id', ele_val='cafe_main')
                                            self.change_frame(element=frame_ele[0], mode=1)
                                            self.action_wait(mode='css', ele_val='#main-area > div:nth-child(6) > table > tbody')

                                            # 데이터 테이블의 마지막 행인 경우
                                            if idx == 49:
                                                if page_num % 10 == 0:
                                                    page_num = page_num + 1
                                                    list_pages = self.driver.find_elements_by_css_selector('div.prev-next')
                                                    page_ele = self.get_elements(mode='css',
                                                                                 ele_val='a.pgR',
                                                                                 ele_parent=list_pages[0])
                                                    self.driver.execute_script('arguments[0].scrollIntoView();', page_ele[0])
                                                    # action = ActionChains(self.driver)
                                                    # action.move_to_element(page_ele[0]).perform()
                                                    page_ele[0].click()
                                                else:
                                                    page_num = page_num + 1
                                                    list_pages = self.driver.find_elements_by_css_selector('div.prev-next')
                                                    page_ele = self.get_elements(mode='xpath',
                                                                                 ele_val='//a[text()="' + str(page_num) + '"]',
                                                                                 ele_parent=list_pages[0])
                                                    self.driver.execute_script('arguments[0].scrollIntoView();', page_ele[0])
                                                    # action = ActionChains(self.driver)
                                                    # action.move_to_element(page_ele[0]).perform()
                                                    page_ele[0].click()
                                                self.setPrint('{} Page 페이지로 이동'.format(page_num))
                                                break
                                        except UnexpectedAlertPresentException:
                                            self.setPrint('회원글 삭제')
                                            # 데이터 테이블의 마지막 행인 경우
                                            if idx == 49:
                                                if page_num % 10 == 0:
                                                    page_num = page_num + 1
                                                    list_pages = self.driver.find_elements_by_css_selector('div.prev-next')
                                                    page_ele = self.get_elements(mode='css',
                                                                                ele_val='a.pgR',
                                                                                ele_parent=list_pages[0])
                                                    self.driver.execute_script('arguments[0].scrollIntoView();',
                                                                                page_ele[0])
                                                    page_ele[0].click()
                                                else:
                                                    page_num = page_num + 1
                                                    list_pages = self.driver.find_elements_by_css_selector(
                                                            'div.prev-next')
                                                    page_ele = self.get_elements(mode='xpath',
                                                                                ele_val='//a[text()="' + str(page_num) + '"]',
                                                                                ele_parent=list_pages[0])
                                                    self.driver.execute_script('arguments[0].scrollIntoView();',
                                                                            page_ele[0])
                                                    page_ele[0].click()
                                                self.setPrint('{} Page 페이지로 이동'.format(page_num))
                                                break
                                            continue
                    # mongoDB에 최근 record가 있는 경우
                    else:
                        while True:
                            if flag_end:
                                break
                            else:
                                # 테이블 리스트 each tr 조회
                                for idx in range(1, 50):
                                    # tr element 대기
                                    sleep(self.delay_time)
                                    self.action_wait(mode='css', ele_val='#main-area')
                                    div_parents = self.driver.find_elements_by_css_selector('div.article-board')
                                    # tr 값 추출
                                    tr_ele = self.get_elements(mode='css', ele_val='table > tbody > tr:nth-child(' + str(idx) + ')', ele_parent=div_parents[1])
                                    board_num = tr_ele[0].find_element_by_css_selector('td.td_article > div.board-number > div').text.strip()
                                    board_num = int(board_num.strip())
                                    # 서버에 있는 보더 넘버를 현재 번호와 비교하여 flag_end 결정
                                    flag_end = self.compared_num(recent_num, board_num)
                                    if flag_end:
                                        break
                                    else:
                                        # 중복 데이터일 경우
                                        if board_num in list_bo_no:
                                            # 데이터 테이블의 마지막 행인 경우
                                            if idx == 49:
                                                if page_num % 10 == 0:
                                                    page_num = page_num + 1
                                                    list_pages = self.driver.find_elements_by_css_selector('div.prev-next')
                                                    page_ele = self.get_elements(mode='css',
                                                                                 ele_val='a.pgR',
                                                                                 ele_parent=list_pages[0])
                                                    self.driver.execute_script('arguments[0].scrollIntoView();', page_ele[0])
                                                    page_ele[0].click()
                                                else:
                                                    page_num = page_num + 1
                                                    list_pages = self.driver.find_elements_by_css_selector('div.prev-next')
                                                    page_ele = self.get_elements(mode='xpath',
                                                                                 ele_val='//a[text()="' + str(page_num) + '"]',
                                                                                 ele_parent=list_pages[0])
                                                    self.driver.execute_script('arguments[0].scrollIntoView();', page_ele[0])
                                                    page_ele[0].click()
                                                self.setPrint('{} Page 페이지로 이동'.format(page_num))
                                                break
                                            continue
                                        # self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, )))
                                        title_ele = tr_ele[0].find_element_by_css_selector('td.td_article > div.board-list > div > a.article')
                                        title = title_ele.text.strip()
                                        # story_url = title_ele.get_attribute('href').strip()
                                        story_url = 'https://cafe.naver.com/anycallusershow/'+str(board_num)
                                        view_num = int(tr_ele[0].find_element_by_css_selector('td.td_view').text.replace(',', '').strip())
                                        # 해당 본문 페이지 이동
                                        try:
                                            title_ele.click()
                                            sleep(self.delay_time)
                                            ############################################본문 페이지 메인 엘러먼트##########################################
                                            self.action_wait(mode='css', ele_val='#app > div > div > div.ArticleContentBox')
                                            article_main_ele = self.driver.find_element_by_css_selector('#app > div > div > div.ArticleContentBox')
                                            # main article header Date 부분
                                            reportDate_ele = self.get_elements(mode='css', ele_val='div.article_header > div.WriterInfo > div > div.article_info > span.date', ele_parent=article_main_ele)
                                            reportDate_str = reportDate_ele[0].text.strip()
                                            list_reportDate = self.get_date_sc(reportDate_str)
                                            reportDate = list_reportDate[0]
                                            reportTime = list_reportDate[1]

                                            # main article header reply_num 부분
                                            reply_num_ele = self.get_elements(mode='css', ele_val='div.article_header > div.ArticleTool > a.button_comment > strong', ele_parent=article_main_ele)
                                            reply_num = int(reply_num_ele[0].text.strip().replace(",", ""))

                                            # story 또는 image_url 또는 video_url 또는 댓글 부분
                                            list_main_article = self.get_main_article_sc()

                                            self.setPrint(
                                                '게시번호: {}\n카페이름: {}\nnav: {}\n타입: {}\n디바이스: {}\n제목: {}\nDate: {} {}\n조회수: {}\n댓글수: {}\n내용:\n{}\n이미지:\n{}\n비디오:\n{}\n댓글:\n{}'.format
                                                (board_num, cafeName, nav_name, type_name, device_name, title, reportDate, reportTime,
                                                 view_num, reply_num, list_main_article[0], list_main_article[1], list_main_article[2],
                                                 list_main_article[3]))

                                            # set each list value
                                            list_bo_no.append(board_num)
                                            list_navi.append(nav_name)
                                            list_type.append(type_name)
                                            list_device.append(device_name)
                                            list_report_date.append(reportDate)
                                            list_report_time.append(reportTime)
                                            list_title.append(title)
                                            list_stroy.append(list_main_article[0])
                                            list_reply.append(list_main_article[3])
                                            list_cate.append('Unknown')
                                            list_status.append('Unknown')
                                            list_reply_num.append(reply_num)
                                            list_view_num.append(view_num)
                                            list_story_url.append(story_url)
                                            list_img_url.append(list_main_article[1])
                                            list_video_url.append(list_main_article[2])

                                            extract_num = extract_num + 1
                                            # tr 리스트로 이동
                                            self.action_page_move(mode='back')

                                            # iframe으로 변경
                                            self.change_frame(mode=2)
                                            frame_ele = self.get_elements(mode='id', ele_val='cafe_main')
                                            self.change_frame(element=frame_ele[0], mode=1)
                                            self.action_wait(mode='css', ele_val='#main-area > div:nth-child(6) > table > tbody')

                                            # 데이터 테이블의 마지막 행인 경우
                                            if idx == 49:
                                                if page_num % 10 == 0:
                                                    page_num = page_num + 1
                                                    list_pages = self.driver.find_elements_by_css_selector('div.prev-next')
                                                    page_ele = self.get_elements(mode='css',
                                                                                 ele_val='a.pgR',
                                                                                 ele_parent=list_pages[0])
                                                    # action = ActionChains(self.driver)
                                                    # action.move_to_element(page_ele[0]).perform()
                                                    self.driver.execute_script('arguments[0].scrollIntoView();', page_ele[0])
                                                    page_ele[0].click()
                                                else:
                                                    page_num = page_num + 1
                                                    list_pages = self.driver.find_elements_by_css_selector('div.prev-next')
                                                    page_ele = self.get_elements(mode='xpath',
                                                                                 ele_val='//a[text()="' + str(page_num) + '"]',
                                                                                 ele_parent=list_pages[0])
                                                    self.driver.execute_script('arguments[0].scrollIntoView();', page_ele[0])
                                                    # action = ActionChains(self.driver)
                                                    # action.move_to_element(page_ele[0]).perform()
                                                    page_ele[0].click()
                                                self.setPrint('{} Page 페이지로 이동'.format(page_num))
                                                break
                                        except UnexpectedAlertPresentException:
                                            self.setPrint('회원글 삭제')
                                            # 데이터 테이블의 마지막 행인 경우
                                            if idx == 49:
                                                if page_num % 10 == 0:
                                                    page_num = page_num + 1
                                                    list_pages = self.driver.find_elements_by_css_selector('div.prev-next')
                                                    page_ele = self.get_elements(mode='css',
                                                                                 ele_val='a.pgR',
                                                                                 ele_parent=list_pages[0])
                                                    self.driver.execute_script('arguments[0].scrollIntoView();',page_ele[0])
                                                    page_ele[0].click()
                                                else:
                                                    page_num = page_num + 1
                                                    list_pages = self.driver.find_elements_by_css_selector('div.prev-next')
                                                    page_ele = self.get_elements(mode='xpath',
                                                                                 ele_val='//a[text()="' + str(page_num) + '"]',
                                                                                 ele_parent=list_pages[0])
                                                    self.driver.execute_script('arguments[0].scrollIntoView();', page_ele[0])
                                                    page_ele[0].click()
                                                self.setPrint('{} Page 페이지로 이동'.format(page_num))
                                                break
                                            continue

                    # frame main content로 변경
                    self.setPrint('삼성스마트폰 커뮤니티 {} 구역 페이지 크롤링 종료 총 {} Data 추출 완료'.format(nav_name, extract_num))
                # Upload data가 있다면
                if len(list_bo_no) != 0:
                    # generate dict_result
                    # generate cafe name list
                    regiDate = self.getCurrent_time()[1]

                    for idx in range(len(list_bo_no)):

                        list_cafeName.append(cafeName)
                        unique_id = self.generate_id()
                        list_uniqueID.append(unique_id)
                        list_regiDate.append(regiDate)

                    # grouping each list values
                    list_group = [list_bo_no, list_cafeName, list_navi, list_type, list_device, list_report_date, list_report_time, list_regiDate,
                                  list_title, list_stroy, list_reply, list_cate, list_status, list_reply_num, list_view_num, list_story_url,
                                  list_img_url, list_video_url, list_uniqueID]

                    # generate dict_result
                    for idx, item in enumerate(list_group):
                        dict_result[self.list_cols[idx]] = item
                    # append dict_result to total result list array
                    self.list_result.append({'삼성스마트폰 커뮤니티': dict_result})
                    # insert data to mongoDB server
                    upload_stauts = self.myDB.insertData(dict_result, 1)
                    self.list_upload_status.append(upload_stauts)
                # Upload Data가 없다면
                else:
                    # append empty dict to total result
                    self.list_result.append({'삼성스마트폰 커뮤니티': {}})
                    self.list_upload_status.append('Data None')

                sleep(self.delay_time)
                self.setPrint('{} 사이트 크롤링 작업 완료'.format(cafeName))
        except:
            self.setPrint('Error Occurred : {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno))
            self.list_result.append({cafeName: {}})
            self.list_upload_status.append('Error Occurred : {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno))
            # self.process_flag = False

    # 엘지 커뮤니티 실행 함수
    def activate_lgComm(self, dict_object, name):

        cafeName = name
        try:
            # config values
            url = dict_object['URL'][0]
            list_search = dict_object['검색어']
            list_nav = dict_object['네비게이션']
            list_primary = dict_object['PRIMARY_KEYS']
            list_secondary = dict_object['SECONDARY_KEYS']
            list_exclude = dict_object['EXCLUDE_KEYS']
            execute_mode = dict_object['EXECUTES_MODE'][0]
            work_mode = dict_object['WORK_MODE'][0]
            dict_result = {}

            # ON/OFF 설정 값에서 'OFF'일 경우
            if work_mode == 'OFF':
                self.setPrint('{} 구역 페이지 설정에 의해 크롤링 Skip 처리'.format(cafeName))
                self.list_result.append({cafeName: {}})
                self.list_upload_status.append('설정에 의해 {} 크롤링 Skip 처리'.format(cafeName))
                pass

            # ON/OFF 설정 값에서 'ON'일 경우
            else:
                # data groups
                list_bo_no = []
                list_cafeName = []
                list_navi = []
                list_type = []
                list_device = []
                list_report_date = []
                list_report_time = []
                list_regiDate = []
                list_title = []
                list_stroy = []
                list_reply = []
                list_cate = []
                list_status = []
                list_reply_num = []
                list_view_num = []
                list_story_url = []
                list_img_url = []
                list_video_url = []
                list_uniqueID = []


                # 메인 페이지 이외 팝업 삭제
                self.driver.get(url)
                # self.close_window(mode=1)
                sleep(self.delay_time)
                self.action_wait(mode='id', ele_val='front-cafe')

                for item in list_nav:

                    recent_num = 0
                    page_num = 1
                    extract_num = 0
                    flag_end = False

                    # nav_url parsing
                    list_text = item.split('(')
                    nav_url = list_text[0]
                    nav_name = list_text[1]
                    nav_name = nav_name[:len(nav_name) - 1]

                    self.setPrint('{} {} 구역 페이지 크롤링 시작'.format(cafeName, nav_name))
                    # main 프레임으로 변경
                    self.change_frame(mode=2)
                    # 해당 페이지로 이동
                    self.driver.get(nav_url)
                    sleep(0.5)

                    # iframe으로 변경
                    frame_ele = self.get_elements(mode='id', ele_val='cafe_main')
                    self.change_frame(element=frame_ele[0], mode=1)

                    # title 대기
                    self.action_wait(mode='css', ele_val='#sub-tit > div.title_area > div > h3')
                    # device_name , type_name 값 추출
                    title_raw = self.get_elements(mode='css', ele_val='#sub-tit > div.title_area > div > h3')[0].text
                    titles = title_raw.split()
                    device_name = titles[0]
                    type_name = titles[1]
                    flag_search_mode = 'today'
                    sleep(self.delay_time)

                    # DB에 최신 값을 조회한 후 DB가 비어 있다면 오늘 데이터만 찾는 방식이고 있다면 최신 보드 번호를 기록 후 이를 기준으로 이후 데이터만 크롤링이 실행된다
                    list_recent = self.myDB.check_recent(cafeName, nav_name, type_name, 2)
                    if len(list_recent) != 0 and execute_mode.lower() != 'today' and execute_mode != 'Null':
                        flag_search_mode = 'recent'
                        recent_num = int(list_recent[0]['bo_no'])
                        self.setPrint("최근 {} 게시글 번호: {}".format(item, recent_num))

                    self.setPrint('조회방법 : {}'.format(flag_search_mode))
                    # 15개 보기를 50개 보는 방식으로 변경
                    self.action_wait(mode='css', ele_val='#main-area > div:nth-child(6) > table > tbody')
                    self.action_click(mode='css', ele_val='#listSizeSelectDiv > a')
                    sleep(self.delay_time)
                    self.action_click(mode='css', ele_val='#listSizeSelectDiv > ul > li:nth-child(7) > a')
                    sleep(self.delay_time)

                    # 순회 크롤링 시작
                    # 서버에 데이터가 하나도 없는 경우 당일 데이터만 추출
                    if flag_search_mode == 'today':
                        while True:
                            if flag_end:
                                break
                            else:
                                self.action_wait(mode='css', ele_val='#main-area > div:nth-child(6) > table > tbody')
                                # 테이블 리스트 each tr 조회
                                for idx in range(1, 50):
                                    # tr element 대기
                                    sleep(self.delay_time)
                                    self.action_wait(mode='css', ele_val='#main-area')
                                    div_parents = self.driver.find_elements_by_css_selector('div.article-board')
                                    # tr 값 추출
                                    tr_ele = self.get_elements(mode='css', ele_val='table > tbody > tr:nth-child(' + str(idx) + ')', ele_parent=div_parents[1])
                                    board_num = tr_ele[0].find_element_by_css_selector('td.td_article > div.board-number > div').text.strip()
                                    board_num = int(board_num.strip())
                                    time_value = tr_ele[0].find_element_by_css_selector('td.td_date').text.strip()
                                    # 당일 데이터만 획득
                                    flag_end = self.check_today(time_value)
                                    if flag_end:
                                        break
                                    else:
                                        # 중복 데이터일 경우
                                        if board_num in list_bo_no:
                                            # 데이터 테이블의 마지막 행인 경우
                                            if idx == 49:
                                                if page_num % 10 == 0:
                                                    page_num = page_num + 1
                                                    list_pages = self.driver.find_elements_by_css_selector('div.prev-next')
                                                    page_ele = self.get_elements(mode='css',
                                                                                 ele_val='a.pgR',
                                                                                 ele_parent=list_pages[0])
                                                    self.driver.execute_script('arguments[0].scrollIntoView();', page_ele[0])
                                                    page_ele[0].click()
                                                else:
                                                    page_num = page_num + 1
                                                    list_pages = self.driver.find_elements_by_css_selector('div.prev-next')
                                                    page_ele = self.get_elements(mode='xpath',
                                                                                 ele_val='//a[text()="' + str(page_num) + '"]',
                                                                                 ele_parent=list_pages[0])
                                                    self.driver.execute_script('arguments[0].scrollIntoView();', page_ele[0])
                                                    page_ele[0].click()
                                                self.setPrint('{} Page 페이지로 이동'.format(page_num))
                                                break
                                            continue

                                        # self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, )))
                                        title_ele = tr_ele[0].find_element_by_css_selector('td.td_article > div.board-list > div > a.article')
                                        title = title_ele.text.strip()
                                        # story_url = title_ele.get_attribute('href').strip()
                                        story_url = 'https://cafe.naver.com/optimuslteuser/'+str(board_num)
                                        view_num = int(tr_ele[0].find_element_by_css_selector('td.td_view').text.strip().replace(",", ""))

                                        # 해당 본문 페이지 이동
                                        try:
                                            title_ele.click()
                                            sleep(self.delay_time)
                                            ############################################본문 페이지 메인 엘러먼트##########################################
                                            self.action_wait(mode='css', ele_val='#app > div > div > div.ArticleContentBox')
                                            article_main_ele = self.driver.find_element_by_css_selector('#app > div > div > div.ArticleContentBox')
                                            # main article header Date 부분
                                            reportDate_ele = self.get_elements(mode='css',
                                                                               ele_val='div.article_header > div.WriterInfo > div > div.article_info > span.date',
                                                                               ele_parent=article_main_ele)
                                            reportDate_str = reportDate_ele[0].text.strip()
                                            list_reportDate = self.get_date_sc(reportDate_str)
                                            reportDate = list_reportDate[0]
                                            reportTime = list_reportDate[1]

                                            # main article header reply_num 부분
                                            reply_num_ele = self.get_elements(mode='css',
                                                                              ele_val='div.article_header > div.ArticleTool > a.button_comment > strong',
                                                                              ele_parent=article_main_ele)
                                            reply_num = int(reply_num_ele[0].text.strip().replace(",", ""))

                                            # story 또는 image_url 또는 video_url 또는 댓글 부분
                                            list_main_article = self.get_main_article_lg()

                                            self.setPrint(
                                                '게시번호: {}\n카페이름: {}\nnav: {}\n타입: {}\n디바이스: {}\n제목: {}\nDate: {} {}\n조회수: {}\n댓글수: {}\n내용:\n{}\n이미지:\n{}\n비디오:\n{}\n댓글:\n{}'.format
                                                (board_num, cafeName, nav_name, type_name, device_name, title, reportDate, reportTime,
                                                 view_num, reply_num, list_main_article[0], list_main_article[1], list_main_article[2],
                                                 list_main_article[3]))

                                            # set each list value
                                            list_bo_no.append(board_num)
                                            list_navi.append(nav_name)
                                            list_type.append(type_name)
                                            list_device.append(device_name)
                                            list_report_date.append(reportDate)
                                            list_report_time.append(reportTime)
                                            list_title.append(title)
                                            list_stroy.append(list_main_article[0])
                                            list_reply.append(list_main_article[3])
                                            list_cate.append('Unknown')
                                            list_status.append('Unknown')
                                            list_reply_num.append(reply_num)
                                            list_view_num.append(view_num)
                                            list_story_url.append(story_url)
                                            list_img_url.append(list_main_article[1])
                                            list_video_url.append(list_main_article[2])

                                            extract_num = extract_num + 1
                                            # tr 리스트로 이동
                                            self.action_page_move(mode='back')

                                            # iframe으로 변경
                                            self.change_frame(mode=2)
                                            frame_ele = self.get_elements(mode='id', ele_val='cafe_main')
                                            self.change_frame(element=frame_ele[0], mode=1)
                                            self.action_wait(mode='css', ele_val='#main-area > div:nth-child(6) > table > tbody')

                                            # 데이터 테이블의 마지막 행인 경우
                                            if idx == 49:
                                                if page_num % 10 == 0:
                                                    page_num = page_num + 1
                                                    list_pages = self.driver.find_elements_by_css_selector('div.prev-next')
                                                    page_ele = self.get_elements(mode='css',
                                                                                 ele_val='a.pgR',
                                                                                 ele_parent=list_pages[0])
                                                    # action = ActionChains(self.driver)
                                                    # action.move_to_element(page_ele[0]).perform()
                                                    self.driver.execute_script('arguments[0].scrollIntoView();', page_ele[0])
                                                    page_ele[0].click()
                                                else:
                                                    page_num = page_num + 1
                                                    list_pages = self.driver.find_elements_by_css_selector('div.prev-next')
                                                    page_ele = self.get_elements(mode='xpath',
                                                                                 ele_val='//a[text()="' + str(page_num) + '"]',
                                                                                 ele_parent=list_pages[0])
                                                    # action = ActionChains(self.driver)
                                                    # action.move_to_element(page_ele[0]).perform()
                                                    self.driver.execute_script('arguments[0].scrollIntoView();', page_ele[0])
                                                    page_ele[0].click()
                                                self.setPrint('{} Page 페이지로 이동'.format(page_num))
                                                break
                                        except UnexpectedAlertPresentException:
                                            self.setPrint('회원글 삭제')
                                            # 데이터 테이블의 마지막 행인 경우
                                            if idx == 49:
                                                if page_num % 10 == 0:
                                                    page_num = page_num + 1
                                                    list_pages = self.driver.find_elements_by_css_selector('div.prev-next')
                                                    page_ele = self.get_elements(mode='css',
                                                                                 ele_val='a.pgR',
                                                                                 ele_parent=list_pages[0])
                                                    self.driver.execute_script('arguments[0].scrollIntoView();',page_ele[0])
                                                    page_ele[0].click()
                                                else:
                                                    page_num = page_num + 1
                                                    list_pages = self.driver.find_elements_by_css_selector('div.prev-next')
                                                    page_ele = self.get_elements(mode='xpath',
                                                                                 ele_val='//a[text()="' + str(page_num) + '"]',
                                                                                 ele_parent=list_pages[0])
                                                    self.driver.execute_script('arguments[0].scrollIntoView();', page_ele[0])
                                                    page_ele[0].click()
                                                self.setPrint('{} Page 페이지로 이동'.format(page_num))
                                                break
                                            continue

                    # mongoDB에 최근 record가 있는 경우
                    else:
                        while True:
                            if flag_end:
                                break
                            else:
                                # 테이블 리스트 each tr 조회
                                for idx in range(1, 50):
                                    # tr element 대기
                                    sleep(self.delay_time)
                                    self.action_wait(mode='css', ele_val='#main-area')
                                    div_parents = self.driver.find_elements_by_css_selector('div.article-board')
                                    # tr 값 추출
                                    tr_ele = self.get_elements(mode='css', ele_val='table > tbody > tr:nth-child(' + str(idx) + ')', ele_parent=div_parents[1])
                                    board_num = tr_ele[0].find_element_by_css_selector('td.td_article > div.board-number > div').text.strip()
                                    board_num = int(board_num.strip())
                                    # 서버에 있는 보더 넘버를 현재 번호와 비교하여 flag_end 결정
                                    flag_end = self.compared_num(recent_num, board_num)
                                    if flag_end:
                                        break
                                    else:
                                        if board_num in list_bo_no:
                                            continue
                                        # self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, )))
                                        title_ele = tr_ele[0].find_element_by_css_selector('td.td_article > div.board-list > div > a.article')
                                        title = title_ele.text.strip()
                                        # story_url = title_ele.get_attribute('href').strip()
                                        story_url = 'https://cafe.naver.com/optimuslteuser/'+str(board_num)
                                        view_num = int(tr_ele[0].find_element_by_css_selector('td.td_view').text.replace(',', '').strip())
                                        # 해당 본문 페이지 이동
                                        try:
                                            title_ele.click()
                                            sleep(self.delay_time)
                                            ############################################본문 페이지 메인 엘러먼트##########################################
                                            self.action_wait(mode='css', ele_val='#app > div > div > div.ArticleContentBox')
                                            article_main_ele = self.driver.find_element_by_css_selector('#app > div > div > div.ArticleContentBox')
                                            # main article header Date 부분
                                            reportDate_ele = self.get_elements(mode='css', ele_val='div.article_header > div.WriterInfo > div > div.article_info > span.date', ele_parent=article_main_ele)
                                            reportDate_str = reportDate_ele[0].text.strip()
                                            list_reportDate = self.get_date_sc(reportDate_str)
                                            reportDate = list_reportDate[0]
                                            reportTime = list_reportDate[1]

                                            # main article header reply_num 부분
                                            reply_num_ele = self.get_elements(mode='css', ele_val='div.article_header > div.ArticleTool > a.button_comment > strong', ele_parent=article_main_ele)
                                            reply_num = int(reply_num_ele[0].text.strip().replace(",", ""))

                                            # story 또는 image_url 또는 video_url 또는 댓글 부분
                                            list_main_article = self.get_main_article_lg()

                                            self.setPrint(
                                                '게시번호: {}\n카페이름: {}\nnav: {}\n타입: {}\n디바이스: {}\n제목: {}\nDate: {} {}\n조회수: {}\n댓글수: {}\n내용:\n{}\n이미지:\n{}\n비디오:\n{}\n댓글:\n{}'.format
                                                (board_num, cafeName, nav_name, type_name, device_name, title, reportDate, reportTime,
                                                view_num, reply_num,list_main_article[0], list_main_article[1], list_main_article[2],
                                                 list_main_article[3]))

                                            # set each list value
                                            list_bo_no.append(board_num)
                                            list_navi.append(nav_name)
                                            list_type.append(type_name)
                                            list_device.append(device_name)
                                            list_report_date.append(reportDate)
                                            list_report_time.append(reportTime)
                                            list_title.append(title)
                                            list_stroy.append(list_main_article[0])
                                            list_reply.append(list_main_article[3])
                                            list_cate.append('Unknown')
                                            list_status.append('Unknown')
                                            list_reply_num.append(reply_num)
                                            list_view_num.append(view_num)
                                            list_story_url.append(story_url)
                                            list_img_url.append(list_main_article[1])
                                            list_video_url.append(list_main_article[2])

                                            extract_num = extract_num + 1
                                            # tr 리스트로 이동
                                            self.action_page_move(mode='back')

                                            # iframe으로 변경
                                            self.change_frame(mode=2)
                                            frame_ele = self.get_elements(mode='id', ele_val='cafe_main')
                                            self.change_frame(element=frame_ele[0], mode=1)
                                            self.action_wait(mode='css', ele_val='#main-area > div:nth-child(6) > table > tbody')

                                            # 데이터 테이블의 마지막 행인 경우
                                            if idx == 49:
                                                if page_num % 10 == 0:
                                                    page_num = page_num + 1
                                                    list_pages = self.driver.find_elements_by_css_selector('div.prev-next')
                                                    page_ele = self.get_elements(mode='css',
                                                                                 ele_val='a.pgR',
                                                                                 ele_parent=list_pages[0])
                                                    # action = ActionChains(self.driver)
                                                    # action.move_to_element(page_ele[0]).perform()
                                                    self.driver.execute_script('arguments[0].scrollIntoView();', page_ele[0])
                                                    page_ele[0].click()
                                                else:
                                                    page_num = page_num + 1
                                                    list_pages = self.driver.find_elements_by_css_selector('div.prev-next')
                                                    page_ele = self.get_elements(mode='xpath',
                                                                                 ele_val='//a[text()="' + str(page_num) + '"]',
                                                                                 ele_parent=list_pages[0])
                                                    # action = ActionChains(self.driver)
                                                    # action.move_to_element(page_ele[0]).perform()
                                                    self.driver.execute_script('arguments[0].scrollIntoView();', page_ele[0])
                                                    page_ele[0].click()
                                                self.setPrint('{} Page 페이지로 이동'.format(page_num))
                                                break
                                        except UnexpectedAlertPresentException:
                                            self.setPrint('회원글 삭제')
                                            # 데이터 테이블의 마지막 행인 경우
                                            if idx == 49:
                                                if page_num % 10 == 0:
                                                    page_num = page_num + 1
                                                    list_pages = self.driver.find_elements_by_css_selector('div.prev-next')
                                                    page_ele = self.get_elements(mode='css',
                                                                                 ele_val='a.pgR',
                                                                                 ele_parent=list_pages[0])
                                                    self.driver.execute_script('arguments[0].scrollIntoView();',page_ele[0])
                                                    page_ele[0].click()
                                                else:
                                                    page_num = page_num + 1
                                                    list_pages = self.driver.find_elements_by_css_selector('div.prev-next')
                                                    page_ele = self.get_elements(mode='xpath',
                                                                                 ele_val='//a[text()="' + str(page_num) + '"]',
                                                                                 ele_parent=list_pages[0])
                                                    self.driver.execute_script('arguments[0].scrollIntoView();', page_ele[0])
                                                    page_ele[0].click()
                                                self.setPrint('{} Page 페이지로 이동'.format(page_num))
                                                break
                                            continue

                    # frame main content로 변경
                    self.setPrint('엘지모바일 커뮤니티 {} 구역 페이지 크롤링 종료 총 {} Data 추출 완료'.format(nav_name, extract_num))

                # Upload data가 있다면
                if len(list_bo_no) != 0:
                    # generate dict_result
                    # generate cafe name list
                    regiDate = self.getCurrent_time()[1]

                    for idx in range(len(list_bo_no)):

                        list_cafeName.append(cafeName)
                        unique_id = self.generate_id()
                        list_uniqueID.append(unique_id)
                        list_regiDate.append(regiDate)

                    # grouping each list values
                    list_group = [list_bo_no, list_cafeName, list_navi, list_type, list_device, list_report_date, list_report_time, list_regiDate,
                                  list_title, list_stroy, list_reply, list_cate, list_status, list_reply_num, list_view_num, list_story_url,
                                  list_img_url, list_video_url, list_uniqueID]

                    # generate dict_result
                    for idx, item in enumerate(list_group):
                        dict_result[self.list_cols[idx]] = item
                    # append dict_result to total result list array
                    self.list_result.append({'엘지모바일 커뮤니티': dict_result})
                    # insert data to mongoDB server
                    upload_stauts = self.myDB.insertData(dict_result, 2)
                    self.list_upload_status.append(upload_stauts)

                # Upload Data가 없다면
                else:
                    # append empty dict to total result
                    self.list_result.append({'엘지모바일 커뮤니티': {}})
                    self.list_upload_status.append('Data None')

                sleep(self.delay_time)
                self.setPrint('{} 사이트 크롤링 작업 완료'.format(cafeName))
        except:
            self.setPrint('Error Occurred : {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno))
            self.list_result.append({cafeName: {}})
            self.list_upload_status.append('Error Occurred : {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno))
            # self.process_flag = False

    # ##############################################################################__메인 실행__###############################################################################

    # Class Main 실행 함수
    def activate_spider(self):

        try:
            # set_directory
            self.set_directory()
            # mongoDB set Connection
            self.myDB.set_connect()
            # set chrome driver
            self.setDriver()
            self.focus_flag = True
            self.hold_flag = True
            # naver log in
            self.naver_login()
            # 네이버 메인페이지 확인
            self.action_wait(mode='css', ele_val='#header > div.special_bg > div > div.logo_area')
            # samsung community start
            self.activate_samsungComm(self.dict_crawl['삼성스마트폰 커뮤니티'], '삼성스마트폰 커뮤니티')
            # samsung home community start
            self.activate_samsungHome(self.dict_crawl['삼성 커뮤니티'], '삼성 커뮤니티')
            # ppomp community start
            self.activate_ppopm(self.dict_crawl['뽐뿌 커뮤니티'], '뽐뿌 커뮤니티')
            # clien community start
            self.activate_clien(self.dict_crawl['클리앙 커뮤니티'], '클리앙 커뮤니티')
            # lg community start
            self.activate_lgComm(self.dict_crawl['엘지모바일 커뮤니티'], '엘지모바일 커뮤니티')

            # generate report
            report = ResultReport(self.report_path, self.list_result)
            report_flag = report.generate_report()
            if not report_flag:
                self.process_flag = False
            # send e-mail
            sender = SendMail(self.dict_email, report.list_dict_result, self.list_upload_status)
            sender_flag = sender.send_email(attach_path=report.report_final_path)
            if not sender_flag:
                self.process_flag = False

            self.stop()
        except:
            self.setPrint('Error Occurred : {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno))
            self.stop()

if __name__ == "__main__":
    pass
