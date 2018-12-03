import pandas as pd
import keras
import DB_index_pull as db_pull
from sklearn.preprocessing import LabelEncoder

def db_getlabel(input):
    if input == "variable":
        return 1
    elif input == "print":
        return 2
    elif input == "loop":
        return 3
    elif input == "if":
        return 4
    else:
        return -1


# reads sentences from filename
# returns a list of Series of words in the sentence
#   each index of list is one sentence
def read_sentences(filename):
    return pd.read_csv("data/" + filename)["sen"], pd.read_csv("data/" + filename)["cat"]


# parse input through a file
# sentences returns the list of series words in each sentence
def parse_input(filename, save):
    sentences, targets = read_sentences(filename)
    indices, wordlist, poslist = db_pull.in_pipe(sentences, save)
    # pad sequences to the same length
    indices = pd.DataFrame.from_dict(keras.preprocessing.sequence.pad_sequences(indices, 10, padding='post'))
    poslist = pd.DataFrame.from_dict(keras.preprocessing.sequence.pad_sequences(poslist, 10, padding='post'))
    # print(len(indices))
    # print(len(wordlist))
    # print(len(poslist))
    # TODO: assert to confirm shape of dataframes
    assert type(indices) == pd.DataFrame
    return indices, poslist, targets
#  Categories:
#  1: variable
#  2: print
#  3: loop
#  4: if
def gather(save=True):
    # training data
    if_indices, if_poslist, if_targets = parse_input("if_data.csv", save)
    variable_indices, variable_poslist, variable_targets = parse_input("variable_data.csv", save)
    print_indices, print_poslist, print_targets = parse_input("print_data.csv",save)
    loop_indices, loop_poslist, loop_targets = parse_input("loop_data.csv", save)

    #concatenate data to a meaningful shape for the neural network
    id_list = pd.concat([variable_indices, print_indices, loop_indices, if_indices], axis=0, ignore_index=True)
    pos_list = pd.concat([variable_poslist, print_poslist, loop_poslist, if_poslist], axis=0, ignore_index=True)

    input_data = pd.concat([id_list, pos_list], axis=1, ignore_index=True)
    input_labels = pd.concat([variable_targets, print_targets, loop_targets, if_targets], axis=0, ignore_index=True)
    shuffled_data = pd.DataFrame.reset_index(pd.DataFrame.sample(pd.concat([input_data, input_labels],
                                                                       axis=1, ignore_index=True),
                                                             frac=1), drop=True)
    # onehot encode class values as integers
    encoder = LabelEncoder()
    encoder.fit(["variable", "print", "loop", "if"])
    encoded_labels = encoder.transform(shuffled_data[20])
    #   convert integers to variables
    encoded_labels = pd.DataFrame(keras.utils.to_categorical(encoded_labels))
    # drop label column from training data
    train_data = shuffled_data.drop(columns=[20])
    # save values
    pd.DataFrame.to_csv(encoded_labels, "encoded_labels.csv",index_label=False)
    pd.DataFrame.to_csv(train_data, "train_data.csv", index_label=False)
    # TODO: assert for file writing
    return 0

