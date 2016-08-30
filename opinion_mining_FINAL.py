# -*- coding: cp1252 -*-
import string, xlrd, nltk, unicodedata, pickle, re, time, random, difflib
import numpy as np
from sklearn import cross_validation, datasets, svm
from sklearn.feature_selection import RFE
#import xml.etree.cElementTree as ET
global_start = time.time()

# indlæser artikel-klassen
class artikel:
    def __init__(self, tekst = "", overskrift = "", kategori = "", kilde = "", id_kode = "",
                 klasse = ""):
        self.tekst = tekst
        self.overskrift = overskrift
        self.kategori = kategori
        self.kilde = kilde
        self.id_kode = id_kode
        self.klasse = klasse

# indlæser alle de picklede elementer fra pre_processing.py

start = time.time()
f = open("artikler_USD", "r")
artikler = pickle.load(f)
f.close()

#f = open("semidubletter", "r")
#semidubletter = pickle.load(f)
f = open("categories", "r")
categories = pickle.load(f)
f = open("leksikon", "r")
leksikon = pickle.load(f)
f = open("termer", "r")
termer = pickle.load(f)
end = time.time()
print ("Loading pickles:", end-start, "seconds")

from nltk.corpus import stopwords
stopord = stopwords.words('danish')
for i in range(len(stopord)):
    stopord[i] = stopord[i].decode('utf-8')

start = time.time()
def find_feature_termer(leksikon, lo=50, hi=400): # finder featuretermerne baseret på en hi- og lo-tærskel
    feature_termer = []        
    for term in leksikon:
        if leksikon[term] > lo and leksikon[term] < hi and term not in stopord:
            feature_termer.append(term)
    return feature_termer
feature_termer = find_feature_termer(leksikon)
feature_termer_uden_tal = [] # fjerner tal-strenge
for term in feature_termer:
    try:
        tal = int(term)
    except:
        feature_termer_uden_tal.append(term)
feature_termer = feature_termer_uden_tal
end = time.time()
print ("Constructing feature_termer:", end-start, "seconds")

def term_extract(doc): # udtrækker dokumentets termer. Dubletter forekommer
    tekst = re.sub('["-,.:;()\'!?]', '', doc.tekst.lower())
    termer = set(tekst.split())
    return termer

def doc_feature_vector(doc): # laver dokumentets featurevektor
    features = {}
    doc_termer = term_extract(doc)
    for term in feature_termer:
        if term in doc_termer:
            features[term] = 1
        else:
            features[term] = 0
    return features

try: # indlæs IM_featuresets, hvis det eksisterer - ellers oprettes dette
    start = time.time()
    f = open("Infomedia_featuresets", "r")
    IM_featuresets = pickle.load(f)
    f.close()
    end = time.time()
    print ("Indlæser featuresets:", end-start, "sekunder")
except:
    f = open("Infomedia_featuresets", "w")
    IM_featuresets = []
    for doc in artikler:
        IM_featuresets.append((doc_feature_vector(doc), doc.klasse))
    pickle.dump(IM_featuresets, f)
    f.close()
    end = time.time()
    print ("Opretter featuresets:", end-start, "sekunder")

## SCIKIT-LEARN

#indlæser IM_data og IM_target
start = time.time()
try:
    f = open('IM_data', 'r')
    g = open('IM_target', 'r')
    IM_data = pickle.load(f)
    IM_target = pickle.load(g)
    f.close()
except:
    IM_data = []
    IM_target = np.array([])
    for fv in IM_featuresets:
        vector = np.array([])
        for term in feature_termer:
            vector = np.append(vector, fv[0][term])
        IM_data.append(vector)
        IM_target = np.append(IM_target, fv[1])
    f = open('IM_data', 'w')
    g = open('IM_target', 'w')
    pickle.dump(IM_data, f)
    pickle.dump(IM_target, g)
    f.close()
    g.close()
end = time.time()
print ("Indlæsning af IM_data og IM_target:", end-start)

print (IM_data[:2])

X_train, X_test, y_train, y_test = cross_validation.train_test_split(
    IM_data, IM_target, test_size=0.1, random_state=0)

from sklearn.naive_bayes import BernoulliNB
bnb = BernoulliNB()
svc = svm.SVC(kernel='linear', C=1)

#10-fold stratified shufflesplits:
from sklearn.cross_validation import StratifiedShuffleSplit
sss = StratifiedShuffleSplit(IM_target, folds, test_size=0.1,
                                     indices=True, random_state=None)
#scores = cross_validation.cross_val_score(svc, IM_data, IM_target, cv=sss)

global_end = time.time()

print ("Total runtime:", global_end-global_start, "seconds")

# skriver oversigt over kategorier til et Excel-ark
##from tempfile import TemporaryFile
##from xlwt import Workbook
##
##kategori_xls = Workbook()
##sheet1 = kategori_xls.add_sheet('Pos+neg artikler_USD')
##for i in range(len(k_sorted)):
##    for j in range(len(kat_liste[i])):
##        sheet1.write(i, j, kat_liste[i][j])
##kategori_xls.save('kategorier_USD.xls')
