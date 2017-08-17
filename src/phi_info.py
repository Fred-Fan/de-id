#import os
#import sys
import glob
#from multiprocessing.dummy import Pool as ThreadPool
#import MySQLdb as mdb
import string
import time
import pickle
import re
import pymysql as pm
from nltk import word_tokenize

#pool = ThreadPool(20)



# fetch data from mysql:
def generate_from_database():
    start_time = time.time()
    data_dict = {}
    db = pm.connect("localhost",    # your host, usually localhost
                    "sf238989",    # username
                    "8LiH15E2grnhJBGANAys409R1",  #password
                    "proj_emr_UCSF2017Jan_identified")      # name of the data base

    # you must create a Cursor object. It will let
    #  you execute all the queries you need

    # first names
    cur_f = db.cursor()
    #takes <10mins for complete search
    cur_f.execute("SELECT clean_value FROM PHI_Probes where phi_type = 'fname' ")
    fname_tuples = cur_f.fetchall()
    fname_list = [i[0] for i in fname_tuples]
    stripped_fname = [s.rstrip().lower() for s in fname_list]
    # there's some elements in that don't seem to be names
    not_names = ['', 'b', 'er', 'jb', 'uy', 'no']
    stripped_fname = set(stripped_fname).difference(not_names)
    data_dict['fname'] = stripped_fname
    print('stripped_fname created', time.time()-start_time, len(stripped_fname))

    # print 'result: {}'.format(fname_tuples)
    # print 'n_r: {}'.format(fname_list)
    # print 'stripped_fname: {}'.format(stripped_fname)
    # last names
    cur_l = db.cursor()
    cur_l.execute("SELECT clean_value FROM PHI_Probes where phi_type = 'lname' ")
    lname_tuples = cur_l.fetchall()
    lname_list = [i[0] for i in lname_tuples]
    stripped_lname = set([s.rstrip().lower() for s in lname_list])
    data_dict['lname'] = stripped_lname
    print('stripped_lname created', time.time()-start_time, len(stripped_lname))

    # mrn
    cur_mrn = db.cursor()
    cur_mrn.execute("SELECT clean_value FROM PHI_Probes where phi_type = 'MRN' ")
    mrn_tuples = cur_mrn.fetchall()
    mrn_list = [i[0] for i in mrn_tuples]
    stripped_mrn = set([s.rstrip() for s in mrn_list])
    data_dict['mrn'] = stripped_mrn
    print('stripped_mrn created', time.time()-start_time, len(stripped_mrn))

    # ssn
    cur_ssn = db.cursor()
    cur_ssn.execute("SELECT clean_value FROM PHI_Probes where phi_type = 'SSN' ")
    ssn_tuples = cur_ssn.fetchall()
    ssn_list = [i[0] for i in ssn_tuples]
    stripped_ssn = set([s.rstrip() for s in ssn_list])
    data_dict['ssn'] = stripped_ssn
    print('stripped_ssn created', time.time()-start_time, len(stripped_ssn))

    #account number: acct
    cur_acct = db.cursor()
    cur_acct.execute("SELECT clean_value FROM PHI_Probes where phi_type = 'ACCT' ")
    acct_tuples = cur_acct.fetchall()
    acct_list = [i[0] for i in acct_tuples]
    stripped_acct = set([s.rstrip() for s in acct_list])
    data_dict['acct'] = stripped_acct
    print('stripped_acct created', time.time()-start_time, len(stripped_acct))

    #medical device identifier: DEVID
    cur_devid = db.cursor()
    cur_devid.execute("SELECT clean_value FROM PHI_Probes where phi_type = 'DEVID' ")
    devid_tuples = cur_devid.fetchall()
    devid_list = [i[0] for i in devid_tuples]
    stripped_devid = set([s.rstrip() for s in devid_list])
    data_dict['devid'] = stripped_devid
    print('stripped_devid created', time.time()-start_time, len(stripped_devid))

    #coverage beneficiary id - or subscriber number: BENID
    # DANGER, THIS REMOVES A LOT OF 2 & 3 DIGIT NUMBERS THAT PROBABLY AREN'T BENIDs
    cur_benid = db.cursor()
    cur_benid.execute("SELECT clean_value FROM PHI_Probes where phi_type = 'BENID' ")
    benid_tuples = cur_benid.fetchall()
    benid_list = [i[0] for i in benid_tuples]
    stripped_benid = set([s.rstrip() for s in benid_list])
    data_dict['benid'] = stripped_benid
    print('stripped_benid created', time.time()-start_time, len(stripped_benid))

    #email
    cur_email = db.cursor()
    cur_email.execute("SELECT clean_value FROM PHI_Probes where phi_type = 'email' limit 500 ")
    email_tuples = cur_email.fetchall()
    email_list = [i[0] for i in email_tuples]
    stripped_email = set([s.rstrip().lower() for s in email_list])
    stripped_email_pre = [s.split('@')[0] for s in stripped_email]
    #tricky things must be done with email usernames that contain '.'
    # here I'm deciding that for email usernames with dots: eg b.norgeot
    # I'm going to only keep the second portion.
    # Thinking: first portion will either be a letter or initials
    # or it might be a first name and if that's the case the f_name look up should catch it.
    stripped_email = set([s.split('.')[1] if '.' in s else s for s in stripped_email_pre])
    data_dict['email'] = stripped_email
    print('stripped_email created', time.time()-start_time, len(stripped_email))

    db.close()
    return data_dict

