from functional import seq
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.multiclass import OneVsRestClassifier
from sklearn.model_selection import GridSearchCV
from functional.streams import Sequence
import pandas as pd
import numpy as np
import os
from typing import Dict, List, Tuple, Optional
import random
from collections import namedtuple
from random import shuffle
import pandas as pd
from IPython.core.display import HTML

files = os.listdir("../ustawy")

ustawy = []

for f in files:
    ustawy.append(open("../ustawy/"+f).read())

print(ustawy[1])

def is_bill_changing(string):
    return "o zmianie ustawy" in string.replace("\n", " ")

files_not_changing = []
files_changing = []

for f in files:
    if is_bill_changing(f):
        files_changing.append(f)
    else:
        files_not_changing.append(f)

fc = []
fnc = []

for f in files_not_changing:
    if "art" in f:
        fnc.append(f.split("art", maxsplit=1)[1])

for f in files_changing:
    if "art" in f:
        fc.append(f.split("art", maxsplit=1)[1])

data = fc + fnc
shuffle(data)

def select_full(string):
    return string

def select_percent(string):
    lines = string.split("\n")
    count = len(lines)*0.1
    return "\n".join(random.choices(lines,k=count))

def select_ten(string):
    lines = string.split("\n")
    return "\n".join(random.choices(lines,k=10))

def select_one(string):
    lines = string.split("\n")
    return random.choices(lines, k=1)

size = 0
for d in data:
    size = size + len(d)

training = []
validation = []
testing = []

current_size=0

for d in data:
    if current_size < 0.6 * size:
        training.append(d)
    elif current_size < 0.8 * size:
        validation.append(d)
    else:
        testing.append(d)
    current_size = current_size + len(d)


#SVM + TF_IDF
stopwords = open("./stopwords").read().split("\n")

def svmtf(selector):
    selected = selector(training)
    xtrain,ytrain = [x for x in selected], [x in fc for x in selected]
    #xvalid,yvalid = [x for x in validation], [x in fc for x in validation\]
    #xtest,ytest = [x for x in testing], [x in fc for x in testing]
    params = [('tfidf', TfidfVectorizer(stop_words=stopwords)),('clf', OneVsRestClassifier(LinearSVC(), n_jobs=3)),]
    grid_params = {'tfidf__max_df': ( 0.25, 0.5,0.75,),'tfidf__ngram_range': [(1,2),(1, 3)],"clf__estimator__C": [0.1,0.2,0.25,0.3],}


    grid_search_tune = GridSearchCV(params, grid_params, cv=2, n_jobs=3, verbose=10, return_train_score =True)
    grid_search_tune.fit(xtrain, ytrain)


    return (
        grid_search_tune.best_estimator_,
        grid_search_tune.best_params_,
        grid_search_tune.cv_results_
    )


best_est, best_params, results  = svmtf(select_full)
print(best_params)




