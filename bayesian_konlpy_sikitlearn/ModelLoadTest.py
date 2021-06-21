import re
import os
import sys

import pickle
import joblib
import pandas as pd
import numpy as np

from konlpy.tag import Okt
from konlpy.tag import Komoran

from collections import Counter
from datetime import datetime
import matplotlib.pyplot as plt


# Konlpy text parsing

class ModelLoad():

    def __init__(self):
        super(ModelLoad, self).__init__()
        self.p_type = 1
        self.current_path = os.getcwd()
        self.load_path = self.current_path + '\\sklearn_models\\'
        self.vect_path = self.current_path + '\\sklearn_vect\\'
        self.train_path = self.current_path + "\\learn_data.xlsx"
        self.konlpy_parser = None
        if self.p_type == 1:
            self.konlpy_parser = Okt()
        else:
            self.konlpy_parser = Komoran()
        self.test_file_path = self.current_path + '\\데이터분류_50.xlsx'
        self.list_load_models = []
        self.list_text = []
        self.list_true_label = []
        self.dict_assemble = None
        self.dict_labels = {0: '데이터', 1: '데이터 지연', 2: '통화불량', 3: '분류없음', 4: 'USIM', 5: '음질불량',
                            6: 'APP', 7: '문자 지연', 8: '문자', 9: '통화권이탈', 10: '부가서비스'}

        self.list_special = []
        self.list_rmstring = []
        self.pattern = re.compile("([1-9]{1,2}\.)")
        self.stopString = ["안내", "여부", "사항", "장비", "확인", "원클릭", "품질", "후", "문의", "이력", "진단", "부탁드립니다.",
                           "증상", "종료", "문의", "양호", "정상", "고객", "철회", "파이", "특이", "간다", "내부", "외부", "권유",
                           "성향", "하심", "해당", "주심", "고함", "초기", "무관", "반려", "같다", "접수", " 무관", "테스트", "연락",
                           "바로", "처리", "모두", "있다", "없다", "하다", "드리다", "않다", "되어다", "되다", "부터", "예정", "드리다",
                           "해드리다", "신내역", "현기", "가신", 'ㅜ', "ㅠ"]

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

    # def remove_special(self, text):
    #
    #     # 영문 모두 소문자로 변경
    #     text_data = text.lower()
    #     # 전화번호 모두 'tel로 치환'
    #     text_data = re.sub(r'\d{2,3}[-\.\s]*\d{3,4}[-\.\s]*\d{4}(?!\d)', 'tel', text_data)
    #     # 화폐는 'money'로 치환
    #     text_data = re.sub(r'\d{1,3}[,\.]\d{1,3}[만\천]?\s?[원]|\d{1,5}[만\천]?\s?[원]', 'money', text_data)
    #     text_data = re.sub(r'일/이/삼/사/오/육/칠/팔/구/십/백][만\천]\s?[원]', 'money', text_data)
    #     text_data = re.sub(r'(?!-)\d{2,4}[0]{2,4}(?!년)(?!.)|\d{1,3}[,/.]\d{3}', 'money', text_data)
    #     text_data = re.sub(r'[1-9]g', ' cellular ', text_data)
    #     text_data = re.sub(r'(유심|usim|sim|esim)', 'usim', text_data)
    #     text_data = re.sub(r'(sms|mms|메시지)', 'message', text_data)
    #     text_data = re.sub(r'통신.?내역', 'list', text_data)
    #     # web 주소는 'url'로 변경
    #     text_data = re.sub(
    #         r'(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})',
    #         'url',
    #         text_data)
    #     # 그 외의 특수문자는 모두 삭제
    #     text_data = re.sub(r'[-=+,_#/\?^$@*\"※~&%ㆍ!』\‘|\(\)\[\]\<\>\{\}`><\':;■◈▶●★☎]', ' ', text_data)
    #     # 앞서 list_rmstring 선언된 단어들 모두 제거
    #     for item in self.list_rmstring:
    #         text_data = text_data.replace(item, "")
    #     # 필수 제거 단어 제거
    #     for item in self.stopString:
    #         text_data = text_data.replace(item, "")
    #
    #     # 앞 뒤 공백 제거
    #     text_data = text_data.strip()
    #     return text_data

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

    # remove text special char and replace
    def remove_special(self, text):

        # text_data = re.sub(r'(t.?와이.?파이.?존|t.?wifi|티.?와이.?파이)', 'wifi', text_data)
        # text_data = re.sub(r'(1.?칸|2.?칸|3.?칸|안테나.?감도|한.?칸|두.?칸|세.?칸|감도)', 'antenna', text_data)
        # text_data = re.sub(r'(모바일.?데이터|(셀|샐|세).?룰러.?데이터|데이터.?(품질|네트.?워크)|(셀|샐|세).?룰러|데이터)', ' cellular ', text_data)
        # text_data = re.sub(r'((장소|위치).?무관|위치.?(무고|유.?무관))', 'place', text_data)
        # text_data = re.sub(r'(목소리|(음성|통화).?소리|스피커|통화.?(음성|음질)|음성|음질|소리)', 'sound', text_data)
        # text_data = re.sub(r'(서비스.?(없음|이용.?불가|이탈|제한)|신호.?(이탈|없음))', 'nonservice', text_data)
        # text_data = re.sub(r'(속도.?제어|제어.?상태)', 'sctrl', text_data)
        # text_data = re.sub(r'(오프|끔|끄고|꺼서|꺼짐|꺼지고)', 'off', text_data)
        # text_data = re.sub(r'(켬|키고|켜고|켜서|켜짐|켜지고)', 'on', text_data)

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

    # Train set 과 Test set 생성하는 함수
    def generate_data(self):

        try:
            # input excel 읽어서 data frame으로 변환
            df_config1 = pd.read_excel(self.train_path, sheet_name="예약어리스트", index_col=None)
            df_config2 = pd.read_excel(self.train_path, sheet_name="Stop word", index_col=None)
            df_test = pd.read_excel(self.test_file_path, sheet_name="통품전체VOC", index_col=None)

            # N/A 값 drop
            # df_config1 = df_config1.dropna()
            # df_config2 = df_config2.dropna()

            # df_config1.reset_index(drop=True)
            # df_config2.reset_index(drop=True)

            # 예약어 설정 값 선택
            self.list_special = df_config1['Special예약어'].dropna().tolist()
            # 단어 제거 형식 선택
            self.list_rmstring = df_config2['일반형식'].dropna().tolist()
            # test 데이터 추출
            self.list_text = df_test['메모'].tolist()
            self.list_true_label = df_test['메모분류'].tolist()
            self.dict_assemble = df_test['메모분류'].value_counts().to_dict()

        except:
            self.setPrint('Error: {}. {}, line: {}'.format(sys.exc_info()[0], sys.exc_info()[1],
                                                           sys.exc_info()[2].tb_lineno))

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
            return None, None

    def load_model(self, list_path):

        try:
            for path in list_path:
                algorithm = joblib.load(path)
                self.list_load_models.append(algorithm)
            self.setPrint('모델 Load 작업 완료. 완료 모델 수: {}'.format(len(self.list_load_models)))
        except:
            self.setPrint('모델 Load 작업 중 에러 발생...')
            self.setPrint('Error: {}. {}, line: {}'.format(sys.exc_info()[0],
                                                           sys.exc_info()[1],
                                                           sys.exc_info()[2].tb_lineno))


