#import cPickle
#import _pickle as cPickle 
from __future__ import print_function
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
import nltk
from nltk.stem.porter import *
from nltk import sent_tokenize, word_tokenize
from nltk.stem.porter import *
from nltk.tag.stanford import StanfordNERTagger
from searchterms import *
import requests
import json
import argparse
import time


stemmer = PorterStemmer()

#apikey = input("input your api >")
#searchterms = search_terms(apikey)
searchterms1 = search_terms("81602583-1f6f-400a-a49f-618975025bec")
searchterms2 = search_terms("81602583-1f6f-400a-a49f-618975025bec")

st = StanfordNERTagger('/media/DataHD/r_phi_corpus/src_fred/english.all.3class.distsim.crf.ser.gz','/media/DataHD/r_phi_corpus/src_fred/stanford-ner.jar')
#st = StanfordNERTagger('F:\\Google Drive\\\Jupyter\\ICHS\\english.all.3class.distsim.crf.ser.gz','F:\\Google Drive\\\Jupyter\\ICHS\\stanford-ner.jar')

stemmer = PorterStemmer()

finpath = "/media/DataHD/baby_notes/"
#finpath = "/media/DataHD/r_phi_corpus/src_fred/input_temp/"
foutpath = "/media/DataHD/r_phi_corpus/src_fred/output_temp/"
#finpath = "input_test\\"
#foutpath = "output_test\\"

#with open("whitelist.txt",'rb') as fin:
#    whitelist = fin.read()
#whitelist = set(whitelist)

with open("whitelist.pkl", "rb") as fp:
#with open("/media/DataHD/r_phi_corpus/src_temp/whitelist.pkl", "rb") as fp:
    #whitelist = pickle.load(fp, encoding="bytes")
    whitelist = pickle.load(fp)
print('length of whitelist: {}'.format(len(whitelist)))

### initialize variables
total_records = 0
phi_containing_records = 0
screened_words = []
screens_per_file = { }
corrected_words = []
corrects_per_file = {}

### configure the regex patterns
pattern=re.compile("[^\w+]") #we're going to want to remove all special characters
pattern_sens = re.compile(r"""\b(
addr|street|lane|ave       # addres
|phone|fax|number|tel      # phone
|ip                                # ip address
|date                      # date
|md                        # MD ID
|age|year[s]?\sold         # age   
|ssn|security             #SSN           
)""",re.X|re.I)   

'''
pattern_time = re.compile(r"""\b(
(\d{4}|\d{2})[-/:]\d{2}([-/:](\d{4}|\d{2}))+    # time-format
)""",re.X|re.I)   
'''
start_time_all = time.time()

