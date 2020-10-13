#-*- coding:utf-8 -*-

import pymysql
import sys
import numpy
import threading
import pandas as pd

from datetime import datetime
from time import sleep

class ConnMyDB():


    def __init__(self, host, port, id, pw, db_name, table_name):

        super().__init__()
        self.address = host
        self.port = port
        self.user = id
        self.password = pw
        self.db_name = db_name
        self.table_name = table_name
        self.conn = None
        self.cur = None
        self.flag_upload = False
        self.flag_delete = False
        self.conn = pymysql.connect(host=self.address, user=self.user, password=self.password, db=self.db_name, charset='utf8')
        self.cur = self.conn.cursor(pymysql.cursors.DictCursor)
        # self.db_name = 'testenc'
        # self.table_name = 'web_monitor_data'
        # self.id = 'root'
        # self.pw = 'navy1063'

        self.list_cols = ["no", "id", "cafeName", "address", "reportDate", "reportTime", "regiDate", "deviceName", "title",
                          "story", "reply", "hists", "reply_num", "pos_num", "uniqueId"]

        #remove duplication columns for rename excel columns

    # 현재 시간 구하여 3가지 타입으로 list return
    def getCurrent_time(self):

        now_datetime = datetime.now()
        now_datetime_str = now_datetime.strftime('%Y-%m-%d %H:%M:%S')
        now_datetime_str2 = now_datetime.strftime('%Y-%m-%d %H %M %S')
        return [now_datetime, now_datetime_str, now_datetime_str2]

    def stop(self):

        sleep(0.1)
        self.conn.close()
        self.cur.close()

    # 시간 정보와 함께 Console에 Print 하는 함수
    def setPrint(self, text):

        current = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        print("{}:\n{}".format(current, text)+"\n")

    # 문장 맨앞에서부터 서치하여 특이 지점까지 문자열 parsing
    def find_between(self, s, first, last):
        try:
            start = s.index(first)+len(first)
            end = s.index(last, self.start)
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

    def removeString(self, text):

        try:
            temp_text = text.replace("[","")
            temp_text = temp_text.replace("]","")
            temp_text = temp_text.replace("-","")
            # temp_text = temp_text.replace("/","")
            temp_text = temp_text.replace("=","")
            temp_text = temp_text.replace("<","")
            temp_text = temp_text.replace(">","")
            temp_text = temp_text.replace("#","")
            temp_text = temp_text.replace("*","")
            temp_text = temp_text.replace(",","")
            temp_text = temp_text.replace(";","")
            temp_text = temp_text.replace("$","")
            # temp_text = temp_text.encode('utf-8').decode('utf-8')
            return temp_text
        except:
            self.setPrint('Error occurred : {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno))

    def deleteData(self, path):

        try:
            file_path = path
            df_delete_data = pd.read_excel(file_path, sheet_name='result', index_col=None)
            ids = df_delete_data["unique"].tolist()
            ids = [x for x in ids if str(x) != 'nan']
            # Web monitoring data delete SQL
            sql = "DELETE FROM " + self.table_name + " WHERE issueId = %s"
            #통품전체VOC
            totalRows = len(ids)

            self.setPrint('DB Server에 {}건 통품전체 data 삭제 수행 중...'.format(totalRows))
            for item in ids:
                self.cur.execute(sql, item)

            self.conn.commit()
            self.setPrint('DB Server에 {}건 data 삭제 완료...'.format(totalRows))
            self.flag_delete = True
        except:
            self.setPrint('Error: {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno))
            self.flag_delete = True



    def check_recent(self, cafeName, classname, type):

        # dict_recent_data = {}
        search_query = "SELECT * FROM "+self.table_name+" WHERE cafeName='{}' AND class='{}' AND type='{}' ORDER BY reportDate DESC, reportTime DESC LIMIT 1".format(cafeName, classname, type)
        self.setPrint(search_query)
        self.cur.execute(search_query)
        # self.rows dict형 리스트 리턴 하나만 리턴의 경우 fetchone() 이용
        row = self.cur.fetchone()
        return  row


    def insertData(self, df_data):

        ########################## web spider Table #################################
        id = df_data["id"].tolist()
        cafeName = df_data["cafeName"].tolist()
        address = df_data["address"].tolist()
        className = df_data["class"].tolist()
        type = df_data["type"].tolist()
        reportDate = df_data["reportDate"].tolist()
        reportTime = df_data["reportTime"].tolist()
        deviceName = df_data["deviceName"].tolist()
        title = df_data["title"].tolist()
        story = df_data["story"].tolist()
        reply = df_data["reply"].tolist()
        hits = df_data["hits"].tolist()
        reply_num = df_data["reply_num"].tolist()
        pos_num = df_data["pos_num"].tolist()
        uniqueId = df_data["uniqueId"].tolist()

        #generate regiDate list
        regiDate = list()
        for i in range(len(uniqueId)):
            regiDate.append(self.getCurrent_time()[1])

        values = [id, cafeName, className, type, address, reportDate, reportTime, regiDate, deviceName, title, story, reply, hits, reply_num, pos_num, uniqueId]


        # Generate insert web spider table sql
        sql_insert = "INSERT INTO "+self.table_name+"(id, cafeName, class, type, address, reportDate, reportTime, regiDate, deviceName, title, story, reply,"\
                     "hits, reply_num, pos_num, uniqueId) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        try:
            self.setPrint('DB Server에 {} 건 통품전체 data 업로드 수행 중...'.format(len(uniqueId)))

            for i in range(len(cafeName)):
                tuple_value = ()
                temp_list = []
                for j in range(len(values)):
                    item = values[j]
                    temp_list.append(item[i])
                tuple_value = tuple(temp_list)
                self.cur.execute(sql_insert, tuple_value)

            self.conn.commit()
            self.setPrint('DB Server에 {} 건 data 등록 완료...'.format(len(uniqueId)))
            self.flag_upload = True
        except:
            self.setPrint('Error: {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno))
            self.flag_upload = True


if __name__ == "__main__":


    nowTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df_test = pd.DataFrame({'id':['77777'], 'cafeName':['삼성커뮤니티'], 'class':['group777'], 'type':['질문답'], 'address':['http://www.naver.com'], 'reportDate':['2020-05-13'], 'reportTime':['09:22:22'], 'regiDate':['2020-05-12 11:20:45'], 'deviceName':['갤럭시7'],
                            'title':['사용하기 불편하지 않나요?4'], 'story':['사용하기 불편해서 그러는데 자판 바꾸는거 어떻게 하나요'], 'reply':['1. 그거 설정에서 바꾸면 됨\n2. 다시 만들면 되는데...'],'hits':[2],'reply_num':[2],'pos_num':[10],'uniqueId':['11AASDWFED43321']})
    mydb = ConnMyDB("localhost", 3306, "root", "navy1063", "testenc", "web_monitor_data")
    mydb.insertData(df_test)
    myRecent_data = mydb.check_recent('삼성커뮤니티', 'group777', '질문답')
    mydb.setPrint(myRecent_data)
    mydb.setPrint('System finished!')
    mydb.stop()
    mydb = None
