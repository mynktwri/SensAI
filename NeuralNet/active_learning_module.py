from NeuralNet import db_clean
import pandas as pd
#takes a new word and adds it to the database
def new_word(word, data_df):
    new_df = None
    for i in data_df:
        if i == "word":
            # TODO: ask through command line what category the word is in.
            new_df = data_df.append(pd.DataFrame([[word, 0, 0, 0, 0]], columns=["word","if-then","variable","print","loop"]))
    return new_df


def word_test(word, data_df):
    flag = 0
    for i in data_df["word"]:
        if i == word:
            flag = 1
    assert flag