def generate_checknote(data_dict):
    # create counters for each occurrence of each type of phi
    foutpath = "/media/DataHD/r_phi_corpus/"
    #finpath = "/media/DataHD/corpus/notes/"
    finpath = "/media/DataHD/baby_notes/"

    first = 0
    last = 0
    mrn = 0
    ssn = 0
    total_records = 0
    phi_containing_records = 0
    acct = 0
    devid = 0
    benid = 0
    email = 0

    mydict = {}
    mydict['fname'] = set()
    mydict['lname'] = set()
    mydict['mrn'] = set()
    mydict['ssn'] = set()
    mydict['acct'] = set()
    mydict['devid'] = set()
    mydict['benid'] = set()
    mydict['email'] = set()
    translator = str.maketrans('', '', string.punctuation)
    
    for file in glob.glob(finpath+"*.txt"):
        with open(file, encoding='utf-8', errors='ignore') as fin:
            total_records += 1
            safe = True
            #print f
            # take the note name for writing
            f_name = file.split("/")[-1]
            #f_name = f.split("\\")[-1]
            f_name = re.findall(r'\d+', f_name)[0]
            # print name_tmp
            # create a new string that will become the note, with known phi removed
            phi_reduced = ''
            #print(fin)
            #words = word_tokenize(fin.read())
            #for word in words:
            for line in fin.read():
                tmp = line.strip()
               
                for word in tmp.translate(translator).split():
                #tmp = line.strip()
                #print tmp
                # the .translate() stuff is just removing punctuation
                # phi_reduced = ''
                #for word in tmp.translate(None, string.punctuation).split():
                    #print word + ' '+'YAAYYY!!'
                    ######
                    #make sure to convert words and phi to lower case later
                    if word.lower() in data_dict['fname']:
                        #print word
                        word = 'f_name'
                        first += 1
                        mydict['fname'].add(f_name)
                        safe = False
                    elif word.lower() in data_dict['lname']:
                        #print word
                        word = 'l_name'
                        last += 1
                        mydict['lname'].add(f_name)
                        safe = False
                    elif word in data_dict['mrn']:
                        #print word
                        word = 'mrn'
                        mrn += 1
                        mydict['mrn'].add(f_name)
                        safe = False
                    elif word in data_dict['ssn']:
                        #print word
                        word = 'ssn'
                        ssn += 1
                        mydict['ssn'].add(f_name)
                        safe = False
                    elif word in data_dict['acct']:
                        #print word
                        word = 'acct'
                        acct += 1
                        mydict['acct'].add(f_name)
                        safe = False
                    elif word in data_dict['devid']:
                        #print word
                        word = 'devid'
                        devid += 1
                        mydict['devid'].add(f_name)
                        safe = False
                    elif word in data_dict['benid']:
                        #print word
                        word = 'benid'
                        benid += 1
                        mydict['benid'].add(f_name)
                        safe = False
                    # judgement: too many 1-3 digits numbers removed if don't filter for larger
                    elif word.lower() in data_dict['email'] and len(word) > 3:
                        #print word
                        word = 'email'
                        email += 1
                        mydict['email'].add(f_name)
                        safe = False
                    else:
                        word = word
                    phi_reduced = phi_reduced + ' ' + word
            # print phi_reduced
            if not safe:
                phi_containing_records += 1
            print(total_records)

    foutfile = "phi_dict.pkl"
    with open(foutfile, "wb") as fout:
        pickle.dump(mydict, fout)

            #print 'Wrote {}'.format(os.path.join(foutpath,name_tmp))

    print('total records processed: {}'.format(total_records))
    print('num records with phi: {}'.format(phi_containing_records))
    print('num of notes first names found: {}'.format(mydict['fname']))
    print('num of notes last names found: {}'.format(mydict['lname']))
    print('num of notes mrns found: {}'.format(mydict['mrn']))
    print('num of notes ssns found: {}'.format(mydict['ssn']))
    print('num of notes account numbers found: {}'.format(mydict['acct']))
    print('num of notes med device ids found: {}'.format(mydict['devid']))
    print('num of notes beneficiary ids found: {}'.format(mydict['benid']))
    print('num of notes emails found: {}'.format(mydict['email']))

def readfile():
    foutpath = "/media/DataHD/r_phi_corpus/"
    with open("phi_dict.pkl", "rb") as fin:
        mydict = pickle.load(fin)
        #print(mydict)
    while True:
        option = input("fname, lname, mrn, ssn, acct, devid, benid, email, 0 to exit> ")
        try:
            if option == "0":
                break
            else:
                print(mydict[option])
        except:
            print("input is wrong")


def main():
    option = input("1 to generate data dict, 2 to check note, 3 to read result >")
    if option == "1":
        data_dict = generate_from_database()
        with open("data_dict.pkl", "wb") as fout:
            pickle.dump(data_dict, fout)
    elif option == "2":
        with open("data_dict.pkl", "rb") as fin:
            data_dict = pickle.load(fin)
        generate_checknote(data_dict)
    elif option == "3":
        readfile()
    else:
        print("input is wrong. Re-run the script")

if __name__ == "__main__":
    main()
