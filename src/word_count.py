from collections import Counter 
import pickle
import os, sys
import glob, glob
import nltk
import re
from nltk import sent_tokenize, word_tokenize
from nltk.probability import FreqDist
from nltk.corpus import stopwords
from nltk import bigrams

finpath = "input_test\\"
foutpath = "output_test\\"

word_filtered = []
word_filtered_bigram = []

for f in glob.glob(finpath+"*.txt"):
    with open(f, encoding='utf-8', errors='ignore') as fin:
        '''
        f_name = f.split("\\")[-1]
        f_name = re.findall(r'\d+', f_name)[0]
        '''
        # uni-gram
        note = fin.read()
        
        text = word_tokenize(note)
        
        word_filtered_incre = [word.lower() for word in text if word.lower() not in stopwords.words('english') and re.search('\w+', word) and not re.search('\d', word)]
        
        word_filtered += word_filtered_incre
        
        # bi-gram
        sents = sent_tokenize(note)
        word_sent = [word_tokenize(sent) for sent in sents]
        
        for sent in word_sent:
            word_filter_bi = [word.lower() for word in sent if word.lower() not in stopwords.words('english') and re.search('\w+', word) and not re.search('\d', word)]
            word_filtered_bigram_incre = list(bigrams(word_filter_bi))
            word_filtered_bigram += word_filtered_bigram_incre
        
        
deid_freqdist = FreqDist(word_filtered) 
deid_freqdist_bi = FreqDist(word_filtered_bigram) 

with open('word_count.pkl', 'wb') as fout:
    pickle.dump(deid_freqdist, fout)
    
with open('word_count_bi.pkl', 'wb') as fout:
    pickle.dump(deid_freqdist_bi, fout)

print(deid_freqdist.most_common(50))
print(deid_freqdist_bi.most_common(50))