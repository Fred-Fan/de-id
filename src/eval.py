#import cPickle
#import _pickle as cPickle 
import pickle
import os, sys
import glob, glob
#import MySQLdb as mdb
import string
import re
from collections import defaultdict
import nltk
from nltk import sent_tokenize, word_tokenize
import argparse


ap = argparse.ArgumentParser()
ap.add_argument('-o', "--original_note", help = "Path to the directory that contains the original text", default = 'compare_o')
ap.add_argument("-p", "--phi_note",  help = "Path to the directory that contains the phi text", default = 'compare_p')
args = vars(ap.parse_args())
    
    
class phi_evaluation:
        
    def __init__(self,note1,note2):
        self.note1 = note1
        self.note2 = note2
        
    def preprocess(self):

        temp_id = re.search(r'\s\d+\s', self.note1).group(0)
        self.note_id = re.search(r'\d+', temp_id).group(0)
        phi_note_id = self.note1[:self.note1.index(temp_id)+len(temp_id)]
        self.note1 = self.note1.replace(phi_note_id, 'FILTERED ')
        note1_sent = sent_tokenize(self.note1.replace('-', ' ').replace('/', ' '))
        note2_sent = sent_tokenize(self.note2.replace('-', ' ').replace('/', ' '))
        self.word_sent_note1 = [word_tokenize(sent) for sent in note1_sent]
        self.word_sent_note2 = [word_tokenize(sent) for sent in note2_sent]
        if len(self.word_sent_note1) != len(self.word_sent_note2):
            print("note lengths are not match")
        else:
            print("ok to start to compare")
        
    def evaluation(self):
        
        temp_dict = defaultdict(int)
        error_dict = {}

        try:
            for i in range(len(self.word_sent_note1)):
                if len(self.word_sent_note1[i]) != len(self.word_sent_note2[i]):
                    print("sentence ",i," not match.")
                    print(" ".join(self.word_sent_note1[i]), len(self.word_sent_note1[i]))
                    print(" ".join(self.word_sent_note2[i]), len(self.word_sent_note2[i]))
                else:
                    print("sentence",i, ":")
                    print(" ".join(self.word_sent_note1[i]))
                    print(" ".join(self.word_sent_note2[i]))
                    print("input 1 for true positive(TP), the word is filtered properly")
                    print("input 2 for false positive(FP), the word should not be filtered but is.")
                    print("input 3 for true negative(TN), the word should not be filtered and is not.")
                    print("input 4 for false negative(FN), the word should be filtered but not")
                    for j in range(len((self.word_sent_note1[i]))):
                        print(self.word_sent_note1[i][j], self.word_sent_note2[i][j])
                        answer = input("your feedback (please input 1-4)> ")
                        while True:
                            if answer.isdigit() and 1<= int(answer) <= 4:
                                temp_dict[answer] += 1
                                if int(answer) == 2 or int(answer) == 4:
                                    if answer not in error_dict.keys():
                                        error_dict[answer] = [[self.word_sent_note1[i][j], self.word_sent_note2[i][j]]]
                                    else:
                                        error_dict[answer].append([self.word_sent_note1[i][j], self.word_sent_note2[i][j]])
                                break
                            else:
                                answer = input("please reinput > ")
            return self.note_id, temp_dict, error_dict        
        except:
            print(self.word_sent_note1[i][j], self.word_sent_note2[i][j])
            
                            

def main():
    
    #result_all = {}
    
    with open("result_all.pkl", "rb") as fin:
        result_all = pickle.load(fin)
    
    ori_list = []
    phi_list =[]
    
    #for f in glob.glob(args['original_note']+"\\*.txt"):
    for f in glob.glob(args['original_note']+'\\*.txt'):
        with open(f) as fin:
            ori_list.append(fin.read())

    for f in glob.glob(args['phi_note']+"\\*.txt"):
        with open(f) as fin:
            phi_list.append(fin.read())    

    if len(ori_list) != len(phi_list):
        print("the numbers of the input notes are not match.")
    else:
        for i in range(len(ori_list)):
           # print(3)
            result_file = {}
            phi_eval = phi_evaluation(ori_list[i], phi_list[i])
            phi_eval.preprocess()
            note_id, temp_dict, error_dict = phi_eval.evaluation()
            result_file['summary'] = temp_dict
            result_file['word'] = error_dict
            result_all[note_id] = result_file
    print(result_all)
    with open('result_all.pkl', 'wb') as fout:
        pickle.dump(result_all, fout)
    
if __name__ == '__main__':
    main()