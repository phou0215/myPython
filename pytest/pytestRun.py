import pytest

from bs4 import BeautifulSoup
from Check_Chromedriver import Check_Chromedriver
from os.path import expanduser

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
from selenium.common.exceptions import UnexpectedAlertPresentException


class testSamples():

    def __init__(self):

        super(testSamples, self).__init__()
        self.home = expanduser("~")
        self.start_time = ""
        self.end_time = ""
        # 각 카페에서 얻어진 dict 데이터를 해당 배열에 저장
        self.wait_time = 15
        self.paging_num = 0
        self.delay_time = 2
        self.chrome_driver_path = self.home+"\\Desktop\\Pytest\\driver\\"
        self.report_path = self.home+"\\Desktop\\Pytest\\report\\"
        self.image_path = self.home+"\\Desktop\\Pytest\\image\\"
        self.driver = None
        self.chrome_option = None
        self.wait = None

# Chrome GUI Driver 생성
    def setDriver(self):
        try:
            self.chrome_option = webdriver.ChromeOptions()
            # 네이버 로그인 같은 경우 사용할 수 없음(네이버 정책상 로그인 시 headless 허용 안함)
            self.chrome_option.add_argument('headless')
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
            self.chrome_option.add_argument(
                'user-agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36')
            self.driver = webdriver.Chrome(executable_path=self.chrome_driver_path, options=self.chrome_option)
            self.driver.implicitly_wait(10)
            self.wait = WebDriverWait(self.driver, self.wait_time)
            self.setPrint("Generated Chrome Driver is Success...")
        except:
            self.setPrint('Occurred Error at generate chrome driver spot!')
            self.setPrint('Error Occurred : {}. {}, line: {}'.format(sys.exc_info()[0],
                                                                     sys.exc_info()[1],
                                                                     sys.exc_info()[2].tb_lineno))
            self.process_flag = False

    def set_driver(self):

        if not os.path.isdir(self.driver_root_path):
            os.makedirs(self.driver_root_path)

        Check_Chromedriver.driver_mother_path = self.driver_root_path
        Check_Chromedriver.main()
        self.chrome_driver_path = self.driver_root_path + "chromedriver.exe"


    def setUp(self):
        self.driver.get("http://www.naver.com")
        self.driver.find_element_by_id("NM_THEMECAST_CONTENTS_CONTAINER")