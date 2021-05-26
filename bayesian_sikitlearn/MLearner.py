# -*- coding: utf-8 -*-
"""
Created on Fri May 22 10:12:12 2020
@author: TestEnC hanrim lee

"""
import re
import os
import sys
import pandas as pd
import numpy as np
# import nltk
import pickle
import joblib


from konlpy.tag import Okt
from konlpy.tag import Komoran
from collections import Counter
from datetime import datetime
# from nltk.tokenize import word_tokenize

# from xgboost import plot_importance
# from xgboost import XGBClassifier

# from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.svm import LinearSVC
from sklearn.linear_model import SGDClassifier
# from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, KFold

class VOCLearner():
    # l_type은 러닝 방식을 선택하는 것으로 '1'은 naive 방식 '2'는 SGD 방식 '3'은 SVM기본 '4'는 LinearSVC 방식 '5'는 모두다
    # p_type은 문장 분류시 tokenizer 모드 선택으로 '1'은 Okt '2'는 Komoran 방식
    # t_type은 테스트 시 테스트 파일을 따로 할 것인지 선택하는 것으로 1
    def __init__(self):
        super(VOCLearner, self).__init__()
        #현재 위치
        self.current_path = os.getcwd()
        self.train_path = ''
        self.test_path = ''
        self.save_path = self.current_path+'\\sklearn_models\\'

        self.list_load_models = []
        self.l_type = 5
        self.p_type = 1
        self.t_type = 1
        self.test_rate = 0.3
        self.flag_shuffle = True

        self.model_nb = Pipeline([('vect', TfidfVectorizer()), ('clf', MultinomialNB(alpha=1e-2))])
        # self.model_svm = Pipeline([('vect', TfidfVectorizer()), ('clf-svm', SGDClassifier(loss='modified_huber', epsilon=0.1, penalty='l2', alpha=1e-4, random_state=42, fit_intercept=True))])
        # self.model_svm = Pipeline([('vect', TfidfVectorizer()), ('clf-svm', SGDClassifier(loss='hinge', penalty='l2', alpha=1e-3, random_state=42, max_iter=5, tol=None))])
        self.model_svm = Pipeline([('vect', TfidfVectorizer()), ('clf', SGDClassifier(loss='hinge', epsilon=0.1, penalty='l2', alpha=1e-4, random_state=42, fit_intercept=True))])
        self.model_svc = Pipeline([('vect', TfidfVectorizer()), ('clf', SVC(C=1000, random_state=42))])
        self.model_linerSVC = Pipeline([('vect', TfidfVectorizer()), ('clf', LinearSVC(random_state=42))])
        # n_estimators=1500
        # self.model_random =  Pipeline([('vect', TfidfVectorizer()), ('clf', RandomForestClassifier(n_estimators=1500, random_state=42))])
        # self.model_xgboost = Pipeline([('vect', TfidfVectorizer()), ('clf', XGBClassifier(random_state=42))])

        self.df_data = None
        self.list_memo = None
        self.list_special = None
        self.list_rmstring = None
        self.Train_Data_X = None
        self.Train_Data_Y = None
        self.Test_Data_X = None
        self.Test_Data_Y = None
        self.custome_vocab = None
        self.word_vector = None
        self.pattern = re.compile("[1-9]{1}[.]{1}")
        self.komoran = Komoran()
        self.twitter = Okt()
        self.stopString = ["안내","여부","사항","장비","확인","원클릭","품질","후","문의","이력","진단","부탁드립니다.","증상","종료","문의","양호","정상","고객","철회","파이","특이","간다"\
        "내부","외부","권유","성향","하심","해당","주심","고함","초기","무관","반려","같다","접수","무관","테스트","연락","바로","처리","모두","있다","없다","하다","드리다","않다","되어다",\
        "되다","부터","예정","드리다","해드리다", "신내역", "현기", "가신", 'ㅜ', "ㅠ"]

        self.introText = """
        ############################################-VOC Learner-###########################################

            1. VOC 분류 모델 생성 프로그램 입니다.
            2. 현재 프로그램이 위치한 경로에 input excel 파일이 존재해야 합니다.
            3. 현재 프로그램이 위치한 경로에 'sklearn_models' 폴더 이름으로 저장이 됩니다.
            4. t_type이 1인 경우는 학습 데이터 Set의 일부를 test_rate만큼 때어내어 저장 합니다.
            5. t_type이 2인 경우는 테스트 전용 데이터 파일을 따로 준비하셔야 합니다.

        #####################################################################################################\n\n
        """


    # 시간 정보와 함께 Console에 Print 하는 함수
    def setPrint(self, text):

        current = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        print("{}:\n{}".format(current, text)+"\n")
    # Train set 과 Test set 생성하는 함수
    def generate_data(self):

        try:
            # input excel 읽어서 data frame으로 변환
            self.df_data = pd.read_excel(self.train_path, sheet_name="통품전체VOC", index_col=None)
            df_config1 = pd.read_excel(self.train_path, sheet_name="예약어리스트", index_col=None)
            df_config2 = pd.read_excel(self.train_path, sheet_name="Stop word", index_col=None)
            df_config3 = pd.read_excel(self.train_path, sheet_name='Config', index_col=None)
            # N/A 값 drop
            self.df_data = self.df_data.dropna()
            df_config1 = df_config1.dropna()
            dF_config2 = df_config2.dropna()
            # data frame index 번호 reset
            self.df_data.reset_index(drop=True)
            df_config1.reset_index(drop=True)
            df_config2.reset_index(drop=True)

            # 예약어 설정 값 선택
            self.list_special = df_config1['Special예약어'].tolist()
            # 단어 제거 형식 선택
            self.list_rmstring = df_config2['일반형식'].tolist()

            #config setting values extract
            list_settings = df_config3['설정 값'].tolist()
            list_settings = [str(x) for x in list_settings if x]

            if list_settings[0] != 'nan':
                self.l_type = int(list_settings[0])
            if list_settings[1] != 'nan':
                self.p_type = int(list_settings[1])
            if list_settings[2] != 'nan':
                self.t_type = int(list_settings[2])
            # if list_settings[3] != 'nan':
            #     if list_settings[3] == 1:
            #         self.flag_shuffle = True
            #     else:
            #         self.flag_shuffle = False
            if list_settings[3] != 'nan':
                self.test_rate = float(list_settings[3])
            if list_settings[4] != 'nan':
                self.test_path = list_settings[4]

            if self.t_type == 1:

                self.list_memo = self.text_filter(self.df_data['메모'].tolist())
                self.Train_Data_X, self.Test_Data_X, self.Train_Data_Y, self.Test_Data_Y = train_test_split(self.list_memo, self.df_data['메모분류'].tolist(), test_size=self.test_rate, random_state=42, shuffle=self.flag_shuffle)
                self.setPrint('t_type 1에 따라 Train, Test 데이터 셋 분리 완료...')
            else:
                self.list_memo = self.text_filter(self.df_data['메모'].tolist())
                df_test_data = pd.read_excel(self.test_path, sheet_name=0, index_col=None)
                df_test_data = df_test_data.dropna()
                df_test_data.reset_index(drop=True)
                self.Train_Data_X, self.Test_Data_X, self.Train_Data_Y, self.Test_Data_Y = train_test_split(self.list_memo, self.df_data['메모분류'].tolist(), test_size=0.01, random_state=42, shuffle=True)
                self.Test_Data_X = df_test_data['메모'].tolist()
                self.Test_Data_Y = df_test_data['메모분류'].tolist()
                self.setPrint('t_type 2에 따라 Train, Test 데이터 셋 분리 완료...')

        except:
            self.setPrint('Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno))
    # TF-IDF Vector vocabulary 생성기
    def generate_vector(self):
      try:
          self.setPrint('TF-IDF Vector vocabulary 생성 작업 시작...')
          self.word_vector = TfidfVectorizer(sublinear_tf=True, tokenizer=self.splitNouns, max_df=0.75, norm='l2', ngram_range=(1, 2))
          self.custome_vocab = self.word_vector.fit_transform(self.list_memo)
          self.setPrint('TF-IDF Vector vocabulary 생성 완료...')
          self.setPrint('WORD VECTOR 형태, ({} 문장, {} 단어 추출)'.format(self.custome_vocab.shape[0], self.custome_vocab.shape[1]))
          # print(self.word_vector.vocabulary_)
          # print(self.word_vector.vocabulary_.get('와이파이'))
          # print(self.custome_vocab)
      except:
          self.setPrint('TF-IDF Vector vocabulary 생성 중 에러 발생...')
          self.setPrint('Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno))

    # 특정 문자 구간 Parsing 함수(앞에서부터)
    def find_between(self, s, first, last):
        try:
            start = s.index(first)+len(first)
            end = s.index(last, start)
            return s[start:end]
        except ValueError:
            return ""

    # 특정 문자 구간 Parsing 함수(뒤에서부터)
    def find_between_r(self, s, first, last ):
        try:
            start = s.rindex(first) + len(first)
            end = s.rindex(last, start)
            return s[start:end]
        except ValueError:
            return ""

    # 특수문자 제거 함수
    def removeString(self, text):

        text_data = re.sub('[-=+,_#/\?^$@*\"※~&%ㆍ!』\‘|\(\)\[\]\<\>\{\}`><\']', '', text)
        text_data = text_data.lower()
        for item in self.list_rmstring:
            text_data = text_data.replace(item, "")

        text_data = text_data.strip()
        return text_data

    # tokenizer 함수
    def splitNouns(self, text):

        # for item in self.list_special:
        #     if item in text:
        #         specString = item
        #         text = text+"/e"
        #         text = self.find_between(text, specString, "/e")
        #         if self.pattern.search(text):
        #             pattern_list = self.pattern.findall(text)
        #             text = self.find_between(text, specString, pattern_list[0])
        #         else:
        #             text.replace("/e", "")
        #         break
        #
        # text = self.removeString(text)
        # text = "\n".join([s for s in text.split('\n') if s])
        result = []
        if self.p_type == 1:
            malist = self.twitter.pos(text)
            for word in malist:
                if word[1] in ['Noun','Adjective','Verb', 'Unknown'] and not word[0] in self.stopString and len(word[0]) > 1:
                    result.append(word[0])
        else:
            malist = self.komoran.pos(text)
            for word in malist:
                if word[1] in ['NNG', 'NNP', 'NNB', 'VV', 'MAG', 'VA', 'UN', 'MAJ', 'SL', 'NA', 'NF'] and not word[0] in self.stopString and len(word[0]) > 1:
                    result.append(word[0])
        return result

    # 메모 데이터 filtering 함수
    def text_filter(self, list_doc):

        list_return = list_doc
        for idx, doc in enumerate(list_return):
            for item in self.list_special:
                if item in doc:
                    specString = item
                    doc = doc+"/e"
                    text = self.find_between(doc, specString, "/e")
                    if self.pattern.search(text):
                        pattern_list = self.pattern.findall(text)
                        doc = self.find_between(doc, specString, pattern_list[0])
                    else:
                        doc = doc.replace("/e", "")
                    break
            doc = self.removeString(doc)
            doc = "\n".join([s for s in doc.split('\n') if s])
            list_return[idx] = doc

        return list_return

    # 모델 저장 함수
    def save_models(self):

        self.setPrint('생성된 학습모델 저장 작업 시작...')
        # 디렉토리 생성
        if not os.path.isdir(self.save_path):
            os.makedirs(self.save_path, exist_ok=True)
        # 타입별 모델 저장하기
        if self.l_type == 1:
            self.setPrint('위치 : {}'.format(self.save_path+'model_nb.pkl'))
            # save_model = pickle.dumps(self.model_nb)
            joblib.dump(self.model_nb, self.save_path+'model_nb.pkl')
        elif self.l_type == 2:
            self.setPrint('위치 : {}'.format(self.save_path+'model_svm.pkl'))
            # save_model = pickle.dumps(self.model_svm)
            joblib.dump(self.model_svm, self.save_path+'model_svm.pkl')
        elif self.l_type == 3:
            self.setPrint('위치 : {}'.format(self.save_path+'model_svc.pkl'))
            # save_model = pickle.dumps(self.model_svc)
            joblib.dump(self.model_svc, self.save_path+'model_svc.pkl')
        elif self.l_type == 4:
            self.setPrint('위치 : {}'.format(self.save_path+'model_linerSVC.pkl'))
            # save_model = pickle.dumps(self.model_linerSVC)
            joblib.dump(self.model_linerSVC, self.save_path+'model_linerSVC.pkl')
        # elif self.l_type == 5:
        #     self.setPrint('위치 : {}'.format(self.save_path+'model_random.pkl'))
        #     # save_model = pickle.dumps(self.model_random)
        #     joblib.dump(self.model_random, self.save_path+'model_random.pkl')
        # elif self.l_type == 6:
        #     self.setPrint('위치 : {}'.format(self.save_path+'model_xgboost.pkl'))
        #     # save_model = pickle.dumps(self.model_xgboost)
        #     joblib.dump(self.model_xgboost, self.save_path+'model_xgboost.pkl')
        else:
            self.setPrint('위치1 : {}'.format(self.save_path+'model_nb.pkl'))
            self.setPrint('위치2 : {}'.format(self.save_path+'model_svm.pkl'))
            self.setPrint('위치3 : {}'.format(self.save_path+'model_svc.pkl'))
            self.setPrint('위치4 : {}'.format(self.save_path+'model_linerSVC.pkl'))
            # self.setPrint('위치5 : {}'.format(self.save_path+'model_random.pkl'))
            # self.setPrint('위치6 : {}'.format(self.save_path+'model_xgboost.pkl'))
            # save_model_1 = pickle.dumps(self.model_nb)
            # save_model_2 = pickle.dumps(self.model_svm)
            # save_model_3 = pickle.dumps(self.model_svc)
            # save_model_4 = pickle.dumps(self.model_linerSVC)
            # save_model_5 = pickle.dumps(self.model_random)
            joblib.dump(self.model_nb, self.save_path+'model_nb.pkl')
            joblib.dump(self.model_svm, self.save_path+'model_svm.pkl')
            joblib.dump(self.model_svc, self.save_path+'model_svc.pkl')
            joblib.dump(self.model_linerSVC, self.save_path+'model_linerSVC.pkl')
            # joblib.dump(self.model_random, self.save_path+'model_random.pkl')
            # joblib.dump(self.model_xgboost, self.save_path+'model_xgboost.pkl')

        self.setPrint('모델 저장 작업 완료...')
    # 모델 저장 경로에 있는 모델 불러와서 Array 로 리턴
    def load_model(self, list_path):

        try:
            for path in list_path:
                model = joblib.load(path)
                self.list_load_models.append(model)
            self.setPrint('모델 Load 작업 완료. 완료 모델 수: {}'.format(len(self.list_load_models)))
        except:
              self.setPrint('모델 Load 작업 중 에러 발생...')
              self.setPrint('Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno))
    # 모델 교차검증 함수
    def cross_validation(self, dict_model):

        for idx, (key, model) in enumerate(dict_model.items()):

            self.setPrint("{} 모델 {} 교차 검증 시작...".format(idx, key))
            kfold = KFold(n_splits=10, shuffle=self.flag_shuffle)
            score = cross_val_score(model, self.Test_Data_X, self.Test_Data_Y, cv=kfold, scoring="accuracy")
            self.setPrint("{} 모델 {} 교차 검증 평균 accuracy : {}".format(idx, key, score.mean()))
    # main 실행함수
    def run(self):

        try:
            print(self.introText)
            input_filename = input("머신러닝 모델 학습 input excel 파일명만 입력하여 주세요.(현재 프로그램과 같은 위치에 있어야 합니다.) : ")
            file_flag = os.path.isfile(self.current_path+"\\"+input_filename+".xlsx")
            while file_flag is False:
                input_filename = input("입력하신 파일명이 경로에 존재하지 않습니다. 정확히 다시 입력하여 주세요. : ")
                file_flag = os.path.isfile(self.current_path+"\\"+input_filename+".xlsx")

            start_time = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            self.setPrint("START_TIME : " + start_time)
            self.train_path = self.current_path+"\\"+input_filename+".xlsx"
            self.setPrint('분석대상 파일 정보 수집 시작...')
            #학습데이터와 정확도 테스트를 위한 테스트 set 생성 함수 실행
            self.generate_data()
            self.setPrint('Train 메모 Data 수: {}'.format(len(self.Train_Data_X)))
            self.setPrint('Train 메모분류 Data 수: {}'.format(len(self.Train_Data_Y)))
            self.setPrint('Test 메모 Data 수: {}'.format(len(self.Test_Data_X)))
            self.setPrint('Test 메모분류 Data 수: {}'.format(len(self.Test_Data_Y)))
            # 단어장 vector 생성 함수 실행
            self.generate_vector()

            #########################################################################__학습 시작__#########################################################################
            # Naive Bayesian 방식으로 모델 생성 처리
            if self.l_type == 1:
                self.setPrint('NB Naive Bayesian classifier 모델 학습 시작...')
                self.mode_nb = self.model_nb.fit(self.Train_Data_X, self.Train_Data_Y)
                self.setPrint('NB Naive Bayesian classifier 모델 학습 완료...')
                # 테스트 시작
                # self.setPrint('트레이닝 테스트 시작...')
                # predicted = self.mode_nb.predict(self.Test_Data_X)
                # accurracy  = np.mean(predicted == self.Test_Data_Y)
                # self.setPrint('NB Naive Bayesian 정확도: {} %'.format(accurracy*100))
                self.cross_validation({'Naive Bayesian':self.model_nb})

            # SVM SGDClassifier 방식으로 모델 생성 처리
            elif self.l_type == 2:
                self.setPrint('SVM SGDClassifier 모델 학습 시작...')
                self.model_svm = self.model_svm.fit(self.Train_Data_X, self.Train_Data_Y)
                self.setPrint('SVM SGDClassifier 모델 학습 완료...')
                # 테스트 시작
                # self.setPrint('테스트 시작...')
                # predicted = self.model_svm.predict(self.Test_Data_X)
                # accurracy  = np.mean(predicted == self.Test_Data_Y)
                # self.setPrint('SVM SGDClassifier 정확도: {} %'.format(accurracy*100))
                self.cross_validation({'SGDClassifier':self.model_svm})

            elif self.l_type == 3:
                self.setPrint('SVC classifier 모델 학습 시작...')
                self.model_svc = self.model_svc.fit(self.Train_Data_X, self.Train_Data_Y)
                self.setPrint('SVC classifier 모델 학습 완료...')
                # 테스트 시작
                self.cross_validation({'SVC':self.model_svc})

            elif self.l_type == 4:
                self.setPrint('LinerSVC classifier 모델 학습 시작...')
                self.model_linerSVC = self.model_linerSVC.fit(self.Train_Data_X, self.Train_Data_Y)
                self.setPrint('LinerSVC classifier 모델 학습 완료...')
                # 테스트 시작
                self.cross_validation({'LinearSVC':self.model_linerSVC})

            # elif self.l_type == 5:
            #     self.setPrint('RandomForest classifier 모델 학습 시작...')
            #     self.model_random = self.model_random.fit(self.Train_Data_X, self.Train_Data_Y)
            #     self.setPrint('RandomForest classifier 모델 학습 완료...')
            #     # 테스트 시작
            #     self.cross_validation({'Random':self.model_random})
            #
            # elif self.l_type == 6:
            #     self.setPrint('Xgboost classifier 모델 학습 시작...')
            #     self.model_xgboost = self.model_xgboost.fit(self.Train_Data_X, self.Train_Data_Y)
            #     self.setPrint('Xgboost classifier 모델 학습 완료...')
            #     # 테스트 시작
            #     self.cross_validation({'Xgboost':self.model_xgboost})

            # 둘다 모델 생성 처리
            else:
                self.setPrint('4개 모델 학습 시작...')
                self.mode_nb = self.model_nb.fit(self.Train_Data_X, self.Train_Data_Y)
                self.setPrint('Naive Bayesian classifier 모델 학습 완료...')
                self.model_svm = self.model_svm.fit(self.Train_Data_X, self.Train_Data_Y)
                self.setPrint('SVM SGDClassifier 모델 학습 완료...')
                self.model_svc = self.model_svc.fit(self.Train_Data_X, self.Train_Data_Y)
                self.setPrint('SVC classifier 모델 학습 완료...')
                self.model_linerSVC = self.model_linerSVC.fit(self.Train_Data_X, self.Train_Data_Y)
                self.setPrint('LinerSVC classifier 모델 학습 완료...')
                # self.model_random = self.model_random.fit(self.Train_Data_X, self.Train_Data_Y)
                # self.setPrint('RandomForest classifier 모델 학습 완료...')
                # self.model_xgboost = self.model_xgboost.fit(self.Train_Data_X, self.Train_Data_Y)
                # self.setPrint('Xgboost classifier 모델 학습 완료...')

                # 테스트 시작
                self.setPrint('테스트 시작...')
                self.cross_validation({'Naive Bayesian':self.model_nb, 'SGDClassifier':self.model_svm, 'SVC':self.model_svc,
                'LinearSVC':self.model_linerSVC})
                # self.cross_validation({'Naive Bayesian':self.model_nb, 'SGDClassifier':self.model_svm, 'SVC':self.model_svc,
                # 'LinearSVC':self.model_linerSVC, 'RandomFoest':self.model_random, 'Xgboost':self.model_xgboost})

            self.save_models()
            # self.load_model([self.save_path+'model_nb.pkl', self.save_path+'model_svm.pkl', self.save_path+'model_svc.pkl', self.save_path+'model_linerSVC.pkl'])
            #
            # sentence = ["카카오톡 이랑 카트라이더 앱 안됨 실행 시 튕기고 강제 종료 됨", "'핸드폰 자체 소프트웨어 업데이트 이후 문자발송시 글자수 제한되고 있음.  기존 동일한 문자정상 발송 되던것이나, 이용안됨 .  \
            # - 80명 단체문자  - 이미지 동영상 문자메세지만 보낼수 있어요. 라고 나오면서 발신 불가 .   개별로 보내면 정상  > 제조사 문의 안내 . 연결"]
            # sentence = [self.removeString(x) for x in sentence if x]
            # label_1 = self.list_load_models[0].predict(sentence)
            # label_2 = self.list_load_models[1].predict(sentence)
            # label_3 = self.list_load_models[2].predict(sentence)
            # label_4 = self.list_load_models[3].predict(sentence)
            #
            # self.setPrint(label_1)
            # self.setPrint(label_2)
            # self.setPrint(label_3)
            # self.setPrint(label_4)
            end_time = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            self.setPrint("FINISH_TIME : " + end_time)
            input("\nPress any key to exit")

        except:
          self.setPrint('학습기 실행 중 에러 발생...')
          self.setPrint('Error: {}. {}, line: {}'.format(sys.exc_info()[0],  sys.exc_info()[1], sys.exc_info()[2].tb_lineno))


if __name__ == "__main__":
    vl = VOCLearner()
    vl.run()
