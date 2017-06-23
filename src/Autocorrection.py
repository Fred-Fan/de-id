
# coding: utf-8

# In[130]:

from nltk.corpus import wordnet as wn
import re
from collections import Counter
import pickle

# In[131]:
'''
with open('whitedict.txt', 'r') as fin:
    WORDS = set(fin.read().split(','))
'''
with open("whitelist.pkl", "rb") as fp:
    #whitelist = pickle.load(fp, encoding="bytes")
    whitelist = pickle.load(fp)


'''
def words(text): 
    return re.findall(r'\w+', text.lower())

def P(word, N=sum(WORDS.values())): 
    #"Probability of `word`."
    return WORDS[word] / N


def correction(word): 
    #"Most probable spelling correction for word."
    return max(candidates(word), key=P)

'''
class autocorrect:
    def __init__(self,word, whitelist):
        self.word = word
        self.whitelist = whitelist
    
    def candidates(self): 
        #"Generate possible spelling corrections for word."
        #return (self.known([self.word]) or self.known(self.edits1(self.word)) or self.known(self.edits2()) or [self.word])
        return (self.known([self.word]) or self.known(self.edits1(self.word.lower())) or [self.word])

    def known(self, words):
        #"The subset of `words` that appear in the dictionary of WORDS."
        return list(w for w in words if w in self.whitelist)

    def edits1(self, word_test):
        "All edits that are one edit away from `word`."
        letters    = 'abcdefghijklmnopqrstuvwxyz'
        splits     = [(word_test[:i], word_test[i:])    for i in range(len(word_test) + 1)]
        deletes    = [L + R[1:]               for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
        replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
        inserts    = [L + c + R               for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    def edits2(self): 
        "All edits that are two edits away from `word`."
        return (e2 for e1 in self.edits1(self.word) for e2 in self.edits1(e1))

    def autocheck(self):
        if self.word.lower() in self.whitelist:
            return self.word,1
        elif self.word.lower() == self.candidates()[0].lower():
            #print(2)
            return self.word, 2
        else:
            #print(3)
            return self.candidates()[0], 3


# In[186]:

def main():
    word = input('>')
    a= autocorrect(word, whitelist)
    word,flag = a.autocheck()
    print(word, flag)


# In[188]:

if __name__ == "__main__":
    main()


# In[ ]:



