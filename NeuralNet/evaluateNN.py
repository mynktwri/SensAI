import os, sys
# sys.path.append(os.path.join(os.getcwd()))
import tensorflow as tf
from tensorflow import keras
import DB_index_pull as db_pull
import numpy as np
import pandas as pd
import random
random.seed(7)


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
def parse_input(filename):
    sentences, targets = read_sentences(filename)
    indices, wordlist, poslist = db_pull.in_pipe(sentences)
    indices = keras.preprocessing.sequence.pad_sequences(indices, 10, padding='post')
    poslist = keras.preprocessing.sequence.pad_sequences(poslist, 10, padding='post')
    # print(len(indices))
    # print(len(wordlist))
    # print(len(poslist))
    indices = pd.DataFrame.from_dict(indices)
    poslist = pd.DataFrame.from_dict(poslist)
    #TODO: assert to confirm shape of dataframes
    return indices, poslist, targets


# data_df = pd.read_csv("../Webscrape/clean_terms.csv")

# data_df = data_df.drop(data_df.columns[:1], axis=1)
#  Categories:
#  1: variable
#  2: print
#  3: loop
#  4: if
#

# training data
# if_indices, if_poslist, if_targets = parse_input("if_data.csv")
variable_indices, variable_poslist, variable_targets = parse_input("variable_data.csv")
print_indices, print_poslist, print_targets = parse_input("print_data.csv")
loop_indices, loop_poslist, loop_targets = parse_input("loop_data.csv")

#concatenate data to a meaningful shape for the neural network
id_list = pd.concat([variable_indices, print_indices, loop_indices], axis=0, ignore_index=True)
pos_list = pd.concat([variable_poslist, print_poslist, loop_poslist], axis=0, ignore_index=True)

input_data = pd.concat([id_list, pos_list], axis=1, ignore_index=True)
input_labels = pd.concat([variable_targets, print_targets, loop_targets], axis=0, ignore_index=True)


train_data = pd.DataFrame()
train_labels = pd.Series()
# validation_data = pd.DataFrame()
# validation_labels = pd.Series()
test_data = pd.DataFrame()
test_labels = pd.Series()

shuffled_data = pd.DataFrame.reset_index(pd.DataFrame.sample(pd.concat([input_data, input_labels],
                                                                       axis=1, ignore_index=True),
                                                             frac=1))
train_labels = shuffled_data[20]
train_data = shuffled_data.drop(columns=20)
train_data, test_data = np.split(train_data, [int(.9*len(train_data))])
train_labels, test_labels = np.split(train_labels, [int(.9*len(train_labels))])


# for i in range(1, len(input_data)):
#     if i % 7 == 0:
#         test_data = pd.concat([test_data, input_data[:i]], axis=0, ignore_index=True)
#         test_labels.append(pd.Series(input_labels[i]), ignore_index=True)
#         print(i/len(input_data))
#     if i % 10 == 0:
#         validation_data = pd.concat([validation_data, input_data[:i]], axis=0, ignore_index=True)
#         validation_labels.append(pd.Series(input_labels[i]), ignore_index=True)
#         print(i / len(input_data))
#     else:
#         train_data = pd.concat([train_data, input_data[:i]], axis=0, ignore_index=True)
#         train_labels.append(pd.Series(input_labels[i]), ignore_index=True)
print(test_data.shape)
print(test_labels.shape)
# print(validation_data.shape)
# print(validation_labels.shape)
print(train_data.shape)
print(train_labels.shape)
exit(0)
# Build the model

# vocab_size is the size of our database at model initialization.
# this ensures that all new words have already been added to the database.
vocab_size = db_pull.db_len

model = keras.Sequential()
# Input Layer
model.add(keras.layers.Embedding(vocab_size, 16))
#   Outputs shape=
model.add(keras.layers.GlobalAveragePooling1D())
#   Outputs 1D shape=
# Hidden Layer
model.add(keras.layers.Dense(16, activation=tf.nn.relu))
# Output Layer: needs as many nodes as there are categories.
model.add(keras.layers.Dense(3, activation='softmax'))

model.compile(optimizer=tf.train.AdamOptimizer(),
              loss='categorical_crossentropy',
              metrics=['accuracy']) # consider RMSE or MSE as metric for error

#  Train the model

history = model.fit(x=train_data,
                    y=train_labels,
                    epochs=40,
                    batch_size=512,
                    validation_split = 0.1,
                    # validation_data=(validation_data, validation_labels),
                    verbose=1)
print(history)
results = model.evaluate(test_data, test_labels)

print(results)