for f in glob.glob(finpath+"*.txt"):
    with open(f, encoding='utf-8', errors='ignore') as fin:
        #print f
        f_name = f.split("/")[-1]
        #f_name = f.split("\\")[-1]
        f_name = re.findall(r'\d+', f_name)[0]
        print(f_name)
        start_time_single = time.time()
        total_records += 1
        safe = True
        screens_per_file[f_name] = 0
        corrects_per_file[f_name] = 0
        #take the note name for writing
        out_name = 'whiteListed_'+ f_name
        phi_reduced = ''
        searchterms2.search("")
        note = fin.read()
        #sent_end_prev = ' '
        '''
        try:
            note = fin.read()
            # remove note id,e.g. "A30000091        2006-10-15 22:28:00.000 6789784"     
            note_id = re.search(r'\s\d+\s', note).group(0)
            phi_note_id = note [:note.index(note_id)+len(note_id)]
            note = note.replace(phi_note_id, 'FILTERED ')
        except:
            continue
        '''
        # remove "-"
        note = sent_tokenize(note.replace('-', ' ').replace('/',' '))
        word_sent = [word_tokenize(sent) for sent in note]
        for sent in word_sent:
            tmp = ' '.join(sent)
            sent_tag = nltk.pos_tag_sents([sent])
            for word in sent_tag[0]:
                word_output = word[0]
                check_flag = 0
                if word[0] not in string.punctuation:
                    word_position = sent.index(word[0])
                    
                    #print(word)
                # keep the number format, others will remove the special chars
                    if word[1] != 'CD':
                        word_output = str(pattern.sub('',word[0])) #actually remove the speical chars
                    
                    try:
                    # nouns or Proper noun | plurals and the first letter is upperclass |
                    # the first letter is upperclass and not in the begining of the sentence
                    # numbers and in the same sentence that contains sensetive words, e.g. address, street, road
                        word_lower = word_output.lower()
                        if ((word[1] == 'NN' or word[1] == 'NNP') or
                        ((word[1] == 'NNS' or word[1] == 'NNPS') and word_output.istitle())):
                    #or ((word[1] == 'CD' or (word[1] == 'JJ') and pattern_time.findall(word)))

                            #print("1")
                            word_ori = word_output
                            autoc = autocorrect(word_output, whitelist)
                            word_modif, check_flag = autoc.autocheck()
                            
                        
                         #   elif word_output.lower().encode("utf8") not in whitelist and stemmer.stem(word_output.lower()).encode('utf8') not in whitelist:
                                #print("2")
                                #print(st.tag([word_output])[0])
                                #name
                            if check_flag != 1:
                                '''
                                if ((st.tag([word_ori])[0][1] != 'PERSON' and st.tag([word_ori])[0][1] != 'LOCATION') or 
                                ((st.tag([word_ori])[0][1] == 'PERSON' or st.tag([word_ori])[0][1] != 'LOCATION') and not word_ori.istitle())):
                                    #print(word_output)
                                    searchterms1.search(word_ori)
                                 #   print("5")
                                    if not searchterms1.ifumls():
                                    #      print(word_output)
                                        searchterms2.search(stemmer.stem(word_ori))
                                   #     print("6")
                                       
                                        if not searchterms2.ifumls():
                                            if  check_flag == 3:
                                                word_output = word_modif + '***F***'
                                                corrected_words.append(word_ori)
                                                corrects_per_file[f_name] += 1
                                                safe = False
                                            else:
                                                screened_words.append(word_lower)
                                                word_output  = "**FILTERED**"
                                                safe = False
                                                screens_per_file[f_name] += 1 
                                        else:
                                            whitelist.add(word_lower)
                                            print(word_ori, 'length of whitelist: {}'.format(len(whitelist)))

     
                                    else:
                                        whitelist.add(word_lower)
                                        print(word_ori, 'length of whitelist: {}'.format(len(whitelist)))


                                    
                                    
                                else: 
                                    # filter names,locations
                                    #print(word_output, st.tag([word_output])[0][1])
                                    #print("7")
                                    screened_words.append(word_lower)
                                    word_output  = "**FILTERED**"
                                    safe = False
                                    screens_per_file[f_name] += 1
                                    '''
                                screened_words.append(word_lower)
                                word_output  = "**FILTERED**"
                                safe = False
                                screens_per_file[f_name] += 1
                                    
                                    
 
                        elif ((word[1] == 'CD' and pattern_sens.findall(tmp)) or (word[1] == 'CD' and len(word_output) > 7)):
                            #print("4")
                             #print(word_output)
                            screened_words.append(word_lower)
                            word_output  = "**FILTERED**"
                            safe = False
                            screens_per_file[f_name] += 1

                           # print(word_output)  
                    except:
                        print(word[0])
                        #word_output = "+"+word_output + "+"
                        #print(sent.index(word))
                        #print(nltk.pos_tag(word))
                        pass
  
                phi_reduced = phi_reduced + ' ' + word_output
        if safe == False:
            phi_containing_records += 1
        fout = foutpath+"whitelisted_nlp_noNER"+f_name+".txt"
        
        with open(fout,"w") as phi_reduced_note:
            phi_reduced_note.write(phi_reduced)
        
        print(total_records, "--- %s seconds ---" % (time.time() - start_time_single))

print(total_records, "--- %s seconds ---" % (time.time() - start_time_all))
print('total records processed: {}'.format(total_records))
print('num records with phi: {}'.format(phi_containing_records))
print('length of whitelist: {}'.format(len(whitelist)))
with open("whitelist.pkl", "wb") as fout:
    pickle.dump(whitelist,fout )

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

#pickle.dump(screened_dict, open( "output\\words_screened_dict.pkl", "wb" ) )
#pickle.dump(screens_per_file, open( "output\\words_perFile_dict.pkl", "wb" ) )
#pickle.dump(corrects_per_file, open( "output\\corrects_per_file.pkl", "wb" ) )