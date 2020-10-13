import pymysql
import sys
import pkg_resources.py2_warn
# import numpy
# import threading
# import pandas as pd

from PyQt5.QtCore import QThread, pyqtSignal
from datetime import datetime
from time import sleep

class connMyDb(QThread):

    print_conn_flag = pyqtSignal(str)
    end_conn_flag = pyqtSignal()
    count_conn_flag = pyqtSignal()
    finish_count = "n"

    def __init__(self, path, sheetName_tot, sheetName_sort, sheetName_subscriber, sheetName_models, sheetName_models2, host, port, id, pw, mode, parent=None):
        QThread.__init__(self, parent)
        self.address = host
        self.port = port
        self.user = id
        self.password = pw
        self.totalRows = 0
        self.currentRow = 0
        self.conn = None
        self.cur = None
        self.file_path = path
        self.select_mode = mode
        self.sheet_name_tot = sheetName_tot
        self.sheet_name_sort = sheetName_sort
        self.sheet_name_subscriber = sheetName_subscriber
        self.sheet_name_models = sheetName_models
        self.sheet_name_models2 = sheetName_models2
        self.db_name = 'testenc'
        # self.dict_cols = {"네트워크본부":"netHead", "운용팀":"manageTeam", "운용사":"manageCo", "접수일":"regiDate", "접수시간":"regiTime",\
        #                   "상담유형1":"counsel1", "상담유형2":"counsel2", "상담유형3":"counsel3", "상담유형4":"counsel4", "상담사조치1":"action1",\
        #                   "상담사조치2":"action2", "상담사조치3":"action3", "상담사조치4":"action4", "단말기제조사":"manu", "단말기모델명":"model",\
        #                   "단말기모델명2":"model2", "단말기코드":"devCode", "단말기출시일":"devLaunchDate", "HDVoice단말여부":"hdvoiceFlag", "NETWORK방식2":"netMethod2",\
        #                   "발생시기1":"ocSpot1", "발생시기2":"ocSpot2", "지역1":"loc1", "지역2":"loc2", "지역3":"loc3", \
        #                   "시/도":"state", "구/군명":"district", "요금제코드명":"planCode", "사용자AGENT":"userAgent", "단말기애칭":"petName",\
        #                   "USIM카드명":"usimName", "댁내중계기여부":"repeaterFlag", "VOC접수번호":"vocRecieve", "서비스변경일자":"changeDate", "메모":"memo", "메모요약":"memoSum", "메모분류":"class1",\
        #                   "업데이트 유무":"updateFlag", "해외로밍 유무":"roamFlag", "소프트웨어":"swVer", "이슈번호":"issueId", "추출단어":"extractWd"}

        self.list_cols1 = ["issueId", "netHead", "manageTeam", "manageCo", "regiDate", "regiTime", "counsel1", "counsel2", "counsel3", "counsel4"]
        self.list_cols2 = ["issueId", "action1", "action2", "action3", "action4", "manu", "model", "model2", "devCode", "devLaunchDate"]
        self.list_cols3 = ["issueId", "hdvoiceFlag", "netMethod2","ocSpot1", "ocSpot2", "loc1", "loc2", "loc3", "state", "district"]
        self.list_cols4 = ["issueId", "planCode", "userAgent", "petName", "usimName", "repeaterFlag", "vocRecieve", "changeDate", "memo", "memoSum", "class1", "updateFlag", "roamFlag", "swVer", "extractWord"]
        self.temp_cols = self.list_cols1 + self.list_cols2 + self.list_cols3 + self.list_cols4
        #remove duplication columns for rename excel columns
        self.list_cols = []
        for item in self.temp_cols:
            if item not in self.list_cols:
                self.list_cols.append(item)
        del self.list_cols[0]
        self.list_cols.append("issueId")

    def getCurrentDate(self):
        self.nowDate = datetime.now().strftime("%Y-%m-%d")
        return self.nowDate

    # def setErrorText(self, text):
    #
    #     # self.strToday = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    #     self.error_conn_text = text
    #     self.end_conn_signal = "y"
    #     self.error_conn_flag.emit()
    #     self.end_conn_flag.emit()

    def getCountRows(self):
        while True:
            if self.finish_count is "n":
                sleep(0.2)
                self.count_conn_flag.emit()
            else:
                break

    def stop(self):

        sleep(0.5)
        self.terminate()

    def find_between(self, s, first, last):
        try:
            self.returnData = ""
            self.start = s.index(first)+len(first)
            self.end = s.index(last, self.start)
            self.returnData = s[self.start:self.end]
            return self.returnData
        except ValueError:
            return self.returnData

    def find_between_r(self, s, first, last ):
        try:
            self.returnData = ""
            self.start = s.rindex(first)+len(first)
            self.end = s.rindex(last, self.start)
            self.returnData = s[self.start:self.end]
            return self.returnData
        except ValueError:
            return self.returnData

    def setPrintText(self, text):
        self.strToday = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        self.text = self.find_between(text, "/s", "/e")
        self.print_text = self.strToday+":\n"+self.text+"\n"
        self.print_conn_flag.emit(self.print_text)


    def deleteData(self, dataframe, dataframe_sort, dataframe_subscriber):
        self.ids = dataframe["issueId"].tolist()
        self.ids_sort = dataframe_sort["issueId"].tolist()
        self.ids_subs = dataframe_subscriber["고유번호"].tolist();

        self.ids = [x for x in self.ids if str(x) != 'nan']
        self.ids_sort = [x for x in self.ids_sort if str(x) != 'nan']
        self.ids_subs = [x for x in self.ids_subs if str(x) != 'nan']

        #통품전체VOC SQL
        self.sql = "DELETE FROM voc_tot_data WHERE issueId = %s"
        #불만성유형VOC SQL
        self.sql_sort = "DELETE FROM voc_sort_data WHERE issueId = %s"
        #keyword통계 sql
        self.sql_static = "DELETE FROM voc_subscriber WHERE uniqueId = %s"

        try:
            #통품전체VOC
            self.totalRows = len(self.ids)
            self.currentRow = 0
            self.setPrintText('/s DB Server에 통품전체 data 삭제 수행 중 /e')
            for item in self.ids:
                self.cur.execute(self.sql, item)
                self.currentRow = self.currentRow + 1

            #불만성유형VOC
            self.totalRows = len(self.ids_sort)
            self.currentRow = 0
            self.setPrintText('/s DB Server에 불만성유형 data 삭제 수행 중 /e')
            for item in self.ids_sort:
                self.cur.execute(self.sql_sort, item)
                self.currentRow = self.currentRow + 1

            #통품전체VOC
            self.totalRows = len(self.ids_subs)
            self.currentRow = 0
            self.setPrintText('/s DB Server에 가입자 data 삭제 수행 중 /e')
            for item in self.ids_subs:
                self.cur.execute(self.sql_static, item)
                self.currentRow = self.currentRow + 1

            self.conn.commit()
            self.setPrintText('/s DB Server에 data 삭제 완료 /e')
            self.finish_count = "y"
            self.cur.close()
            self.conn.close()
        except:
            self.cur.close()
            self.conn.close()
            self.finish_count = "y"
            self.setPrintText('/s Error: {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno)+' /e')

    def insertData(self, dataframe, dataframe_sort, dataframe_subscriber, dataframe_device, dataframe_device2):
        # key value "issueId"
        self.currentDate = self.getCurrentDate()

        ########################## VOC Total Table #################################
        self.issueId = dataframe["issueId"].tolist()
        self.netHead = dataframe["netHead"].tolist()
        self.manageTeam = dataframe["manageTeam"].tolist()
        self.manageCo = dataframe["manageCo"].tolist()
        self.regiDate = dataframe["regiDate"].tolist()
        self.regiTime = dataframe["regiTime"].tolist()
        self.counsel1 = dataframe["counsel1"].tolist()
        self.counsel2 = dataframe["counsel2"].tolist()
        self.counsel3 = dataframe["counsel3"].tolist()
        self.counsel4 = dataframe["counsel4"].tolist()
        #generate receive date list
        self.receiveDate = list()
        for i in range(len(self.issueId)):
            self.receiveDate.append(self.currentDate)

        self.action1 = dataframe["action1"].tolist()
        self.action2 = dataframe["action2"].tolist()
        self.action3 = dataframe["action3"].tolist()
        self.action4 = dataframe["action4"].tolist()
        self.manu = dataframe["manu"].tolist()
        self.model = dataframe["model"].tolist()
        self.model2 = dataframe["model2"].tolist()
        self.devCode = dataframe["devCode"].tolist()
        self.devLaunchDate = dataframe["devLaunchDate"].tolist()
        self.devLaunchDate = [None if x=="" else x for x in self.devLaunchDate]
        self.hdvoiceFlag = dataframe["hdvoiceFlag"].tolist()
        self.netMethod2 = dataframe["netMethod2"].tolist()
        self.ocSpot1 = dataframe["ocSpot1"].tolist()
        self.ocSpot2 = dataframe["ocSpot2"].tolist()
        self.loc1 = dataframe["loc1"].tolist()
        self.loc2 = dataframe["loc2"].tolist()
        self.loc3 = dataframe["loc3"].tolist()
        self.state = dataframe["state"].tolist()
        self.district = dataframe["district"].tolist()


        self.planCode = dataframe["planCode"].tolist()
        self.userAgent = dataframe["userAgent"].tolist()
        self.petName = dataframe["petName"].tolist()
        self.usimName = dataframe["usimName"].tolist()
        self.repeaterFlag = dataframe["repeaterFlag"].tolist()
        self.vocRecieve = dataframe["vocRecieve"].tolist()
        self.changeDate = dataframe["changeDate"].tolist()
        self.changeDate = [None if x=="" else x for x in self.changeDate]
        self.memo = dataframe["memo"].tolist()
        self.memoSum = dataframe["memoSum"].tolist()
        self.class1 = dataframe["class1"].tolist()
        self.updateFlag = dataframe["updateFlag"].tolist()
        self.roamFlag = dataframe["roamFlag"].tolist()
        self.swVer = dataframe["swVer"].tolist()
        self.extractWord = dataframe["extractWord"].tolist()

        self.voc_values = [self.issueId, self.netHead, self.manageTeam, self.manageCo, self.regiDate, self.regiTime,\
        self.counsel1, self.counsel2, self.counsel3, self.counsel4, self.receiveDate, self.action1, self.action2, self.action3,\
        self.action4, self.manu, self.model, self.model2, self.devCode, self.devLaunchDate, self.hdvoiceFlag, self.netMethod2,\
        self.ocSpot1, self.ocSpot2, self.loc1, self.loc2, self.loc3, self.state, self.district, self.planCode, self.userAgent,\
        self.petName, self.usimName, self.repeaterFlag, self.vocRecieve, self.changeDate, self.memo, self.memoSum, self.class1, \
        self.updateFlag, self.roamFlag, self.swVer, self.extractWord]


        ####################### VOC sort Table #################################
        self.issueId_sort = dataframe_sort["issueId"].tolist()
        self.netHead_sort = dataframe_sort["netHead"].tolist()
        self.manageTeam_sort = dataframe_sort["manageTeam"].tolist()
        self.manageCo_sort = dataframe_sort["manageCo"].tolist()
        self.regiDate_sort = dataframe_sort["regiDate"].tolist()
        self.regiTime_sort = dataframe_sort["regiTime"].tolist()
        self.counsel1_sort = dataframe_sort["counsel1"].tolist()
        self.counsel2_sort = dataframe_sort["counsel2"].tolist()
        self.counsel3_sort = dataframe_sort["counsel3"].tolist()
        self.counsel4_sort = dataframe_sort["counsel4"].tolist()

        self.action1_sort = dataframe_sort["action1"].tolist()
        self.action2_sort = dataframe_sort["action2"].tolist()
        self.action3_sort = dataframe_sort["action3"].tolist()
        self.action4_sort = dataframe_sort["action4"].tolist()
        self.manu_sort = dataframe_sort["manu"].tolist()
        self.model_sort = dataframe_sort["model"].tolist()
        self.model2_sort = dataframe_sort["model2"].tolist()
        self.devCode_sort = dataframe_sort["devCode"].tolist()
        self.devLaunchDate_sort = dataframe_sort["devLaunchDate"].tolist()
        self.devLaunchDate_sort = [None if x=="" else x for x in self.devLaunchDate_sort]

        self.hdvoiceFlag_sort = dataframe_sort["hdvoiceFlag"].tolist()
        self.netMethod2_sort = dataframe_sort["netMethod2"].tolist()
        self.ocSpot1_sort = dataframe_sort["ocSpot1"].tolist()
        self.ocSpot2_sort = dataframe_sort["ocSpot2"].tolist()
        self.loc1_sort = dataframe_sort["loc1"].tolist()
        self.loc2_sort = dataframe_sort["loc2"].tolist()
        self.loc3_sort = dataframe_sort["loc3"].tolist()
        self.state_sort = dataframe_sort["state"].tolist()
        self.district_sort = dataframe_sort["district"].tolist()

        self.planCode_sort = dataframe_sort["planCode"].tolist()
        self.userAgent_sort = dataframe_sort["userAgent"].tolist()
        self.petName_sort = dataframe_sort["petName"].tolist()
        self.usimName_sort = dataframe_sort["usimName"].tolist()
        self.repeaterFlag_sort = dataframe_sort["repeaterFlag"].tolist()
        self.vocRecieve_sort = dataframe_sort["vocRecieve"].tolist()
        self.changeDate_sort = dataframe_sort["changeDate"].tolist()
        self.changeDate_sort = [None if x=="" else x for x in self.changeDate_sort]
        self.memo_sort = dataframe_sort["memo"].tolist()
        self.memoSum_sort = dataframe_sort["memoSum"].tolist()
        self.class1_sort = dataframe_sort["class1"].tolist()
        self.updateFlag_sort = dataframe_sort["updateFlag"].tolist()
        self.roamFlag_sort = dataframe_sort["roamFlag"].tolist()
        self.swVer_sort = dataframe_sort["swVer"].tolist()
        self.extractWord_sort = dataframe_sort["extractWord"].tolist()

        self.voc_values_sort = [self.issueId_sort, self.netHead_sort, self.manageTeam_sort, self.manageCo_sort, self.regiDate_sort, self.regiTime_sort,\
        self.counsel1_sort, self.counsel2_sort, self.counsel3_sort, self.counsel4_sort, self.receiveDate, self.action1_sort, self.action2_sort, \
        self.action3_sort, self.action4_sort, self.manu_sort, self.model_sort, self.model2_sort, self.devCode_sort, self.devLaunchDate_sort, \
        self.hdvoiceFlag_sort, self.netMethod2_sort, self.ocSpot1_sort, self.ocSpot2_sort, self.loc1_sort, self.loc2_sort, self.loc3_sort, self.state_sort, \
        self.district_sort, self.planCode_sort, self.userAgent_sort, self.petName_sort, self.usimName_sort, self.repeaterFlag_sort, self.vocRecieve_sort, \
        self.changeDate_sort, self.memo_sort, self.memoSum_sort, self.class1_sort, self.updateFlag_sort, self.roamFlag_sort, self.swVer_sort, \
        self.extractWord_sort]


        ####################### VOC subscriber Table #################################

        self.uniqueId = dataframe_subscriber["고유번호"].tolist()
        self.subsDate = dataframe_subscriber["일자"].tolist()
        self.model_subs = dataframe_subscriber["단말기명"].tolist()
        self.model2_subs = dataframe_subscriber["단말기모델명2"].tolist()
        self.hdv_subs = dataframe_subscriber["HD-V가입자"].tolist()
        self.hdv_subs = [0 if x == '' else x for x in self.hdv_subs]
        self.lte_subs = dataframe_subscriber["LTE(전체(a+b))"].tolist()
        self.lte_subs = [0 if x == '' else x for x in self.lte_subs]
        self.fiveG_subs = dataframe_subscriber["5G"].tolist()
        self.fiveG_subs = [0 if x == '' else x for x in self.fiveG_subs]
        self.totNum_subs = dataframe_subscriber["전체가입자"].tolist()
        self.totNum_subs = [0 if x == '' else x for x in self.totNum_subs]


        ####################### VOC device Table #################################
        # self.mapping_model = dataframe_device["단말기모델명"].tolist()
        # self.mapping_launch = dataframe_device['출시일'].tolist()
        # self.mapping_network = dataframe_device['네트워크방식'].tolist()
        self.compare_model = []
        self.uptarget_model = []
        self.search_query = "SELECT * FROM voc_models"
        self.cur.execute(self.search_query)
        self.rows = self.cur.fetchall()

        ####################### VOC device Table #################################
        # self.mapping_model2 = dataframe_device2["단말기모델명2"].tolist()
        self.compare_model2 = []
        self.uptarget_model2 = []
        self.search_query2 = "SELECT * FROM voc_models2"
        self.cur.execute(self.search_query2)
        self.rows2 = self.cur.fetchall()

        #generate receive date list
        self.regiDate_subs = list()
        for i in range(len(self.uniqueId)):
            self.regiDate_subs.append(self.currentDate)

        self.voc_values_subs = [self.subsDate, self.model_subs, self.model2_subs, self.regiDate_subs, self.hdv_subs, self.lte_subs, self.fiveG_subs, self.totNum_subs, self.uniqueId]


        # Generate tot sql
        self.sql_insert = "INSERT INTO voc_tot_data(issueId, netHead, manageTeam, manageCo, regiDate, regiTime, counsel1, counsel2, counsel3, counsel4, receiveDate,"\
        "action1, action2, action3, action4, manu, model, model2, devCode, devLaunchDate, hdvoiceFlag, netMethod2, ocSpot1, ocSpot2, loc1, loc2, loc3, state, district,"\
        "planCode, userAgent, petName, usimName, repeaterFlag, vocRecieve, changeDate, memo, memoSum, class1, updateFlag, roamFlag, swVer, extractWord) "\
        "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "\
        "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        # Generate sort sql
        self.sql_sort_insert = "INSERT INTO voc_sort_data(issueId, netHead, manageTeam, manageCo, regiDate, regiTime, counsel1, counsel2, counsel3, counsel4, receiveDate,"\
        "action1, action2, action3, action4, manu, model, model2, devCode, devLaunchDate, hdvoiceFlag, netMethod2, ocSpot1, ocSpot2, loc1, loc2, loc3, state, district,"\
        "planCode, userAgent, petName, usimName, repeaterFlag, vocRecieve, changeDate, memo, memoSum, class1, updateFlag, roamFlag, swVer, extractWord) "\
        "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "\
        "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        # Generate sort sql
        self.sql_subs_insert = "INSERT INTO voc_subscriber(subsDate, model, model2, regiDate, subsHDV, subsLTE, subs5G, numSubs, uniqueId) "\
        "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"

        # voc_model insert
        self.sql_device_insert = "INSERT INTO voc_models (model, regiDate, flag, focusOn, launchDate, cellType, manu) VALUES(%s, %s, 1, 0, %s, %s, %s)"
        # voc_model2 insert
        self.sql_device_insert2 = "INSERT INTO voc_models2 (model, regiDate, flag, focusOn, launchDate, cellType, manu) VALUES(%s, %s, 1, 0, %s, %s, %s)"

        try:
            self.setPrintText('/s DB Server에 통품전체 data 업로드 수행 중 /e')
            self.totalRows = len(self.issueId)
            self.currentRow = 0
            for i in range(len(self.issueId)):
                self.tuple_value = ()
                self.temp_list = []
                for j in range(len(self.voc_values)):
                    self.item = self.voc_values[j]
                    self.temp_list.append(self.item[i])
                self.tuple_value = tuple(self.temp_list)
                self.cur.execute(self.sql_insert, self.tuple_value)
                self.currentRow = self.currentRow + 1

            self.totalRows = len(self.issueId_sort)
            self.currentRow = 0
            self.setPrintText('/s DB Server에 불만성유형 data 업로드 수행 중 /e')
            for i in range(len(self.issueId_sort)):
                self.tuple_value = ()
                self.temp_list = []
                for j in range(len(self.voc_values_sort)):
                    self.item = self.voc_values_sort[j]
                    self.temp_list.append(self.item[i])
                self.tuple_value = tuple(self.temp_list)
                self.cur.execute(self.sql_sort_insert, self.tuple_value)
                self.currentRow = self.currentRow + 1

            self.totalRows = len(self.uniqueId)
            self.currentRow = 0
            self.setPrintText('/s DB Server에 가입자 data 업로드 수행 중 /e')
            for i in range(len(self.uniqueId)):
                self.tuple_value = ()
                self.temp_list = []
                for j in range(len(self.voc_values_subs)):
                    self.item = self.voc_values_subs[j]
                    self.temp_list.append(self.item[i])
                self.tuple_value = tuple(self.temp_list)
                self.cur.execute(self.sql_subs_insert, self.tuple_value)
                self.currentRow = self.currentRow + 1

            self.setPrintText('/s DB Server에 model data 업데이트 체크 수행 중 /e')
            #generate DB models list
            for item in self.rows:
                self.compare_model.append(item["model"])
            #generate target upload models and excute upload to voc_models table
            for idx in range(dataframe_device.shape[0]):
                model = dataframe_device.at[idx, '단말기모델명']
                if model in self.compare_model:
                    continue
                else:
                    launchDate = dataframe_device.at[idx, '출시일']
                    network = dataframe_device.at[idx, '네트워크방식']
                    manufact = dataframe_device.at[idx, '단말기제조사']
                    self.uptarget_model.append([model, self.currentDate, launchDate, network, manufact])

            if len(self.uptarget_model) == 0:
                self.setPrintText('/s DB Server에 model data 업데이트 필요 없음 /e')
                pass
            else:
                self.setPrintText('/s DB Server에 model data 업데이트 수행 중 /e')
                self.totalRows = len(self.uptarget_model)
                self.currentRow = 0
                for item in self.uptarget_model:
                    self.tuple_value = tuple(item)
                    self.cur.execute(self.sql_device_insert, self.tuple_value)
                    self.currentRow = self.currentRow + 1

            self.setPrintText('/s DB Server에 model2 data 업데이트 체크 수행 중 /e')
            #generate DB models2 list
            for item in self.rows2:
                self.compare_model2.append(item["model"])
            #generate target upload models and excute upload to voc_models2 table
            for idx in range(dataframe_device2.shape[0]):
                model = dataframe_device2.at[idx, '단말기모델명2']
                if model in self.compare_model2:
                    continue
                else:
                    launchDate = dataframe_device2.at[idx, '출시일']
                    network = dataframe_device2.at[idx, '네트워크방식']
                    manufact = dataframe_device2.at[idx, '단말기제조사']
                    self.uptarget_model2.append([model, self.currentDate, launchDate, network, manufact])

            if len(self.uptarget_model2) == 0:
                self.setPrintText('/s DB Server에 model2 data 업데이트 필요 없음 /e')
                pass
            else:
                self.setPrintText('/s DB Server에 model2 data 업데이트 수행 중 /e')
                self.totalRows = len(self.uptarget_model2)
                self.currentRow = 0
                for item in self.uptarget_model2:
                    self.tuple_value = tuple(item)
                    self.cur.execute(self.sql_device_insert2, self.tuple_value)
                    self.currentRow = self.currentRow + 1

            self.finish_count = "y"
            self.conn.commit()
            self.setPrintText('/s DB Server에 data 등록 완료 /e')
            self.cur.close()
            self.conn.close()
            self.end_conn_flag.emit()
        except:
            self.finish_count = "y"
            self.cur.close()
            self.conn.close()
            self.setPrintText('/s Error: {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno)+' /e')
            self.end_conn_flag.emit()


    # def run(self):
    #     try:
    #         # self.thread_print = threading.Thread(target=self.getPrintText, args=())
    #         self.thread_count = threading.Thread(target=self.getCountRows, args=())
    #         self.thread_count.daemon = True
    #         # self.thread_print.start()
    #         self.thread_count.start()
    #
    #         self.conn = pymysql.connect(host=self.address, user=self.user, password=self.password, db=self.db_name, charset='utf8')
    #         self.cur = self.conn.cursor(pymysql.cursors.DictCursor)
    #         # self.sql_update_db = "INSERT INTO "+self.table_name+"(question_text, pub_date) VALUES(%s,%s)"
    #         # 통품전체VOC
    #         self.df_mysql = pd.read_excel(self.file_path, sheet_name=self.sheet_name_tot, index_col=None)
    #         # 불만성유형VOC
    #         self.df_mysql_sort = pd.read_excel(self.file_path, sheet_name=self.sheet_name_sort, index_col=None)
    #         #가입자데이터
    #         self.df_mysql_subscriber = pd.read_excel(self.file_path, sheet_name=self.sheet_name_subscriber, index_col=None)
    #         #모델정보데이터
    #         self.df_mysql_devices = pd.read_excel(self.file_path, sheet_name=self.sheet_name_models, index_col=None)
    #         #모델2정보데이터
    #         self.df_mysql_devices2 = pd.read_excel(self.file_path, sheet_name=self.sheet_name_models2, index_col=None)
    #
    #         self.setPrintText("/s DB Data Excel 파일 DateFrame 변환 완료 /e")
    #         # change columns name to db's name(dict_cols)
    #         self.df_mysql.columns = self.list_cols
    #         self.df_mysql_sort.columns = self.list_cols
    #
    #         # if cell is empty change type numpy nan to empty string ""
    #         self.df_mysql = self.df_mysql.replace(numpy.nan, "")
    #         self.totalRows = self.df_mysql.shape[0]
    #
    #         self.df_mysql_sort = self.df_mysql_sort.replace(numpy.nan, "")
    #         self.totalRows_sort = self.df_mysql_sort.shape[0]
    #
    #         self.df_mysql_subscriber = self.df_mysql_subscriber.replace(numpy.nan, "")
    #         self.totalRows_subscriber = self.df_mysql_subscriber.shape[0]
    #
    #         # regiDate column exchange to new date type "%Y-%m-%d"
    #         self.d1 = self.df_mysql["regiDate"].tolist()
    #         self.d2 = self.df_mysql["devLaunchDate"].tolist()
    #         self.d3 = self.df_mysql["changeDate"].tolist()
    #
    #         self.d1_sort = self.df_mysql_sort["regiDate"].tolist()
    #         self.d2_sort = self.df_mysql_sort["devLaunchDate"].tolist()
    #         self.d3_sort = self.df_mysql_sort["changeDate"].tolist()
    #
    #         self.d1_subs = self.df_mysql_subscriber["일자"].tolist()
    #
    #         # regiDate and devLaunchDate change string to date type
    #         self.df_mysql = self.df_mysql.drop(["regiDate"], axis=1)
    #         self.df_mysql = self.df_mysql.drop(["devLaunchDate"], axis=1)
    #         self.df_mysql = self.df_mysql.drop(["changeDate"], axis=1)
    #
    #         self.df_mysql_sort = self.df_mysql_sort.drop(["regiDate"], axis=1)
    #         self.df_mysql_sort = self.df_mysql_sort.drop(["devLaunchDate"], axis=1)
    #         self.df_mysql_sort = self.df_mysql_sort.drop(["changeDate"], axis=1)
    #
    #         self.df_mysql_subscriber = self.df_mysql_subscriber.drop(["일자"], axis=1)
    #
    #         self.df_mysql["regiDate"] = ""
    #         self.df_mysql["devLaunchDate"] = ""
    #         self.df_mysql["changeDate"] = ""
    #
    #         self.df_mysql_sort["regiDate"] = ""
    #         self.df_mysql_sort["devLaunchDate"] = ""
    #         self.df_mysql_sort["changeDate"] = ""
    #
    #         self.df_mysql_subscriber["일자"] = ""
    #
    #         # 통품전체VOC make new regiDate column and input new date type string
    #         self.totatlCount = len(self.d1)
    #         for i in range(self.totatlCount):
    #             if self.d1[i] is not "":
    #                 self.temp_date = None
    #                 if isinstance(self.d1[i], int) is not True:
    #                     self.temp_date = self.d1[i].strftime("%Y-%m-%d")
    #                 else:
    #                     self.temp_date = pd.to_datetime(self.d1[i], unit='ns')
    #                     self.temp_date = self.temp_date.strftime("%Y-%m-%d")
    #                 self.df_mysql.at[i,"regiDate"] = self.temp_date
    #
    #             if self.d2[i] is not "":
    #                 self.temp_date = None
    #                 if isinstance(self.d2[i], int) is not True:
    #                     self.temp_date = self.d2[i].strftime("%Y-%m-%d")
    #                 else:
    #                     self.temp_date = pd.to_datetime(self.d2[i], unit='ns')
    #                     self.temp_date = self.temp_date.strftime("%Y-%m-%d")
    #                 self.df_mysql.at[i,"devLaunchDate"] = self.temp_date
    #
    #             if self.d3[i] is not "":
    #                 self.temp_date = None
    #                 if isinstance(self.d3[i], int) is not True:
    #                     self.temp_date = self.d3[i].strftime("%Y-%m-%d")
    #                 else:
    #                     self.temp_date = pd.to_datetime(self.d3[i], unit='ns')
    #                     self.temp_date = self.temp_date.strftime("%Y-%m-%d")
    #                 self.df_mysql.at[i,"changeDate"] = self.temp_date
    #
    #         # 불만성유형VOC make new regiDate column and input new date type string
    #         self.totatlCount = len(self.d1_sort)
    #         for i in range(self.totatlCount):
    #             if self.d1_sort[i] is not "":
    #                 self.temp_date = None
    #                 if isinstance(self.d1_sort[i], int) is not True:
    #                     self.temp_date = self.d1_sort[i].strftime("%Y-%m-%d")
    #                 else:
    #                     self.temp_date = pd.to_datetime(self.d1_sort[i], unit='ns')
    #                     self.temp_date = self.temp_date.strftime("%Y-%m-%d")
    #                 self.df_mysql_sort.at[i,"regiDate"] = self.temp_date
    #
    #             if self.d2_sort[i] is not "":
    #                 self.temp_date = None
    #                 if isinstance(self.d2_sort[i], int) is not True:
    #                     self.temp_date = self.d2_sort[i].strftime("%Y-%m-%d")
    #                 else:
    #                     self.temp_date = pd.to_datetime(self.d2_sort[i], unit='ns')
    #                     self.temp_date = self.temp_date.strftime("%Y-%m-%d")
    #                 self.df_mysql_sort.at[i,"devLaunchDate"] = self.temp_date
    #
    #             if self.d3_sort[i] is not "":
    #                 self.temp_date = None
    #                 if isinstance(self.d3_sort[i], int) is not True:
    #                     self.temp_date = self.d3_sort[i].strftime("%Y-%m-%d")
    #                 else:
    #                     self.temp_date = pd.to_datetime(self.d3_sort[i], unit='ns')
    #                     self.temp_date = self.temp_date.strftime("%Y-%m-%d")
    #                 self.df_mysql_sort.at[i,"changeDate"] = self.temp_date
    #
    #         # 가입자현황 날짜 변경
    #         self.totatlCount = len(self.d1_subs)
    #         for i in range(self.totatlCount):
    #             if self.d1_subs[i] is not "":
    #                 self.temp_date = None
    #                 if isinstance(self.d1_subs[i], int) is not True:
    #                     self.temp_date = self.d1_subs[i].strftime("%Y-%m-%d")
    #                 else:
    #                     self.temp_date = pd.to_datetime(self.d1_subs[i], format='%Y%m%d', errors='ignore')
    #                     self.temp_date = self.temp_date.strftime("%Y-%m-%d")
    #                 self.df_mysql_subscriber.at[i,"일자"] = self.temp_date
    #
    #
    #         if self.select_mode is 'upload':
    #             self.setPrintText('/s Input Excel Data 업로드 작업 시작/e')
    #             self.setPrintText('/s 통품전체VOC 총 '+str(self.totalRows)+' rows data uploading.../e')
    #             self.setPrintText('/s 불만성유형VOC 총 '+str(self.totalRows_sort)+' rows data uploading.../e')
    #             self.setPrintText('/s 가입자정보 총 '+str(self.totalRows_subscriber)+' rows data uploading.../e')
    #             self.setPrintText('/s DB Server에 data 등록 작업 진행중.../e')
    #             self.insertData(self.df_mysql, self.df_mysql_sort, self.df_mysql_subscriber, self.df_mysql_devices, self.df_mysql_devices2)
    #         else:
    #             self.setPrintText('/s Input Excel Data 삭제 작업 시작/e')
    #             self.setPrintText('/s 통품전체VOC 총 '+str(self.totalRows)+' rows data delete.../e')
    #             self.setPrintText('/s 불만성유형VOC 총 '+str(self.totalRows_sort)+' rows data delete.../e')
    #             self.setPrintText('/s 가입자정보 총 '+str(self.totalRows_subscriber)+' rows data delete.../e')
    #             self.setPrintText('/s DB Data Excel 파일 data 삭제 작업 진행중 /e')
    #             self.deleteData(self.df_mysql, self.df_mysql_sort, self.df_mysql_subscriber)
    #
    #         # self.end_conn_signal = "y"
    #         self.end_conn_flag.emit()
    #
    #     except:
    #         self.setPrintText('/s Error: {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2].tb_lineno)+' /e')
    #         # self.end_conn_signal = "y"
    #         self.end_conn_flag.emit()


# if __name__ == "__main__":
#     nowTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     sample_dict = {"question_text":["사랑하는 사람들이 주변에 많은가요?"],"pub_date":[nowTime]}
#     mydb = connMyDb("192.168.0.163", "3306", "root", "navy1063", "testenc", "polls_question", sample_dict)
#     mydb.executeCommit()
