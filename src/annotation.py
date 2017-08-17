from nltk import sent_tokenize
from nltk import word_tokenize
import argparse
from string import punctuation
import pickle
import os
import re

"""
Annotate each word in a text file as either being PHI (if so, annotate the type of PHI)
or not.

When the program launches, each word from the input file is displayed preceded by it's word index for reference, one sentence
at a time.

Labels each word as a category of PHI (not-phi is an option). Writes the annotated file out as a list of lists
Into a pickle file with the original file name and .ano as the file extention.
Each sublist contains 2 elements: [word_from_original_text, phi_label]

This is useful to generate a ground-truth corpus for the evaluation of the phi-reducer
software on your own files, or for the creation of a training corpus for machine learning de-id
methods.

"""
def annotating(note):
    annotation_list = []
    note = sent_tokenize(note)
    allowed_category = ('0', '1', '2', '3', '4', '5', '6', '7', '8',
                        '9', '10', '11', '12', '13', '14', '15', '16',
                        '17', '18')
    allowed_command = ('exit', 'all', 'range', 'select', 'show', 'done', 'help')
    for sent in note:
        sent_list = []
        words = word_tokenize(sent)
        word = [word for word in words if word not in punctuation]
        print(sent)
        for j in range(len(word)):
            sent_list.append([word[j], '0', j + 1])
        print('\n')
        [print("({}){}[{}]".format(temp[2], temp[0], temp[1]), end=' ') for temp in sent_list]
        print('\n')
        print('Category to use: 0:Non-phi, 1:Name, 2:Address, 3:DOB,'
             '4:Phone, 5:FAX, 6:Email, 7:SSN, 8:MRN, 9:Health insurance'
             ' beneficiary numbers, 10:Account Number, 11:Certificate number,'
             ' 12:Vehicle number, 13:Device number,'
             ' 14:URLs, 15:IP, 16:Biometric identifiers, 17:Imanges, 18:Otheres\n')

        while True:
            user_input = input('Please input command (enter \'help\' for more info): ')

            if user_input not in allowed_command:
                print("Command is not right, please re-input.")

            else:
                if user_input == 'exit':
                    return []

                elif user_input == 'all':
                    user_input = input('which phi-category do you want to assign to all words? > ')
                    if user_input in allowed_category:
                        for j in range(0, len(word)):
                            sent_list[j][1] = user_input
                        user_input = input('Press Enter to finish the'
                                     ' editing of this sentence, or others'
                                     ' to go back to the commend type. > ')
                        if user_input == '':
                            break
                    else:
                        print('Wrong category. Will go back to the commend type.')

                elif user_input == 'range':
                    start_word = input('From which word to edit at the same time: ')
                    if start_word.isdigit() and 0 < int(start_word) <= len(word):
                        end_word = input('To which word to edit at the same time: ')
                        if end_word.isdigit() and int(start_word) < int(end_word) <= len(word):
                            category = input('which phi-category do you want to assign to these words? > ')
                            if category in allowed_category:
                                for j in range(int(start_word)-1, int(end_word)):
                                    sent_list[j][1] = category
                            else:
                                print('Wrong category. Will go back to the commend type.')
                        else:
                            print('Wrong word. Will go back to the commend type.')
                    else:
                        print('Wrong word. Will go back to the commend type.')

                elif user_input == 'select':
                    user_input = input('which words are you going to edit, seperated by space: ')
                    pick_list = user_input.split(' ')
                    user_input = input('which phi-category do you want to assign to these words? > ')
                    if user_input in allowed_category:
                        for j in pick_list:
                            if j.isdigit() and 0 < int(j) <= len(word):
                                sent_list[int(j) - 1][1] = user_input
                                print('{} is changed.'.format(sent_list[int(j) - 1][0]))
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

                elif user_input == 'help':
                    print('(X)WORD[Y]: X is the sequence number of the word,'
                        ' Y is the current phi-category of the word. All words'
                        ' will be set to 0, non-phi, as default.')
                    print('Command:')
                    print('all: enter \'all\' to change the phi-category of all'
                         ' words in the document at the same time.')
                    print('range: enter \'range\' to select a range of word indices'
                         ' and then assign the same phi-category to all words in'
                         ' that range. Enter the index of the first word and hit'
                         ' RETURN.Enter the index of the last word and hit RETURN. ')
                    print('select: enter \'select\' to select a list of word indices'
                         ' and then assign the same phi-category to all words in that'
                         ' list.Enter the index of each word, using spaces to separate'
                         ' each word index, hit RETURN when you have listed all desired word indices.')
                    print('show: enter \'show\' to show the current current phi-category of all words')
                    print('done: enter \'done\' to finish annotating the current'
                        ' sentence and start the next one.')
                    print('exit: enter \'exit\' to exit the script without saving. \n')
        for result in sent_list:
            temp = re.sub(r'[\/\-\:\~\_]', ' ', result[0])
            temp = temp.split(' ')
            for j in temp:
                annotation_list.append([j, result[1]])
        print("\n")

    return annotation_list


def main():

    """
Does: labels each word as a category of PHI (not-phi is an option). Writes the annotated file out as a list of lists
Into a pickle file with the original file name and .ano as the file extention.
Each sublist contains 2 elements: [word_from_original_text, phi_label]

Uses:
nltk.sent_tokenize: Splits a file into sentence-by-sentence chunks.
nltk.word_tokenize: Splits a sentence in word-by-word chunks.
string.punctuation: Checks characters to see if they are punctuation. Punctuation is displayed for annotation
but will be defined as non-phi within the annotated file
re: Some words contain special characters such as '-' or '/'. The phi-reducer script splits words on these
characters as filters each subword independently. RE are used to also split words for annotation on special characters.


Arguments:
"-i", "--inputfile", help="Path to the file you would like to annotate.")
"-o", "--output", help="Path to the directory where the annotated note will be saved.")

Returns:
pickled list of lists with the original file name and .ano as the file extention.
Each sublist contains 2 elements: [word_from_original_text, phi_label]

    """

    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--inputfile", required=True,
                    help="Path to the file you would like to annotate.")
    ap.add_argument("-o", "--output", required=True,
                    help="Path to the directory where the annotated note will be saved.")
    ap.add_argument("-n", "--name", default="phi_reduced",
                   help="The key word of the annotated file, the default is *_phi_reduced.ano.")

    args = ap.parse_args()
    key_word = args.name

    finpath = args.inputfile
    if os.path.isfile(finpath):
        head, tail = os.path.split(finpath)
    else:
        print("Input file does not exist.")
        os._exit(0)
    foutpath = args.output
    if not os.path.isdir(foutpath):
        user_input = input("Output folder:{} does not exist, would you like to create it?: press y to create: ".format(foutpath))
        if user_input == 'y':
            print("Creating {}".format(foutpath))
            os.mkdir(foutpath)
        else:
            print("Quitting")
            os._exit(0)
    with open(finpath, encoding='utf-8', errors='ignore') as fin:
        note = fin.read()
    annotation_list = annotating(note)
    file_name = '.'.join(tail.split('.')[:-1]) + "_"+ key_word + ".ano"
    file_path = os.path.join(foutpath, file_name)
    if annotation_list != []:
        print(annotation_list)
        with open(file_path, 'wb') as fout:
            pickle.dump(annotation_list, fout)


if __name__ == "__main__":
    main()
