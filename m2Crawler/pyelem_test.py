import sys
import os
import keyB as kb
import string
import json
import random
import pywinauto
from pywinauto import application
import threading

from bs4 import BeautifulSoup
from os.path import expanduser
from datetime import date, time, datetime
from time import sleep
from Check_Chromedriver import Check_Chromedriver

from m2CrawlerMongoDB import ConnDB
from m2CrawlerSender import SendMail
from m2CrawlerReporter import ResultReport

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

from m2CrawlerMongoDB import ConnDB
from m2CrawlerSender import SendMail
from m2CrawlerReporter import ResultReport


class ElemTest():

    # 클래스 초기화
    def __init__(self):

        super().__init__()
        self.start_time = ""
        self.end_time = ""

        # data groups
        self.list_bo_no = []
        self.list_cafe = []
        self.list_nav = []
        self.list_type = []
        self.list_device = []
        self.list_report_date = []
        self.list_report_time = []
        self.list_title = []
        self.list_stroy = []
        self.list_reply = []
        self.list_cate = []
        self.list_status = []
        self.list_reply_num = []
        self.list_view_num = []
        self.list_story_url = []
        self.list_img_url = []
        self.list_video_url = []
        self.list_uniqueID = []

        # config value
        self.wait_time = 15
        self.paging_num = 0
        self.delay_time = 2
        self.naver_id = 'testenc2018'
        self.naver_pw = 'Qwer1234!'
        self.error_flag = False
        self.process_flag = True
        self.dict_result = {}
        self.home = expanduser("~")
        self.image_path = self.home + "\\Desktop\\Crawler\\image\\"
        self.driver_root_path = self.home + "\\Desktop\\Crawler\\driver\\"
        self.driver_app = None
        self.chrome_driver_path = None
        self.driver = None
        self.chrome_option = None
        self.on_top_thread = None
        self.wait = None
        self.myDB = ConnDB("localhost", 27017, None, None, "crawler")
        self.myDB.set_connect()
        self.cur = None

    # always fixed chrome driver browser until finished crwaling
    def set_on_focus(self):

        # self.driver_app.top_window().set_focus()
        # self.driver.execute_script("window.focus();")

        while True:
            if not self.process_flag:
                break
            w_handle = pywinauto.findwindows.find_windows(title_re=r'.*Chrome.*')[0]
            window = self.driver_app.window(handle=w_handle)
            window.set_focus()
            sleep(0.5)

    # 설치된 Chrome 버전 확인 후 전용 Driver 자동 Download
    def set_driver(self):

        if not os.path.isdir(self.driver_root_path):
            os.makedirs(self.driver_root_path)

        Check_Chromedriver.driver_mother_path = self.driver_root_path
        Check_Chromedriver.main()
        self.chrome_driver_path = self.driver_root_path + "chromedriver.exe"

    # 현재 시간 구하여 3가지 타입으로 list return
    def getCurrent_time(self):

        nowTime = datetime.now()
        now_datetime_str = nowTime.strftime('%Y-%m-%d %H:%M:%S')
        now_datetime_str2 = nowTime.strftime('%Y-%m-%d %H %M %S')
        return [nowTime, now_datetime_str, now_datetime_str2]

    # Chrome GUI Driver 생성
    def setDriver(self):
        try:
            self.chrome_option = webdriver.ChromeOptions()
            # self.chrome_option.add_argument('headless')
            self.chrome_option.add_argument('disable-gpu')
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
            self.setPrint('Error Occurred : {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno))
            self.error_flag = True

    # 시간 정보와 함께 Console에 Print 하는 함수
    def setPrint(self, text):

        current = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        print("{}:\n{}".format(current, text) + "\n")

    # spider 함수 종료 시 Teardown
    def stop(self):

        self.driver.quit()
        self.setPrint("드라이버 종료")
        self.process_flag = False

    # URL 페이지 값 인코딩 값
    def encoding_url(self, main_url, path):

        return_url = main_url + '/' + path
        return return_url

    # unique 아이디 생성 함수
    def generate_id(self):
        charset = string.ascii_uppercase + string.digits
        uniqueId = ''.join(random.sample(charset * 15, 15))
        return uniqueId

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
                sleep(1)
                kb.typer(self.naver_id)
                sleep(1)
                ele_pw.clear()
                ele_pw.click()
                # self.driver.execute_script("arguments[0].click();", self.ele_pw)
                kb.typer(self.naver_pw)
                sleep(1)

                # login id and password print values
                self.setPrint('{} 회 로그인 시도'.format(i+1))
                self.setPrint('로그인 아이디 : {}'.format(ele_id.get_attribute('value')))
                self.setPrint('로그인 비밀번호 : {}'.format(ele_pw.get_attribute('value')))
                self.driver.execute_script("arguments[0].click();", ele_summit)
                sleep(2)

            else:
                break

        return flag_status

    # 네이버 로그인 함수(activate_crawler 실행 시 앞서 먼저 실행됨)
    def naver_login(self):

        try:
            self.driver.get("https://nid.naver.com/nidlogin.login")
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#id')))

            # chrome on top Thread
            self.driver_app = application.Application(backend='uia').connect(path=self.chrome_driver_path)
            self.on_top_thread = threading.Thread(target=self.set_on_focus, args=())
            self.on_top_thread.setDaemon(True)
            self.on_top_thread.start()

            flag = self.retry_login()
            if not flag:
                self.error_flag = True
                self.stop()
        except:
            self.setPrint('Occurred Error at naver login spot!')
            self.setPrint('Error Occurred : {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno))
            self.error_flag = True
            self.stop()



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
            self.setPrint('Error Occurred : {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno))

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

    # iframe 대응
    def change_frame(self, element=None, mode=1):

        if mode == 1:
            self.driver.switch_to.frame(element)
        else:
            self.driver.switch_to.default_content()

    # baorder num compare
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
            return True
        else:
            return False

    # 이전 버전 엘레먼트 가져오기
    def get_main_article_sd(self, ele_parent=None):

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

        #########################################################ContentRenderer 타입###################################################
        if self.is_element(mode='css', ele_val='div.ContentRenderer', ele_parent=ele_parent):
            self.setPrint('1구간')
            # get contentRender element
            content_render = self.get_elements(mode='css', ele_val='div.ContentRenderer', ele_parent=ele_parent)[0]

            # text 값이 있으면 값을 모두 획득
            if self.is_element(mode='css', ele_val='div > p', ele_parent=content_render):
                p_tags = self.get_elements(mode='css', ele_val='div > p', ele_parent=content_render)
                for ele in p_tags:
                    line = ele.text
                    if line == '':
                        story_text = story_text+'\n'
                    else:
                        story_text = story_text + line.strip()

            # 이미지가 있으면 src url 모두 획득
            if self.is_element(mode='css', ele_val='div > img', ele_parent=content_render):
                img_tags = self.get_elements(mode='css', ele_val='div > img', ele_parent=content_render)
                for idx, ele in enumerate(img_tags):
                    url = ele.get_attribute('src')
                    img_url_text = img_url_text + str(idx) + '. ' + str(url) + '\n'

            # 동영상이 있으면 src url 모두 획득
            if self.is_element(mode='css', ele_val='div > iframe', ele_parent=content_render):
                iframe_tags = self.get_elements(mode='css', ele_val='div > iframe', ele_parent=content_render)
                for idx, ele in enumerate(iframe_tags):
                    url = ele.get_attribute('src')
                    video_url_text = video_url_text + str(idx) + '. ' + str(url) + '\n'

            # NHN_Writeform이면 해당 로직 실행
            if self.is_element(mode='css', ele_val='div > div.NHN_Writeform_Main', ele_parent=content_render):

                # p tag 있다면 text 합
                if self.is_element(mode='css', ele_val='div > div.NHN_Writeform_Main p', ele_parent=content_render):
                    p_tags = self.get_elements(mode='css', ele_val='div > div.NHN_Writeform_Main p', ele_parent=content_render)
                    for ele in p_tags:
                        line = ele.text
                        if line == '':
                            story_text = story_text+'\n'
                        else:
                            story_text = story_text + line.strip()

                # div tag 있다면 text 합
                if self.is_element(mode='css', ele_val='div > div.NHN_Writeform_Main div', ele_parent=content_render):
                    p_tags = self.get_elements(mode='css', ele_val='div > div.NHN_Writeform_Main div', ele_parent=content_render)
                    for ele in p_tags:
                        line = ele.text
                        if line == '':
                            story_text = story_text+'\n'
                        else:
                            story_text = story_text + line.strip()

                # img tag 있다면 src url 모두 획득
                if self.is_element(mode='css', ele_val='div > div.NHN_Writeform_Main img', ele_parent=content_render):
                    img_tags = self.get_elements(mode='css', ele_val='div > div.NHN_Writeform_Main img', ele_parent=content_render)
                    for idx, ele in enumerate(img_tags):
                        url = ele.get_attribute('src')
                        img_url_text = img_url_text + str(idx) + '. ' + str(url) + '\n'

                # 동영상이 있으면 src url 모두 획득
                if self.is_element(mode='css', ele_val='div > div.NHN_Writeform_Main iframe', ele_parent=content_render):
                    iframe_tags = self.get_elements(mode='css', ele_val='div > div.NHN_Writeform_Main iframe', ele_parent=content_render)
                    for idx, ele in enumerate(iframe_tags):
                        url = ele.get_attribute('src')
                        video_url_text = video_url_text + str(idx) + '. ' + str(url) + '\n'
        #########################################################se viewer 타입#########################################################
        elif self.is_element(mode='css', ele_val='div.se-viewer', ele_parent=ele_parent):
            self.setPrint('2구간')
            # get se-viewer element
            se_viewer = self.get_elements(mode='css', ele_val='div.se-viewer', ele_parent=ele_parent)[0]
            # text 값이 있으면 값을 모두 획득
            if self.is_element(mode='css', ele_val='div.se-text', ele_parent=se_viewer):
                span_tags = self.get_elements(mode='css', ele_val='div.content.CafeViewer > div > div > div.se-text p > span', ele_parent=se_viewer)
                for ele in span_tags:
                    line = ele.text
                    if line == '':
                        story_text = story_text+'\n'
                    else:
                        story_text = story_text + line.strip()

            # 이미지가 있으면 src url 모두 획득
            if self.is_element(mode='css', ele_val='div.se-image', ele_parent=se_viewer):
                img_tags = self.get_elements(mode='css', ele_val='div.content.CafeViewer > div > div > div.se-image img', ele_parent=se_viewer)
                for idx, ele in enumerate(img_tags):
                    url = ele.get_attribute('src')
                    img_url_text = img_url_text + str(idx) + '. ' + str(url) + '\n'

            # 동영상이 있으면 src url 모두 획득
            if self.is_element(mode='css', ele_val='div.se-video', ele_parent=se_viewer):
                script_tags = self.get_elements(mode='css', ele_val='div.content.CafeViewer > div > div > div.se-video script', ele_parent=se_viewer)
                for idx, ele in enumerate(script_tags):
                    data_module = ele.get_attribute('data-module')
                    if data_module == '':
                        continue
                    else:
                        try:
                            dict_module = json.loads(data_module)
                            vid = dict_module['data']['vid']
                            inkey = dict_module['data']['inkey']
                            video_url_text = video_url_text + str(idx) + '. ' + str(nhn_video_url.format(vid, inkey)) + '\n'
                        except:
                            continue
        # 해당 없음 Pass
        else:
            self.setPrint('3구간')
            pass

        # reply
        # 댓글 임시공간
        # return values
        return [story_text, img_url_text, video_url_text, reply_text]

    # 삼성커뮤니티 본문 글 정리 함수
    def get_main_article_sc(self, ele_parent=None):

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
                    url = ele['src']
                    img_url_text = img_url_text + str(idx+1) + '. ' + str(url) + '\n'

            # 동영상이 있으면 src url 모두 획득
            if iframe_tag:

                for idx, ele in enumerate(iframe_tag):
                    url = ele['src']
                    video_url_text = video_url_text + str(idx+1) + '. ' + str(url) + '\n'

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
                        url = ele['src']
                        img_url_text = img_url_text + str(idx+1) + '. ' + str(url) + '\n'

                # 동영상이 있으면 src url 모두 획득
                if nhn_tag[0].select('iframe'):
                    iframe_tags = nhn_tag[0].select('iframe')
                    for idx, ele in enumerate(iframe_tags):
                        url = ele['src']
                        video_url_text = video_url_text + str(idx+1) + '. ' + str(url) + '\n'
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
                    line = ele.text.replace()
                    if line == '':
                        story_text = story_text+'\n'
                    else:
                        story_text = story_text + line.strip() + '\n'

            # 이미지가 있으면 src url 모두 획득
            if img_tags:
                for idx, ele in enumerate(img_tags):
                    url = ele['src']
                    img_url_text = img_url_text + str(idx+1) + '. ' + str(url) + '\n'

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
                list_reply_comment = item.select('span.text_comment')
                list_reply_img = item.select('a.comment_image_link > img')
                reply_info = item.select('span.comment_info_date')

                # text만 있을 경우
                if list_reply_comment and not list_reply_img:
                    reply_text = reply_text + str(idx+1) + ". " + list_reply_comment[0].text + "(" + reply_info[0].text + ")\n"
                # 첨부 img만 있을 경우
                elif list_reply_img and not list_reply_comment:
                    reply_text = reply_text + str(idx+1) + ". " + list_reply_img[0]['src'] + "(" + reply_info[0].text + ")\n"
                # 이미지 text 모두 있을 경우
                elif list_reply_img and list_reply_comment:
                    reply_text = reply_text + str(idx+1) + ". " + list_reply_comment[0].text + "\n"
                    reply_text = reply_text + '첨부 이미지 : ' + list_reply_img[0]['src'] + "(" + reply_info[0].text + ")\n"
                else:
                    continue
        # 페이지 대기
        sleep(2)
        # return values
        return [story_text, img_url_text, video_url_text, reply_text]

    # 삼성커뮤니티 실행 함수
    def run_Test(self):

        try:
            list_nav = ['menuLink1007', 'menuLink1009']
            # 드라이버 생성
            self.set_driver()
            self.setDriver()
            # 네이버 로그인
            self.naver_login()
            self.action_wait(mode='css', ele_val='#header > div.special_bg > div > div.logo_area')

            # 메인 페이지 이외 팝업 삭제
            self.close_window(mode=1)
            self.driver.get('https://cafe.naver.com/anycallusershow/')
            self.action_wait(mode='id', ele_val='front-cafe')

            # # 뒤로 이동
            # self.action_page_move('back')
            # self.action_wait(mode='css', ele_val='#header > div.special_bg > div > div.logo_area > h1 > a')
            #
            # # 다시 삼성 커뮤니티로
            # self.driver.get('https://cafe.naver.com/anycallusershow/')
            # self.action_wait(mode='id', ele_val='front-cafe')

            # # 맨 아래 요소까지 스크롤 다운
            # self.action_scroll(direction='down', mode='class', ele_val='banner_chatbot', idx=0)
            # self.action_wait(mode='class', ele_val='banner_chatbot')
            # self.setPrint('페이지 하단 스크롤 테스트')
            # sleep(2)

            # # 갤노트 20/질문답 요소까지 스크롤 업
            # self.action_scroll(direction='up', mode='id', ele_val='menuLink1007', idx=0)
            # self.action_wait(mode='id', ele_val='menuLink1007')
            # self.setPrint('갤노트 20 질문/답 엘러먼트 페이지 이동')
            # sleep(2)

            for item in list_nav:

                recent_num = 0
                page_num = 0
                extract_num = 0
                flag_end = False
                self.setPrint('삼성커뮤니티 {} 구역 페이지 크롤링 시작'.format(item))
                # main 프레임으로 변경
                self.change_frame(mode=2)
                # 해당 페이지로 이동
                self.action_click(mode='id', ele_val=item)

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
                nav_name = item
                flag_search_mode = 'today'
                sleep(1)

                # DB에 최신 값을 조회한 후 DB가 비어 있다면 오늘 데이터만 찾는 방식이고 있다면 최신 보드 번호를 기록 후 이를 기준으로 이후 데이터만 크롤링이 실행된다
                list_recent = self.myDB.check_recent('삼성커뮤니티', nav_name, type_name, 1)
                if len(list_recent) != 0:
                    flag_search_mode = 'recent'
                    recent_num = int(list_recent[0]['bo_no'])
                    self.setPrint("최근 {} 게시글 번호: {}".format(item, recent_num))

                self.setPrint('조회방법 : {}'.format(flag_search_mode))
                # 15개 보기를 50개 보는 방식으로 변경
                self.action_wait(mode='css', ele_val='#main-area > div:nth-child(6) > table > tbody')
                self.action_click(mode='css', ele_val='#listSizeSelectDiv > a')
                sleep(1)
                self.action_click(mode='css', ele_val='#listSizeSelectDiv > ul > li:nth-child(7) > a')
                sleep(1)

                # '3406043'
                # set 50 items
                # self.driver.get('https://cafe.naver.com/ArticleList.nhn?search.clubid=13764661&search.boardtype=L&search.menuid=1007&search.marketBoardTab=D&search.specialmenutype=&userDisplay=50')

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
                                # iframe으로 변경
                                frame_ele = self.get_elements(mode='id', ele_val='cafe_main')
                                self.change_frame(element=frame_ele[0], mode=1)

                                tr_ele = self.get_elements(mode='css', ele_val='#main-area > div:nth-child(6) > table > tbody > tr:nth-child(' + str(idx) + ')')
                                board_num = tr_ele[0].find_element_by_css_selector('td.td_article > div.board-number > div').text.strip()
                                board_num = int(board_num.strip())
                                time_value = tr_ele[0].find_element_by_css_selector('td.td_date').text.strip()
                                # 당일 데이터만 획득
                                flag_end = self.check_today(time_value)
                                if flag_end:
                                    break
                                else:
                                    # self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, )))
                                    title_ele = tr_ele[0].find_element_by_css_selector('td.td_article > div.board-list > div > a.article')
                                    title = title_ele.text.strip()
                                    view_num = int(tr_ele[0].find_element_by_css_selector('td.td_view').text.strip())
                                    # 해당 본문 페이지 이동
                                    title_ele.click()

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
                                    reply_num = int(reply_num_ele[0].text.strip())

                                    # story 또는 image_url 또는 video_url 또는 댓글 부분
                                    list_main_article = self.get_main_article_sc(ele_paren=article_main_ele)

                                    self.setPrint(
                                        '게시번호: {}\n제목: {}\nDate: {} {}\n조회수: {}\n댓글수: {}\n내용:\n{}\n이미지:\n{}\n비디오:\n{}\n댓글:\n{}'.format
                                        (board_num, title, reportDate, reportTime, view_num, reply_num,
                                         list_main_article[0], list_main_article[1], list_main_article[2], list_main_article[3]))

                                    extract_num = extract_num + 1
                                    # tr 리스트로 이동
                                    self.action_page_move(mode='back')

                                    # 데이터 테이블의 마지막 행인 경우
                                    if idx == 49:
                                        page_num = page_num + 1
                                        page_ele = self.get_elements(mode='css', ele_val='#main-area > div.prev-next > a')
                                        page_ele[page_num].click()
                                        sleep(2)
                                        break

                # mongoDB에 최근 record가 있는 경우
                else:
                    while True:
                        if flag_end:
                            break
                        else:
                            # 테이블 리스트 each tr 조회
                            for idx in range(1, 50):
                                # tbody element 대기
                                self.action_wait(mode='css', ele_val='#main-area > div:nth-child(6) > table > tbody')
                                # tr 값 추출
                                tr_ele = self.get_elements(mode='css', ele_val='#main-area > div:nth-child(6) > table > tbody > tr:nth-child('+str(idx)+')')
                                board_num = tr_ele[0].find_element_by_css_selector('td.td_article > div.board-number > div').text.strip()
                                board_num = int(board_num.strip())
                                # 서버에 있는 보더 넘버를 현재 번호와 비교하여 flag_end 결정
                                flag_end = self.compared_num(recent_num, board_num)
                                if flag_end:
                                    break
                                else:
                                    # self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, )))
                                    title_ele = tr_ele[0].find_element_by_css_selector('td.td_article > div.board-list > div > a.article')
                                    title = title_ele.text.strip()
                                    view_num = int(tr_ele[0].find_element_by_css_selector('td.td_view').text.replace(',', '').strip())
                                    # 해당 본문 페이지 이동
                                    title_ele.click()

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
                                    reply_num = int(reply_num_ele[0].text.strip())

                                    # story 또는 image_url 또는 video_url 또는 댓글 부분
                                    list_main_article = self.get_main_article_sc(ele_parent=article_main_ele)

                                    self.setPrint(
                                        '게시번호: {}\n제목: {}\nDate: {} {}\n조회수: {}\n댓글수: {}\n내용:\n{}\n이미지:\n{}\n비디오:\n{}\n댓글:\n{}'.format
                                        (board_num, title, reportDate, reportTime, view_num, reply_num,
                                         list_main_article[0], list_main_article[1], list_main_article[2], list_main_article[3]))

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
                                        page_num = page_num + 1
                                        page_ele = self.get_elements(mode='css', ele_val='#main-area > div.prev-next > a')
                                        page_ele[page_num].click()
                                        self.setPrint('{}Page 다음 페이지로 이동')
                                        break

                # frame main content로 변경
                self.setPrint('삼성커뮤니티 {} 구역 페이지 크롤링 종료 총 {} Data 추출 완료'.format(item, extract_num))

            sleep(3)
            self.setPrint('크롤링 작업 완료')
            self.stop()
        except:
            self.setPrint('Error Occurred : {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno))
            self.stop()


if __name__ == "__main__":
    tester = ElemTest()
    tester.run_Test()
