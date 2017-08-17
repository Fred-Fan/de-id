#import cPickle
#import _pickle as cPickle
import pickle
import os, sys
import glob, glob
from multiprocessing.dummy import Pool as ThreadPool
#import MySQLdb as mdb
import string
import re
from collections import Counter
from collections import OrderedDict
from Autocorrection import *
import time
from nltk import word_tokenize

start_time = time.time()

finpath = "/media/DataHD/baby_notes/"
#finpath = "/media/DataHD/r_phi_corpus/src_fred/input_temp/"
foutpath = "/media/DataHD/r_phi_corpus/src_fred/output_temp/"
#finpath = "input\\"
#foutpath = "output\\"

#with open("whitelist.txt",'rb') as fin:
#    whitelist = fin.read()
#whitelist = set(whitelist)

with open("safelist.pkl", "rb") as fp:
    whitelist = pickle.load(fp, encoding="bytes")
print('length of safelist: {}'.format(len(whitelist)))


total_records = 0
phi_containing_records = 0
screens_per_file = { }
corrected_words = []
corrects_per_file = {}


pattern=re.compile("[^\w']") #we're going to want to remove all special characters

for f in glob.glob(finpath+"*.txt"):
    with open(f, encoding ='utf-8', errors='ignore') as fin:
        screened_words = []
        #print f
        #f_name = f.split("\\")[5]
        f_name = f.split("/")[-1]
        # f_name = f.split("\\")[-1]
        f_name = re.findall(r'\d+', f_name)[0]

        #print f_name
        total_records += 1
        safe = True
        screens_per_file[f_name] = 0
        corrects_per_file[f_name] = 0
        note = fin.read()
        note_length = len(word_tokenize(note))
        #take the note name for writing
        phi_reduced = ''
        #for line in note:
        note = note.replace('/', ' ').replace('-', ' ').replace(':', ' ').replace('~',' ')
            #tmp = line.strip()
            #tmp = tmp.replace('-', ' ')
            #print(tmp)
            #for word in tmp.translate(None, string.punctuation).split():
        for word in note.translate(string.punctuation).split():
            #print(word)
            word = str(pattern.sub('',word)) #actually remove the speical chars
            #a = autocorrect()
            #word_ori = word
            #word, correct_flag = a.autocorrection(word)
            #if correct_flag:
            #    corrected_words.append(word.ori)
            #    corrects_per_file[f_name] += 1
            if word.isdigit() and len(word) <= 2: # 1 or 2 digit values are probably harmless
                word = word
            #elif word.lower() in whitelist:
            elif word.lower() in whitelist:
                # print word
                word = word
            else:
                screened_words.append(word)
                word = "**FILTERED**"
                safe = False
                screens_per_file[f_name] += 1
            phi_reduced = phi_reduced + ' ' + word
	        #print phi_reduced
        if safe == False:
            phi_containing_records += 1

        fout = foutpath+"whitelisted_V1_"+f_name+".txt"

        with open(fout,"w") as phi_reduced_note:
            phi_reduced_note.write(phi_reduced)

        with open("filter_summary_V1.txt", 'a') as fout:
            fout.write(str(f_name)+' '+ str(note_length) + ' ' +
                str(len(screened_words)) + ' ' + ' '.join(screened_words)+'\n')


print('total records processed: {}'.format(total_records))
print('num records with phi: {}'.format(phi_containing_records))
print(time.time()-start_time)
screened_dict = Counter(screened_words)
screened_sorted_by_value = OrderedDict(sorted(screened_dict.items(), key=lambda x: x[1], reverse = True))

screens_per_file = OrderedDict(sorted(screens_per_file.items(), key = lambda x: x[1], reverse = True))
# print screens_per_file

# screened_to_list = {k: v for k, v in screened_sorted_by_value.items() if v > 3}
# screened_to_list = list(screened_to_list.keys()) #this is just to use for print/copy if want to examine and add to whitelist


# screened_words_out = set(screened_words) # remove redundancy
# screened_words_out = list(screened_words)
# screened_words_out.sort() # sorts normally by alphabetical order
# screened_words_out.sort(key=len) #sort by length
#print screened_words

# out_dict = open('/media/DataHD/screened_dict.pkl', 'ab+')
# pickle.dump(screened_sorted_by_value, out_dict)
# out_dict.close()


# thefile = open('/media/DataHD/screened_words.txt', 'w')
# for item in screened_words_out:
#   print>>thefile, item

pickle.dump(screened_dict, open( "output\\words_screened_dict.pkl", "wb" ) )
pickle.dump(screens_per_file, open( "output\\words_perFile_dict.pkl", "wb" ) )
pickle.dump(corrects_per_file, open( "output\\corrects_per_file.pkl", "wb" ) )