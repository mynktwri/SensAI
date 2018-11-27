import os, sys
# sys.path.append(os.path.join(os.getcwd()))
import tensorflow as tf
from tensorflow import keras
import DB_index_pull as db_pull
import numpy as np
import pandas as pd

input_data = []
input_labels = []


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
    return pd.read_csv("data/" + filename)["sen"].transpose()


def parse_sentences(sentences):
    for s in sentences:
        test = pos_sentence(s)
        print(test)



def pos_sentence(sentence):
    print(sentence)

# parse input through a file
# sentences returns the list of series words in each sentence
def parse_input(filename):
    sentences = read_sentences(filename)
    indices, wordlist, poslist = db_pull.in_pipe(sentences)

    # print(len(indices))
    # print(len(wordlist))
    # print(len(poslist))

    return indices, poslist




# data_df = pd.read_csv("../Webscrape/clean_terms.csv")

# data_df = data_df.drop(data_df.columns[:1], axis=1)
#  Categories:
#  1: variable
#  2: print
#  3: loop
#  4: if
#

# training data
# parse_input("if_data.csv")
# parse_input("variable_data.csv")
print_indices, print_poslist = parse_input("print_data.csv")
loop_indices, loop_poslist = parse_input("loop_data.csv")

train_data = []
train_labels = []
validation_data = []
validation_labels = []
test_data = []
test_labels = []

i = 0
for row in input_data:
    if (i % 3 == 0):
        train_data = train_data + [input_data[i]]
        train_labels = train_labels + [input_labels[i]]
    if (i % 3 == 1):
        validation_data = validation_data + [input_data[i]]
        validation_labels = validation_labels + [input_labels[i]]
    if (i % 3 == 2):
        test_data = test_data + [input_data[i]]
        test_labels = test_labels + [input_labels[i]]
    i = i + 1

train_data = keras.preprocessing.sequence.pad_sequences(train_data, value=9998, padding='post', maxlen=20)
validation_data = keras.preprocessing.sequence.pad_sequences(validation_data, value=9998, padding='post', maxlen=20)
test_data = keras.preprocessing.sequence.pad_sequences(test_data, value=9998, padding='post', maxlen=20)

# Build the model

vocab_size = 10000

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
