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
from autocorrection import *
import nltk
from nltk.stem.porter import *
from nltk import sent_tokenize

autoc = autocorrect()
stemmer = PorterStemmer()


#finpath = "/media/DataHD/beau/baby_notes/"
#finpath = "/media/DataHD/corpus/notes/"
#foutpath ="/media/DataHD/r_phi_corpus/"
finpath = "input\\"
foutpaht = "output\\"

#with open("whitelist.txt",'rb') as fin:
#    whitelist = fin.read()
#whitelist = set(whitelist)

with open("whitelist.pkl", "rb") as fp:
    whitelist = pickle.load(fp, encoding="bytes")
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
|ip                        # ip address
|date                      # date
|md                        # MD ID
|age|year[s]?\sold           # age             
)""",re.X|re.I)   

'''
pattern_time = re.compile(r"""\b(
(\d{4}|\d{2})[-/:]\d{2}([-/:](\d{4}|\d{2}))+    # time-format
)""",re.X|re.I)   
'''

for f in glob.glob(finpath+"*.txt"):
    with open(f) as fin:
        #print f
        #f_name = f.split("\\")[5]
        f_name = f
        #print f_name
        total_records += 1
        safe = True
        screens_per_file[f_name] = 0
        corrects_per_file[f_name] = 0
        #take the note name for writing
        out_name = 'whiteListed_'+ f_name
        phi_reduced = ''
        note = sent_tokenize(fin.read())
        for sent in note:
            tmp = sent.strip()
            tmp = tmp.replace('-', ' ') 
            #tmp = sent
            #print(tmp)
            #for word in tmp.translate(None, string.punctuation).split():
            for word in tmp.translate(string.punctuation).split():
                #print(word)
                #get the punctuation for later recombination
                word_end=' '
                if word[-1] in string.punctuation:
                    word_end= word[-1]
                
                # keep the number format, others will remove the special chars
                if nltk.pos_tag([word])[0][1] != 'CD':
                    word = str(pattern.sub('',word)) #actually remove the speical chars
                #print(word, word_end)
                #print(word)
                try:
                    # nouns or Proper noun | plurals and the first letter is upperclass |
                    # the first letter is upperclass and not in the begining of the sentence
                    # numbers and in the same sentence that contains sensetive words, e.g. address, street, road
                    if ((nltk.pos_tag([word])[0][1] == 'NN' or nltk.pos_tag([word])[0][1] == 'NNP') or
                    ((nltk.pos_tag([word])[0][1] == 'NNS' or nltk.pos_tag([word])[0][1] == 'NNPS') and word[0].istitle()) or
                    (word[0].istitle() and word_prev not in string.punctuation) or
                    (nltk.pos_tag([word])[0][1] == 'CD' and pattern_sens.findall(tmp))): 
                        #print(1)
                        word_ori = word
                        word, correct_flag = autoc.autocorrection(word)
                        
                        if correct_flag:
                            corrected_words.append(word.ori)
                            corrects_per_file[f_name] += 1
                        
                        #if word.isdigit() and len(word) <= 2: # 1 or 2 digit values are probably harmless
                        #    word = word
                        #elif word.lower() in whitelist:
                        if word.lower().encode("utf8") not in whitelist:
                            # print word
                            #word = word
                        #else:
                            screened_words.append(word.lower())
                            word = "**FILTERED**"
                            safe = False
                            screens_per_file[f_name] += 1
                            #phi_reduced = phi_reduced + ' ' + word
                                     
                            
                    if word_end == ' ' or nltk.pos_tag([word])[0][1] == 'CD':
                        phi_reduced = phi_reduced + ' ' + word
                    else:
                        phi_reduced = phi_reduced + ' ' + word + word_end
                    word_prev = word_end
                
                except:
                    #print(word)
                    pass
                #print(word_prev)
                #print(word, word_prev)
                                
            #print phi_reduced
        if safe == False:
            phi_containing_records += 1
        fout = "output\\phi_reduced_note_pos"+str(total_records)+".txt"
        
        with open(fout,"w") as phi_reduced_note:
            phi_reduced_note.write(phi_reduced)

print('total records processed: {}'.format(total_records))
print('num records with phi: {}'.format(phi_containing_records))

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