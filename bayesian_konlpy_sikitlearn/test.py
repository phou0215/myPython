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
import matplotlib.pyplot as plt
# from nltk.tokenize import word_tokenize

# from xgboost import plot_importance
# from xgboost import XGBClassifier

# from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.svm import LinearSVC
from sklearn.linear_model import SGDClassifier
# from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, KFold

model_file_path