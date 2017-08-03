
# coding: utf-8

# In[130]:

from nltk.corpus import wordnet as wn
import re
from collections import Counter


# In[131]:

with open('whitedict.txt', 'r') as fin:
    WORDS = set(fin.read().split(','))



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
    def candidates(self,word): 
        #"Generate possible spelling corrections for word."
        return (self.known(set(word)) or self.known(self.edits1(word)) or self.known(self.edits2(word)) or [word])

    def known(self,words): 
        #"The subset of `words` that appear in the dictionary of WORDS."
        return list(w+'***' for w in words if w in WORDS)

    def edits1(self,word):
        "All edits that are one edit away from `word`."
        letters    = 'abcdefghijklmnopqrstuvwxyz'
        splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
        deletes    = [L + R[1:]               for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
        replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
        inserts    = [L + c + R               for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    def edits2(self,word): 
        "All edits that are two edits away from `word`."
        return (e2 for e1 in self.edits1(word) for e2 in self.edits1(e1))

    def autocorrection(self,word):
        if len(wn.synsets(word.lower(),pos=wn.NOUN)) != 0:
            return word, False
        else:
            if word.lower() == self.candidates(word.lower())[0]:
                return word, False
            else:
                return self.candidates(word.lower())[0], True


# In[186]:

def main():
    a= autocorrect()
    word = input('>')
    word,flag = a.autocorrection(word)
    print(word,flag )


# In[188]:

if __name__ == "__main__":
    main()


# In[ ]:



