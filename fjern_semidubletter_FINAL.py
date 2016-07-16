# -*- coding: cp1252 -*-
import string, xlrd, nltk, unicodedata, pickle, re, time, random, difflib

start = time.time()
f = open('artikler', 'r')
artikler = pickle.load(f)
f.close()

semidubletter = []
i = 0
while i < len(artikler):
    semi_dub_set = [0, []]
    j = len(artikler)-1
    if i % 10 == 0:
        print (i),
    while j > i:
        if difflib.SequenceMatcher(None, artikler[i].tekst, artikler[j].tekst).ratio() > 0.75:
            semi_dub_set[0] = artikler[i]
            semi_dub_set[1].append(artikler[j])
            artikler.remove(artikler[j])
        j -= 1
    if semi_dub_set != [0, []]:
        semidubletter.append(semi_dub_set)
    i += 1
end = time.time()
print ("Væk med semidubletter:", end-start)

f = open("semidubletter", "wb") # gem semidubletter i en fil
pickle.dump(semidubletter, f)
f.close()

f = open("artikler_USD", "wb") # gem artikler uden semi-dubletter i en fil
pickle.dump(artikler, f)
f.close()
