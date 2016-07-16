# -*- coding: cp1252 -*-
import string, xlrd, nltk, unicodedata, pickle, os, re, time
import xml.etree.cElementTree as ET

start = time.time()

# indlæser Excel-arket med xlrd
nykredit = xlrd.open_workbook('Nykredit_feed.xls')
nykredit_data = nykredit.sheet_by_index(0)
nykredit_tekst = nykredit.sheet_by_index(1)

docs_raw_XML = {} # dict-entries af formen docs_raw_XML[id] = xml
docs_data_temp = []
for i in range(0,2333):
    docs_raw_XML[nykredit_tekst.row_values(i)[0]] = nykredit_tekst.row_values(i)[1]
    try:
        docs_data_temp.append(nykredit_data.row_values(i))
    except:
        pass
del docs_raw_XML[''] # xls-filen indeholder dokumenter, der ikke har noget id
print ("Elementer i docs_raw_XML: ", len(docs_raw_XML))

docs_data = []
# docs_data_temp indeholder dubletter. Disse bliver fjernet i docs_data
for key in docs_raw_XML.keys():
    for doc in docs_data_temp:
        if doc[2] == key:
            docs_data.append(doc)
            break

class artikel:
    def __init__(self, tekst = "", overskrift = "", kategori = "", kilde = "", id_kode = "",
                 klasse = ""):
        self.tekst = tekst
        self.overskrift = overskrift
        self.kategori = kategori
        self.kilde = kilde
        self.id_kode = id_kode
        self.klasse = klasse

artikler = [] # liste af artikel-objekter
error_list = [] # liste, der indeholder dokumenter, der ikke kan parses med regex
regex = re.compile("<block[^>]*>(.*)</block>", re.UNICODE|re.DOTALL)
for doc in docs_data:
    xml = docs_raw_XML[doc[2]]
    clean_xml = xml.replace('\\', '/')
    try:
        mobj = regex.search(clean_xml)
        content = mobj.groups()[0]
        content = re.sub('<[^>]*>', '', content)
        artikler.append(artikel(tekst=content, id_kode=doc[2], kategori=doc[1],
                                kilde=doc[8], overskrift=doc[11], klasse=doc[15]))
    except:
        error_list.append((clean_xml, doc[0]))
print ("Antal artikler:", len(artikler))

# fjerner dubletter (hvad content angår)
artikler_content = []
artikler_filtered = []
artikler_duplicates = {} # registrerer dubletter og deres id og klasse
artikler_neutral = []
for a in artikler:
    if not a.tekst in artikler_content:
        artikler_content.append(a.tekst)
        if a.klasse == -1:
            artikler_neutral.append(a)
        else:
            artikler_filtered.append(a)
    else:
        try:
            artikler_duplicates[a.tekst]["id"].append(a.id_kode)
            artikler_duplicates[a.tekst]["polarities"].append(a.klasse)
        except:
            artikler_duplicates[a.tekst] = {"id": a.id_kode,
                                                 "polarities": a.klasse}

"""
# counters, der registrerer hvor mange dubletter af hver klasse
neg_count = 0
pos_count = 0
neu_count = 0
for a in artikler_duplicates:
    if artikler_duplicates[a]["polarities"][0] == 0:
        neg_count += len(artikler_duplicates[a]["polarities"])
    if artikler_duplicates[a]["polarities"][0] == 1:
        pos_count += len(artikler_duplicates[a]["polarities"])
    if artikler_duplicates[a]["polarities"][0] == -1:
        neu_count += len(artikler_duplicates[a]["polarities"])
print ("Dubletter:\n\tpos:", pos_count, "\n\tneg:", neg_count, "\n\tneu:", neu_count)
"""

artikler = artikler_filtered

print ("Antal artikler (efter dubletter fjernet):", len(artikler)+len(artikler_neutral))
print ("Antal neutrale artikler:", len(artikler_neutral))

f = open("artikler", "wb") # gemmer artikler i en fil
pickle.dump(artikler, f)
f.close()

# oversigt over fordelingen af artikler klassevist
pos_docs = []
neg_docs = []
neutral_docs = []
for doc in artikler:
    if doc.klasse == -1:
        neutral_docs.append(doc)
    if doc.klasse == 1:
        pos_docs.append(doc)
    if doc.klasse == 0:
        neg_docs.append(doc)
print ("Artikler fordelt klassevist, efter de neutrale er fjernet:")
print ("\tpos:", len(pos_docs), "\n\tneg:", len(neg_docs), "\n\tneutral:", len(neutral_docs))

kategorier = {}
# laver en oversigt over hvor mange dokumenter af de forskellige kategorier:
for doc in artikler:
    if doc.kategori in kategorier.keys():
        kategorier[(doc.kategori)] += 1
    else:
       kategorier[(doc.kategori)] = 1 

f = open("kategorier", "wb") # gemmer kategorier i en fil
pickle.dump(kategorier, f)
f.close()

"""
f = open('ia_artikler', 'r')
ia_artikler = pickle.load(f)
f.close()
"""

# frekvensdistribution af termerne i dokumentsamlingen
leksikon = {}
for doc in artikler:
    content_clean = re.sub('["-,.:;\'!?]', '', doc.tekst)
    for term in content_clean.split():
        term = term.lower()
        if term in leksikon:
            leksikon[term] += 1
        else:
            leksikon[term] = 1

f = open("leksikon", "wb") # gemmer leksikon i en fil
pickle.dump(leksikon, f)
f.close()

termer = list(leksikon.keys())
f = open("termer", "wb") # gemmer termer i en fil
pickle.dump(termer, f)
f.close()

end = time.time()
print ("Samlet processeringstid:", end-start)
