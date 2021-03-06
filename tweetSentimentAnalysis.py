# -*- coding: utf-8 -*-
"""
Created on Sat Sep 02 00:34:54 2017

@author: shyam
"""
import pandas as pd
import re

import nltk
from nltk.corpus import stopwords

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import PCA
from sklearn.decomposition import TruncatedSVD
from sklearn.model_selection import train_test_split

import numpy as np

from keras.layers import Dense
from keras.models import Sequential
from keras import optimizers
#%%
def polishData(df):
    
    data = []

    for i in xrange(0, df.shape[0]):
        no_links = re.sub("https?:\/\/.*[\r\n]*", " ", df.iloc[:,0][i], flags=re.MULTILINE)

        letters_only = re.sub("[^a-zA-Z]", " ", no_links)

        lower_case = letters_only.lower()
        words = lower_case.split()
    
        words = [w for w in words if not w in stopwords.words("english")]

        final_string = " ".join(words)
    
        data.append(final_string)
    
    return data
#%%
def labelsOneHot(df):
    sentiOneHot = pd.get_dummies(df.iloc[:,1])

    labels = np.empty((sentiOneHot.shape), dtype = int)

    for i in xrange(0,sentiOneHot.shape[1]):
        numbers = np.array(sentiOneHot.iloc[:,i])
        labels[:,i] = numbers

    return labels
#%%
def polishDataSet(df):
    data = polishData(df)
    labels = labelsOneHot(df)
    
    return data, labels
#%%
def BOW(train_data, analyzerType, ngram_value):
    
    bow = CountVectorizer(analyzer = analyzerType, ngram_range = (ngram_value, ngram_value))
    train_data_bow = bow.fit_transform(train_data)
    print train_data_bow.shape
    return train_data_bow, bow
#%%
def TFIDF(train_data, analyzerType, ngram_value):
    
    tfidf = TfidfVectorizer(analyzer = analyzerType, ngram_range = (ngram_value, ngram_value))
    train_data_tfidf = tfidf.fit_transform(train_data)
    print train_data_tfidf.shape
    return train_data_tfidf, tfidf
#%%
def SVD(train_data_vectorized, n_components):
    svd = TruncatedSVD(n_components=n_components, n_iter=7, random_state=42)
    train_data_reduced = svd.fit_transform(train_data_vectorized)
    train_data_reduced = np.array(train_data_reduced)
    print train_data_reduced.shape
    return train_data_reduced, svd
#%%
"""change the n_components value so that 85% of the variance is captured"""

def dataReduce(train_data, vectorizer, reducer = None, n_components = 1000, ngram = False, ngram_value = 1):
    """test_split = value in decimals"""

    if ngram == False:
        analyzerType = 'word'
    else:
        analyzerType = 'char'
        
    if vectorizer == 'bow':
        train_data_vectorized, vectorizer = BOW(train_data, analyzerType, ngram_value)
    elif vectorizer == 'tfidf':
        train_data_vectorized, vectorizer = TFIDF(train_data, analyzerType, ngram_value)
        
    train_data_reduced, reducer = SVD(train_data_vectorized, n_components)
    
    return train_data_reduced, vectorizer, reducer
#%%
def makeModel(train_data_reduced, train_labels, hidden_layer = 30, 
              activation = 'relu', optimizer = 'adam', loss = 'categorical_crossentropy'):
    
    model = Sequential()
    model.add(Dense(hidden_layer,input_dim = train_data_reduced.shape[1], activation = activation))
    model.add(Dense(train_labels.shape[1], activation = 'softmax'))
    model.compile(optimizer = optimizer, loss = loss, metrics = ['accuracy'])
    
    return model
#%%
def evaluateModel(test_data, test_labels, model, vectorizer = None, reducer = None):
    
    if vectorizer:
        test_data_vectorized = vectorizer.transform(test_data)
    else:
        test_data_vectorized = test_data
        
    if reducer:
        test_data_reduced = reducer.transform(test_data_vectorized)
        test_data_reduced = np.array(test_data_reduced)
    else:
        test_data_reduced = np.array(test_data_vectorized)
             
    scores = model.evaluate(test_data_reduced, test_labels)
    print("\n%s: %.2f%%" % (model.metrics_names[1], scores[1]*100))   
        
    return scores
#%%
path = "./twitter.csv"
df = pd.read_csv(path)
#%%
data, labels = polishDataSet(df)
#%%
test_split = 0.20
train_data, test_data, train_labels, test_labels = train_test_split(data, labels, test_size = test_split, random_state = 42)
#%%
train_data_reduced, vectorizer, reducer = dataReduce(train_data,'tfidf', n_components = 550 , ngram = True, ngram_value = 2)
#%%
model = makeModel(train_data_reduced, train_labels, hidden_layer = 50, 
                  activation = 'relu', optimizer = 'adam', loss = 'categorical_crossentropy')
#%%
epochs = 20
batch_size = 32
model.fit(train_data_reduced, train_labels, epochs = epochs, batch_size = batch_size)
#%%
model.evaluateModel(test_data, test_labels, model, vectorizer, reducer)

