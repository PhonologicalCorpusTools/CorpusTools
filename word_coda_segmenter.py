import csv

import csv

#http://stackoverflow.com/questions/24662571/python-import-csv-to-list


import csv
from collections import OrderedDict
coda_dict = OrderedDict()
with open('codas.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        for column, value in row.items():
            coda_dict.setdefault(column, []).append(value)


corpus = ["m.e.t.e.s.a", "a.s.a.m.k.y.o", "u.h.a.l.u", "s.i", "m.e.s.e.r.a", "m.e.s.e.t.a", "e", "n.j.o.s.o",
          "l.u.N.o.b.a", "r.w.i", "m.a.s.e.s.a", "a.l.a.m.k.y.o", "a.n.a", "k.i", "m.e.r.e.s.a", "i.N.i.f.w.e", "a",
          "r.o.d.u.s.u", "t.i", "f.p.e.m.i", "l.w.a.f.w.a.s.u", "l.j.o.s.a", "h.e.N", "m.e.s.e.s.a", "l.o.s.u.d.u",
          "r.i", "o.N", "r.o.s.u.d.u", "s.u.N.o.b.a", "e.N.i.f.w.e", "h.k.a.h.j.e", "u.s.a.l.u", "s.w.i",
          "n.w.a.f.w.a.p.u", "l.w.a.f.w.a.p.u", "f.j.a.N", "a.N", "f.m.u", "s.w.a.f.w.a.p.u", "l.j.o.s.o"]

#Defines the syllable delimiter
try:
    SyllableDelimiter
except NameError:
    SyllableDelimiter = "$"


codas = coda_dict['Coda']
#segments syllables, putting in the delimiter at syllable boundaries and replacing periods with dashes to indicate

coda_dict = OrderedDict()
for cluster in codas:
    dash_cluster = cluster.replace(".", "-")
    new_cluster =  dash_cluster + SyllableDelimiter
    coda_dict[cluster] = new_cluster

#http://stackoverflow.com/questions/6116978/python-replace-multiple-strings
def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text


segmented_words = []
for word in corpus:
    segmented_words.append(replace_all(word, coda_dict))

SegmentDict = OrderedDict(zip(corpus,segmented_words))


#http://stackoverflow.com/questions/8685809/python-writing-a-dictionary-to-a-csv-file-with-one-line-for-every-key-value
with open('segmented_by_codas.csv', 'w') as csvfile:
    fieldnames=('Word','Segmented_Word')
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for key, value in SegmentDict.items():
        writer.writerow({'Word': key, 'Segmented_Word': value})