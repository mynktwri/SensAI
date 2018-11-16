import tensorflow as tf
from tensorflow import keras

import numpy as np
import pandas as pd

input_data = []
input_labels = []

def db_get(word):
    count = 0
    for i in data_df["word"].str.match(word):
        if i:
            return count
        else:
            count += 1
    return 9999

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
        return 9999

def parse_input():
    global input_data
    global input_labels
    #data_sentences = pd.read_csv("test.txt")
    data_sentences = pd.read_csv("../setVar_bigSet/out_script_16000sentences.txt")
    for (index, row) in data_sentences.iterrows():
        sentence_data = []
        count = 0
        for word in row[0].split(' '):
            index = db_get(word)
            sentence_data = sentence_data + [index]
            if ((word == row[2].strip()) and (len(input_data) == len(input_labels))):
                input_labels = input_labels + [count]
            count = count + 1
        input_data = input_data + [sentence_data]

# training data
data_df = pd.read_csv("../Webscrape/clean_terms.csv")

data_df = data_df.drop(data_df.columns[:1], axis=1)
#  Categories:
#  1: variable
#  2: print
#  3: loop
#  4: if
#

parse_input()

train_data = []
train_labels = []
validation_data = []
validation_labels = []
test_data = []
test_labels = []

i = 0
for row in input_data:
    if(i%3 == 0):
        train_data = train_data + [input_data[i]]
        train_labels = train_labels + [input_labels[i]]
    if(i%3 == 1):
        validation_data = validation_data + [input_data[i]]
        validation_labels = validation_labels + [input_labels[i]]
    if(i%3 == 2):
        test_data = test_data + [input_data[i]]
        test_labels = test_labels + [input_labels[i]]
    i = i + 1

train_data = keras.preprocessing.sequence.pad_sequences(train_data,value=9998,padding='post', maxlen=20)
validation_data = keras.preprocessing.sequence.pad_sequences(validation_data,value=9998,padding='post', maxlen=20)
test_data = keras.preprocessing.sequence.pad_sequences(test_data,value=9998,padding='post', maxlen=20)

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

