# import cPickle
# import _pickle as cPickle
from __future__ import print_function
import pickle
# import os
# import sys
import glob
# from multiprocessing.dummy import Pool as ThreadPool
# import MySQLdb as mdb
import string
import re
# from collections import Counter
# from collections import OrderedDict
from Autocorrection import *
import nltk
from nltk.stem.porter import *
from nltk import sent_tokenize, word_tokenize
from nltk.tree import Tree
from nltk import pos_tag_sents, ne_chunk
# from nltk.tag.stanford import StanfordNERTagger
from Searchterms import *
# import requests
# import json
# import argparse
import time
from multiprocessing import Pool, Manager
import multiprocessing
from Sql import *
# from functools import partial
import spacy

# st = StanfordNERTagger(
#       '/media/DataHD/r_phi_corpus/src_fred/english.all.3class.distsim.crf.ser.gz',
#       '/media/DataHD/r_phi_corpus/src_fred/stanford-ner.jar')
# st = StanfordNERTagger(
#       'F:\\Google Drive\\\Jupyter\\ICHS\\english.all.3class.distsim.crf.ser.gz',
#       'F:\\Google Drive\\\Jupyter\\ICHS\\stanford-ner.jar')
foutpath = "output_test\\"
finpath = "input_test\\"
#finpath = "/media/DataHD/baby_notes/test/"
#foutpath = "/media/DataHD/r_phi_corpus/src_fred/output_temp/"
stemmer = PorterStemmer()
nlp = spacy.load('en')
# name_whitelist = {'Pain', 'Count'}
name_whitelist = {}
# sql = sqlquery()

screens_per_file  = {}
corrected_words   = []
corrects_per_file = {}

# configure the regex patterns
pattern = re.compile(r"[^\w+]")
# we're going to want to remove all special characters
pattern_sens = re.compile(r"""\b(
addr|street|lane|ave       # addres
|phone|fax|number|tel      # phone
|ip                                # ip address
|date                      # date
|md                        # MD ID
|age|year[s]?\sold         # age
|ssn|security             #SSN
)""", re.X | re.I)
'''
pattern_number = re.compile(r"""\b(
\d{6}\d*         # MRN
|\d{1}[\d(\(\)-.\'\s)?]{9}\d+    # SSN|Phone|Fax
|\d{5}(-\d{4})?            # postal code
)\b""", re.X | re.I)
'''
pattern_number = re.compile(r"""\b(
\d{6}\d*         # MRN
|(\d[\(\)-.\']?\s?){8}\d+   # SSN|Phone|Fax
|\d{5}(-\d{4})?            # postal code
)\b""", re.X | re.I)

pattern_dob = re.compile(r"""\b(
.*?(?=\b(\d{1,2}[-./\s]\d{1,2}[-./\s]\d{2}
|\d{1,2}[-./\s]\d{1,2}[-./\s]\d{4}
|\d{2}[-./\s]\d{1,2}[-./\s]\d{1,2}
|\d{4}[-./\s]\d{1,2}[-./\s]\d{1,2}
)\b)
)\b""", re.X|re.I)

pattern_email = re.compile(r"""\b(
[a-zA-Z0-9_.+-@\"]+@[a-zA-Z0-9-\:\]\[]+[a-zA-Z0-9-.]*
)\b""", re.X | re.I)

pattern_date = re.compile(r"""\b(
\d{1,2}[-./\s]\d{1,2}[-./\s]\d{2}
|\d{1,2}[-./\s]\d{1,2}[-./\s]\d{4}
|\d{2}[-./\s]\d{1,2}[-./\s]\d{1,2}
|\d{4}[-./\s]\d{1,2}[-./\s]\d{1,2}
)\b""", re.X | re.I)

pattern_name = re.compile(r'''^[A-Z]\'?[-a-zA-Z]+$''')

pattern_age = re.compile(r'''\b(age|year[s-]?\s?old|y.o[.]?)''', re.X | re.I)

pattern_salutation = re.compile(r"""
(Dr\.|Mr\.|Mrs\.|Ms\.|Miss|Sir|Madam)\s
(([A-Z]\'?[A-Z]?[-a-z ]+)*
)""",  re.X)


# pattern_time = re.compile(r'''\b(
# (\d{4}|\d{2})[-/:]\d{2}([-/:](\d{4}|\d{2}))+    # time-format
# )''',re.X|re.I)

