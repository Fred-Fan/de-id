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
import nltk


extraction_set = {'temp', 'resp', 'rate', 'pulse', 'pressure',}

with open("data\\ext.pkl", 'wb') as fout:
    pickle.dump(extraction_set, fout)


