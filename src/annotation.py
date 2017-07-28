from nltk import sent_tokenize
from nltk import word_tokenize
import argparse
from string import punctuation
import pickle
import os
import sys
import re


def annotating(note):
    annotation_list = []
    note = sent_tokenize(note)
    allowed_category = ('0', '1', '2', '3', '4', '5', '6', '7')
    allowed_command = ('exit', 'all', 'skip', 'next', 'pick', 'show',  'done')
    allowed_input = allowed_category + allowed_command
    for sent in note:
        sent_list = []
        words = word_tokenize(sent)
        word = [word for word in words if word not in punctuation]
        print(sent)
        for j in range(len(word)):
            sent_list.append([word[j], '0', j+1])
        print('\n')
        [print("({}){}[{}]".format(temp[2], temp[0], temp[1]), end=' ') for temp in sent_list]
        print('\n')
        # for idx, val in enumerate(word):
           # print("({}){} ".format(idx + 1, val), end='')
        print('\n0:Non-phi, 1:Name, 2:Address, 3:Postal code,'
             '4:Phone/FAX, 5:SSN, 6:DOB, 7:others >')

        i = 0
        while True:
            if i == len(word):
                user_input = input('The end of the sentence. Enter done to next sentence or others to edit. > ')
                if user_input == 'done':
                    break
                else:
                    i = i - 1


            user_input = input('({}){}> '.format(i+1, word[i]))

            if user_input not in allowed_input:
                print("Input is not right, please re-input.")

            else:
                if user_input == 'exit':
                    return []

                elif user_input == 'all':
                    user_input = input('which kind of info are all words? > ')
                    if user_input in allowed_category:
                        for j in range(0,len(word)):
                            sent_list[j][1] = user_input
                        user_input = input('Press Enter to finish the'
                                     ' editing of this sentence, or others'
                                     ' to go back to the last word. > ')
                        if user_input == '':
                            break
                        else:
                            i = len(word) - 1
                    else:
                        print('Wrong category. Will go back to the word you were editing.')

                elif user_input == 'skip':
                    user_input = input("which words are you going back to: ")
                    if user_input.isdigit() and 1 <= int(user_input) <= len(word):
                        i = int(user_input) - 1
                    else:
                        print('Wrong word. Will go back to the word you were editing.')

                elif user_input == 'next':
                    user_input = input('To which word to edit at the same time: ')
                    if user_input.isdigit() and i+1 < int(user_input) <= len(word):
                        category = input('which kind of info are these words? > ')
                        if category in allowed_category:
                            for j in range(i, int(user_input)):
                                sent_list[j][1] = category
                                #annotation_list.append([word[j], category])
                            i = int(user_input)
                        else:
                            print('Wrong category. Will go back to the word you were editing.')

                elif user_input == 'pick':
                    user_input = input('which words are you going to edit, seperated by space: ')
                    pick_list = user_input.split(' ')
                    user_input = input('which kind of info are these words? > ')
                    if user_input in allowed_category:
                        for j in pick_list:
                            if j.isdigit() and 0 < int(j) <= len(word):
                                sent_list[int(j)-1][1] = user_input
                                print('{} is changed.'.format(sent_list[int(j)-1][0]))
                            else:
                                print('{} is not a right sequence'.format(j))
                    else:
                        print('Wrong category. Will go back to the word you were editing.')

                elif user_input == 'show':
                    print('\n')
                    [print("({}){}[{}]".format(temp[2], temp[0], temp[1]), end=' ') for temp in sent_list]
                    print('\n')

                elif user_input == 'done':
                    break

                else:
                    #temp = re.sub(r'[\/\-\:\~\_]', ' ', word[i])
                    #temp = temp.split(' ')
                    #for j in temp:
                    #    annotation_list.append([j, user_input])
                    sent_list[i][1] = user_input
                    i += 1
        '''
        for i in word:
            if i not in punctuation:
                category = input("{} > ".format(i))
                # sys.stdout.flush()
                i = re.sub(r'[\/\-\:\~\_]', ' ', i)
                temp = i.split(' ')
                for j in temp:
                    annotation_list.append([j, category])
                    '''
        for result in sent_list:
            temp = re.sub(r'[\/\-\:\~\_]', ' ', result[0])
            temp = temp.split(' ')
            for j in temp:
                annotation_list.append([j, result[1]])
        #[annotation_list.append(result) for result in sent_list]
        print("\n")
            # else:
                # annotation_list.append((i,'0'))
        # annotation_list.append([sent_list])

    return annotation_list


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--inputfile", required=True,
                    help="Path to the file that contains the PHI note.")
    ap.add_argument("-o", "--output", required=True,
                    help="Path to the directory that save the annotated notes.")

    args = ap.parse_args()

    finpath = args.inputfile
    if os.path.isfile(finpath):
        head, tail = os.path.split(finpath)
    foutpath = args.output

    with open(finpath, encoding='utf-8', errors='ignore') as fin:
        note = fin.read()
    annotation_list = annotating(note)
    print(annotation_list)
    file_name = foutpath + "/annotated_" + tail.split('.')[0] + ".ano"
    if annotation_list != []:
        with open(file_name, 'wb') as fout:
            pickle.dump(annotation_list, fout)


if __name__ == "__main__":
    main()