# apikey = input("input your api >")
# searchterms = search_terms(apikey)
# searchterms1 = search_terms("81602583-1f6f-400a-a49f-618975025bec")
# searchterms2 = search_terms("81602583-1f6f-400a-a49f-618975025bec")



def namecheck(word_output, name_check, screened_words, safe):
    if word_output.title() in name_check:
        with open("name.txt" , 'a') as fout:
            fout.write(word_output+'\n')
        print('Name:', word_output)
        screened_words.append(word_output)
        word_output  = "**PHI**"
        safe = False
        #screens_per_file[f_name] += 1

    else:
        #print(word_output)
        doc1 = nlp(word_output.title())
        doc2 = nlp(word_output.upper())
        if (doc1.ents != () and doc1.ents[0].label_ == 'PERSON' and
            doc2.ents != () and doc2.ents[0].label_ is not None):
            with open("name.txt" , 'a') as fout:
                fout.write(word_output+'\n')
            print('Name:', word_output)
            screened_words.append(word_output)
            name_check.add(word_output.title())
            word_output  = "**PHI**"
            safe = False
            #screens_per_file[f_name] += 1

    return word_output, name_check, screened_words, safe

def filter_task(f, whitelist_dict, filterlist_dict):
    # global total_records
    # global phi_containing_records
    # global screened_words
    # global screens_per_file
    # global corrected_words
    # global corrects_per_file
    # searchterms1 = search_terms("81602583-1f6f-400a-a49f-618975025bec")
    # searchterms2 = search_terms("81602583-1f6f-400a-a49f-618975025bec")

    with open(f, encoding='utf-8', errors='ignore') as fin:

        # logging = ''
        # print f
        # print(len(whitelist_dict))
        # print(len(filterlist_dict))
        f_name = f.split("/")[-1]
        # f_name = f.split("\\")[-1]
        f_name = re.findall(r'\d+', f_name)[0]
        print(f_name)
        start_time_single = time.time()
        # total_records += 1
        total_records = 1
        phi_containing_records = 0
        safe = True
        screened_words    = []
        name_check = set()
        screens_per_file[f_name] = 0
        corrects_per_file[f_name] = 0
        # take the note name for writing
        phi_reduced = ''
        # searchterms2.search("")
        note = fin.read()
        # sent_end_prev = ' '
        # try:
        #    note = fin.read()
            # remove note id,e.g. "A30000091        2006-10-15 22:28:00.000 6789784"
            # note_id = re.search(r'''\s\d+\s''', note).group(0)
            # phi_note_id = note [:note.index(note_id)+len(note_id)]
            # note = note.replace(phi_note_id, 'FILTERED ')
        # except:
            # continue

        # remove "-"
        re_list = pattern_salutation.findall(note)
        for i in range(len(re_list)):
            #print(re_list)
            name_check = name_check | set(re_list[i][1].split(' '))
            #print(name_check)
        note_length = len(word_tokenize(note))
        note = sent_tokenize(note)
        # print(note)
        for sent in note:
            # tmp = ' '.join(sent)
            # sent = str(pattern_number.sub('**PHI**',sent))

            # name
            # doc = nlp(sent)
            # name_set = set()
            # for ent in doc.ents:
            #   if ent.label_ == 'PERSON':
            #      [name_set.add(t) for t in ent.text.split(' ')]

            if pattern_number.findall(sent) != []:
                for item in pattern_number.findall(sent):
                    # print(item)
                    if pattern_date.match(item[0]) is None:
                        sent = sent.replace(item[0], '**PHI**')
                        screened_words.append(item[0])
            # email check
            sent = str(pattern_email.sub('**PHI**',sent))

            # dob check
            re_list = pattern_dob.findall(sent)
            i = 0
            while True:
                if i >= len(re_list):
                    break
                else:
                    text = ' '.join(re_list[i][0].split(' ')[-6:])
                    if re.findall(r'\b(birth|dob)\b', text, re.I) != []:
                        sent = sent.replace(re_list[i][1], '**PHI**')
                        screened_words.append(re_list[i][1])
                    i += 2
            '''
            if pattern_date.findall(sent) != []:
                for item in pattern_dob.findall(sent):
                    if re.findall(r'birth|dob', item, re.I) != []:
                        # replacement = re.sub(r'\d{2}[-./]\d{2}[-./]\d{4}', '**PHI**', item)
                        replacement = str(pattern_date.sub('**PHI**',item))
                        screened_words.append(item)
                        sent = sent.replace(item, replacement)
                        '''
            # saluation check

            sent = sent.replace('/', ' ').replace('-', ' ').replace(':', ' ').replace('~',' ').replace('_',' ')


            doc = nlp(sent)
            sent = [word_tokenize(sent)]

            # print(len(sent[0]))
            address_indictor = ['street', 'avenue', 'road', 'boulevard', 'drive', 'trail', 'way', 'lane', 'ave', 'blvd', 'st', 'rd', 'trl', 'wy', 'ln']
            for position in range(0, len(sent[0])):
                # address check
                #sent[0][position] = str(pattern.sub('', sent[0][position]))
                #print(sent[0][position])
                word = sent[0][position]
                if (position >= 1 and position < len(sent[0])-1 and
                    (word.lower() in address_indictor or (word.lower() == 'dr' and
                    sent[0][position+1] != '.')) and (word.istitle() or word.isupper())):
                    # indices = [i for i, x in enumerate(sent[0]) if x == word]
                    if sent[0][position - 1].istitle() or sent[0][position-1].isupper():
                        screened_words.append(sent[0][position - 1])
                        sent[0][position - 1] = '**PHI**'
                        i = position - 2
                        while True:
                            if re.findall(r'^[\d-]+$', sent[0][i]) != []:
                                screened_words.append(sent[0][i])
                                sent[0][i] = '**PHI**'
                                break
                            elif i == 0 or position - i > 5:
                                break
                            else:
                                i -= 1
                # age check
                elif word.isdigit() and int(word) > 90:
                    if position <= 2:
                        word_previous = ' '.join(sent[0][:position])
                    else:
                        word_previous = ' '.join(sent[0][position - 2:position])
                    if position >= len(sent[0]) - 2:
                        word_after = ' '.join(sent[0][position+1:])
                    else:
                        word_after = ' '.join(sent[0][position+1:position +3])

                    age_string = str(word_previous) + str(word_after)
                    if pattern_age.findall(age_string) != []:
                        screened_words.append(sent[0][position])
                        sent[0][position] = '**PHI**'
            # print(sent)

            sent_tag = nltk.pos_tag_sents(sent)
            for ent in doc.ents:
            # print(ent)
            # print(ent.label_)
                #name_flag = 0
                if ent.label_ == 'PERSON':
                #print(ent.text)
                    doc1 = nlp(ent.text)
                    if doc1.ents != () and doc1.ents[0].label_ == 'PERSON':
                        name_tag = word_tokenize(ent.text)
                        name_tag = pos_tag_sents([name_tag])
                        chunked = ne_chunk(name_tag[0])
                        for i in chunked:
                            if type(i) == Tree:
                                if i.label() == 'PERSON':
                                    for token, pos in i.leaves():
                                        if pos == 'NNP':
                                            name_check.add(token)
                                # print(i)
                                # [continuous_chunk.append(token) for token, pos in i.leaves() if pos == 'NNP' ]
                                else:
                                    for token, pos in i.leaves():
                                        doc2 = nlp(token.upper())
                                        if doc2.ents != ():
                                            name_check.add(token)
                        #for word in name_tag[0]:
                #print(word)
                            #if word[1] != "NNP":
                    #print(doc1.ents)

            # print(sent_tag[0])
            # ne_list = list(nltk.ne_chunk(sent_tag[0], binary=True))

            # i = 0
            # for item in ne_list:
                # if type(item) == nltk.tree.Tree:
                    # for j in range(len(list(item))):
                        # sent_tag[0][i+j] = sent_tag[0][i+j] + tuple("1")
                    # i += j + 1
                # else:
                    # sent_tag[0][i] = sent_tag[0][i] + tuple("0")
                    # i += 1
            # print(sent_tag[0])

            for i in range(len(sent_tag[0])):
                word = sent_tag[0][i]
                # print(word)
                word_output = word[0]
                check_flag = 0
                if word_output not in string.punctuation:
                    #word_position = sent[0].index(word[0])
                    #print(word)
                # keep the number format, others will remove the special chars
                    #if word[1] != 'CD':
                    word_check = str(pattern.sub('', word_output))
                        #actually remove the speical chars
                    try:
                    # nouns or Proper noun | plurals and the first letter is upperclass |
                    # the first letter is upperclass
                    # and not in the begining of the sentence
                    # numbers and in the same sentence
                    #that contains sensetive words, e.g. address, street, road
                        word_lower = word_check.lower()

                        if ((word[1] == 'NN' or word[1] == 'NNP') or
                        ((word[1] == 'NNS' or word[1] == 'NNPS') and word_check.istitle())):
                    #or ((word[1] == 'CD' or (word[1] == 'JJ') and pattern_time.findall(word)))
                            #print("1")
                            # word_ori = word_output
                            autoc = autocorrect(word_check, whitelist_dict)
                            word_modif, check_flag = autoc.autocheck()

                        #   elif word_output.lower().encode("utf8") not in whitelist and stemmer.stem(word_output.lower()).encode('utf8') not in whitelist:
                                #print("2")
                                #print(st.tag([word_output])[0])
                                #name


                            if check_flag != 1:
                                '''
                                if re.findall(r'[A-Za-z]+\d+[\.\d+]*', word_output) != []:
                                    results = sql.sql_query(word_output)
                                    if results == ():
                                        screened_words.append(word_output)
                                        word_output  = "**PHI**"
                                        safe = False
                                        screens_per_file[f_name] += 1
                                else:
                                    screened_words.append(word_output)
                                    word_output  = "**PHI**"
                                    safe = False
                                    screens_per_file[f_name] += 1
                                '''
                                '''
                                if word_lower not in filterlist_dict:

                                    #phase0 = time.time()
                                    #logging = logging + word_ori + ' '
                                    #print(word_output)
                                    #if ((st.tag([word_ori])[0][1] != 'PERSON' and st.tag([word_ori])[0][1] != 'LOCATION') or
                                    #((st.tag([word_ori])[0][1] == 'PERSON' or st.tag([word_ori])[0][1] != 'LOCATION') and not word_ori.istitle())):
                                    if pattern_name.findall(word_ori) == [] or (pattern_name.findall(word_ori) != [] and not word_ori.istitle()):
                                        #searchterms1.search(word_ori)
                                        #phase1 = time.time()
                                        #logging = logging + 'phase 1 NER:'+str(phase1-phase0)
                                        results = sql.sql_query(word_ori)
                                        #   print("5")
                                        #if not searchterms1.ifumls():
                                        #      print(word_output)
                                        #phase2 = time.time()
                                        #logging = logging + ' phase 2 1st sql:'+str(phase2-phase1)
                                        if results == ():
                                            results = sql.sql_query(stemmer.stem(word_ori))
                                            #searchterms2.search(stemmer.stem(word_ori))
                                    #     print("6")
                                            #phase3 = time.time()
                                            #logging = logging + ' phase 3 2st sql:'+str(phase3-phase2)
                                            #if not searchterms2.ifumls():
                                            if results == ():
                                                if  check_flag == 3:
                                                    word_output = word_modif + '***F***'
                                                    corrected_words.append(word_ori)
                                                    corrects_per_file[f_name] += 1
                                                    safe = False
                                                else:
                                                    screened_words.append(word_lower)
                                                    word_output  = "**PHI**"
                                                    #filter_set.add(word_lower)
                                                    filterlist_dict[word_lower] = 0
                                                    print(word_ori, 'length of filterlist: {}'.format(len(filterlist_dict)))
                                                    safe = False
                                                    screens_per_file[f_name] += 1
                                            else:
                                                #whitelist.add(word_lower)
                                                whitelist_dict[word_lower] = 0
                                                print(word_ori, 'length of whitelist: {}'.format(len(whitelist_dict)))


                                        else:
                                            #whitelist.add(word_lower)
                                            whitelist_dict[word_lower] = 0
                                            print(word_ori, 'length of whitelist: {}'.format(len(whitelist_dict)))
                                    else:
                                        #filter names,locations
                                        #print(word_output, st.tag([word_output])[0][1])
                                        #print("7")
                                        screened_words.append(word_lower)
                                        word_output  = "**PHI**"
                                        safe = False
                                        screens_per_file[f_name] += 1
                                else:
                                    screened_words.append(word_lower)
                                    word_output  = "**PHI**"
                                    safe = False
                                    screens_per_file[f_name] += 1

                                #logging = logging + "\n"

                                '''
                                '''
                                if stemmer.stem(word_lower) not in whitelist_dict:
                                    screened_words.append(word_output)
                                    word_output  = "**PHI**"
                                    safe = False
                                    screens_per_file[f_name] += 1
                                else:
                                    word_output, name_check, screend_words, safe = namecheck(word_output, name_check, screened_words, safe)
                                '''
                                
                                screened_words.append(word_output)
                                word_output  = "**PHI**"
                                safe = False
                                screens_per_file[f_name] += 1
                                
                            elif (check_flag == 1 and (word_output.istitle() or word_output.isupper()) and pattern_name.findall(word_output) != []):
                                word_output, name_check, screend_words, safe = namecheck(word_output, name_check, screened_words, safe)
                                '''
                                if word_output in name_check:
                                    with open("name.txt" , 'a') as fout:
                                        fout.write(word[0]+'\n')
                                    print('Name:', word[0], word[1], i)
                                    screened_words.append(word[0])
                                    word_output  = "**PHI**"
                                    safe = False
                                    screens_per_file[f_name] += 1
                                else:
                                    #print(word_output)
                                    doc1 = nlp(word_output.title())
                                    doc2 = nlp(word_output.upper())
                                    if (doc1.ents != () and doc1.ents[0].label_ == 'PERSON' and
                                        doc2.ents != () and doc2.ents[0].label_ is not None):
                                        with open("name.txt" , 'a') as fout:
                                            fout.write(word[0]+'\n')
                                        print('Name:', word[0], word[1], i)
                                        screened_words.append(word[0])
                                        word_output  = "**PHI**"
                                        safe = False
                                        screens_per_file[f_name] += 1
                            #elif check_flag == 1 and word[0].istitle() and pattern_name.findall(word[0]) != [] and word[1] == 'NNP' and word[2] == '1':
                            '''
                            '''
                            elif check_flag == 1 and (word[0].istitle() or word[0].isupper()) and pattern_name.findall(word[0]) != []:
                                doc1 = nlp(word[0].title())
                                doc2 = nlp(word[0].upper())
                                if (doc1.ents != () and doc1.ents[0].label_ == 'PERSON' and
                                    doc2.ents != () and doc2.ents[0].label_ is not None):
                                    with open("name.txt" , 'a') as fout:
                                        fout.write(word[0]+'\n')
                                    print('Name:', word[0], word[1], i)
                                    screened_words.append(word_ori)
                                    word_output  = "**PHI**"
                                    safe = False
                                    screens_per_file[f_name] += 1

                                else:
                                    doc3 = nlp('')
                                    doc4 = nlp('')
                                    doc5 = nlp('')
                                    doc6 = nlp('')
                                    j = 1
                                    while True:
                                        if i-j < 0:
                                            break
                                        elif sent_tag[0][i-j][0] not in string.punctuation:
                                            if sent_tag[0][i-j][0].istitle():
                                                doc3 = nlp(sent_tag[0][i-j][0])
                                                doc4 = nlp(sent_tag[0][i-j][0].upper())
                                            break
                                        else:
                                            j += 1
                                    j = 1
                                    while True:
                                        if i+j > len(sent_tag[0])-1:
                                            break
                                        elif sent_tag[0][i+j][0] not in string.punctuation:
                                            if sent_tag[0][i+j][0].istitle():
                                                doc5 = nlp(sent_tag[0][i+j][0])
                                                doc6 = nlp(sent_tag[0][i+j][0].upper())
                                            break
                                        else:
                                            j += 1
                                    if ((doc3.ents != () and doc3.ents[0].label_ == 'PERSON' and
                                        doc4.ents != () and doc4.ents[0].label_ is not None) or
                                        (doc5.ents != () and doc5.ents[0].label_ == 'PERSON' and
                                        doc6.ents != () and doc6.ents[0].label_ is not None)):
                                        with open("name.txt" , 'a') as fout:
                                            fout.write(word[0]+'\n')
                                        print('Name:', word[0], word[1], i)
                                        screened_words.append(word_lower)
                                        word_output  = "**PHI**"
                                        safe = False
                                        screens_per_file[f_name] += 1
                                        '''

                        '''

                        elif word[1] == 'CD' and (sent[0][word_position-1].lower == 'birth' or sent[0][word_position-2].lower == 'birth' ):
                            #print("4")
                            #print(word_output)
                            screened_words.append(word_lower)
                            word_output  = "**PHI**"
                            safe = False
                            screens_per_file[f_name] += 1
                        '''

                        # print(word_output)
                    except:
                        print(word[0])
                        #word_output = "+"+word_output + "+"
                        #print(sent.index(word))
                        #print(nltk.pos_tag(word))
                        pass

                phi_reduced = phi_reduced + ' ' + word_output
        if safe == False:
            #phi_containing_records += 1
            phi_containing_records = 1
        fout = foutpath+"whitelisted_V2_all_"+f_name+".txt"

        with open(fout,"w") as phi_reduced_note:
            phi_reduced_note.write(phi_reduced)
        with open("filter_summary_V2_all.txt", 'a') as fout:
            fout.write(str(f_name)+' '+ str(note_length) + ' ' +
                str(len(screened_words)) + ' ' + ' '.join(screened_words)+'\n')

        print(total_records, f,  "--- %s seconds ---" % (time.time() - start_time_single))
        #with open("logging.txt", 'a') as fout:
        #    fout.write(logging)
        return total_records, phi_containing_records


def main():

    start_time_all = time.time()
    pool = Pool(processes=6)              # start 4 worker processes


    with open("all.pkl", "rb") as fp:
        whitelist = pickle.load(fp)
    print('length of safelist: {}'.format(len(whitelist)))


    with open("filterset.pkl", "rb") as fp:
        filter_set = pickle.load(fp)
    print('length of filterlist: {}'.format(len(filter_set)))


    filename_list = []
    results_list = []
    manager = Manager()
    whitelist_dict_g = manager.dict()
    filter_dict_g = manager.dict()
    for i in whitelist:
        whitelist_dict_g[i] = 0
    for i in filter_set:
        filter_dict_g[i] = 0


        #results_list.append(results.get())
    for f in glob.glob(finpath+"*.txt"):
        filename_list.append(f)
    #print(filename_list[:10])
        #filter_task(f)
    filter_time = time.time()

    results = [pool.apply_async(filter_task,(f,)+(whitelist_dict_g, filter_dict_g)) for f in glob.glob(finpath+"*.txt")]
    results_list = [r.get() for r in results]
    total_records, phi_containing_records = zip(*results_list)

    #results_list = pool.map_async(partial(filter_task, whitelist_dict = whitelist_dict_g, filterlist_dict = filter_dict_g),filename_list)  
    #total_records, phi_containing_records = zip(*results_list.get())

    total_records = sum(total_records)
    phi_containing_records = sum(phi_containing_records)

    pool.close()
    pool.join()
   # sql.sql_close()
    #print(sum(total_records), sum(phi_containing_records))
    #print(sum(total_records))
    #total_records = sum(total_records_list)
    #phi_containing_records = sum(phi_containing_records_list)
    print(total_records, "--- %s seconds ---" % (time.time() - start_time_all)) 
    print('filter_time', "--- %s seconds ---" % (time.time() - filter_time)) 
    print('total records processed: {}'.format(total_records))
    print('num records with phi: {}'.format(phi_containing_records))
    print('length of whitelist: {}'.format(len(whitelist_dict_g)))
    print('length of filterlist: {}'.format(len(filter_dict_g)))
    whitelist = set(whitelist_dict_g.keys())
    filter_set = set(filter_dict_g.keys())

    #with open("whitelist.pkl", "wb") as fout:
    #    pickle.dump(whitelist,fout )
    #with open("filterset.pkl", "wb") as fout:
    #    pickle.dump(filter_set,fout )

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()

