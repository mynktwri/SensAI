import os, sys
import pandas as pd
sys.path.append(os.path.join(os.getcwd(), "..", "NLP"))
sys.path.append(os.path.join(os.getcwd(), "..", "NeuralNet"))

import active_learning_module as learn
import Process


def db_clean(data_df, save=False):
    # data_df = data_df.drop(data_df.columns[:1], axis=1)
    data_df["word"] = data_df["word"].str.lower()
    data_df = data_df.drop_duplicates(["word"])
    data_df = data_df.sort_values(by="word", axis=0)
    data_df = data_df.reset_index(drop=True)
    if save:
        data_df.to_csv("clean_terms_saved.csv")
    return data_df


def db_binary(array, l, r, word):
    if r >= l:
        mid = int(l + (r - l) / 2)
        # middle
        if array[mid] == word:
            return mid
        # left
        if array[mid] > word:
            return db_binary(array, l, mid - 1, word)
        # right
        if array[mid] < word:
            return db_binary(array, mid + 1, r, word)
    else:
        return -1


def db_get(word, df):
    db_1D = df["word"].ravel()
    return db_binary(db_1D, 0, len(db_1D) - 1, word)


def changePOS(poslist):
    # Verb = 1, noun = 2, adj = 3, adv = 4,
    # Preposition = 5, article = 6, participle = 7, quantifier = 8,
    # number = 9, symbol = 10
    for x in range(0, len(poslist)):
        # if poslist[x] == "punctuation":
        #     poslist[x] = 0
        #
        # else
        if poslist[x] == "verb":
            poslist[x] = 1

        elif poslist[x] == "noun":
            poslist[x] = 2

        elif poslist[x] == "adjective":
            poslist[x] = 3

        elif poslist[x] == "adverb":
            poslist[x] = 4

        elif poslist[x] == "preposition":
            poslist[x] = 5

        elif poslist[x] == "article":
            poslist[x] = 6

        elif poslist[x] == "participle":
            poslist[x] = 7

        elif poslist[x] == "quantifier":
            poslist[x] = 8

        elif poslist[x] == "numeral":
            poslist[x] = 9

        elif poslist[x] == "symbol":
            poslist[x] = 10

        elif poslist[x] == "coordinating_conj":
            poslist[x] = 11

    return poslist


def parse_input(sentences, df):
    sentences_list = []
    sentences_pos = []
    indices = []
    count = 0
    for s in sentences:
        poslist = Process.getTag(s)
        wordlist = Process.getWord(s)
        for i in range(0, len(poslist)):
            if poslist[i] == "punctuation":
                # remove it
                print("removing " + wordlist[i])
                wordlist.remove(wordlist[i])
                poslist.remove(poslist[i])
        # poslist = changePOS(poslist)
        sentences_list.append(wordlist)
        sentences_pos.append(changePOS(poslist))
        newword = False
        while not newword:
            word_db_id = []
            newword = True
            for i in range(len(wordlist)):
                temp = db_get(wordlist[i].lower(), df)
                if temp == -1:
                    df = learn.new_word(wordlist[i].lower(), df)
                    newword = False
                else:
                    word_db_id.append(temp)
            if not newword: df = db_clean(df, save=True)
        if count % 1000 == 0:
            print(f'{count / len(sentences):1.4f}')
        count += 1
        indices.append(word_db_id)
    # parse through our database
    return df, indices, sentences_list, sentences_pos


def in_pipe(sentences):
    data_df = pd.read_csv("clean_terms_saved.csv")
    data_df = data_df.drop(data_df.columns[:1], axis=1)
    #  Categories:
    #  1: variable
    #  2: print
    #  3: loop
    #  4: if
    data_df, indices, wordlist, poslist = parse_input(sentences, data_df)
    return indices, wordlist, poslist

# SAMPLE USAGE
# print(in_pipe(sentences=[["set", "x", "equal", "to", "5"], ["output", "x"], ["loop", "through", "array", "A", "ten", "times"],
#                    ["print", "test"], ["set", "total", "to", "zero"]]))
# returns:
# [[1036, 1275, 431, 1161, 0], [797, 1275], [708, 1155, 80, 1, 1140, 1160], [872, 1145], [1036, 1167, 1161, 1278]]
