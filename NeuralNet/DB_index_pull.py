import pandas as pd
from NeuralNet import active_learning_module as learn
from NLP import Process


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


def parse_input(sentences, df):
    # TODO: sentence into NLP goes here
    sentences_list = []
    sentences_pos = []
    for s in sentences:
        poslist = Process.getTag(s)
        wordlist = Process.getWord(s)
        for i in range(len(wordlist), 0):
            if poslist[i] == "punctuation":
                # remove it
                print("removing " + wordlist[i])
                wordlist.remove(wordlist[i])
                poslist.remove(poslist[i])
        sentences_list.append(wordlist)
        sentences_pos.append(poslist)
    # parse through our database
    indices = []
    count = 0
    for sentence in sentences_list:
        newword = False
        while not newword:
            word_db_id = []
            newword = True
            for i in range(len(sentence)):
                temp = db_get(sentence[i].lower(), df)
                if temp == -1:
                    df = learn.new_word(sentence[i].lower(), df)
                    newword = False
                else:
                    word_db_id.append(temp)
            if not newword: df = db_clean(df, save=True)
        print(count / len(sentences_list))
        count += 1
        indices.append(word_db_id)
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
