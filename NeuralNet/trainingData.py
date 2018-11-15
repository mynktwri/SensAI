import tensorflow as tf
from tensorflow import keras

import numpy as np
import pandas as pd


def db_get(word):
    count = 0
    for i in data_df["word"].str.match(word):
        if i:
            return count
        else:
            count += 1
    return -1


def parse_input(sentence):
    # TODO: sentence into NLP goes here

    # TODO: parse through our database and add that to tensor
    db_get(sentence)
    #


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
    sentence = []
    for j in i:
        sentence.append(db_get(j))
        # print(data_df["word"])
        # if (data_df[i][j] != None):
        #     print(data_df[j])
        # else:
        #     print("not found")
    test_train_data.append(sentence)
print(test_train_data)

#
#
#
#
# train_data = keras.preprocessing.sequence.pad_sequences(train_data,value=9998,padding='post', maxlen=20)
#
# # validation data
#
# validation_labels = [3,1,2,3]
# validation_string = [["iterate", "through", "m", "for", "i", "=", "1", "to", "3"],["let","x","equal","4"],["output","the","variable","x"],["print","hello","for","each","element","in","array","m"]]
# validation_data = [[19,20,9999,15,9999,9999,9999,9999,9999],[9999,9999,5,9999],[46,9999,3,9999],[45,9999,15,16,24,37,30,9999]]
#
# validation_data = keras.preprocessing.sequence.pad_sequences(validation_data,value=9998,padding='post', maxlen=20)
#
# # test data
#
# test_labels = [1,2,2,1]
# test_string = [["initialize","y","to","6"],["print","hello","world"],["express","the","value","of","x"],["change","x","to","17"]]
# test_data = [[9999,9999,9999,9999],[45,9999,9999],[607,422,9999,9999],[6,9999,9999,9999]]
#
# test_data = keras.preprocessing.sequence.pad_sequences(test_data,value=9998,padding='post', maxlen=20)
#
# # Build the model
#
# vocab_size = 10000
#
# model = keras.Sequential()
# model.add(keras.layers.Embedding(vocab_size, 16))
# model.add(keras.layers.GlobalAveragePooling1D())
# model.add(keras.layers.Dense(16, activation=tf.nn.relu))
# model.add(keras.layers.Dense(1, activation=tf.nn.sigmoid))
#
# #  ???
#
# model.compile(optimizer=tf.train.AdamOptimizer(),
#               loss='binary_crossentropy',
#               metrics=['accuracy'])
#
# #  Train the model
#
# history = model.fit(train_data,
#                     train_labels,
#                     epochs=40,
#                     batch_size=512,
#                     validation_data=(validation_data, validation_labels),
#                     verbose=1)
#
# results = model.evaluate(test_data, test_labels)
#
# print(results)
#
#
