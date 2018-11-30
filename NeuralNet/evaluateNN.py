import os, sys
# sys.path.append(os.path.join(os.getcwd()))
import tensorflow as tf
from tensorflow import keras
import DB_index_pull as db_pull
import numpy as np
import pandas as pd



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






id_list = pd.concat([variable_indices, print_indices, loop_indices], axis=0, ignore_index=True)
pos_list = pd.concat([variable_poslist, print_poslist, loop_poslist], axis=0, ignore_index=True)

input_data = pd.concat([id_list, pos_list], axis=1, ignore_index=True)
input_labels = pd.concat([variable_targets, print_targets, loop_targets], axis=0, ignore_index=True)

train_data = []
train_labels = []
validation_data = []
validation_labels = []
test_data = []
test_labels = []

i = 0
for row in input_data:
    if (i % 7 == 0):
        test_data = test_data + [input_data[i]]
        test_labels = test_labels + [input_labels[i]]
    else:
        train_data = train_data + [input_data[i]]
        train_labels = train_labels + [input_labels[i]]
    i = i + 1

train_data = keras.preprocessing.sequence.pad_sequences(train_data, value=9, padding='post', maxlen=20)
validation_data = keras.preprocessing.sequence.pad_sequences(validation_data, value=9, padding='post', maxlen=20)
test_data = keras.preprocessing.sequence.pad_sequences(test_data, value=9, padding='post', maxlen=20)

# Build the model

vocab_size = 10

model = keras.Sequential()
model.add(keras.layers.Embedding(vocab_size, 16))
model.add(keras.layers.GlobalAveragePooling1D())
model.add(keras.layers.Dense(16, activation=tf.nn.relu))
model.add(keras.layers.Dense(1, activation=tf.nn.sigmoid))

model.compile(optimizer=tf.train.AdamOptimizer(),
              loss='binary_crossentropy',
              metrics=['accuracy'])

#  Train the model

history = model.fit(train_data,
                    train_labels,
                    epochs=40,
                    batch_size=512,
                    validation_data=(validation_data, validation_labels),
                    verbose=1)

results = model.evaluate(test_data, test_labels)

print(results)
