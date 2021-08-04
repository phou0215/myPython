from src.testproject.sdk.drivers import webdriver
from selenium.webdriver import ChromeOptions

class SampleTest():

    def __init__(self):

        super().__init__()
        self.driver = None
        self.chrome_option = None

    def set_up(self):
        self.chrome_option = ChromeOptions()
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
        self.chrome_option.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36')
        self.driver = webdriver.Chrome(chrome_options=self.chrome_option, project_name="Sample_Test", job_name="Sample")
        yield self.driver

    def tear_down(self):
        self.driver.quit()

    # Function of console print
    def set_print(self, text):

        current = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        if self.serial_num != "" and self.modelName != "":
            print("[{}({})]{}:\n{}".format(self.modelName, self.serial_num, current, text) + "\n")
        else:
            print("{}:\n{}".format(current, text) + "\n")

    # 특정 문자 구간 Parsing 함수(앞에서부터)
    def find_between(self, s, first, last):

        try:
            start = s.index(first) + len(first)
            end = s.index(last, start)
            return s[start:end]
        except ValueError:
            return ""

    # 특정 문자 구간 Parsing 함수(뒤에서부터)
    def find_between_r(self, s, first, last):

        try:
            start = s.rindex(first) + len(first)
            end = s.rindex(last, start)
            return s[start:end]
        except ValueError:
            return ""

    def simple_test(self):

        self.driver.get("https://example.testproject.io/web/")

        self.driver.find_element_by_css_selector("#name").send_keys("John Smith")
        self.driver.find_element_by_css_selector("#password").send_keys("12345")
        self.driver.find_element_by_css_selector("#login").click()
        passed = driver.find_element_by_css_selector("#logout").is_displayed()

        self.set_print("Test passed") if passed else self.set_print("Test failed")


if __name__ == "__main__":

    sample_test = SampleTest()
    sample_test.set_up()
    sample_test.simple_test()
    sample_test.tear_down()