if __name__ == "__main__":
    load = ModelLoad()

    current_path = os.getcwd()
    load_path = current_path + '\\sklearn_models\\'

    list_load_path = [load_path + 'model_svm.pkl',
                      load_path + 'model_svc.pkl',
                      load_path + 'model_linerSVC.pkl',
                      load_path + 'model_xgboost.pkl',
                      ]
    load.load_model(list_load_path)
    load.setPrint("업로드 모델 시험 시작...")
    load.generate_data()
    # ############################## 로드 모델 시험 ##############################
    list_text, list_true_label = load.text_filter(load.list_text, load.list_true_label)
    total_data = len(list_text)

    # load.setPrint("시험 Sentence : {}".format(list_text))
    load.setPrint("시험 Text 수 : {}".format(len(list_text)))
    load.setPrint("True 라벨링 수 : {}".format(len(list_true_label)))
    load.setPrint("클레스 분포 : {}".format(load.dict_assemble))

    for idx, model in enumerate(load.list_load_models):

        dict_true_class = {'데이터': 0, '데이터 지연': 0, '통화불량': 0, '분류없음': 0, 'USIM': 0, '음질불량': 0,
                           'APP': 0, '문자': 0, '통화권이탈': 0}
        dict_true_accuracy = dict_true_class.copy()
        predict_labels = model.predict(list_text).tolist()
        labels = [load.dict_labels[x] for x in predict_labels]
        total_flag = []

        for idx2, item2 in enumerate(labels):
            if item2 == list_true_label[idx2]:
                dict_true_class[item2] = dict_true_class[item2] + 1
                total_flag.append(1)
            else:
                total_flag.append(0)

        accuracy = round(sum(total_flag) / total_data, 3)
        for (key, value) in load.dict_assemble.items():
            dict_true_accuracy[key] = round(dict_true_class[key]/value, 3)

        load.setPrint('{} model predict Sentence label: {}'.format(idx, labels))
        load.setPrint('{} model True/False {} : '.format(idx, total_flag))
        load.setPrint('{} model Total accuracy : {}'.format(idx, accuracy))
        load.setPrint('{} model True count each class: {}'.format(idx, dict_true_class))
        load.setPrint('{} model accuracy each class: {}'.format(idx, dict_true_accuracy))

    load.setPrint("업로드 모델 시험 완료")
