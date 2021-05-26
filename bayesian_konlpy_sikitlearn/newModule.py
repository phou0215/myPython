# -*- coding: utf-8 -*-
"""
Created on Thr Oct 18 14:25:12 2019
@author: TestEnC hanrim lee

"""
import os
import sys
import re
import json
import math
import random
import string
import openpyxl
import pandas as pd
import pickle
import joblib

from ftplib import FTP
from operator import itemgetter
from os.path import expanduser
import threading

from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.svm import LinearSVC
from sklearn.linear_model import SGDClassifier

#from konlpy.tag import Komoran
from time import sleep
from datetime import datetime
from collections import Counter
from konlpy.tag import Okt
from konlpy.tag import Komoran
from lexrankr import LexRank
#import pytagcloud
from PyQt5.QtCore import QThread, pyqtSignal
#selenium library
from openpyxl.styles import Alignment, Font, NamedStyle, PatternFill
from openpyxl import formatting, styles, Workbook
from openpyxl.styles.borders import Border, Side
from openpyxl.styles.differential import DifferentialStyle
from openpyxl.formatting.rule import ColorScaleRule, CellIsRule, FormulaRule

class avocParser(QThread):
    print_flag = pyqtSignal(str)
    end_flag = pyqtSignal()
    fileCheck_flag = pyqtSignal()
    progress_flag = pyqtSignal()
    count_flag = pyqtSignal()
    dict_result = None
    tot_count = 0

    def __init__(self, filePath, mappingFlag, opFlag, modelFlag, posFlag, parent=None):
        QThread.__init__(self, parent)
        self.filePath = filePath
        self.mappingFlag = mappingFlag
        self.opFlag = opFlag
        self.modelFlag = modelFlag
        self.posFlag = posFlag
        # self.limit_value = limit
        # self.mini_value = minimum
        self.end_count = "n"
        self.totalRows = 0
        self.subscribe_date = ''
        self.currentRow = 0
        self.words = None
        self.word_dict = None
        self.category_dict = None
        self.obj_list = []
        self.current_path = os.getcwd()
        self.okt = Okt()
        self.komoran = Komoran()
        self.stopString = ["안내","여부","사항","장비","확인","원클릭","품질","후","문의","이력","진단","부탁드립니다.","증상","종료","문의","양호","정상","고객","철회","파이","특이","간다"\
        "내부","외부","권유","성향","하심","해당","주심","고함","초기","무관","반려","같다","접수","무관","테스트","연락","바로","처리","모두","있다","없다","하다","드리다","않다","되어다",\
        "되다","부터","예정","드리다","해드리다", "신내역", "현기", "가신"]
        self.mapping_models = []
        self.mapping_models2 = []
        self.launch_model = []
        self.launch_model2 = []
        self.network_model = []
        self.network_model2 = []
        self.manufact_model = []
        self.manufact_model2 = []
        self.dict_load_models = {}
        # each category reserved word list
        self.cate_reserved = {}
        # normal filtering
        self.normal_string = []
        # ftp 관련 변수 및 설정
        self.hostname = '192.168.0.108'
        self.port = 21
        self.username = 'voc'
        self.password = 'testenc@01'
        self.list_file = []
        self.dict_files = {'naive':'model_nb.pkl', 'sgd':'model_svm.pkl', 'svc':'model_svc.pkl', 'linear':'model_linerSVC.pkl'}

        #connect SSH server
        self.ftp_client = FTP()

    def ftp_check_files(self):

        # model flag에 따라 정함
        flag = False
        if self.modelFlag == 'naive':
            for item in self.list_file:
                if 'model_nb.pkl' in item:
                    flag = True
                    break
        elif self.modelFlag == 'sgd':
            for item in self.list_file:
                if 'model_svm.pkl' in item:
                    flag = True
                    break
        elif self.modelFlag == 'svc':
            for item in self.list_file:
                if 'model_svc.pkl' in item:
                    flag = True
                    break
        elif self.modelFlag == 'linear':
            for item in self.list_file:
                if 'model_linerSVC.pkl' in item:
                    flag = True
                    break
        else:
            list_flag = []
            for item in self.list_file:
                if 'model_nb.pkl' in item:
                    list_flag.append(True)
                if 'model_svm.pkl' in item:
                    list_flag.append(True)
                if 'model_svc.pkl' in item:
                    list_flag.append(True)
                if 'model_linerSVC.pkl' in item:
                    list_flag.append(True)
            if list_flag[0] and  list_flag[1] and  list_flag[2] and  list_flag[3]:
                flag = True

        if flag:
            self.setPrintText("/s FTP Server Connected: HOST({}) PORT({}) /e".format(self.hostname, str(self.port)))
            self.setPrintText('/s FTP Server has all files.../e')
        else:
            self.setPrintText('/s FTP Server Does Not Have model pickle file.. please run learner first and try again /e')

    def ftp_download_file(self):

        try:
            # 다운로드 디렉토리 만들기
            if not os.path.isdir(self.current_path+"\\sklearn_models"):
                os.mkdir(self.current_path+"\\sklearn_models")

            if self.modelFlag != 'all':
                rf = open(self.current_path+"\\sklearn_models\\"+self.dict_files[self.modelFlag], "wb")
                self.ftp_client.retrbinary("RETR " + self.dict_files[self.modelFlag], rf.write, 8*1024)
                rf.close()
                while not os.path.isfile(self.current_path+"\\sklearn_models\\"+self.dict_files[self.modelFlag]):
                    sleep(1)

                self.load_models(self.modelFlag, self.current_path+"\\sklearn_models\\"+self.dict_files[self.modelFlag])
            else:
                for (key, value) in self.dict_files.items():
                    rf = open(self.current_path+"\\sklearn_models\\"+value, "wb")
                    self.ftp_client.retrbinary("RETR " + value, rf.write, 8*1024)
                    rf.close()
                    while not os.path.isfile(self.current_path+"\\sklearn_models\\"+value):
                        sleep(1)

                    self.load_models(key, self.current_path+"\\sklearn_models\\"+value)
        except:
            self.setPrintText('/s Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno)+' /e')
            self.end_count = "y"
            self.end_flag.emit()

    def load_models(self, key, path):

        try:
            model = joblib.load(path)
            self.dict_load_models[key] = model
            self.setPrintText('/s {} 모델 Load 작업 완료./e'.format(key))
        except:
            self.setPrintText('/s {} 모델 Load 작업 중 Error 발생... /e'.format(key))
            self.setPrintText('/s Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno)+' /e')
            self.end_count = "y"
            self.end_flag.emit()

    def ftp_stop(self):

        self.ftp_client.quit()

    # 분석 처리 개수 체크 함수
    def getCountRows(self):
        while True:
            if self.end_count is "n":
                sleep(0.5)
                self.count_flag.emit()
            else:
                break

    # 로그 문자 처리 함수
    def setPrintText(self, text):
        self.strToday = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        self.text = self.find_between(text, "/s", "/e")
        self.print_text = self.strToday+":\n"+self.text+"\n"
        self.print_flag.emit(self.print_text)

    # 쓰레드 종료 함수
    def stop(self):
        self.okt = None
        sleep(0.5)
        self.terminate()

    # 특수 문자 제거 함수
    def removeString(self, text):

        tempText = re.sub('[-=+,#/\?^$@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>\{\}`><]\'', '', text)
        return tempText

    # 문자열 Filtering 함수
    def setFilter(self, text):

        resubText = text.lower()
        resubText = self.removeString(resubText)

        # special characters regexp filter handler
        for item in self.normal_string:
            resubText = resubText.replace(item, "")
        resubText = resubText.strip()
        return resubText

    # 문장 앞 부터 조건에 맞는 문자열 substring
    def find_between(self, s, first, last):
        try:
            self.returnData = ""
            self.start = s.index(first)+len(first)
            self.end = s.index(last, self.start)
            self.returnData = s[self.start:self.end]
            return self.returnData
        except ValueError:
            return self.returnData

    # 문장 뒤 부터 조건에 맞는 문자열 substring
    def find_between_r(self, s, first, last ):
        try:
            self.returnData = ""
            self.start = s.rindex(first)+len(first)
            self.end = s.rindex(last, self.start)
            self.returnData = s[self.start:self.end]
            return self.returnData
        except ValueError:
            return self.returnData

    # text 형태소 분리 및 명사에서 '조사 어미 관용어 제외 후 리스트 리턴'
    def splitNouns(self, text):
        try:
            result_part = []
            if self.posFlag == 'okt':
                malist = self.okt.pos(text)
                for word in malist:
                    if word[1] in ['Noun','Adjective','Verb', 'Unknown'] and not word[0] in self.stopString and len(word[0]) > 1:
                        result_part.append(word[0])
            else:
                malist = self.komoran.pos(text)
                for word in malist:
                    if word[1] in ['NNG', 'NNP', 'NNB', 'VV', 'MAG', 'VA', 'VXV', 'UN', 'MAJ', 'SL', 'NA', 'NF'] and not word[0] in self.stopString and len(word[0]) > 1:
                        result_part.append(word[0])

            return result_part
        except:
            self.setPrintText('/s Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno)+' /e')
            return result_part

    # # 카테고리에 속한 단어 출현 횟수 기록하기
    # def inc_word(self, word, category):
    #     if category not in self.word_dict:
    #         self.word_dict[category] = {}
    #     if word not in self.word_dict[category]:
    #         self.word_dict[category][word] = 0
    #     self.word_dict[category][word] += 1
    #     self.words.add(word)
    #
    # # 카테고리 출현 및 횟수 기록
    # def inc_category(self, category):
    #     if category not in self.category_dict:
    #         self.category_dict[category] = 0
    #     self.category_dict[category] += 1
    #
    # # 매칭 단어 리스트에 점수 계산
    # def mat_score(self, words, category):
    #
    #     self.score = math.log(self.category_prob(category))
    #     for word in words:
    #         self.score += math.log(self.word_prob(word, category))
    #     return self.score
    #
    # #카테고리 내부의 단어 출현 횟수 구하기
    # def get_word_count(self, word, category):
    #     if word in self.word_dict[category]:
    #         return self.word_dict[category][word]
    #     else:
    #         return 0
    #
    # #카테고리 계산
    # def category_prob(self, category):
    #     self.sum_categories = sum(self.category_dict.values())
    #     self.category_v = self.category_dict[category]
    #     return self.category_v / self.sum_categories
    #
    # #카테고리 내부의 단어 춣현 비율 계산
    # def word_prob(self, word, category):
    #     self.n = self.get_word_count(word, category) + 1
    #     self.d = sum(self.word_dict[category].values()) + len(self.words)
    #     return self.n / self.d

    # 예측함수
    def predict(self, text):

        try:
            list_labels = []
            dict_labels = {}
            best_category = ''
            benchmark_category = ''
            ex_word = self.splitNouns(text)
            strings = ",".join(ex_word)

            if self.modelFlag != 'all':
                list_predict = self.dict_load_models[self.modelFlag].predict([text])
                best_category = list_predict[0]
            else:
                # 각 모델에서 predict vote 실행
                for (key, value) in self.dict_load_models.items():
                    if key == 'linear':
                        benchmark_category = value.predict([text])[0]
                        list_labels.append(benchmark_category)
                    else:
                        list_labels.append(value.predict([text])[0])
                # 각 카테고리 예측 리스트에 담고 순위별로 정리
                dict_labels = Counter(list_labels)
                dict_labels = sorted(dict_labels.items(), key=lambda x:x[1], reverse=True)
                if len(dict_labels) > 1:
                    # 1순위와 2순위가 같으면
                    if dict_labels[0][1] == dict_labels[1][1]:
                        best_category = benchmark_category
                    # 같지 않으면 1순위가 best_category
                    else:
                        best_category = dict_labels[0][0]
                else:
                    best_category = dict_labels[0][0]

            retrunData = [best_category, strings]
            return retrunData
        except:
            print('/s Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno)+' /e')
            self.setPrintText('/s Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno)+' /e')
    # find software Version return data: String
    def find_version(self, text, model_name):
        self.os_string = str(text).replace(" ","")
        self.name = model_name.upper()
        self.returnData = "N/A"
        try:
            if (self.os_string is not "") and (self.name is not "") and (self.os_string is not "0"):
                #ios android flag
                self.os_string = self.os_string+"/e"
                if "iOS" in self.os_string and "iPhone" in self.os_string:
                    self.returnData = self.find_between(self.os_string, "iOS/", "iPhone")
                elif "iOS" in self.os_string and "Watch" in self.os_string:
                    self.returnData = self.find_between(self.os_string, "iOS/", "Watch")
                else:
                    if re.search(self.name + r".*" + "/", self.os_string):
                        if "_AND" in self.os_string:
                            self.os_string = re.sub(self.name+r".?.?.?.?.?.?"+"_", self.name+"_", self.os_string, 1)
                            self.returnData = self.find_between(self.os_string, self.name+"_", "/e")
                        elif "Device_Type" in self.os_string:
                            self.os_string = re.sub(self.name+r".?.?.?.?.?.?"+"/",self.name+"/",self.os_string,1)
                            self.returnData = self.find_between(self.os_string, self.name+"/", "Device_Type")
                        else:
                            self.os_string = re.sub(self.name+r".?.?.?.?.?.?"+"/", self.name+"/", self.os_string,1)
                            self.returnData = self.find_between(self.os_string, self.name+"/", "/e")
                    else:
                        self.returnData = "불일치"

                self.returnData = self.returnData.replace(" ","")
                return self.returnData
            else:
                self.returnData = "정보없음"
                return self.returnData
        except:
            self.setPrintText('/s Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno)+' /e')
            self.returnData = "정보없음"
            return self.returnData
    # 업데이트 예약어 포함 여부 확인
    def check_update(self, memo, update_list):
        self.update_flag = "N"
        self.textMemo_short = memo.lower().replace(" ","")
        for item in update_list:
            if item.lower().replace(" ","") in self.textMemo_short:
                self.update_flag = "Y"
                break
        return self.update_flag
    # 로밍 예약어 포함 여부 확인
    # def check_roaming(self, memo, roaming_list):
    #     self.roaming_flag = "N"
    #     self.textMemo_short = memo.lower().replace(" ","")
    #     for item in roaming_list:
    #         if item.lower().replace(" ","") in self.textMemo_short:
    #             self.roaming_flag = "Y"
    #             break
    #     return self.roaming_flag
    # 키워드 분류 및 업데이트 로밍 소프트웨어 버전 검사 함수
    def analysis_data(self, dataframe, update_list, special_list, repeater_list, repeater_col4_list, local1_list):
        try:
            # 변수 선언
            lexrank = LexRank()
            self.df_target = dataframe
            self.update = update_list
            self.special = special_list
            self.repeater = repeater_list
            self.repeater_col4 = repeater_col4_list
            self.local_1 = local1_list
            self.part_total_rows = self.df_target.shape[0]
            self.p = re.compile("[1-9]{1}[.]{1}")
            #############################__analysis of dataFrame__#############################
            for i in range(self.part_total_rows):
                self.disText = ""
                self.disText = "/s Index_"+str(i+1)+" DATA: \n"
                self.memoString = self.df_target.at[i, "메모"]
                self.memoString = self.setFilter(self.memoString)
                ####################__1 작업 메모요약 작업__####################
                try:
                    if(len(self.memoString) >= 40):
                        lexrank.summarize(self.memoString)
                        self.summ = lexrank.probe(2)
                        self.summ_text = ""
                        for j in range(len(self.summ)):
                            self.temp_str = self.summ[j].replace("-", "")
                            self.summ_text = self.summ_text+"*"+self.temp_str+"\n\n"
                        self.df_target.at[i, "메모요약"] = self.summ_text
                except:
                    self.df_target.at[i, "메모요약"] = ""
                ####################__2 작업 키워드 검사__########################
                self.disText = self.disText + "ORIGINAL MEMO : "+self.memoString+"\n"
                self.treat = ""
                self.local = ""
                self.model_name = ""
                self.specString = ""
                self.softVersion = ""
                self.select_category = ""
                # 지역1 값 Null 조회
                if not pd.isnull(self.df_target.at[i, "지역1"]):
                    self.local = self.df_target.at[i, "지역1"]

                if not pd.isnull(self.df_target.at[i, "상담사조치4"]):
                    self.treat = self.df_target.at[i, "상담사조치4"]

                # 소프트웨어 버전 조회
                if not pd.isnull(self.df_target.at[i, "단말기모델명2"]):
                    self.model_name = self.df_target.at[i, "단말기모델명2"]

                if not pd.isnull(self.df_target.at[i, "사용자AGENT"]):
                    self.softVersion = self.df_target.at[i, "사용자AGENT"]

                if len(self.memoString) < 10:
                    self.df_target.at[i, "메모분류"] = "분류없음"
                    self.df_target.at[i, "업데이트 유무"] = "N"

                    if self.model_name is not "" and self.softVersion is not "":
                        self.version_info = self.find_version(self.softVersion, self.model_name)
                        self.df_target.at[i, "소프트웨어"] = self.version_info
                    else:
                        self.df_target.at[i, "소프트웨어"] = "정보없음"
                    self.select_category = "분류없음"

                # 지역1 값이 local_1 리스트에 있는지 확인 : True ==> 중계기이며 소프트웨어 검사
                elif self.local is not "" and self.local in self.local_1:
                    self.df_target.at[i, "메모분류"] = "중계기"
                    self.df_target.at[i, "업데이트 유무"] = "N"

                    if self.model_name is not "" and self.softVersion is not "":
                        self.version_info = self.find_version(self.softVersion, self.model_name)
                        self.df_target.at[i, "소프트웨어"] = self.version_info
                    else:
                        self.df_target.at[i, "소프트웨어"] = "정보없음"
                    self.select_category = "중계기"

                # 상담사조치4 값이 repeater_col4 리스트에 있는지 확인 : True ==> 중계기이며 소프트웨어 검사
                elif self.treat is not "" and self.treat in self.repeater_col4:
                    self.df_target.at[i, "메모분류"] = "중계기"
                    self.df_target.at[i, "업데이트 유무"] = "N"

                    if self.model_name is not "" and self.softVersion is not "":
                        self.version_info = self.find_version(self.softVersion, self.model_name)
                        self.df_target.at[i, "소프트웨어"] = self.version_info
                    else:
                        self.df_target.at[i, "소프트웨어"] = "정보없음"
                    self.select_category = "중계기"

                # 해당 사항이 없는 경우
                else:
                    # Type 1 => 중계기 예약어 메모 내용에 있는 경우
                    # Type 2 => 특수 parsing이 필요한 언어가 있는 경우
                    # 그 외 정상적인 메모 내용 확인
                    self.type = ""
                    for item in self.repeater:
                        if item.replace(" ", "") in self.memoString:
                            self.type = "1"
                            break

                    if self.type is "":
                        for item in self.special:
                            if item.replace(" ", "") in self.memoString:
                                self.specString = item
                                self.type = "2"
                                break

                    ########################__type 1인 경우__########################
                    if self.type is "1":
                        self.df_target.at[i, "메모분류"] = "중계기"
                        self.df_target.at[i, "업데이트 유무"] = "N"
                        # 소프트웨어버전 조회
                        if self.model_name is not "" and self.softVersion is not "":
                            self.version_info = self.find_version(self.softVersion, self.model_name)
                            self.df_target.at[i, "소프트웨어"] = self.version_info
                        else:
                            self.df_target.at[i, "소프트웨어"] = "정보없음"
                        self.select_category = "중계기"
                    ########################__type 2인 경우__########################
                    elif self.type is "2":
                        flag_pre_selected = False
                        key_pre_selected = ""
                        self.memoString = self.memoString+"/e"
                        # 특수문인 경우 특수문과 기준점 사이에 문자를 Parsing 함
                        self.temp_text = self.find_between(self.memoString, self.specString, "/e")
                        if self.p.search(self.temp_text):
                            self.pattern_list = self.p.findall(self.temp_text)
                            self.memoString = self.find_between(self.memoString, self.specString, self.pattern_list[0])
                        else:
                            self.memoString = self.temp_text

                        # manul pattern 분석 self.cate_reserved에 속하는지 검사
                        if len(self.cate_reserved) > 0:
                            for key in list(self.cate_reserved.keys()):
                                values = self.cate_reserved[key]
                                if not flag_pre_selected:
                                    for item in values:
                                        if re.search(item, self.memoString):
                                            flag_pre_selected = True
                                            key_pre_selected = key
                                            break
                                else:
                                    break

                        # flag_pre_selected에 따라
                        if flag_pre_selected:
                            self.df_target.at[i, "메모분류"] = key_pre_selected
                            self.flag1 = self.check_update(self.memoString, self.update)
                            self.df_target.at[i, "업데이트 유무"] = self.flag1
                            # 소프트웨어버전 조회
                            if self.model_name is not "" and self.softVersion is not "":
                                self.version_info = self.find_version(self.softVersion, self.model_name)
                                self.df_target.at[i, "소프트웨어"] = self.version_info
                            else:
                                self.df_target.at[i, "소프트웨어"] = "정보없음"
                            self.select_category = key_pre_selected
                            words = self.splitNouns(self.memoString)
                            strings = ",".join(words)
                            self.df_target.at[i, "추출단어"] = strings

                        else:
                            # 문자열을 가지고 Bayesian 함수 실행
                            self.result_data = self.predict(self.memoString)
                            self.df_target.at[i, "메모분류"] = self.result_data[0]
                            self.select_category = self.result_data[0]
                            self.flag1 = self.check_update(self.memoString, self.update)
                            self.df_target.at[i, "업데이트 유무"] = self.flag1

                            # 소프트웨어버전 조회
                            if self.model_name is not "" and self.softVersion is not "":
                                self.version_info = self.find_version(self.softVersion, self.model_name)
                                self.df_target.at[i, "소프트웨어"] = self.version_info
                            else:
                                self.df_target.at[i, "소프트웨어"] = "정보없음"
                            self.df_target.at[i, "추출단어"] = self.result_data[1]

                    ########################__해당 없는 정상 경우__########################
                    else:

                        flag_pre_selected = False
                        key_pre_selected = ""
                        #메모내용 길이 조정
                        # if self.limit_value is not "0" and self.mini_value is not "0":
                        #     if len(self.memoString) > int(self.mini_value):
                        #         self.endPoint_n = int(len(self.memoString) * float("0."+self.limit_value))
                        #         self.memoString = self.memoString[:self.endPoint_n]


                        # manul pattern 분석 self.cate_reserved에 속하는지 검사
                        if len(self.cate_reserved) > 0:
                            for key in list(self.cate_reserved.keys()):
                                values = self.cate_reserved[key]
                                if not flag_pre_selected:
                                    for item in values:
                                        if re.search(item, self.memoString):
                                            flag_pre_selected = True
                                            key_pre_selected = key
                                            break
                                else:
                                    break

                        # flag_pre_selected에 따라
                        if flag_pre_selected:
                            self.df_target.at[i, "메모분류"] = key_pre_selected
                            self.flag1 = self.check_update(self.memoString, self.update)
                            self.df_target.at[i, "업데이트 유무"] = self.flag1
                            # 소프트웨어버전 조회
                            if self.model_name is not "" and self.softVersion is not "":
                                self.version_info = self.find_version(self.softVersion, self.model_name)
                                self.df_target.at[i, "소프트웨어"] = self.version_info
                            else:
                                self.df_target.at[i, "소프트웨어"] = "정보없음"
                            self.select_category = key_pre_selected
                            words = self.splitNouns(self.memoString)
                            strings = ",".join(words)
                            self.df_target.at[i, "추출단어"] = strings
                        else:
                            # 문자열을 가지고 Bayesian 함수 실행
                            self.result_data = self.predict(self.memoString)
                            self.df_target.at[i, "메모분류"] = self.result_data[0]
                            self.select_category = self.result_data[0]
                            self.flag1 = self.check_update(self.memoString, self.update)
                            self.df_target.at[i, "업데이트 유무"] = self.flag1

                            # 소프트웨어버전 조회
                            if self.model_name is not "" and self.softVersion is not "":
                                self.version_info = self.find_version(self.softVersion, self.model_name)
                                self.df_target.at[i, "소프트웨어"] = self.version_info
                            else:
                                self.df_target.at[i, "소프트웨어"] = "정보없음"
                            self.df_target.at[i, "추출단어"] = self.result_data[1]

                self.disText = self.disText + "SELECTED CATEGORY : "+self.select_category+"\n/e"
                self.setPrintText(self.disText)
                self.currentRow = self.currentRow+1
                self.issueId = ""
                self.charset = string.ascii_uppercase + string.digits
                self.issueId = ''.join(random.sample(self.charset*15, 15))
                self.df_target.at[i, "이슈번호"] = self.issueId

            self.setPrintText("/s VOC 전체 메모정보 요약 및 카테고리 작업 완료 /e")
            return self.df_target
        except:
            self.setPrintText('/s Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno)+' /e')

    # main method
    def run(self):

        try:
            ###########################__print Text Thread delay 1.5 second__######################
            self.ftp_client.connect(host=self.hostname, port=self.port)
            self.ftp_client.login(user=self.username, passwd=self.password)
            # self.ftp_client.cwd("Learning")
            self.ftp_client.cwd("sklearn_models")
            self.ftp_client.retrlines("LIST", self.list_file.append)

            #ftp server check files
            self.ftp_check_files()
            #ftp server file download
            self.ftp_download_file()
            # ftp server quit connector
            self.ftp_stop()

            # self.thread_print = threading.Thread(target=self.getPrintText, args=())
            self.thread_count = threading.Thread(target=self.getCountRows, args=())
            self.thread_count.daemon = True
            # self.thread_print.start()
            self.thread_count.start()

            self.home = expanduser("~")
            self.nowTime = datetime.today().strftime("%Y-%m-%d")

            #################################################################_SETTING INPUT_###########################################################################
            # Input and save user select each mode
            self.input_file = self.filePath
            self.file_name = self.find_between_r(self.input_file,"/",".")
            if os.path.isdir(self.home+"\\Desktop\\VOC\\"):
                self.output_file = self.home+"\\Desktop\\VOC\\result_"+self.file_name+"("+self.nowTime+").xlsx"
            else:
                os.mkdir(self.home+"\\Desktop\\VOC\\")
                self.output_file = self.home+"\\Desktop\\VOC\\result_"+self.file_name+"("+self.nowTime+").xlsx"

            #################################################################_SETTING INPUT_###########################################################################

            #Core Code
            self.start_time = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            #Excel input Data read
            self.setPrintText("/s START_TIME: "+self.start_time+" /e")
            self.setPrintText("/s Start to read the Excel File Data /e")
            self.df_subscriber = pd.read_excel(self.input_file, sheet_name="가입자정보", index_col=None)
            self.setPrintText("/s 가입자정보 DataFrame으로 변환 완료 /e")
            self.df_swing = pd.read_excel(self.input_file, sheet_name="VOC데이터", index_col=None)
            self.setPrintText("/s VOC정보 DataFrame으로 변환 완료 /e")
            self.df_device = pd.read_excel(self.input_file, sheet_name="단말", index_col=None)
            self.setPrintText("/s 단말 리스트 정보 DataFrame으로 변환 완료 /e")
            self.df_reserved = pd.read_excel(self.input_file, sheet_name="예약어리스트", index_col=None)
            self.setPrintText("/s 예약어 리스트 정보 DataFrame으로 변환 완료 /e")
            self.df_stop = pd.read_excel(self.input_file, sheet_name="Stop word", index_col=None)
            self.setPrintText("/s STOP 리스트 정보 DataFrame으로 변환 완료 /e")
            self.df_cate_reserved = pd.read_excel(self.input_file, sheet_name="카테고리별예약어", index_col=None)
            self.setPrintText("/s 카테고리별예약어 리스트 정보 DataFrame으로 변환 완료 /e")

            # each config dataframe cover to Array list
            self.update_list = self.df_reserved["업데이트예약어"].tolist()
            self.update_list = [x for x in self.update_list if str(x) != 'nan']
            self.special_list = self.df_reserved["Special예약어"].tolist()
            self.special_list = [x for x in self.special_list if str(x) != 'nan']
            self.repeater_list = self.df_reserved["중계기예약어"].tolist()
            self.repeater_list = [x for x in self.repeater_list if str(x) != 'nan']
            self.repeater_col4_list = self.df_reserved["상담사조치4예약어(중계기)"].tolist()
            self.repeater_col4_list = [x for x in self.repeater_col4_list if str(x) != 'nan']
            self.local1_list = self.df_reserved["지역1예약어(중계기)"].tolist()
            self.local1_list = [x for x in self.local1_list if str(x) != 'nan']
            self.cate_list = self.df_reserved['선택카테고리'].tolist()
            self.cate_list = [x for x in self.cate_list if str(x) != 'nan']
            self.normal_string = self.df_stop['일반형식'].tolist()
            self.normal_string = [x for x in self.normal_string if str(x) != 'nan']

            # 최근로밍여부/T전화가입여부 값이 비어 있는 경우 값을 "N"으로 값 변경
            self.df_swing['최근로밍여부'].fillna("N", inplace=True)
            self.df_swing['T전화가입여부'].fillna("N", inplace=True)
            # self.df_swing['접수일'] = pd.to_datetime(self.df_swing['접수일'].dt.strftime('%Y-%d-%m'))
            # self.df_swing['단말기출시일'] = pd.to_datetime(self.df_swing['단말기출시일'].dt.strftime('%Y-%d-%m'))
            # self.df_swing['서비스변경일자'] = pd.to_datetime(self.df_swing['서비스변경일자'].dt.strftime('%Y-%d-%m'))

            # 카테고리별 예약어 dict 생성
            for i in range(self.df_cate_reserved.shape[0]):
                if pd.isnull(self.df_cate_reserved.at[i, "카테고리"]) or pd.isnull(self.df_cate_reserved.at[i, "정규패턴"]):
                    continue
                key = self.df_cate_reserved.at[i, "카테고리"].strip()
                value = self.df_cate_reserved.at[i, "정규패턴"].strip()
                if key not in self.cate_reserved:
                    values_list = [value]
                    self.cate_reserved[key] = values_list
                else:
                    self.cate_reserved[key].append(value)

            self.setPrintText("/s 예약어 리스트 정보 DataFrame으로 변환 완료 /e")

            # self.df_column = pd.read_excel(self.input_file, sheet_name="상담사조치분류", index_col=None)
            # self.col_index_text = self.df_column.columns.tolist()
            # self.col_text = self.col_index_text[0]
            #
            # self.counsel_list = self.df_column[self.col_text].tolist()
            # self.counsel_list = [x for x in self.counsel_list if str(x) != 'nan']
            #
            # self.setPrintText("/s 상담사조치분류 리스트 정보 DataFrame으로 변환 완료 /e")
            #############################################__progress 10%__#############################################
            self.progress_flag.emit()

            #Device Dictionary Generate
            self.setPrintText("/s Start to create device dictionary /e")
            #VOC 단말리스트 dictionary
            self.df_swing_dic = pd.Series(self.df_device["Swing_Change"].values, index=self.df_device["Swing_Origin"]).to_dict()
            self.setPrintText("/s VOC 단말 Dict 생성 완료 /e")
            #가입자정보 단말리스트 dictionary
            self.df_sub_dic = pd.Series(self.df_device["Sub_Change"].values, index=self.df_device["Sub_Origin"]).to_dict()
            self.setPrintText("/s 가입자정보 단말 Dict 생성 완료 /e")

            #가입자정보 B2B/B2C구분 "전체"만 선택
            self.df_subscriber = self.df_subscriber.loc[self.df_subscriber["B2B/B2C구분"] == "0. 전체", :]
            self.setPrintText("/s Start to match model /e")
            #############################################__progress 20%__#############################################
            self.progress_flag.emit()
            #sort column name VOC info and 가입자정보 info
            self.swing_column_list = ["네트워크본부","운용팀","운용사","서비스관리번호","접수일","접수시간","상담유형1","상담유형2","상담유형3","상담유형4",\
                                      "상담사조치1","상담사조치2","상담사조치3","상담사조치4","단말기제조사","단말기모델명","단말기코드","단말기출시일","HDVoice단말여부",\
                                      "NETWORK방식2","발생시기1","발생시기2","지역1","지역2","지역3","시/도","구/군명","요금제코드명",\
                                      "사용자AGENT","단말기애칭", "최근로밍여부", "T전화가입여부", "USIM카드명","댁내중계기여부","VOC접수번호","서비스변경일자","메모"]

            self.sub_column_list = ["일자","단말기명","전체가입자","HD-V가입자","LTE(전체(a+b))","LTE(무선모뎀제외)(a)",\
                                    "LTE무선모뎀(b)", "WCDMA전체(a+b+c+d)","WCDMA일반(a+b))","WCDMA일반(SBSM)(a)","WCDMA일반(DBDM)(b)","WCDMA무선모뎀(c+d))",\
                                    "WCDMA무선모뎀(SBSM)(c)","WCDMA무선모뎀(DBDM)(d)","CDMA전체(a+b+c+d)","2G(a)","1X합계(b+c+d)","1X(b)","EV-DO(c)",\
                                    "Video Phone(d)","와이브로","5G"]


            ########################################################################Start to generate VOC and Subscriber DateFrame########################################################################
            #put up and generate the VOC DataFrame what 상담유형1 is 통화품질, 통품외상담
            self.df_swing = self.df_swing.loc[:, self.swing_column_list]
            self.df_swing = self.df_swing.loc[(self.df_swing["상담유형1"] == "통화품질") | (self.df_swing["상담유형1"] == "통품외상담"), :]
            # 단말기모델명이 삭제 상태이면 해당 row 삭제(공통)
            self.df_swing = self.df_swing[self.df_swing['단말기모델명'].notnull()]
            #DataFrame VOC reindex(통품전체)
            self.df_swing.reset_index(drop=True, inplace=True)

            #put up and generate the 가입자정보 DataFrame by select column
            self.df_subscriber = self.df_subscriber.loc[:, self.sub_column_list]
            #DataFrame 가입자정보 reindex
            self.df_subscriber.reset_index(drop=True, inplace=True)

            self.setPrintText("/s VOC 및 가입자정보 DataFrame 구성 작업완료 /e")
            #############################################__progress 30%__#############################################
            self.progress_flag.emit()
            #Swing VOC data frame mapping Swing 단말기리스트 and present "단말기모델명2"
            self.df_swing["단말기모델명2"] = self.df_swing.단말기모델명.map(self.df_swing_dic)
            #Subscriber SKT data frame mapping Subscriber 단말기리스트 and present "단말기모델명2"
            self.df_subscriber["단말기모델명2"] = self.df_subscriber.단말기명.map(self.df_sub_dic)


            # #drop row if 단말기모델명2 column value "삭제"
            # self.df_swing = self.df_swing.loc[self.df_swing["단말기모델명2"] != "삭제",:]
            # self.df_swing = self.df_swing.reset_index(drop=True)
            # self.df_subscriber = self.df_subscriber.loc[self.df_subscriber["단말기모델명2"] != "삭제",:]
            # self.df_subscriber = self.df_subscriber.reset_index(drop=True)

            if self.mappingFlag == "y":

                #drop row if 단말기모델명2 column value "삭제"
                self.df_swing = self.df_swing.loc[self.df_swing["단말기모델명2"] != "삭제", :]
                self.df_swing.reset_index(drop=True, inplace=True)
                self.df_subscriber = self.df_subscriber.loc[self.df_subscriber["단말기모델명2"] != "삭제", :]
                self.df_subscriber.reset_index(drop=True, inplace=True)
                # drop row if 단말기모델명2 column value "신규"
                for i in range(self.df_swing.shape[0]):
                    if pd.isnull(self.df_swing.at[i, "단말기모델명2"]):
                        self.df_swing.at[i, "단말기모델명2"] = "."

                for i in range(self.df_subscriber.shape[0]):
                    if pd.isnull(self.df_subscriber.at[i, "단말기모델명2"]):
                        self.df_subscriber.at[i, "단말기모델명2"] = "."
                self.df_swing = self.df_swing.loc[self.df_swing["단말기모델명2"] != ".", :]
                self.df_subscriber = self.df_subscriber.loc[self.df_subscriber["단말기모델명2"] != ".", :]
            else:
                for i in range(self.df_swing.shape[0]):
                    if pd.isnull(self.df_swing.at[i, "단말기모델명2"]) or self.df_swing.at[i, "단말기모델명2"] == "삭제":
                        self.df_swing.at[i, "단말기모델명2"] = self.df_swing.at[i, "단말기모델명"]
                for i in range(self.df_subscriber.shape[0]):
                    if pd.isnull(self.df_subscriber.at[i, "단말기모델명2"]) or self.df_subscriber.at[i, "단말기모델명2"] == "삭제":
                        self.df_subscriber.at[i, "단말기모델명2"] = self.df_subscriber.at[i, "단말기명"]

            self.df_swing.reset_index(drop=True, inplace=True)
            self.df_subscriber.reset_index(drop=True, inplace=True)

            #Monitoring Select Device to list
            self.select_list = []
            if self.mappingFlag == "y":
                self.select_list = self.df_device["SelectModel"].tolist()
                self.select_list = [x for x in self.select_list if str(x) != 'nan']
                #change select_list items to lower word
                for i in range(len(self.select_list)):
                    self.select_list[i] = self.select_list[i].lower() #.replace(" ","")
            else:
                # df_swing의 단말기모델명에서 중복을 제거하고 고유의 값을 추출 후 select_list로 import
                self.select_list = list(set(self.df_swing["단말기모델명"].tolist()))
                self.select_list = [x for x in self.select_list if str(x) != 'nan']
                #change select_list items to lower word
                for i in range(len(self.select_list)):
                    self.select_list[i] = self.select_list[i].lower() #.replace(" ","")

            #Mapping Device extract model and model2
            self.mapping_models = list(set(self.df_swing["단말기모델명"].tolist()))
            self.mapping_models2 = list(set(self.df_swing["단말기모델명2"].tolist()))

            #mapping lunchDate
            for item in self.mapping_models:
                temp_data = self.df_swing.loc[self.df_swing['단말기모델명'] == item, ['단말기출시일', 'NETWORK방식2', '단말기제조사']]
                launch_data = temp_data['단말기출시일'].min()
                launch_data = pd.to_datetime(launch_data, unit='ns')
                launch_data = launch_data.strftime("%Y-%m-%d")
                network_data = temp_data['NETWORK방식2'].iloc[0]
                manufact_data = temp_data['단말기제조사'].iloc[0]
                self.launch_model.append(launch_data)
                self.network_model.append(network_data)
                self.manufact_model.append(manufact_data)

            #mapping lunchDate
            for item in self.mapping_models2:
                temp_data = self.df_swing.loc[self.df_swing['단말기모델명2'] == item, ['단말기출시일', 'NETWORK방식2', '단말기제조사']]
                launch_data = temp_data['단말기출시일'].min()
                launch_data = pd.to_datetime(launch_data, unit='ns')
                launch_data = launch_data.strftime("%Y-%m-%d")
                network_data = temp_data['NETWORK방식2'].iloc[0]
                manufact_data = temp_data['단말기제조사'].iloc[0]
                self.launch_model2.append(launch_data)
                self.network_model2.append(network_data)
                self.manufact_model2.append(manufact_data)


            #get subscibe date and change format %Y-%m-%d
            self.df_subscriber.sort_values(by=['일자'], axis=0, ascending=False, inplace=True)
            self.df_subscriber.reset_index(drop=True, inplace=True)
            self.sb_dateText = str(self.df_subscriber.at[2, "일자"])
            self.sb_date = datetime.strptime(self.sb_dateText, "%Y%m%d")
            self.subscribe_date = datetime.strftime(self.sb_date, "%Y-%m-%d")

            #전체가입자 각 모델별 고유번호 입력
            self.df_subscriber["고유번호"] = ""
            self.charset = string.ascii_uppercase + string.digits
            for i in range(self.df_subscriber.shape[0]):
                self.uniqueId = ''.join(random.sample(self.charset*15,15))
                self.df_subscriber.at[i, "고유번호"] = self.uniqueId

            self.setPrintText("/s VOC 및 가입자정보 DataFrame 단말명 Matching 작업 완료 /e")
            ########################################################################Start to generate 불만성유형  DateFrame########################################################################
            self.setPrintText("/s Start to create the \"불만성유형\" DataFrame /e")
            #############################################__progress 40%__#############################################
            self.progress_flag.emit()
            #Add swing columns
            self.df_swing["메모요약"] = ""
            self.df_swing["메모분류"] = ""
            self.df_swing["업데이트 유무"] = ""
            self.df_swing["소프트웨어"] = ""
            self.df_swing["추출단어"] = ""
            self.df_swing["이슈번호"] = ""
            self.setPrintText("/s VOC 전체 메모정보 요약 및 카테고리 작업 중 /e")

            # 분석대상 행 개수 체크
            self.totalRows = self.df_swing.shape[0]
            self.df_swing = self.analysis_data(self.df_swing, self.update_list, self.special_list, self.repeater_list,
                                               self.repeater_col4_list, self.local1_list)
            # self.df_swing.sort_values(by=["단말기모델명2"], axis=0, inplace=True)
            self.df_swing.reset_index(drop=True, inplace=True)


            #############################################__progress 50%__#############################################
            self.progress_flag.emit()
            #Select 단말설정 기타안내 in 상담유형3
            # self.df_keyword_temp1 = self.df_swing.loc[self.df_swing["상담유형2"] == "단말-설정" ,:]
            self.df_keyword = self.df_swing.loc[(self.df_swing["상담유형2"] == "HD Voice품질")|(self.df_swing["상담유형2"] == "단말-설정")|(self.df_swing["상담유형2"] == "WiFi품질")|\
            (self.df_swing["상담유형2"] == "데이터품질")|(self.df_swing["상담유형2"] == "부가서비스")|(self.df_swing["상담유형2"] == "영상품질")|(self.df_swing["상담유형2"] == "음성품질")|\
            (self.df_swing["상담유형2"] == "제도/프로세스"), :]


            # self.df_keyword = pd.concat([self.df_keyword_temp1, self.df_keyword_temp2])
            self.df_keyword.reset_index(drop=True, inplace=True)

            #Light and Heavy analysis flag
            self.tot_count = self.df_swing.shape[0]
            self.df_swing = self.df_swing[["네트워크본부", "운용팀", "운용사", "서비스관리번호", "접수일", "접수시간", "상담유형1", "상담유형2", "상담유형3", "상담유형4", "상담사조치1",\
                                           "상담사조치2", "상담사조치3", "상담사조치4", "단말기제조사", "단말기모델명", "단말기모델명2", "단말기코드", "단말기출시일", "HDVoice단말여부", "NETWORK방식2",\
                                           "발생시기1", "발생시기2", "지역1", "지역2", "지역3", "시/도", "구/군명", "요금제코드명", "사용자AGENT", "단말기애칭", "최근로밍여부", "T전화가입여부",\
                                           "USIM카드명", "댁내중계기여부", "VOC접수번호", "서비스변경일자", "메모", "메모요약", "메모분류", "업데이트 유무", "소프트웨어", "추출단어", "이슈번호"]]

            self.df_keyword = self.df_keyword[["네트워크본부", "운용팀", "운용사", "서비스관리번호", "접수일", "접수시간", "상담유형1", "상담유형2", "상담유형3", "상담유형4", "상담사조치1",\
                                           "상담사조치2", "상담사조치3", "상담사조치4", "단말기제조사", "단말기모델명", "단말기모델명2", "단말기코드", "단말기출시일", "HDVoice단말여부", "NETWORK방식2",\
                                           "발생시기1", "발생시기2", "지역1", "지역2", "지역3", "시/도", "구/군명", "요금제코드명", "사용자AGENT", "단말기애칭", "최근로밍여부", "T전화가입여부",\
                                           "USIM카드명", "댁내중계기여부", "VOC접수번호", "서비스변경일자", "메모", "메모요약", "메모분류", "업데이트 유무", "소프트웨어", "추출단어", "이슈번호"]]

            self.df_subscriber = self.df_subscriber[["일자", "단말기명", "단말기모델명2", "전체가입자", "HD-V가입자", "LTE(전체(a+b))", "LTE(무선모뎀제외)(a)",\
                                                     "LTE무선모뎀(b)", "WCDMA전체(a+b+c+d)", "WCDMA일반(a+b))", "WCDMA일반(SBSM)(a)", "WCDMA일반(DBDM)(b)", "WCDMA무선모뎀(c+d))",\
                                                     "WCDMA무선모뎀(SBSM)(c)", "WCDMA무선모뎀(DBDM)(d)", "CDMA전체(a+b+c+d)", "2G(a)", "1X합계(b+c+d)", "1X(b)","EV-DO(c)",\
                                                     "Video Phone(d)", "와이브로", "5G", "고유번호"]]

            self.setPrintText("/s 불만성유형 DataFrame 상담유형 및 상담사조치 분류 작업 완료 /e")
            #############################################__progress 60%__#############################################
            self.progress_flag.emit()
            self.setPrintText("/s Start to create the \"단말별종합결과\" DataFrame /e")
            #Generates self.sheet3 dataFrame
            self.data = {}
            self.select_point_total = []
            self.select_point_keyword = []
            self.select_sum_sub = []
            self.select_manu_list = []
            self.devices_swing_list = []
            self.devices_keyword_list = []
            self.df_swing_select = None
            self.df_keyword_select = None

            ########################################################################Start to generate Count DateFrame########################################################################
            if self.mappingFlag == "y":
                self.df_swing["단말기모델명2"] = self.df_swing["단말기모델명2"].str.lower()
                self.df_keyword["단말기모델명2"] = self.df_keyword["단말기모델명2"].str.lower()
                self.df_subscriber["단말기모델명2"] = self.df_subscriber["단말기모델명2"].str.lower()
                self.devices_swing_list = self.df_swing["단말기모델명2"].tolist()
                self.devices_keyword_list = self.df_keyword["단말기모델명2"].tolist()
            else:
                self.df_swing["단말기모델명"] = self.df_swing["단말기모델명"].str.lower()
                self.df_keyword["단말기모델명"] = self.df_keyword["단말기모델명"].str.lower()
                self.df_subscriber["단말기명"] = self.df_subscriber["단말기명"].str.lower()
                self.devices_swing_list = self.df_swing["단말기모델명"].tolist()
                self.devices_keyword_list = self.df_keyword["단말기모델명"].tolist()

            #1000명당 통계를 위해 최신 날짜의 가입자 정보만 들어 있는 DataFrame 추출 후 df_subscriber_recent에 저장
            self.recent_date = self.df_subscriber.at[2, "일자"]
            self.df_subscriber_recent = self.df_subscriber.loc[self.df_subscriber['일자'] == self.recent_date, :]


            self.setPrintText("/s Select Device 통계 계산 작업중 /e")
            for item in self.select_list:
                self.temp_swing = self.devices_swing_list.count(item)
                self.temp_keyword = self.devices_keyword_list.count(item)
                self.select_point_total.append(self.temp_swing)
                self.select_point_keyword.append(self.temp_keyword)

            # ####################################### 모니터링 대상 단말에 대한 Swing/keyword DataFrame Generate#####################################

            if self.mappingFlag == "y":
                self.df_swing_select = self.df_swing
                self.df_keyword_select = self.df_keyword
                for i in range(self.df_swing_select.shape[0]):
                    if self.df_swing_select.at[i,"단말기모델명2"] not in self.select_list:
                        self.df_swing_select = self.df_swing_select.drop(i,0)
                self.df_swing_select.reset_index(drop=True, inplace=True)

                for i in range(self.df_keyword_select.shape[0]):
                    if self.df_keyword_select.at[i,"단말기모델명2"] not in self.select_list:
                        self.df_keyword_select = self.df_keyword_select.drop(i,0)
                self.df_keyword_select.reset_index(drop=True, inplace=True)
                # #####################################################################################################################################
                # Select Manufacture device put in list
                for item in self.select_list:
                    self.df_temp = self.df_swing.loc[self.df_swing["단말기모델명2"] == item ,["단말기제조사"]]
                    self.df_temp.reset_index(drop=True, inplace=True)
                    if not self.df_temp.empty:
                        self.manuString = self.df_temp.at[0,"단말기제조사"]
                        self.select_manu_list.append(self.manuString)
                    else:
                        self.select_manu_list.append("VOC 정보 없음")
            else:
                self.df_swing_select = self.df_swing
                self.df_keyword_select = self.df_keyword
                for i in range(self.df_swing_select.shape[0]):
                    if self.df_swing_select.at[i,"단말기모델명"] not in self.select_list:
                        self.df_swing_select = self.df_swing_select.drop(i,0)
                self.df_swing_select.reset_index(drop=True, inplace=True)

                for i in range(self.df_keyword_select.shape[0]):
                    if self.df_keyword_select.at[i,"단말기모델명"] not in self.select_list:
                        self.df_keyword_select = self.df_keyword_select.drop(i,0)
                self.df_keyword_select.reset_index(drop=True, inplace=True)
                # #####################################################################################################################################
                # Select Manufacture device put in list
                for item in self.select_list:
                    self.df_temp = self.df_swing.loc[self.df_swing["단말기모델명"] == item ,["단말기제조사"]]
                    self.df_temp.reset_index(drop=True, inplace=True)
                    if not self.df_temp.empty:
                        self.manuString = self.df_temp.at[0,"단말기제조사"]
                        self.select_manu_list.append(self.manuString)
                    else:
                        self.select_manu_list.append("VOC 정보 없음")


            self.data = {"단말리스트": self.select_list,\
                         "단말기제조사": self.select_manu_list,\
                         "통품전체": self.select_point_total,\
                         "불만성유형": self.select_point_keyword}

            self.df_count = pd.DataFrame(self.data)
            self.df_count.sort_index(axis=1, ascending=False)
            self.dev_model_list = self.df_count["단말리스트"].tolist()

            self.df_count["전체가입자"] = ""
            self.df_count["통품 1000명당 건수"] = ""
            self.df_count["불만성 1000명당 건수"] = ""
            self.df_count["일자"] = self.subscribe_date

            #subscriber count by device model
            if self.mappingFlag == "y":

                for item in self.select_list:
                    self.df_temp_sub = self.df_subscriber_recent.loc[self.df_subscriber_recent["단말기모델명2"] == item , ["전체가입자","HD-V가입자","LTE(전체(a+b))"]]
                    self.temp_list = self.df_temp_sub["전체가입자"].tolist()
                    self.temp_sum = sum(self.temp_list, 0)
                    self.select_sum_sub.append(self.temp_sum)
            else:

                for item in self.select_list:
                    self.df_temp_sub = self.df_subscriber_recent.loc[self.df_subscriber_recent["단말기명"] == item , ["전체가입자","HD-V가입자","LTE(전체(a+b))"]]
                    self.temp_list = self.df_temp_sub["전체가입자"].tolist()
                    self.temp_sum = sum(self.temp_list, 0)
                    self.select_sum_sub.append(self.temp_sum)

            for i in range(len(self.select_sum_sub)):
                self.df_count.at[i,"전체가입자"] = self.select_sum_sub[i]
            # self.df_count["전체가입자"] = self.select_sum_sub

            #calurating count rate per 1000 subscriber
            for i in range(len(self.select_sum_sub)):
                if self.select_sum_sub[i] > 0.0 and float(self.df_count.at[i,"통품전체"]) > 0.0:
                    self.temp_rate = (float(self.df_count.at[i,"통품전체"]) / float(self.select_sum_sub[i]))*1000
                    self.df_count.at[i,"통품 1000명당 건수"] = round(self.temp_rate, 3)
                else:
                    self.df_count.at[i,"통품 1000명당 건수"] = 0.0

            for i in range(len(self.select_sum_sub)):
                if self.select_sum_sub[i] > 0.0 and float(self.df_count.at[i,"불만성유형"]) > 0.0:
                    self.temp_rate = (float(self.df_count.at[i,"불만성유형"]) / float(self.select_sum_sub[i]))*1000
                    self.df_count.at[i,"불만성 1000명당 건수"] = round(self.temp_rate, 3)
                else:
                    self.df_count.at[i,"불만성 1000명당 건수"] = 0.0

            self.setPrintText("/s Select Device 통계 계산 작업 완료 /e")
            #Light and Heavy analysis flag
            self.setPrintText("/s Select Device 메모 카테고리 및 키워드 통계 계산 작업중 /e")

            self.df_count["키워드 TOP20(통품전체)"] = ""
            self.df_count["키워드 TOP20(불만성유형)"] = ""
            self.df_count["카테고리분류(통품전체)"] = ""
            self.df_count["카테고리분류(불만성유형)"] = ""


            #keyword top 20 in swing VOC
            self.dev_memo_list = []
            if self.mappingFlag == "y":
                for item in self.dev_model_list:
                    self.df_temp = self.df_swing.loc[self.df_swing["단말기모델명2"] == item , ["추출단어"]]
                    self.temp_list = self.df_temp["추출단어"].tolist()
                    self.dev_memo_list.append(self.temp_list)
            else:
                for item in self.dev_model_list:
                    self.df_temp = self.df_swing.loc[self.df_swing["단말기모델명"] == item , ["추출단어"]]
                    self.temp_list = self.df_temp["추출단어"].tolist()
                    self.dev_memo_list.append(self.temp_list)

            for i in range(self.df_count.shape[0]):
                self.dict_keyCount = {}
                if len(self.dev_memo_list[i]) > 0:
                    for item in self.dev_memo_list[i]:
                        self.item2_list = item.split(",")
                        for item2 in self.item2_list:
                            if not item2 in self.dict_keyCount and not len(item2) < 2:
                                self.dict_keyCount[item2] = 1
                            elif item2 in self.dict_keyCount and not len(item2) < 2:
                                self.dict_keyCount[item2] = self.dict_keyCount[item2]+1
                            else:
                                continue
                    self.dict_keyList = sorted(self.dict_keyCount.items(), key=lambda x: x[1], reverse=True)
                    self.dict_keyList = self.dict_keyList[:20]
                    # self.item_list = []
                    # for i in range(10):
                    #     self.item_list.append(self.dict_keyList[i])
                    self.text_value = ""
                    for item in self.dict_keyList:
                        self.text_value = self.text_value+" "+str(item[0])+":"+str(item[1])+"\n"
                    self.df_count.at[i,"키워드 TOP20(통품전체)"] = self.text_value
                else:
                    continue

            #keyword top 20 in keyword VOC
            self.dev_memo_list = []
            if self.mappingFlag == "y":
                for item in self.dev_model_list:
                    self.df_temp = self.df_keyword.loc[self.df_keyword["단말기모델명2"] == item , ["추출단어"]]
                    self.temp_list = self.df_temp["추출단어"].tolist()
                    self.dev_memo_list.append(self.temp_list)
            else:
                for item in self.dev_model_list:
                    self.df_temp = self.df_keyword.loc[self.df_keyword["단말기모델명"] == item , ["추출단어"]]
                    self.temp_list = self.df_temp["추출단어"].tolist()
                    self.dev_memo_list.append(self.temp_list)

            for i in range(self.df_count.shape[0]):
                self.dict_keyCount = {}
                if len(self.dev_memo_list[i]) > 0:
                    for item in self.dev_memo_list[i]:
                        self.item2_list = item.split(",")
                        for item2 in self.item2_list:
                            if not item2 in self.dict_keyCount and not len(item2) < 2:
                                self.dict_keyCount[item2] = 1
                            elif item2 in self.dict_keyCount and not len(item2) < 2:
                                self.dict_keyCount[item2] = self.dict_keyCount[item2]+1
                            else:
                                continue
                    self.dict_keyList = sorted(self.dict_keyCount.items(), key=lambda x: x[1], reverse=True)
                    self.dict_keyList = self.dict_keyList[:20]
                    # self.item_list = []
                    # for i in range(10):
                    #     self.item_list.append(self.dict_keyList[i])
                    self.text_value = ""
                    for item in self.dict_keyList:
                        self.text_value = self.text_value+" "+str(item[0])+":"+str(item[1])+"\n"
                    self.df_count.at[i,"키워드 TOP20(불만성유형)"] = self.text_value
                else:
                    continue

            # keyword memo df_swing and df_keyword data sum count
            for i in range(self.df_count.shape[0]):
                self.countKeys1 = {}
                self.countKeys2 = {}
                for item2 in self.cate_list:
                    self.df_temp = None
                    self.df_temp2 = None
                    if self.mappingFlag == "y":
                        self.df_temp = self.df_swing.loc[(self.df_swing["단말기모델명2"] == self.df_count.at[i, "단말리스트"]) & (self.df_swing["메모분류"] == item2), ["단말기모델명2", "메모분류"]]
                        self.df_temp2 = self.df_keyword.loc[(self.df_keyword["단말기모델명2"] == self.df_count.at[i,"단말리스트"]) & (self.df_keyword["메모분류"] == item2), ["단말기모델명2", "메모분류"]]
                    else:
                        self.df_temp = self.df_swing.loc[(self.df_swing["단말기모델명"] == self.df_count.at[i, "단말리스트"]) & (self.df_swing["메모분류"] == item2), ["단말기모델명", "메모분류"]]
                        self.df_temp2 = self.df_keyword.loc[(self.df_keyword["단말기모델명"] == self.df_count.at[i, "단말리스트"]) & (self.df_keyword["메모분류"] == item2), ["단말기모델명", "메모분류"]]

                    if not self.df_temp.empty:
                        self.countKeys1[item2] = self.df_temp.shape[0]
                    else:
                        self.countKeys1[item2] = 0
                    if not self.df_temp2.empty:
                        self.countKeys2[item2] = self.df_temp2.shape[0]
                    else:
                        self.countKeys2[item2] = 0

                self.count_item1 = len(self.countKeys1.items())
                self.tuple_item1 = list(self.countKeys1.items())
                self.tuple_item1 = sorted(self.tuple_item1, key=itemgetter(1), reverse=True)

                self.j = 0
                for (x, y) in self.tuple_item1:
                    if not self.j == self.count_item1-1 and self.df_count.at[i, "카테고리분류(통품전체)"] == "":
                        if y is not 0:
                            self.per = round((y/int(self.df_count.at[i, "통품전체"]))*100, 2)
                            self.df_count.at[i, "카테고리분류(통품전체)"] = str(x)+": "+str(y)+"\n"
                        else:
                            self.df_count.at[i, "카테고리분류(통품전체)"] = str(x)+": "+str(y)+"\n"
                    else:
                        if y is not 0:
                            self.per = round((y / int(self.df_count.at[i,"통품전체"])) * 100, 2)
                            self.df_count.at[i, "카테고리분류(통품전체)"] = self.df_count.at[i, "카테고리분류(통품전체)"]+str(x)+": "+str(y) + "\n"
                        else:
                            self.df_count.at[i, "카테고리분류(통품전체)"] = self.df_count.at[i, "카테고리분류(통품전체)"]+str(x)+": "+str(y) + "\n"
                    self.j = self.j+1

                self.count_item2 = len(self.countKeys2.items())
                self.tuple_item2 = list(self.countKeys2.items())
                self.tuple_item2 = sorted(self.tuple_item2, key=itemgetter(1), reverse=True)
                self.j = 0
                for (x,y) in self.tuple_item2:
                    if not self.j == self.count_item2-1 and self.df_count.at[i,"카테고리분류(불만성유형)"] == "":
                        if y is not 0:
                            self.per = round((y / int(self.df_count.at[i,"불만성유형"])) * 100, 2)
                            self.df_count.at[i,"카테고리분류(불만성유형)"] = str(x)+": "+str(y)+"\n"
                        else:
                            self.df_count.at[i,"카테고리분류(불만성유형)"] = str(x)+": "+str(y)+"\n"

                    else:
                        if y is not 0:
                            self.per = round((y / int(self.df_count.at[i,"불만성유형"])) * 100, 2)
                            self.df_count.at[i,"카테고리분류(불만성유형)"] = self.df_count.at[i,"카테고리분류(불만성유형)"]+str(x)+": "+str(y)+"\n"
                        else:
                            self.df_count.at[i,"카테고리분류(불만성유형)"] = self.df_count.at[i,"카테고리분류(불만성유형)"]+str(x)+": "+str(y)+"\n"
                    self.j = self.j+1

            self.df_count = self.df_count[["일자", "단말리스트", "단말기제조사", "통품전체", "불만성유형", "전체가입자", "통품 1000명당 건수", "불만성 1000명당 건수", "키워드 TOP20(통품전체)",\
                                        "키워드 TOP20(불만성유형)","카테고리분류(통품전체)", "카테고리분류(불만성유형)"]]
            self.setPrintText("/s Select Device 메모 카테고리 및 키워드 통계 계산 작업 완료 /e")

            #############################################__progress 70%__#############################################
            self.progress_flag.emit()
            #concat dataFrame df_count and df_counsel
            self.setPrintText("/s Select Device 선택 필드 통계 계산 작업중 /e")
            # self.df_counsel = pd.DataFrame()
            # for item in self.counsel_list:
            #     self.df_counsel[item] = ""

            for i in range(len(self.select_list)):
                self.device_name = self.select_list[i]
                self.df_temp_tot = None
                self.df_temp_tr = None

                if self.mappingFlag == "y":
                    self.df_temp_tot = self.df_swing.loc[(self.df_swing["단말기모델명2"] == self.device_name), :]
                    self.df_temp_tr = self.df_keyword.loc[(self.df_keyword["단말기모델명2"] == self.device_name), :]
                else:
                    self.df_temp_tot = self.df_swing.loc[(self.df_swing["단말기모델명"] == self.device_name), :]
                    self.df_temp_tr = self.df_keyword.loc[(self.df_keyword["단말기모델명"] == self.device_name), :]

            self.setPrintText("/s Select Device 선택 필드 통계 계산 작업 완료 /e")
            self.setPrintText("/s Finish to create the \"단말별종합결과\" DataFrame /e")

            ########################################################################Start to generate Summary DateFrame########################################################################
            self.setPrintText("/s Start to create the \"전체종합결과\" DataFrame /e")
            #가입자 정보에서 최신 날짜의 데이터만 가져온다
            self.tot_sub_sum = self.df_subscriber_recent["전체가입자"].sum()
            self.tot_voc_count1 = self.df_swing.shape[0]
            self.tot_voc_count2 = self.df_keyword.shape[0]
            self.tot_voc_select1 = self.df_swing_select.shape[0]
            self.tot_voc_select2 = self.df_keyword_select.shape[0]

            #dataFrame summary
            self.dataSummary = {"총 가입자": [self.tot_sub_sum],\
                                "전체단말 VOC건수(통품전체)": [self.tot_voc_count1],\
                                "전체단말 VOC건수(불만성유형)": [self.tot_voc_count2],\
                                "자사단말 VOC건수(통품전체)": [self.tot_voc_select1],\
                                "자사단말 VOC건수(불만성유형)": [self.tot_voc_select2],\
                                "전체 VOC_Rate(통품전체)": [round((self.tot_voc_count1 / self.tot_sub_sum) * 1000, 3)],\
                                "전체 VOC_Rate(불만성유형)": [round((self.tot_voc_count2 / self.tot_sub_sum) * 1000, 3)],\
                                "자사단말 VOC_Rate(통품전체)": [round((self.tot_voc_select1 / self.tot_sub_sum) * 1000, 3)],\
                                "자사단말 VOC_Rate(불만성유형)": [round((self.tot_voc_select2 / self.tot_sub_sum) * 1000, 3)]
                                }

            self.df_summary = pd.DataFrame(self.dataSummary)
            self.setPrintText("/s Summary 통계 계산 작업 완료 /e")
            #############################################__progress 80%__#############################################
            self.progress_flag.emit()
            #analysis summary voc memo top keyword
            self.keyword_tot1 = ""
            self.keyword_tot2 = ""
            self.rank_dict1 = {}
            self.rank_dict2 = {}
            self.rank_items1 = []
            self.rank_items2 = []
            self.keyword_sum1 = self.df_count["키워드 TOP20(통품전체)"].tolist()
            self.keyword_sum2 = self.df_count["키워드 TOP20(불만성유형)"].tolist()

            #df_count 모델별 통품전체 키워드 Sum 후 키워드 랭크
            for item in self.keyword_sum1:
                if len(item) > 0:
                    self.temp_list = item.split("\n")
                    self.temp_list = self.temp_list[:len(self.temp_list)-1]
                    for item2 in self.temp_list:
                        self.item_list = item2.split(":")
                        self.item_list[0] = self.item_list[0].replace(" ","")
                        self.item_list[1] = self.item_list[1].replace(" ","")
                        if not self.item_list[0] in self.rank_dict1:
                            self.rank_dict1[self.item_list[0]] = int(self.item_list[1])
                        elif self.item_list[0] in self.rank_dict1:
                            self.rank_dict1[self.item_list[0]] = int(self.rank_dict1[self.item_list[0]]) + int(self.item_list[1])
                        else:
                            continue
                else:
                    continue

            #df_count 모델별 불만성유형 키워드 Sum 후 키워드 랭크
            for item in self.keyword_sum2:
                if len(item) > 0:
                    self.temp_list = item.split("\n")
                    self.temp_list = self.temp_list[:len(self.temp_list)-1]
                    for item2 in self.temp_list:
                        self.item_list = item2.split(":")
                        self.item_list[0] = self.item_list[0].replace(" ","")
                        self.item_list[1] = self.item_list[1].replace(" ","")
                        if not self.item_list[0] in self.rank_dict2:
                            self.rank_dict2[self.item_list[0]] = int(self.item_list[1])
                        elif self.item_list[0] in self.rank_dict2:
                            self.rank_dict2[self.item_list[0]] = int(self.rank_dict2[self.item_list[0]]) + int(self.item_list[1])
                        else:
                            continue
                else:
                    continue

            # 통품전체 / 불만성유형 순위 값 dict 정렬
            self.rank_items1 = sorted(self.rank_dict1.items(), key=lambda x:x[1], reverse=True)
            self.rank_items2 = sorted(self.rank_dict2.items(), key=lambda x:x[1], reverse=True)
            # items tuple list

            self.rank_items1 = self.rank_items1[:20]
            self.rank_items2 = self.rank_items2[:20]
            # 통품전체 / 불만성유형 extract 된 tuple 값 string으로 변환
            for item in self.rank_items1:
                self.keyword_tot1 = self.keyword_tot1+" "+str(item[0])+":"+str(item[1])+"\n"

            for item in self.rank_items2:
                self.keyword_tot2 = self.keyword_tot2+" "+str(item[0])+":"+str(item[1])+"\n"


            self.df_summary["키워드 Top 20(통품전체)"] = [self.keyword_tot1]
            self.df_summary["키워드 Top 20(불만성유형)"] = [self.keyword_tot2]
            # 전체 모델에 대한 통계
            self.df_summary["카테고리분류(통품전체)"] = ""
            self.df_summary["카테고리분류(불만성유형)"] = ""
            # Select 모델에 대한 통계
            self.df_summary["자사단말 카테고리분류(통품전체)"] = ""
            self.df_summary["자사단말 카테고리분류(불만성유형)"] = ""

            # 전체 카테고리분류 계산
            self.list_tot_count = []
            self.list_dev_count = []
            # self.text_tot_count = ""
            # self.text_dev_count = ""
            self.list_tot_select = []
            self.list_dev_select = []
            # self.text_tot_select = ""
            # self.text_dev_select = ""

            # 전체/ Select 모델의 값에 대한 통계
            for item in self.cate_list:

                self.df_temp1 = self.df_swing.loc[self.df_swing["메모분류"] == item,:]
                self.df_temp2 = self.df_keyword.loc[self.df_keyword["메모분류"] == item,:]
                self.df_temp3 = self.df_swing_select.loc[self.df_swing_select["메모분류"] == item,:]
                self.df_temp4 = self.df_keyword_select.loc[self.df_keyword_select["메모분류"] == item,:]
                # 전체모델
                self.count_temp1 = self.df_temp1.shape[0]
                self.count_temp2 = self.df_temp2.shape[0]
                self.list_tot_count.append((item, self.count_temp1))
                self.list_dev_count.append((item, self.count_temp2))

                # Select 모델
                self.count_temp3 = self.df_temp3.shape[0]
                self.count_temp4 = self.df_temp4.shape[0]
                self.list_tot_select.append((item, self.count_temp3))
                self.list_dev_select.append((item, self.count_temp4))

            # 내림차순 정렬
            self.list_tot_count = sorted(self.list_tot_count, key=itemgetter(1), reverse=True)
            self.list_dev_count = sorted(self.list_dev_count, key=itemgetter(1), reverse=True)
            self.list_tot_select = sorted(self.list_tot_select, key=itemgetter(1), reverse=True)
            self.list_dev_select = sorted(self.list_dev_select, key=itemgetter(1), reverse=True)

            # 전체 값에 대한 통계
            # for i in range(len(self.list_tot_count)):
            #     if self.list_tot_count[i] is not 0:
            #         self.per = round((self.list_tot_count[i] / self.tot_voc_count1) * 100, 2)
            #         self.text_tot_count = self.text_tot_count + self.cate_list[i]+" : "+str(self.list_tot_count[i])+" ("+str(self.per)+"%)\n"
            #     else:
            #         self.text_tot_count = self.text_tot_count + self.cate_list[i]+" : "+str(self.list_tot_count[i])+" (0.0%)\n"

            self.j = 0
            self.count_item = len(self.list_tot_count)
            for (x,y) in self.list_tot_count:
                if not self.j == self.count_item-1 and self.df_summary.at[0,"카테고리분류(통품전체)"] == "":
                    if y is not 0:
                        self.per = round((y / int(self.df_summary.at[0,"전체단말 VOC건수(통품전체)"]))*100,2)
                        self.df_summary.at[0,"카테고리분류(통품전체)"] = str(x)+": "+str(y)+" ("+str(self.per)+"%)\n"
                    else:
                        self.df_summary.at[0,"카테고리분류(통품전체)"] = str(x)+": "+str(y)+" (0.0%)\n"
                else:
                    if y is not 0:
                        self.per = round((y / int(self.df_summary.at[0,"전체단말 VOC건수(통품전체)"])) * 100, 2)
                        self.df_summary.at[0,"카테고리분류(통품전체)"] = self.df_summary.at[0,"카테고리분류(통품전체)"]+str(x)+": "+str(y)+" ("+str(self.per)+"%)\n"
                    else:
                        self.df_summary.at[0,"카테고리분류(통품전체)"] = self.df_summary.at[0,"카테고리분류(통품전체)"]+str(x)+": "+str(y)+" (0.0%)\n"
                self.j = self.j+1

            self.j = 0
            self.count_item = len(self.list_dev_count)
            for (x,y) in self.list_dev_count:
                if not self.j == self.count_item-1 and self.df_summary.at[0,"카테고리분류(불만성유형)"] == "":
                    if y is not 0:
                        self.per = round((y / int(self.df_summary.at[0,"전체단말 VOC건수(불만성유형)"]))*100,2)
                        self.df_summary.at[0,"카테고리분류(불만성유형)"] = str(x)+": "+str(y)+" ("+str(self.per)+"%)\n"
                    else:
                        self.df_summary.at[0,"카테고리분류(불만성유형)"] = str(x)+": "+str(y)+" (0.0%)\n"
                else:
                    if y is not 0:
                        self.per = round((y / int(self.df_summary.at[0,"전체단말 VOC건수(불만성유형)"])) * 100, 2)
                        self.df_summary.at[0,"카테고리분류(불만성유형)"] = self.df_summary.at[0,"카테고리분류(불만성유형)"]+str(x)+": "+str(y)+" ("+str(self.per)+"%)\n"
                    else:
                        self.df_summary.at[0,"카테고리분류(불만성유형)"] = self.df_summary.at[0,"카테고리분류(불만성유형)"]+str(x)+": "+str(y)+" (0.0%)\n"
                self.j = self.j+1

            self.j = 0
            self.count_item = len(self.list_tot_select)
            for (x,y) in self.list_tot_select:
                if not self.j == self.count_item-1 and self.df_summary.at[0,"자사단말 카테고리분류(통품전체)"] == "":
                    if y is not 0:
                        self.per = round((y / int(self.df_summary.at[0,"자사단말 VOC건수(통품전체)"]))*100,2)
                        self.df_summary.at[0,"자사단말 카테고리분류(통품전체)"] = str(x)+": "+str(y)+" ("+str(self.per)+"%)\n"
                    else:
                        self.df_summary.at[0,"자사단말 카테고리분류(통품전체)"] = str(x)+": "+str(y)+" (0.0%)\n"
                else:
                    if y is not 0:
                        self.per = round((y / int(self.df_summary.at[0,"자사단말 VOC건수(통품전체)"])) * 100, 2)
                        self.df_summary.at[0,"자사단말 카테고리분류(통품전체)"] = self.df_summary.at[0,"자사단말 카테고리분류(통품전체)"]+str(x)+": "+str(y)+" ("+str(self.per)+"%)\n"
                    else:
                        self.df_summary.at[0,"자사단말 카테고리분류(통품전체)"] = self.df_summary.at[0,"자사단말 카테고리분류(통품전체)"]+str(x)+": "+str(y)+" (0.0%)\n"
                self.j = self.j+1


            self.j = 0
            self.count_item = len(self.list_dev_select)
            for (x,y) in self.list_dev_select:
                if not self.j == self.count_item-1 and self.df_summary.at[0,"자사단말 카테고리분류(불만성유형)"] == "":
                    if y is not 0:
                        self.per = round((y / int(self.df_summary.at[0,"자사단말 VOC건수(불만성유형)"]))*100,2)
                        self.df_summary.at[0,"자사단말 카테고리분류(불만성유형)"] = str(x)+": "+str(y)+" ("+str(self.per)+"%)\n"
                    else:
                        self.df_summary.at[0,"자사단말 카테고리분류(불만성유형)"] = str(x)+": "+str(y)+" (0.0%)\n"
                else:
                    if y is not 0:
                        self.per = round((y / int(self.df_summary.at[0,"자사단말 VOC건수(불만성유형)"])) * 100, 2)
                        self.df_summary.at[0,"자사단말 카테고리분류(불만성유형)"] = self.df_summary.at[0,"자사단말 카테고리분류(불만성유형)"]+str(x)+": "+str(y)+" ("+str(self.per)+"%)\n"
                    else:
                        self.df_summary.at[0,"자사단말 카테고리분류(불만성유형)"] = self.df_summary.at[0,"자사단말 카테고리분류(불만성유형)"]+str(x)+": "+str(y)+" (0.0%)\n"
                self.j = self.j+1

            # 전체 모델에 대한 통계
            # self.df_summary["카테고리분류(통품전체)"] = [self.text_tot_count]
            # self.df_summary["카테고리분류(불만성유형)"] = [self.text_dev_count]
            # Select 모델에 대한 통계
            # self.df_summary["자사단말 카테고리분류(통품전체)"] = [self.text_tot_select]
            # self.df_summary["자사단말 카테고리분류(불만성유형)"] = [self.text_dev_select]
            self.setPrintText("/s Summary 메모 카테고리 및 키워드 통계 계산 작업 완료 /e")


            #sorting columns
            self.df_summary = self.df_summary[["총 가입자", "전체단말 VOC건수(통품전체)", "전체단말 VOC건수(불만성유형)", "자사단말 VOC건수(통품전체)", "자사단말 VOC건수(불만성유형)", "전체 VOC_Rate(통품전체)", "전체 VOC_Rate(불만성유형)",\
                                               "자사단말 VOC_Rate(통품전체)", "자사단말 VOC_Rate(불만성유형)", "키워드 Top 20(통품전체)", "키워드 Top 20(불만성유형)", "카테고리분류(통품전체)", "카테고리분류(불만성유형)",\
                                               "자사단말 카테고리분류(통품전체)", "자사단말 카테고리분류(불만성유형)"]]


            #sorting rows
            self.df_summary.sort_index(axis=1, ascending=False)
            if self.mappingFlag == "y":
                self.df_swing['단말기모델명2'] = self.df_swing['단말기모델명2'].str.upper()
                self.df_subscriber['단말기모델명2'] = self.df_subscriber['단말기모델명2'].str.upper()
                self.df_keyword['단말기모델명2'] = self.df_keyword['단말기모델명2'].str.upper()
                self.df_count['단말리스트'] = self.df_count['단말리스트'].str.upper()
            else:
                self.df_swing['단말기모델명'] = self.df_swing['단말기모델명'].str.upper()
                self.df_subscriber['단말기명'] = self.df_subscriber['단말기명'].str.upper()
                self.df_keyword['단말기모델명'] = self.df_keyword['단말기모델명'].str.upper()
                self.df_count['단말리스트'] = self.df_count['단말리스트'].str.upper()

            # mapping models generate dataframe
            self.df_mapping = pd.DataFrame({"단말기모델명":self.mapping_models, "출시일":self.launch_model, "네트워크방식":self.network_model, "단말기제조사":self.manufact_model})
            self.df_mapping2 = pd.DataFrame({"단말기모델명2":self.mapping_models2, "출시일":self.launch_model2, "네트워크방식":self.network_model2, "단말기제조사":self.manufact_model2})

            ########################################################################Start to generate device matching DateFrame########################################################################


            self.setPrintText("/s Summary 선택 필드 통계 계산 작업 완료 /e")
            self.setPrintText("/s Finish to create the \"전체종합결과\" DataFrame /e")
            self.setPrintText("/s Start to write Excel File in \"VOC\" folder /e")
            #write excel file
            self.writer = pd.ExcelWriter(self.output_file)
            self.df_swing.to_excel(self.writer, sheet_name="통품전체VOC", index=False)
            self.df_keyword.to_excel(self.writer, sheet_name="불만성유형VOC", index=False)
            self.df_subscriber.to_excel(self.writer, sheet_name="전체가입자", index=False)
            self.df_count.to_excel(self.writer, sheet_name="단말별종합결과", index=False)
            self.df_summary.to_excel(self.writer, sheet_name="전체종합결과", index=False)
            self.df_mapping.to_excel(self.writer, sheet_name="모델명매칭", index=False)
            self.df_mapping2.to_excel(self.writer, sheet_name="모델명매칭2", index=False)

            self.writer.save()
            self.setPrintText("/s Finish to write Excel File in \"VOC\" folder /e")
            #############################################__progress 90%__#############################################
            self.progress_flag.emit()
            ########################################################################Start to generate openpyXL Sheet Style########################################################################
            ## Excel option adjusting function off case
            if self.opFlag == 'y':

                self.setPrintText("/s Start to adjust the result file by option style /e")
                self.swingRows = self.df_swing.shape[0]+1
                self.subsRows = self.df_subscriber.shape[0]+1
                self.keywordRows = self.df_keyword.shape[0]+1
                self.countRows = self.df_count.shape[0]+1
                self.summaryRows = self.df_summary.shape[0]+1
                self.mappingRows = self.df_mapping.shape[0]+1
                self.mappingRows2 = self.df_mapping2.shape[0]+1

                self.wb = openpyxl.load_workbook(self.output_file)
                self.sheet1 = self.wb['통품전체VOC']
                self.sheet2 = self.wb['전체가입자']
                self.sheet3 = self.wb['불만성유형VOC']
                self.sheet4 = self.wb['단말별종합결과']
                self.sheet5 = self.wb["전체종합결과"]
                self.sheet6 = self.wb["모델명매칭"]
                self.sheet7 = self.wb["모델명매칭2"]
                self.date_style = NamedStyle(name="datetime", number_format="YYYY-MM-DD")
                # 27.75

                #self.sheet1 Style
                self.sheet1_cell_list = ['A','B','C','D','E',
                                         'F','G','H','I','J',
                                         'K','L','M','N','O',
                                         'P','Q','R','S','T',
                                         'U','V','W','X','Y',
                                         'Z','AA','AB','AC','AD',
                                         'AE','AF','AG','AH','AI',
                                         'AJ','AK','AL','AM','AN',
                                         'AO','AP','AQ','AR']

                self.sheet1_width_list = [12.5, 17.5, 10.6, 16.7, 10.6,
                                          10.6, 10.6, 23.5, 23.5, 10.6,
                                          13.3, 11.5, 16.5, 15.8, 18.6,
                                          18.6, 18.6, 10.5, 12.4, 16.7,
                                          15.1, 20.1, 20.1, 16.3, 16.3,
                                          16.3, 16.3, 16.3, 16.3, 34,
                                          20.5, 16.5, 16.5, 16.5, 16.5,
                                          16.5, 16.5, 38, 38, 15.8,
                                          15.8, 15.8, 35.63, 20.13]
                #self.sheet2 Style
                self.sheet2_cell_list = ['A','B','C','D','E',
                                         'F','G','H','I','J',
                                         'K','L','M','N','O',
                                         'P','Q','R','S','T',
                                         'U','V','W','X']
                self.sheet2_width_list = [8.88, 28.38, 28.38, 15.5, 15.5,
                                          15.5, 15.5, 15.5, 15.5, 15.5,
                                          15.5, 15.5, 15.5, 15.5, 15.5,
                                          15.5, 15.5, 15.5, 15.5, 15.5,
                                          15.5, 15.5, 15.5, 18.63]

                #self.sheet3 Style
                self.sheet3_cell_list = ['A','B','C','D','E',
                                         'F','G','H','I','J',
                                         'K','L','M','N','O',
                                         'P','Q','R','S','T',
                                         'U','V','W','X','Y',
                                         'Z','AA','AB','AC','AD',
                                         'AE','AF','AG','AH','AI',
                                         'AJ','AK','AL','AM','AN',
                                         'AO','AP','AQ','AR']

                self.sheet3_width_list = [12.5, 17.5, 10.6, 16.7, 10.6,
                                          10.6, 10.6, 23.5, 23.5, 10.6,
                                          13.3, 11.5, 16.5, 15.8, 18.6,
                                          18.6, 18.6, 10.5, 12.4, 16.7,
                                          15.1, 20.1, 20.1, 16.3, 16.3,
                                          16.3, 16.3, 16.3, 16.3, 34,
                                          20.5, 16.5, 16.5, 16.5, 16.5,
                                          16.5, 16.5, 38, 38, 15.8,
                                          15.8, 15.8, 35.63, 20.13]

                #self.sheet4 Style
                self.sheet4_cell_list = ['A','B','C','D','E',
                                         'F','G','H','I','J',
                                         'K','L','M','N','O',
                                         'P','Q','R','S','T',
                                         'U','V','W']
                self.sheet4_width_list = [21.25, 21.25, 21.25, 14.75, 14.75,
                                          17.83, 17.83, 17.83, 27.5, 27.5,
                                          27.5, 22, 22, 22, 22,
                                          22, 22, 22, 22, 22,
                                          22, 22, 22]

                #self.sheet5 Style
                self.sheet5_cell_list = ['A','B','C','D','E',
                                         'F','G','H','I','J',
                                         'K','L','M','N','O',
                                         'P','Q','R','S','T',
                                         'U','V','W','X']
                self.sheet5_width_list = [21.25, 23.25, 23.25, 23.25, 23.25,
                                          23.25, 23.25, 23.25, 25.25, 23.25,
                                          23.25, 23.25, 23.25, 23.25, 23.25,
                                          23.25, 23.25, 23.25, 23.25, 23.25,
                                          23.25, 23.25, 23.25, 23.25]

                #self.sheet6 style
                self.sheet6_cell_list = ['A','B','C','D']
                self.sheet6_width_list = [34.63, 10.5, 12.63, 12.63]

                #self.sheet6 style
                self.sheet7_cell_list = ['A','B','C','D']
                self.sheet7_width_list = [34.63, 10.5, 12.63, 12.63]



                for i in range(len(self.sheet1_cell_list)):
                    self.sheet1.column_dimensions[self.sheet1_cell_list[i]].width = self.sheet1_width_list[i]
                for i in range(len(self.sheet2_cell_list)):
                    self.sheet2.column_dimensions[self.sheet2_cell_list[i]].width = self.sheet2_width_list[i]
                for i in range(len(self.sheet3_cell_list)):
                    self.sheet3.column_dimensions[self.sheet3_cell_list[i]].width = self.sheet3_width_list[i]
                for i in range(len(self.sheet4_cell_list)):
                    self.sheet4.column_dimensions[self.sheet4_cell_list[i]].width = self.sheet4_width_list[i]
                for i in range(len(self.sheet5_cell_list)):
                    self.sheet5.column_dimensions[self.sheet5_cell_list[i]].width = self.sheet5_width_list[i]
                for i in range(len(self.sheet6_cell_list)):
                    self.sheet6.column_dimensions[self.sheet6_cell_list[i]].width = self.sheet6_width_list[i]
                for i in range(len(self.sheet7_cell_list)):
                    self.sheet7.column_dimensions[self.sheet7_cell_list[i]].width = self.sheet7_width_list[i]

                # Each Sheet set auto filter column
                self.sheet1.auto_filter.ref = "A1:AR"+str(self.swingRows)
                self.sheet2.auto_filter.ref = "A1:X"+str(self.subsRows)
                self.sheet3.auto_filter.ref = "A1:AR"+str(self.keywordRows)
                self.sheet4.auto_filter.ref = "A1:W"+str(self.countRows)
                self.sheet6.auto_filter.ref = "A1:D"+str(self.mappingRows)
                self.sheet7.auto_filter.ref = "A1:D"+str(self.mappingRows2)

                #Set option Style on Cell
                for mCell in self.sheet1["A1:AR"+str(self.swingRows)]:
                    for cell in mCell:
                        if cell.column in [5, 19, 35]:
                            cell.style = self.date_style
                        if cell.row == 1:
                            cell.alignment = Alignment(wrap_text=True,horizontal="center",vertical="center")
                            cell.font = Font(size=10,bold=True,color='7F81FF')
                        else:
                            cell.alignment = Alignment(wrap_text=True,horizontal="left",vertical="center")
                            cell.font = Font(size=10)

                for mCell in self.sheet2["A1:X"+str(self.subsRows)]:
                    for cell in mCell:
                        if cell.row == 1:
                            cell.alignment = Alignment(wrap_text=True,horizontal="center",vertical="center")
                            cell.font = Font(size=10,bold=True,color='7F81FF')
                        else:
                            cell.alignment = Alignment(wrap_text=True,vertical="center")
                            cell.font = Font(size=10)

                for mCell in self.sheet3["A1:AR"+str(self.keywordRows)]:
                    for cell in mCell:
                        if cell.column in [5, 19, 35]:
                            cell.style = self.date_style
                        if cell.row == 1:
                            cell.alignment = Alignment(wrap_text=True,horizontal="center",vertical="center")
                            cell.font = Font(size=10,bold=True,color='7F81FF')
                        else:
                            cell.alignment = Alignment(wrap_text=True,horizontal="left",vertical="center")
                            cell.font = Font(size=10)

                for mCell in self.sheet4["A1:W"+str(self.countRows)]:
                    for cell in mCell:
                        if cell.row == 1:
                            cell.alignment = Alignment(wrap_text=True,horizontal="center",vertical="center")
                            cell.font = Font(size=10,bold=True,color='7F81FF')
                        else:
                            cell.alignment = Alignment(wrap_text=True,vertical="center")
                            cell.font = Font(size=10)

                for mCell in self.sheet5["A1:X"+str(self.summaryRows)]:
                    for cell in mCell:
                        if cell.row == 1:
                            cell.alignment = Alignment(wrap_text=True,horizontal="center",vertical="center")
                            cell.font = Font(size=10,bold=True,color='7F81FF')
                        elif cell.row == self.summaryRows:
                            cell.alignment = Alignment(wrap_text=True,vertical="center")
                            cell.font = Font(size=10,bold=True,color='7F81FF')
                        else:
                            cell.alignment = Alignment(wrap_text=True,vertical="center")
                            cell.font = Font(size=10)

                for mCell in self.sheet6["A1:D"+str(self.mappingRows)]:
                    for cell in mCell:
                        if cell.row == 1:
                            cell.alignment = Alignment(wrap_text=True,horizontal="center",vertical="center")
                            cell.font = Font(size=10,bold=True,color='7F81FF')
                        else:
                            cell.alignment = Alignment(wrap_text=True,vertical="center")
                            cell.font = Font(size=10)

                for mCell in self.sheet7["A1:D"+str(self.mappingRows2)]:
                    for cell in mCell:
                        if cell.row == 1:
                            cell.alignment = Alignment(wrap_text=True,horizontal="center",vertical="center")
                            cell.font = Font(size=10,bold=True,color='7F81FF')
                        else:
                            cell.alignment = Alignment(wrap_text=True,vertical="center")
                            cell.font = Font(size=10)

                #view freeze 'A2' cell
                self.sheet1.freeze_panes = self.sheet1["C2"]
                self.sheet2.freeze_panes = self.sheet2["D2"]
                self.sheet3.freeze_panes = self.sheet3["C2"]
                self.sheet4.freeze_panes = self.sheet4["B2"]

                self.wb.save(self.output_file)
                self.setPrintText("/s Finish to adjust the result file by option style /e")
                self.end_time = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                self.setPrintText("/s All job is Finished. Please Check result file in \"VOC\" folder /e")
                self.setPrintText("/s FINISH_TIME: "+self.end_time+" /e")
            # Excel option adjusting function off case
            else:
                self.end_time = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                self.setPrintText("/s All job is Finished. Please Check result file in \"VOC\" folder /e")
                self.setPrintText("/s FINISH_TIME: "+self.end_time+" /e")

            self.end_count = "y"
            #############################################__progress 100%__#############################################
            self.progress_flag.emit()
            self.end_flag.emit()

        except:
            self.setPrintText('/s Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno)+' /e')
            self.end_count = "y"
            self.end_flag.emit()


if __name__ == '__main__':
    moduler = avocParser('C:\\Users\\TestEnC\\Desktop\\VOC\\input_sample.xlsx', 'n', 'n', 'all', 'okt')
    moduler.ftp_client.connect(host=moduler.hostname, port=moduler.port)
    moduler.ftp_client.login(user=moduler.username, passwd=moduler.password)
    moduler.ftp_client.cwd("sklearn_models")
    moduler.ftp_client.retrlines("LIST", moduler.list_file.append)
    moduler.ftp_check_files()
    moduler.ftp_download_file()
    moduler.ftp_stop()
    returns = moduler.predict('며칠전에 떨어진거 액정깨진후  스피커폰 일반통화 중간느낌이라고하심  통화중 울림증상  -단말기버전 :TCB_TC5  -HDV설정여부: (사용중) -발생시기: 며칠전부터')
    print(returns)
