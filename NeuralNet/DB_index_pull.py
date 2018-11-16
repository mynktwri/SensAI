import tensorflow as tf
from tensorflow import keras
import NeuralNet.db_clean as db_clean
import numpy as np
import pandas as pd
from NeuralNet import active_learning_module as learn


def db_get(word, df):
    count = 0
    found = 0
    for i in df["word"].str.match(word):
        if i:
            found = 1
            break
        else:
            count += 1
    if found:
        return count
    else:
        return -1


def parse_input(sentences, df):
    # TODO: sentence into NLP goes here

    # TODO: parse through our database and add that to tensor
    for sentence in sentences:
        newword = False
        while not newword:
            word_db_id = []
            df = db_clean.db_clean(df)
            newword = True
            for i in range(len(sentence)):
                temp = db_get(sentence[i].lower(), df)
                if temp == -1:
                    df = learn.new_word(sentence[i].lower(), df)
                    newword = False
                else:
                    word_db_id.append(temp)
        return df, word_db_id


# training data
data_df = pd.read_csv("../Webscrape/clean_terms.csv")

data_df = data_df.drop(data_df.columns[:1], axis=1)
#  Categories:
#  1: variable
#  2: print
#  3: loop
#  4: if
#

train_labels = [1, 2, 3, 2, 1]
train_string = [["set", "x", "equal", "to", "5"], ["output", "x"], ["loop", "through", "array", "A", "ten", "times"],
                ["print", "test"], ["set", "total", "to", "zero"]]
train_data = [[0, 9999, 5, 9999, 9999], [46, 9999], [17, 20, 30, 9999, 9999, 9999], [45, 1287], [0, 403, 9999, 9999]]
test_train_data = []
for i in train_string:
    data_df, sentence = parse_input(i, data_df)
    test_train_data.append(sentence)
    print(sentence, " | ", i)
