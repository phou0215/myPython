import re
import sys
import pandas as pd
import nltk
import numpy as np
import pickle
import joblib

# from konlpy.tag import Komoran  #Okt, Kkma
from konlpy.tag import Okt
from konlpy.tag import Komoran
from collections import Counter
from datetime import datetime
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.svm import LinearSVC
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import cross_val_score, KFold

class NaiveLearner():
    # l_type은 러닝 방식을 선택하는 것으로 '1'은 naive 방식 '2'는 SGD 방식 '3'은 SVM기본 '4'는 LinearSVC 방식 '5'는 모두다
    # p_type은 문장 분류시 tokenizer 모드 선택으로 '1'은 Okt '2'는 Komoran 방식
    # t_type은 테스트 시 테스트 파일을 따로 할 것인지 선택하는 것으로 1
    def __init__(self, train_path='.\\', test_path='.\\', t_type=1, l_type=1, p_type=1, test_rate=0.3):
        super(NaiveLearner, self).__init__()
        self.train_path = train_path
        self.test_path = test_path
        self.save_path = 'C:\\Users\\HANRIM\\Desktop\\sklearn_models\\'
        self.list_load_models = []
        self.l_type = l_type
        self.p_type = p_type

        self.model_nb = Pipeline([('vect', TfidfVectorizer()), ('clf', MultinomialNB(alpha=1e-2))])
        self.model_svm = Pipeline([('vect', TfidfVectorizer()), ('clf-svm', SGDClassifier(loss='hinge', epsilon=0.1, penalty='l2', alpha=1e-4, random_state=42, fit_intercept=True))])
        self.model_svc = Pipeline([('vect', TfidfVectorizer()), ('clf-svc', SVC(C=1000, random_state=42))])
        self.model_linerSVC = Pipeline([('vect', TfidfVectorizer()), ('clf-svc', LinearSVC(random_state=42))])

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


    # 시간 정보와 함께 Console에 Print 하는 함수
    def setPrint(self, text):

        current = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        print("{}:\n{}".format(current, text)+"\n")
    # Train set 과 Test set 생성하는 함수
    def generate_data(self):

        self.df_data = pd.read_excel(self.train_path, sheet_name="통품전체VOC", index_col=None)
        df_config1 = pd.read_excel(self.train_path, sheet_name="예약어리스트", index_col=None)
        df_config2 = pd.read_excel(self.train_path, sheet_name="Stop word", index_col=None)
        self.df_data = self.df_data.dropna()
        df_config1 = df_config1.dropna()
        dF_config2 = df_config2.dropna()

        self.df_data.reset_index(drop=True)
        df_config1.reset_index(drop=True)
        df_config2.reset_index(drop=True)

        self.list_special = df_config1['Special예약어'].tolist()
        self.list_rmstring = df_config2['일반형식'].tolist()
        self.list_memo = self.text_filter(self.df_data['메모'].tolist())

        self.Train_Data_X, self.Test_Data_X, self.Train_Data_Y, self.Test_Data_Y = train_test_split(self.list_memo, self.df_data['메모분류'].tolist(),
                                                                                                    test_size=0.3, random_state=42, shuffle=True)
    # TF-IDF Vector vocabulary 생성기
    def generate_vector(self):
      try:
          self.setPrint('TF-IDF Vector vocabulary 생성 작업 시작...')
          self.word_vector = TfidfVectorizer(sublinear_tf=True, tokenizer=self.splitNouns, max_df=0.75, norm='l2', ngram_range=(1, 2))
          self.custome_vocab = self.word_vector.fit_transform(self.list_memo)
          self.setPrint('TF-IDF Vector vocabulary 생성 완료...')
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

        text_data = re.sub('[-=+,#/\?^$@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>\{\}`><]\'', '', text)
        return text_data
    # tokenizer 함수
    def splitNouns(self, text):

        for item in self.list_special:
            if item in text:
                specString = item
                text = text+"/e"
                text = self.find_between(text, specString, "/e")
                if self.pattern.search(text):
                    pattern_list = self.pattern.findall(text)
                    text = self.find_between(text, specString, pattern_list[0])
                else:
                    text.replace("/e", "")
                break

        text = self.removeString(text)
        text = "\n".join([s for s in text.split('\n') if s])

        result = []
        if self.p_type == 1:
            # malist = self.komoran.pos(text)
            malist = self.twitter.pos(text)
            for word in malist:
                # if word[1] in ['NNG', 'NNP', 'NNB', 'VV', 'MAG', 'VA', 'VXV', 'UN', 'MAJ', 'SL', 'NA', 'NF'] and not word[0] in self.stopString and len(word[0]) > 1:
                if word[1] in ['Noun','Adjective','Verb', 'Unknown'] and not word[0] in self.stopString and len(word[0]) > 1:
                    result.append(word[0])
        else:
            malist = self.komoran.pos(text)
            for word in malist:
                if word[1] in ['NNG', 'NNP', 'NNB', 'VV', 'MAG', 'VA', 'VXV', 'UN', 'MAJ', 'SL', 'NA', 'NF'] and not word[0] in self.stopString and len(word[0]) > 1:
                    result.append(word[0])
        return result
    # 메모 데이터 filtering 함수
    def text_filter(self, list_doc):

        list_return = list_doc
        for idx, doc in enumerate(list_return):
            text = doc
            for item in self.list_special:
                if item in doc:
                    specString = item
                    text = text+"/e"
                    text = self.find_between(text, specString, "/e")
                    if self.pattern.search(text):
                        pattern_list = self.pattern.findall(text)
                        text = self.find_between(text, specString, pattern_list[0])
                    else:
                        text.replace("/e", "")
                    break
            text = self.removeString(text)
            text = "\n".join([s for s in text.split('\n') if s])
            list_return[idx] = text
        return list_return
    # 모델 저장 함수
    def save_models(self):

        self.setPrint('생성된 학습모델 저장 작업 시작...')
        if self.l_type == 1:
            self.setPrint('위치 : {}'.format(self.save_path+'model_nb.pkl'))
            save_model = pickle.dumps(self.model_nb)
            joblib.dump(self.model_nb, self.save_path+'model_nb.pkl')
        elif self.l_type == 2:
            self.setPrint('위치 : {}'.format(self.save_path+'model_svm.pkl'))
            save_model = pickle.dumps(self.model_svm)
            joblib.dump(self.model_svm, self.save_path+'model_svm.pkl')
        else:
            self.setPrint('위치1 : {}'.format(self.save_path+'model_nb.pkl'))
            self.setPrint('위치2 : {}'.format(self.save_path+'model_svm.pkl'))
            self.setPrint('위치3 : {}'.format(self.save_path+'model_svc.pkl'))
            self.setPrint('위치4 : {}'.format(self.save_path+'model_linerSVC.pkl'))
            save_model_1 = pickle.dumps(self.model_nb)
            save_model_2 = pickle.dumps(self.model_svm)
            save_model_3 = pickle.dumps(self.model_svc)
            save_model_4 = pickle.dumps(self.model_linerSVC)
            joblib.dump(self.model_nb, self.save_path+'model_nb.pkl')
            joblib.dump(self.model_svm, self.save_path+'model_svm.pkl')
            joblib.dump(self.model_svc, self.save_path+'model_svc.pkl')
            joblib.dump(self.model_linerSVC, self.save_path+'model_linerSVC.pkl')

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
    def cross_validation(self, list_model):

        for idx, model in enumerate(list_model):

            self.setPrint("모델 {} 교차 검증 시작...".format(idx))
            kfold = KFold(n_splits=10, shuffle=True)
            score = cross_val_score(model, self.list_memo,  self.df_data['메모분류'].tolist(), cv=kfold, scoring="accuracy")
            self.setPrint("모델 {} 교차 검증 평균 accuracy : {}".format(idx, score.mean()))

    #     for train_index, validate_index in stratifiedkfold.split(X,y):
    #         print("train index:", train_index, "validate index:", validate_index)
    #         X_train, X_validate = X[train_index], X[validate_index]
    #         y_train, y_validate = y[train_index], y[validate_index]
    #         print("train data")
    #         print(X_train, y_train)
    #         print("validate data")
    #         print(X_validate, y_validate)

    # # main 실행함수
    def run(self):

        try:
            #학습데이터와 정확도 테스트를 위한 테스트 set 생성 함수 실행
            self.generate_data()
            self.setPrint('Train X Data count: {}'.format(len(self.Train_Data_X)))
            self.setPrint('Train Y Data count: {}'.format(len(self.Train_Data_Y)))
            self.setPrint('Test X Data count: {}'.format(len(self.Test_Data_X)))
            self.setPrint('Test Y Data count: {}'.format(len(self.Test_Data_Y)))
            # 단어장 vector 생성 함수 실행
            self.generate_vector()
            self.setPrint('Word Vector 형태, (sentence {}, feature {})'.format(self.custome_vocab.shape[0], self.custome_vocab.shape[1]))
            # print(self.word_vector.vocabulary_)
            # print(self.word_vector.vocabulary_.get('와이파이'))
            # print(self.custome_vocab)

            #########################################################################__학습 시작__#########################################################################
            # Naive Bayesian 방식으로 모델 생성 처리
            if self.l_type == 1:
                self.setPrint('NB Naive Bayesian classifier 모델 학습 시작...')
                self.mode_nb = self.model_nb.fit(self.Train_Data_X, self.Train_Data_Y)
                self.setPrint('NB Naive Bayesian classifier 모델 학습 완료...')
                # 테스트 시작
                self.setPrint('테스트 시작...')
                predicted = self.mode_nb.predict(self.Test_Data_X)
                accurracy  = np.mean(predicted == self.Test_Data_Y)
                self.setPrint('NB Naive Bayesian 정확도: {} %'.format(accurracy*100))

            # SVM SGDClassifier 방식으로 모델 생성 처리
            elif self.l_type == 2:
                self.setPrint('SVM SGDClassifier 모델 학습 시작...')
                self.model_svm = self.model_svm.fit(self.Train_Data_X, self.Train_Data_Y)
                self.setPrint('SVM SGDClassifier 모델 학습 완료...')
                # 테스트 시작
                self.setPrint('테스트 시작...')
                predicted = self.model_svm.predict(self.Test_Data_X)
                accurracy  = np.mean(predicted == self.Test_Data_Y)
                self.setPrint('SVM SGDClassifier 정확도: {} %'.format(accurracy*100))
            # 둘다 모델 생성 처리
            else:
                self.setPrint('NB / SGD / SVC / LinearSVC 4개 모델 학습 시작...')
                self.mode_nb = self.model_nb.fit(self.Train_Data_X, self.Train_Data_Y)
                self.setPrint('NB Naive Bayesian classifier 모델 학습 완료...')
                self.model_svm = self.model_svm.fit(self.Train_Data_X, self.Train_Data_Y)
                self.setPrint('SVM SGDClassifier 모델 학습 완료...')
                self.model_svc = self.model_svc.fit(self.Train_Data_X, self.Train_Data_Y)
                self.setPrint('SVC classifier 모델 학습 완료...')
                self.model_linerSVC = self.model_linerSVC.fit(self.Train_Data_X, self.Train_Data_Y)
                self.setPrint('linerSVC classifier 모델 학습 완료...')
                # 테스트 시작
                self.setPrint('테스트 시작...')
                predicted = self.mode_nb.predict(self.Test_Data_X)
                accurracy  = np.mean(predicted == self.Test_Data_Y)
                self.setPrint('NB Naive Bayesian 정확도: {} %'.format(accurracy*100))
                predicted = self.model_svm.predict(self.Test_Data_X)
                accurracy  = np.mean(predicted == self.Test_Data_Y)
                self.setPrint('SVM SGDClassifier 정확도: {} %'.format(accurracy*100))
                predicted = self.model_svc.predict(self.Test_Data_X)
                accurracy  = np.mean(predicted == self.Test_Data_Y)
                self.setPrint('SVC classifier 정확도: {} %'.format(accurracy*100))
                predicted = self.model_linerSVC.predict(self.Test_Data_X)
                accurracy  = np.mean(predicted == self.Test_Data_Y)
                self.setPrint('linearSVC classifier 정확도: {} %'.format(accurracy*100))

            self.save_models()
            self.load_model([self.save_path+'model_nb.pkl', self.save_path+'model_svm.pkl', self.save_path+'model_svc.pkl', self.save_path+'model_linerSVC.pkl'])

            sentence = ["3G로 뜨면서 음질끊김, 데이터속도느림 - 와이파이 켜져있어서 끔 - 단말기상 3G모드로 되어있어서 데이터네트워크방식 재설정 및 전원 재부팅 후 확인 예정", "'핸드폰 자체 소프트웨어 업데이트 이후 문자발송시 글자수 제한되고 있음.  기존 동일한 문자정상 발송 되던것이나, 이용안됨 .  \
            - 80명 단체문자  - 이미지 동영상 문자메세지만 보낼수 있어요. 라고 나오면서 발신 불가 .   개별로 보내면 정상  > 제조사 문의 안내 . 연결"]
            sentence = [self.removeString(x) for x in sentence if x]
            label_1 = self.list_load_models[0].predict(sentence)
            label_2 = self.list_load_models[1].predict(sentence)
            label_3 = self.list_load_models[2].predict(sentence)
            label_4 = self.list_load_models[3].predict(sentence)

            self.setPrint(label_1)
            self.setPrint(label_2)
            self.setPrint(label_3)
            self.setPrint(label_4)
            # 교차 검증
            self.cross_validation(self.list_load_models)
        except:
          self.setPrint('학습기 실행 중 에러 발생...')
          self.setPrint('Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno))







# def tokenizer(self, doc):
#     return ['/'.join(x) for x in twitter.pos(doc, norm=True, stem=True)]

# # sentence classfication start
# list_train = []
# list_test = []
# twitter = Okt()
# tokens = []
# labels = []
# df_train = pd.read_excel('C:\\Users\\TestEnC\\Desktop\\learn_data.xlsx')
# # df_test = pd.read_excel('C:\\Users\\TestEnC\\Desktop\\메모.xlsx')
#
# for i in range(df_train.shape[0]):
#     temp_memo = df_train.at[i,'메모']
#     temp_label = df_train.at[i,'메모분류']
#     list_train.append((temp_memo, temp_label))
#
# # print(df_train.head(10))
#
# train_doc = [(tokenizer(x),y) for (x,y) in list_train]
# tokens = [x for y in train_doc for x in y[0]]
# # print(tokens[:10])
# print('start')
# df_test['예측'] = ''
# train_final = [(check_exist(x),y) for x ,y  in list_train]
# classifier = nltk.NaiveBayesClassifier(train_final)
#
# print('시작')
# for i in range(df_test.shape[0]):
#     test_doc = twitter.pos(df_test.at[i,'메모'])
#     test_sentence = {word:(word in tokens) for word in test_doc}
#     predict_label = classifier.classify(test_sentence)
#     print(predict_label)
#     df_test.at[i,"예측"] = str(predict_label)
#
# with pd.ExcelWriter('C:\\Users\\TestEnC\\Desktop\\메모예측.xlsx') as writer:
#     df_test.to_excel(witer, sheet_name='예측')



# with open('', wt , encoding='utf-8') as fw:
#     fw.write()


if __name__ == "__main__":
    bl = NaiveLearner(train_path='C:\\Users\\HANRIM\\Desktop\\learn_data_5000.xlsx', test_path=None, l_type=3, p_type=1)
    bl.run()
