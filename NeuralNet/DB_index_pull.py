import pandas as pd
from NeuralNet import active_learning_module as learn


def db_clean(data_df, save=False):
    # data_df = data_df.drop(data_df.columns[:1], axis=1)
    data_df["word"] = data_df["word"].str.lower()
    data_df = data_df.drop_duplicates(["word"])
    data_df = data_df.sort_values(by="word", axis=0)
    data_df = data_df.reset_index(drop=True)
    if save:
        data_df.to_csv("clean_terms_saved.csv")
    return data_df


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

    # parse through our database
    indices = []
    for sentence in sentences:
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
        indices.append(word_db_id)
    return df, indices


def in_pipe(sentences):
    data_df = pd.read_csv("../Webscrape/clean_terms.csv")
    data_df = data_df.drop(data_df.columns[:1], axis=1)
    #  Categories:
    #  1: variable
    #  2: print
    #  3: loop
    #  4: if
    data_df, indices = parse_input(sentences, data_df)
    return indices

# SAMPLE USAGE
# print(in_pipe(sentences=[["set", "x", "equal", "to", "5"], ["output", "x"], ["loop", "through", "array", "A", "ten", "times"],
#                    ["print", "test"], ["set", "total", "to", "zero"]]))
# returns:
# [[1036, 1275, 431, 1161, 0], [797, 1275], [708, 1155, 80, 1, 1140, 1160], [872, 1145], [1036, 1167, 1161, 1278]]
