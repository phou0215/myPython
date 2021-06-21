# -*- coding: utf-8 -*-
"""
Created on Tues June 08 10:30:00 2021
@author: TestEnC hanrim lee

"""

import re
import os
import sys
import pandas as pd
import numpy as np
import pickle
import joblib

from konlpy.tag import Okt
from konlpy.tag import Komoran

from collections import Counter
from datetime import datetime
import matplotlib.pyplot as plt

# from sklearn.preprocessing import StandardScaler
# from sklearn.feature_extraction.text import TfidfTransformer
# from sklearn.model_selection import train_test_split
# from sklearn.model_selection import GridSearchCV

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.svm import SVC
from sklearn.svm import LinearSVC
from sklearn.linear_model import SGDClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import cross_val_score, KFold, cross_validate


class VOCLearner():
    # l_type은 러닝 방식을 선택하는 것으로 '1'==> SGD 방식 '2'==> SVC 방식 '3'==>  LinearSVC 방식 '4'==> XGBoost '5'==> ALL
    # p_type은 문장 분류시 tokenizer 모드 선택으로 '1'은 Okt '2'는 Komoran 방식
    # {'데이터': 0, '데이터 지연': 1, '통화불량': 2, '분류없음': 3, 'USIM': 4, '음질불량': 5, 'APP': 6, '문자 지연': 7, '문자': 8, '통화권이탈': 9,
    #  '부가서비스': 10}

    def __init__(self):
        super(VOCLearner, self).__init__()
        # 현재 위치
        self.current_path = os.getcwd()
        self.train_path = ''
        self.test_path = ''
        self.vocab_path = ''
        self.save_path = self.current_path + '\\sklearn_models\\'
        self.vect_path = self.current_path + '\\sklearn_vect\\'

        self.list_corpus = []
        self.list_load_models = []
        self.list_model_path = []
        self.dict_acc = {}
        self.l_type = 4
        self.p_type = 1
        self.v_type = 1
        self.n_split = 5

        self.flag_shuffle = True
        self.custom_vocab = None
        self.vectorizer = None

        self.dict_label = {}
        self.dict_label_reverse = {}
        self.figure = None
        self.df_data = None
        self.list_memo = None
        self.list_label = None
        self.list_special = None
        self.list_rmstring = None
        self.label_index = None

        # models
        self.dict_model = None

        self.pattern = re.compile("([1-9]{1,2}\.)")
        self.konlpy_parser = None
        self.stopString = ["안내", "여부", "사항", "장비", "확인", "원클릭", "품질", "후", "문의", "이력", "진단", "부탁드립니다.",
                           "증상", "종료", "문의", "양호", "정상", "고객", "철회", "파이", "특이", "간다", "내부", "외부", "권유",
                           "성향", "하심", "해당", "주심", "고함", "초기", "무관", "반려", "같다", "접수", " 무관", "테스트", "연락",
                           "바로", "처리", "모두", "있다", "없다", "하다", "드리다", "않다", "되어다", "되다", "부터", "예정", "드리다",
                           "해드리다", "신내역", "현기", "가신", 'ㅜ', "ㅠ"]

        self.introText = """
        ############################################-VOC Learner-###########################################

            1. VOC 분류 모델 생성 프로그램 입니다.
            2. 현재 프로그램이 위치한 경로에 input excel 파일이 존재해야 합니다.
            3. 현재 프로그램이 위치한 경로에 'sklearn_models' 폴더 이름으로 저장이 됩니다.
            4. v_type이 2인 경우는 vocab 전용 corpus csv 파일을 따로 준비하셔야 합니다.

        #####################################################################################################\n\n
        """

    # 시간 정보와 함께 Console에 Print 하는 함수
    def setPrint(self, text):

        current = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
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

    # # label 인덱스 부여하기
    # def set_label_index(self, df_data, col_name='label'):
    #
    #     labels = df_data[col_name].unique()
    #     label_dict = {}
    #     for index, label in enumerate(labels):
    #         label_dict[label] = index
    #     return label_dict

    # label 인덱스 부여하기
    def set_label_index(self, list_category, list_label):

        try:
            for idx, cate in enumerate(list_category):
                self.dict_label[cate] = int(list_label[idx])
                self.dict_label_reverse[int(list_label[idx])] = cate
        except:
            self.setPrint('Error: {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1],
                                                           sys.exc_info()[2].tb_lineno))

    # grid graph
    def generate_graph(self, max_col=2,  max_row=3):

        # max_col = 2
        # max_row = 3
        x = np.linspace(1, self.n_split, self.n_split)
        # self.figure = plt.figure(figsize=(12, 8))
        self.figure = plt.figure()

        for idx, (key, values) in enumerate(self.dict_acc.items()):
            ax = self.figure.add_subplot(max_row, max_col, idx+1)
            ax.plot(x, values)
            ax.set_xlabel('KFold')
            ax.set_ylabel(key+' ACC Score')
            # ax1.legend(['AVG_ACC', 'AVG_RECALL'])

        plt.show()

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

            # data frame index 번호 reset
            self.df_data.reset_index(drop=True)

            # label cleaning and 데이터 분포 확인
            self.df_data['메모분류'] = self.df_data['메모분류'].apply(lambda x: x.strip())
            self.setPrint('데이터 분포: \n{}'.format(self.df_data['메모분류'].value_counts()))

            # 예약어 설정 값 선택
            self.list_special = df_config1['Special예약어'].dropna().tolist()
            # 단어 제거 형식 선택
            self.list_rmstring = df_config2['일반형식'].dropna().tolist()

            # config setting values extract
            list_settings = df_config3['설정 값'].tolist()
            list_settings = [str(x) for x in list_settings if x]

            # learning type select
            if list_settings[0] != 'nan':
                self.l_type = int(list_settings[0])
            # konlpy 형태소 분리 타입
            if list_settings[1] != 'nan':
                self.p_type = int(list_settings[1])
                if self.p_type == 1:
                    self.konlpy_parser = Okt()
                else:
                    self.konlpy_parser = Komoran()
            # KFold n_split 몇게 데이터호
            if list_settings[2] != 'nan':
                self.n_split = int(list_settings[2])
            # custom vocab flag
            if list_settings[3] != 'nan':
                self.v_type = 2
                self.vocab_path = list_settings[3]

            # train test split data part
            # t_type == 1
            # label change to index format
            list_category = df_config1['카테고리'].dropna().tolist()
            list_label = df_config1['LABEL'].dropna().tolist()
            # self.label_index = self.set_label_index(self.df_data, col_name='메모분류')
            self.set_label_index(list_category, list_label)
            self.df_data['label'] = self.df_data['메모분류'].replace(self.dict_label)
            self.setPrint('index of labels: \n{}'.format(self.dict_label))
            # data frame index reset
            self.df_data.reset_index(drop=True)
            self.list_label = self.df_data['label'].tolist()
            self.list_memo, self.list_label = self.text_filter(self.df_data['메모'].tolist(), self.list_label)

            self.setPrint('L_type: {}\nP_type: {}\nV_type: {}\nn_split: {}'.format(
                self.l_type, self.p_type, self.v_type, self.n_split
            ))
            # vocab text generate part
            if self.v_type == 2:
                df_vocab_data = pd.read_csv(self.vocab_path, encoding='CP949')
                self.list_corpus = df_vocab_data['메모'].tolist()
                # process text cleaning
                self.list_corpus, list_labels = self.text_filter(self.list_corpus, None)

        except:
            self.setPrint('Error: {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1],
                                                           sys.exc_info()[2].tb_lineno))

    # vectorizer 생성
    def generate_vector(self, list_text):
        try:
            self.vectorizer = TfidfVectorizer(sublinear_tf=False,
                                              smooth_idf=True,
                                              input="array",
                                              # tokenizer=self.subword_text,
                                              max_df=0.8,
                                              min_df=2,
                                              norm='l2',
                                              ngram_range=(1, 1)
                                              )
            self.vectorizer.fit_transform(list_text)
            # self.custom_vocab = custom_vector.vocabulary_
            self.setPrint('Custom Vocab {} 개 생성'.format(len(self.vectorizer.get_feature_names())))
            # self.setPrint(tf_idf)
        except:
            self.setPrint('Custom Vocab 생성 중 에러 발생...')
            self.setPrint('Error: {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1],
                                                           sys.exc_info()[2].tb_lineno))

    # make model pipeline
    def generate_pipeline(self):

        # alpha = 1e-4,
        model_svm = Pipeline([
            ('vect', self.vectorizer),
            ('clf', SGDClassifier(loss='log', penalty='l2', random_state=42, fit_intercept=True, class_weight='balanced'))
        ])
        model_svc = Pipeline([
            ('vect', self.vectorizer),
            ('clf', SVC(C=10, kernel='rbf', gamma=0.1, probability=True, class_weight=None, random_state=42))
        ])
        model_linerSVC = Pipeline([
            ('vect', self.vectorizer),
            ('clf', LinearSVC(random_state=42))
        ])
        # google xgboost
        model_xgboost = Pipeline([
            ('vect', self.vectorizer),
            ('clf', XGBClassifier(random_state=42,
                                  max_depth=10,
                                  objective='multi:softmax ',
                                  n_estimators=1500,
                                  learning_rate=0.1,
                                  ))
        ])
        self.dict_model = {'SGDClassifier': model_svm,
                           'SVC': model_svc, 'LinearSVC': model_linerSVC, 'xgboost': model_xgboost}

    # Konlpy text parsing
    def subword_text(self, text):

        try:
            result = []
            if self.p_type == 1:
                malist = self.konlpy_parser.pos(text)
                for word in malist:
                    if word[1] != 'Number':
                        result.append(word[0])
            else:
                malist = self.konlpy_parser.pos(text)
                for word in malist:
                    if word[1] != 'SN':
                        result.append(word[0])
            # mal_ist = self.konlpy_parser.morphs(text)
            return result
        except:
            self.setPrint('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                           sys.exc_info()[1],
                                                           sys.exc_info()[2].tb_lineno))
            return result

    # remove special char and confusing words united only one expression
    def remove_special(self, text):

        # 영문 모두 소문자로 변경
        text_data = text.lower()
        # 전화번호, 화폐, url은 각각 선언된 단어로 치환'
        text_data = re.sub(r'\d{2,3}[-\.\s]*\d{3,4}[-\.\s]*\d{4}(?!\d)', 'tel', text_data)
        text_data = re.sub(r'\d{1,3}[,\.]\d{1,3}[만\천]?\s?[원]|\d{1,5}[만\천]?\s?[원]', 'money', text_data)
        text_data = re.sub(r'일/이/삼/사/오/육/칠/팔/구/십/백][만\천]\s?[원]', 'money', text_data)
        text_data = re.sub(r'(?!-)\d{2,4}[0]{2,4}(?!년)(?!.)|\d{1,3}[,/.]\d{3}', 'money', text_data)
        text_data = re.sub(
            r'(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+'
            r'[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})',
            'url',
            text_data)
        # custom 치환
        text_data = re.sub(r'(유.?심|유심.?칩|심.?카드|sim.?카드|esim|sim)', 'usim', text_data)
        text_data = re.sub(r'(4.?g|4.?지)', 'lte', text_data)
        text_data = re.sub(r'(5.?g|5.?지)', 'fiveg', text_data)
        text_data = re.sub(r'(3.?g|3.?지)', 'threeg', text_data)
        text_data = re.sub(r'((특장|특정).?사이트|(특정|특장).?(어플|app|앱)|카카.?오톡?|(페이스|보이스|카|페|보).?톡|'
                           r'kakao.?talk|tmap|(티|t).?맵|후후.?어?플?|페이스.?타임)', 'app', text_data)
        text_data = re.sub(r'(sms|mms|메시지)', 'message', text_data)
        # 그 외의 특수문자는 모두 삭제
        text_data = re.sub(r'[-=+,_#/\?^$@*\"※~&%ㆍ!』\‘|\(\)\[\]\<\>\{\}`><\':;■◈▶●★☎]', ' ', text_data)

        # 앞서 list_rmstring 선언된 단어들 모두 제거
        for item in self.list_rmstring:
            text_data = text_data.replace(item, "")
        # 필수 제거 단어 제거
        for item in self.stopString:
            text_data = text_data.replace(item, "")

        # 앞 뒤 공백 제거
        text_data = text_data.strip()
        return text_data

    #  Text cleaning 함수
    def text_filter(self, list_doc, list_label):

        try:
            list_return_docs = []
            list_return_labels = []
            for idx, doc in enumerate(list_doc):
                for item in self.list_special:
                    if item in doc:
                        spec_string = item
                        doc = doc + "/e"
                        text = self.find_between(doc, spec_string, "/e")
                        if self.pattern.search(text):
                            pattern_list = self.pattern.findall(text)
                            doc = self.find_between(doc, spec_string, pattern_list[0])
                        else:
                            doc = doc.replace("/e", "")
                        break
                doc = self.remove_special(doc)
                if doc == "":
                    continue
                split_doc = self.subword_text(doc)
                doc = " ".join([s.strip() for s in split_doc if s])
                list_return_docs.append(doc)
                if list_label:
                    list_return_labels.append(list_label[idx])
            return list_return_docs, list_return_labels
        except:
            self.setPrint('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                           sys.exc_info()[1],
                                                           sys.exc_info()[2].tb_lineno))
            return None

    # 모델 저장 함수
    def save_models(self):

        self.setPrint('생성된 학습모델 저장 작업 시작...')
        # 디렉토리 생성
        if not os.path.isdir(self.save_path):
            os.makedirs(self.save_path, exist_ok=True)
        # 타입별 모델 저장하기
        if self.l_type == 1:
            self.setPrint('위치 : {}'.format(self.save_path + 'model_svm.pkl'))
            joblib.dump(self.dict_model['SGDClassifier'], self.save_path + 'model_svm.pkl')
            self.list_model_path.append(self.save_path + 'model_svm.pkl')

        elif self.l_type == 2:
            self.setPrint('위치 : {}'.format(self.save_path + 'model_svc.pkl'))
            joblib.dump(self.dict_model['SVC'], self.save_path + 'model_svc.pkl')
            self.list_model_path.append(self.save_path + 'model_svc.pkl')

        elif self.l_type == 3:
            self.setPrint('위치 : {}'.format(self.save_path + 'model_linerSVC.pkl'))
            joblib.dump(self.dict_model['LinearSVC'], self.save_path + 'model_linerSVC.pkl')
            self.list_model_path.append(self.save_path + 'model_linerSVC')

        elif self.l_type == 4:
            self.setPrint('위치 : {}'.format(self.save_path + 'model_xgboost.pkl'))
            joblib.dump(self.dict_model['xgboost'], self.save_path + 'model_xgboost.pkl')
            self.list_model_path.append(self.save_path + 'model_xgboost.pkl')

        else:
            self.setPrint('위치1 : {}'.format(self.save_path + 'model_svm.pkl'))
            self.setPrint('위치2 : {}'.format(self.save_path + 'model_svc.pkl'))
            self.setPrint('위치3 : {}'.format(self.save_path + 'model_linerSVC.pkl'))
            self.setPrint('위치4 : {}'.format(self.save_path + 'model_xgboost.pkl'))

            joblib.dump(self.dict_model['SGDClassifier'], self.save_path + 'model_svm.pkl')
            joblib.dump(self.dict_model['SVC'], self.save_path + 'model_svc.pkl')
            joblib.dump(self.dict_model['LinearSVC'], self.save_path + 'model_linerSVC.pkl')
            joblib.dump(self.dict_model['xgboost'], self.save_path + 'model_xgboost.pkl')

            self.list_model_path.append(self.save_path + 'model_svm.pkl')
            self.list_model_path.append(self.save_path + 'model_svc.pkl')
            self.list_model_path.append(self.save_path + 'model_linerSVC.pkl')
            self.list_model_path.append(self.save_path + 'model_xgboost.pkl')

        joblib.dump(self.vectorizer, self.vect_path + 'vectorizer.pkl')
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
            self.setPrint('Error: {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1],
                                                           sys.exc_info()[2].tb_lineno))

    # 모델 교차 트레이닝 검증 함수
    def cross_validation(self, dict_model):
        try:
            for idx, (key, model) in enumerate(dict_model.items()):
                self.setPrint("{} 모델 {} 교차 트레이닝 테스트 시작...".format(idx, key))
                kfold = KFold(n_splits=self.n_split, shuffle=self.flag_shuffle)
                result = cross_validate(model,
                                        self.list_memo,
                                        self.list_label,
                                        cv=kfold,
                                        # scoring="accuracy",
                                        n_jobs=-1,
                                        return_estimator=True,
                                        return_train_score=True)
                score = result['test_score'].tolist()
                max_score_index = score.index(max(score))
                estimator = result['estimator'][max_score_index]
                self.dict_model[key] = estimator
                self.setPrint("{} 모델 {} 교차 검증 accuracy : {}".format(idx, key, score))
                self.setPrint("{} 모델 {} 교차 검증 평균 accuracy : {}".format(idx, key, np.array(score).mean()))
                # add acc score for matplot graph
                self.dict_acc[key] = score


        except:
            self.setPrint('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                           sys.exc_info()[1], sys.exc_info()[2].tb_lineno))

    # main 실행함수
    def run(self):

        try:
            print(self.introText)
            input_filename = input("머신러닝 모델 학습 input excel 파일명만 입력하여 주세요.(현재 프로그램과 같은 위치에 있어야 합니다.) : ")
            file_flag = os.path.isfile(self.current_path + "\\" + input_filename + ".xlsx")

            while file_flag is False:
                input_filename = input("입력하신 파일명이 경로에 존재하지 않습니다. 정확히 다시 입력하여 주세요. : ")
                file_flag = os.path.isfile(self.current_path + "\\" + input_filename + ".xlsx")

            start_time = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            self.setPrint("START_TIME : " + start_time)
            self.train_path = self.current_path + "\\" + input_filename + ".xlsx"
            self.setPrint('Training/Test Data 전처리 시작 ...')

            # 학습데이터와 정확도 테스트를 위한 테스트 set 생성 함수 실행
            self.generate_data()
            self.setPrint('Training/Test Data 전처리 완료')

            # 단어장 vector 생성 함수 실행
            if self.v_type == 2:
                self.setPrint('TF-IDF Custom Corpus Tokenizer 생성 작업 시작 ...')
                self.generate_vector(self.list_corpus)
                self.setPrint('TF-IDF Custom Corpus Tokenizer 생성 작업 완료')
            else:
                self.setPrint('TF-IDF 기본 Tokenizer 생성 작업 시작 ...')
                self.generate_vector(self.list_memo)
                self.setPrint('TF-IDF 기본 Tokenizer 생성 작업 완료')

            # model pipeline 생성
            self.setPrint('모델 생성 작업 시작 ...')
            self.generate_pipeline()
            self.setPrint('모델 생성 작업 완료')

            # ########################__학습 시작__#############################
            # SVM SGDClassifier 방식으로 모델 생성 처리
            if self.l_type == 1:
                self.setPrint('SVM SGDClassifier 모델 학습 시작...')
                self.cross_validation({'SGDClassifier': self.dict_model['SGDClassifier']})
                self.setPrint('SVM SGDClassifier 모델 학습 완료...')

            elif self.l_type == 2:
                self.setPrint('SVC classifier 모델 학습 시작...')
                self.cross_validation({'SVC': self.dict_model['SVC']})
                self.setPrint('SVC classifier 모델 학습 완료...')

            elif self.l_type == 3:
                self.setPrint('LinerSVC classifier 모델 학습 시작...')
                self.cross_validation({'LinearSVC': self.dict_model['LinearSVC']})
                self.setPrint('LinerSVC classifier 모델 학습 완료...')

            elif self.l_type == 4:
                self.setPrint('Xgboost classifier 모델 학습 시작...')
                self.cross_validation({'xgboost': self.dict_model['xgboost']})
                self.setPrint('Xgboost classifier 모델 학습 완료...')

            # 둘다 모델 생성 처리
            else:
                self.setPrint('4개 모델 학습 시작...')
                self.cross_validation(
                    {'SGDClassifier': self.dict_model['SGDClassifier'],
                     'SVC': self.dict_model['SVC'],
                     'LinearSVC': self.dict_model['LinearSVC'],
                     'xgboost': self.dict_model['xgboost']
                     }
                )
                self.setPrint("4개 모델 학습 완료")

            self.setPrint("모델 저장 작업 시작...")
            self.save_models()
            self.setPrint("모델 저장 작업 완료")

            self.setPrint("모델 업로드 작업 시작...")
            self.load_model(self.list_model_path)
            self.setPrint("모델 업로드 작업 완료")

            self.setPrint("업로드 모델 시험 시작...")
            # ############################## 로드 모델 시험 ##############################
            sentence = ['카카오톡 이랑 카트라이더 앱 안됨 실행 시 튕기고 강제 종료 됨',
                        "핸드폰 자체 소프트웨어 업데이트 이후 문자발송시 글자수 제한되고 있음. 기존 동일한 문자정상 발송 되던것이나, 이용안됨 ."
                        " - 80명 단체문자  - 이미지 동영상 문자메세지만 보낼수 있어요. 라고 나오면서 발신 불가 ."
                        "개별로 보내면 정상  > 제조사 문의 안내 . 연결"]

            sentence, list_label = self.text_filter(sentence, None)
            self.setPrint("시험 Sentence {}".format(sentence))
            for idx, (key, value) in enumerate(self.dict_acc.items()):
                labels = self.dict_model[key].predict(sentence)
                for idx2, label in enumerate(labels):
                    self.setPrint('{} model predict {} Sentence predict label: {}'.format(key,
                                                                                          idx2,
                                                                                          self.dict_label_reverse[label]))

            self.setPrint("업로드 모델 시험 완료")
            end_time = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            self.setPrint("FINISH_TIME : " + end_time)

            self.generate_graph()
            input("\nPress any key to exit")
        except:
            self.setPrint('학습기 실행 중 에러 발생...')
            self.setPrint('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                           sys.exc_info()[1], sys.exc_info()[2].tb_lineno))


if __name__ == "__main__":
    vl = VOCLearner()
    vl.run()