#screened_dict = Counter(screened_words)
#screened_sorted_by_value = OrderedDict(sorted(screened_dict.items(), key=lambda x: x[1], reverse = True))

#screens_per_file = OrderedDict(sorted(screens_per_file.items(), key = lambda x: x[1], reverse = True))
# print screens_per_file

# screened_to_list = {k: v for k, v in screened_sorted_by_value.items() if v > 3}
# screened_to_list = list(screened_to_list.keys()) #this is just to use for print/copy if want to examine and add to whitelist


# screened_words_out = set(screened_words) # remove redundancy
# screened_words_out = list(screened_words)
# screened_words_out.sort() # sorts normally by alphabetical order
# screened_words_out.sort(key=len) #sort by length
# print screened_words

# out_dict = open('/media/DataHD/screened_dict.pkl', 'ab+')
# pickle.dump(screened_sorted_by_value, out_dict)
# out_dict.close()


# thefile = open('/media/DataHD/screened_words.txt', 'w')
# for item in screened_words_out:
#   print>>thefile, item

# pickle.dump(screened_dict, open( "output\\words_screened_dict.pkl", "wb" ))
# pickle.dump(screens_per_file, open( "output\\words_perFile_dict.pkl", "wb" ))
# pickle.dump(corrects_per_file, open( "output\\corrects_per_file.pkl", "wb" ))
