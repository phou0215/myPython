#-*- coding:utf-8 -*-

import pymysql
import sys
import numpy
import threading
import pandas as pd
import pymongo
from pymongo import MongoClient
import traceback

from datetime import datetime
from time import sleep

class ConnDB():

    def __init__(self, host, port, id, pw, db_name):

        super().__init__()
        self.host = host
        self.port = port
        self.user = id
        self.password = pw
        self.db_name = db_name
        self.client = None
        self.cur = None
        self.samsung_collection = None
        self.lg_collection = None
        self.etc_collection = None
        # self.db_name = 'crawler'
        # self.collection_name = 'samsung_data', 'lg_data', 'etc_data'

        self.list_cols = ['bo_no', 'cafeName', 'nav', 'type', 'deviceName', 'reportDate', 'reportTime', 'regiDate', 'title',
                          'story', 'reply', 'cate', 'status', 'reply_num', 'view_num', 'story_url', 'img_url', 'video_url', 'uniqueId']
        self.list_cols_2 = ["게시글 번호", "카페이름", "네비게이션", "구분", "디바이스", "작성일", "작성시간", "제목", "내용",
                            "댓글", "분류", "감정", "댓글수", "조회수", "url", "img_url", "video_url", "고유번호"]

        #remove duplication columns for rename excel columns

    def set_connect(self):

        try:
            # replica=replica set
            # username=user
            # password=password
            # authSource=auth database
            if self.user is None or self.password is None:
                self.client = MongoClient(host=self.host, port=self.port)
            else:
                self.client = MongoClient(host=self.host, port=self.port, username=self.user, password=self.password)
            # connect DB
            self.cur = self.client[self.db_name]
            self.samsung_collection = self.cur['samsung_data']
            self.lg_collection = self.cur['lg_data']
            self.etc_collection = self.cur['etc_data']
            # names = self.client.list_database_names()
            # collections = self.cur.list_collection_names()
            # print(names)
            # print(collections)
            # datas = self.cur.samsung_data.find()
            # print(list(datas))

            self.setPrint('MongoDB Connected.')
            return True

        except:
            self.setPrint(traceback.format_exc())
            self.setPrint('MongoDB ocurred Error!')
            return False

    # 현재 시간 구하여 3가지 타입으로 list return
    def getCurrent_time(self):

        now_datetime = datetime.now()
        now_datetime_str = now_datetime.strftime('%Y-%m-%d %H:%M:%S')
        now_datetime_str2 = now_datetime.strftime('%Y-%m-%d %H %M %S')
        return [now_datetime, now_datetime_str, now_datetime_str2]

    # DB 연결 해제
    def stop(self):
        self.client.close()
        self.setPrint('MongoDB Closed.')

    # 시간 정보와 함께 Console에 Print 하는 함수
    def setPrint(self, text):

        current = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        print("{}:\n{}".format(current, text)+"\n")

    def deleteData(self, unique_ids, type):

        try:
            #통품전체VOC
            totalRows = len(unique_ids)

            self.setPrint('DB에 {} 건 통품전체 data 삭제 수행 중...'.format(totalRows))
            if type == 1:
                for item in unique_ids:
                    dict_temp = {'uniqueId':item}
                    self.samsung_collection.delete_many(dict_temp)

            elif type == 2:
                for item in unique_ids:
                    dict_temp = {'uniqueId':item}
                    self.lg_collection.delete_many(dict_temp)
            else:
                for item in unique_ids:
                    dict_temp = {'uniqueId':item}
                    self.etc_collection.delete_many(dict_temp)

            self.setPrint('DB Server에 {}건 data 삭제 완료...'.format(totalRows))
            self.flag_delete = True
        except:
            self.setPrint('Error: {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno))
            self.flag_delete = False

    def check_recent(self, cafeName, nav, type, flag):

        try:
            dict_type = {1:'SAMSUNG', 2:'LG', 3:'ETC'}
            #samsung
            dict_query = {'cafeName':cafeName, 'nav': nav, 'type':type}
            dict_returns = {}
            #samsung collection
            if flag == 1:
                dict_returns = self.samsung_collection.find(dict_query).sort([("bo_no", pymongo.DESCENDING)]).limit(1)
            #lg collection
            elif flag == 2:
                dict_returns = self.lg_collection.find(dict_query).sort([("bo_no", pymongo.DESCENDING)]).limit(1)
            #etc collection
            else:
                dict_returns = self.etc_collection.find(dict_query).sort([("bo_no", pymongo.DESCENDING)]).limit(1)

            self.setPrint("\"{}\" Data collection \"{}\" 카페 \"{}\" 의 \"{}\" 게시판 최신 데이터 조회 완료".format(dict_type[flag], cafeName, nav, type))
            return list(dict_returns)

        except Exception as e:
            print(traceback.format_exc())

    def findAllData(self, dict_query, type):
        try:
            dict_returns = None
            if type == 1:
                dict_returns = self.samsung_collection.find(dict_query)
            elif type == 2:
                dict_returns = self.lg_collection.find(dict_query)
            else:
                dict_returns = self.etc_collection.find(dict_query)
            return list(dict_returns)
        except Exception as e:
            print(traceback.format_exc())

    def insertData(self, dict_data, db_type):

        ########################## web spider Table #################################
        bo_no = dict_data["bo_no"]
        cafeName = dict_data["cafeName"]
        nav = dict_data["nav"]
        type = dict_data["type"]
        deviceName = dict_data["deviceName"]
        reportDate = dict_data["reportDate"]
        reportTime = dict_data["reportTime"]
        title = dict_data["title"]
        story = dict_data["story"]
        reply = dict_data["reply"]
        cate = dict_data["cate"]
        status = dict_data["status"]
        reply_num = dict_data["reply_num"]
        view_num = dict_data['view_num']
        story_url = dict_data["story_url"]
        img_url = dict_data["img_url"]
        video_url = dict_data["video_url"]
        uniqueId = dict_data["uniqueId"]

        #generate regiDate list
        regiDate = list()
        for i in range(len(uniqueId)):
            regiDate.append(self.getCurrent_time()[1])

        values = [bo_no, cafeName, nav, type, deviceName, reportDate, reportTime, regiDate, title,
                  story, reply, cate, status, reply_num, view_num, story_url, img_url, video_url, uniqueId]


        # Generate insert web spider table sql
        try:
            self.setPrint('DB에 {} 건 통품전체 data 업로드 수행 중...'.format(len(uniqueId)))
            list_upload = []
            #generate upload_data
            for i in range(len(uniqueId)):
                dict_temp = {}
                for j in range(len(values)):
                    dict_temp[self.list_cols[j]] = values[j][i]
                list_upload.append(dict_temp)

            if db_type == 1:
                self.samsung_collection.insert_many(list_upload)
                self.setPrint('Samsung collection {} 건 data 등록 완료...'.format(len(uniqueId)))
            elif db_type == 2:
                self.lg_collection.insert_many(list_upload)
                self.setPrint('LG collection {} 건 data 등록 완료...'.format(len(uniqueId)))
            else:
                self.etc_collection.insert_many(list_upload)
                self.setPrint('ETC collection {} 건 data 등록 완료...'.format(len(uniqueId)))

            return 'OK'
        except:
            self.setPrint('Error: {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno))
            return 'Error: {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno)

if __name__ == "__main__":

    dict_test = {
        "bo_no": [3421029, 3421031, 3421027, 3421045, 3421129, 3421050, 3421051, 3421017, 3421022, 3421035],
        "cafeName": ["삼성커뮤니티", "삼성커뮤니티", "삼성커뮤니티", "삼성커뮤니티", "삼성커뮤니티", "삼성커뮤니티", "삼성커뮤니티", "삼성커뮤니티", "삼성커뮤니티", "삼성커뮤니티"],
        "nav": ["menuLink1007", "menuLink1007", "menuLink1007", "menuLink1009", "menuLink1007", "menuLink1009", "menuLink1009", "menuLink1007", "menuLink1007", "menuLink1009"],
        "type": ["질문/답", "질문/답", "질문/답", "자유방", "질문/답", "자유방", "자유방", "질문/답", "질문/답", "자유방"],
        "deviceName": ["갤노트20", "갤노트20" , "갤노트20", "갤노트20", "갤노트20", "갤노트20", "갤노트20", "갤노트20", "갤노트20", "갤노트20"],
        "reportDate": ["2020-07-28", "2020-07-21", "2020-07-28", "2020-08-02", "2020-07-28", "2020-08-02", "2020-08-02", "2020-07-28", "2020-08-07", "2020-07-28"],
        "reportTime": ["20:17:23", "10:25:23", "21:45:18", "12:33:56", "09:22:21", "14:20:11", "16:22:32", "11:22:21", "22:20:21", "17:20:21"],
        "title": ['이젠 삼성폰 CSC', '놋20 울트라 오늘내일옵니다.', '지금 노트20 최저가가 여기인거 같은데', '포인트 빨리 모으는방법없나요?', 'ssg 화이트 또 풀렸네요',
               'ㅋㅌㄱㅂ ㅇㅁㅍ 혹시 다들 메일 받으셨나요?', '립 같은거 없이 청구할인은 ssg가 제일 싼거죠?', '듀얼심이 동시에 작동을 하지는 못하나보네요', '노트20 울트라', '지마켓 옥션 브론즈 재고 찼습니다.'],
        "story": ["SAMKEY같은 프로그램에서 쓰는 방법인데_1", "SAMKEY같은 프로그램에서 쓰는 방법인데_2", "SAMKEY같은 프로그램에서 쓰는 방법인데_3", "SAMKEY같은 프로그램에서 쓰는 방법인데_4",
              "SAMKEY같은 프로그램에서 쓰는 방법인데_5", "SAMKEY같은 프로그램에서 쓰는 방법인데_6", "SAMKEY같은 프로그램에서 쓰는 방법인데_7", "SAMKEY같은 프로그램에서 쓰는 방법인데_8",
              "SAMKEY같은 프로그램에서 쓰는 방법인데_9", "SAMKEY같은 프로그램에서 쓰는 방법인데_10"],
        "reply": ["댓글_1","댓글_2","댓글_3","댓글_4","댓글_5","댓글_6","댓글_7","댓글_8","댓글_9","댓글_10"],
        "cate": ["음성통화", "영상통화", "베터리", "베터리", "USIM", "제조사App", "음성통화", "USIM", "영상통화", "음성통화"],
        "status": ["중립", "부정", "부정", "부정", "부정", "부정", "부정", "긍정", "긍정", "중립"],
        "reply_num": [12, 2, 33, 5, 10, 7, 4, 3, 9, 2],
        "view_num": [1002, 400, 1300, 1230, 11, 123, 55, 70, 22, 30],
        "story_url": ["http://www.ppomppu.co.kr", "http://www.ppomppu.co.kr", "http://www.ppomppu.co.kr", "http://www.ppomppu.co.kr", "http://www.ppomppu.co.kr", "http://www.ppomppu.co.kr",
               "http://www.ppomppu.co.kr", "http://www.ppomppu.co.kr", "http://www.ppomppu.co.kr", "http://www.ppomppu.co.kr"],
        "img_url": ["http://www.ppomppu.co.kr/img", "http://www.ppomppu.co.kr", "http://www.ppomppu.co.kr", "http://www.ppomppu.co.kr", "http://www.ppomppu.co.kr", "http://www.ppomppu.co.kr",
                   "http://www.ppomppu.co.kr", "http://www.ppomppu.co.kr", "http://www.ppomppu.co.kr", "http://www.ppomppu.co.kr"],
        "video_url": ["http://www.ppomppu.co.kr/img", "http://www.ppomppu.co.kr", "http://www.ppomppu.co.kr","http://www.ppomppu.co.kr", "http://www.ppomppu.co.kr", "http://www.ppomppu.co.kr",
                    "http://www.ppomppu.co.kr", "http://www.ppomppu.co.kr", "http://www.ppomppu.co.kr","http://www.ppomppu.co.kr"],
        "uniqueId": ["ERT200019ECTX", "ERT200015ECTX", "ERT200013ECTX", "ERT200010ECTX", "ERT200011ECTX", "ERT200012ECTX", "ERT200017ECTX", "ERT200018ECTX", "ERT200010ECTL", "ERT200010ECTC"]
    }

    mydb = ConnDB("localhost", 27017, None, None, "crawler")
    # df_test = pd.DataFrame(dict_test, index=None)
    mydb.set_connect()
    mydb.insertData(dict_test, 1)
    myRecent_data = mydb.check_recent('삼성커뮤니티', 'group777', '자유', 1)
    for idx, item in enumerate(myRecent_data):
        for idx_2, (key, value) in enumerate(item.items()):
            mydb.setPrint("{} {} 번째 요소: {} col, {} value".format('삼성커뮤니티', idx_2, key, value))

    unique_ids = []
    datas = mydb.findAllData({},1)
    for item in datas:
        unique_ids.append(item["uniqueId"])
    # mydb.deleteData(unique_ids, 1)
    mydb.stop()