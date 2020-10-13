#-*- coding:utf-8 -*-

import smtplib
import os
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.utils import COMMASPACE, formatdate
from email import encoders
from datetime import datetime

class SendMail():

    # 클래스 초기화
    def __init__(self, dict_mail, list_dict_result, list_upload_status):

        super().__init__()

        self.sender = dict_mail['계정']
        self.sender_id = dict_mail['아이디']
        self.sender_pw = dict_mail['비밀번호']
        self.list_receivers = dict_mail['수신처']
        self.list_dict_result = list_dict_result
        self.list_upload_status = list_upload_status
        self.keys = []
        self.data_count = []
        self.job_date = ''
        # self.list_receivers_string = str(dict_mail['수신처']).split(",")
        self.message = "웹 모니터링 수집 결과 "
        self.title = "웹모니터링 수집 결과 {}"

    def set_result_statics(self):

        for item in self.list_dict_result:
            list_tuple_data = list(item.items())
            key = list_tuple_data[0][0]
            value = list_tuple_data[0][1]
            if len(value) != 0:
                self.keys.append(key)
                self.data_count.append(len(list_tuple_data[0][1]['bo_no']))
            else:
                self.keys.append(key)
                self.data_count.append(0)

        temp_text = ''
        for idx, item in enumerate(self.keys):
            temp_text = temp_text + '\t{}. {}\n'.format(idx+1, item)
            temp_text = temp_text + '\t\t1) 신규데이터 건수: {}\n'.format(self.data_count[idx])
            temp_text = temp_text + '\t\t2) 업로드 상태: {}\n'.format(self.list_upload_status[idx])

        self.message = self.message + self.job_date + "\n" + temp_text

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

    # mail object 생성 및 send
    def send_email(self, attach_path=None):

        try:
            # self.server = smtplib.SMTP_SSL('smtp.naver.com', 465)
            # self.server.login('hrlee', 'navy1063')
            self.job_date = self.getCurrent_time()[1]
            server = smtplib.SMTP('webmail.testenc.com', 587)
            server.ehlo()
            server.starttls()
            server.login(self.sender[0], self.sender_pw[0])
            self.set_result_statics()

            # self.msg = MIMEBase('multipart','mixed')
            msg = MIMEMultipart()

            # set email text and subject and sender and receivers
            msg['Subject'] = self.title.format(self.job_date)
            msg['From'] = self.sender[0]
            msg['To'] = COMMASPACE.join(self.list_receivers)
            msg['Date'] = formatdate(localtime=True)
            conv = MIMEText(self.message, 'plain', 'utf-8')
            msg.attach(conv)

            # self.attach_path = r""+self.attach_paths
            # self.attc_part = MIMEBase('application','octet-stream')
            if attach_path:

                if os.path.isfile(attach_path):
                    attc_part = MIMEBase('application', 'vnd.ms-excel')
                    excel_file = open(attach_path, 'rb')
                    attc_part.set_payload(excel_file.read())
                    excel_file.close()
                    encoders.encode_base64(attc_part)
                    attc_part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attach_path))
                    msg.attach(attc_part)
                else:
                    self.setPrint('attach_path incorrect. skip attachment file...')
                    pass
            # print(self.msg)
            server.sendmail(self.sender[0], self.list_receivers, msg.as_string())
            self.setPrint("이메일 전송 완료...")
            server.close()
            return True
        except:
            self.setPrint('Error Occurred : {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno))
            return False


 # 'ykkim@testenc.com', 'hjyoo@testenc.com', 'yecho@testenc.com'

if __name__ =='__main__':

    file_path = 'C:\\Users\\HANRIM\\Desktop\\Crawler\\report\\Test.xlsx'
    sender = SendMail('hrlee@testenc.com', 'hrlee', 'navy1063', ['hrlee@testenc.com'],
                     '[전달] Web 모니터링 자동 실행 결과({} , {})', "{} {} 웹 모니터링 결과와 첨부파일",
                     '10:00')
    sender.send_email(attach_path=file_path)

