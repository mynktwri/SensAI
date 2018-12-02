import os, sys
# sys.path.append(os.path.join(os.getcwd()))
import tensorflow as tf
import keras
import DB_index_pull as db_pull
from tensorflow.keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
import pandas as pd
import random
import data_collection as collect
random.seed(7)

collect.gather()

encoded_labels = pd.read_csv("encoded_labels.csv")
input_data = pd.read_csv("train_data.csv")

# Build the model
# vocab_size is the size of our database at model initialization.
# this ensures that all new words have already been added to the database.
vocab_size = db_pull.get_db_len()

def create_model():
    model = keras.Sequential()
    # Input Layer
    model.add(keras.layers.Embedding(db_pull.get_db_len(), 64, input_length=20))
    #   Outputs shape=
    model.add(keras.layers.GlobalAveragePooling1D())
    #   Outputs 1D shape=
    # Hidden Layer
    model.add(keras.layers.Dense(64, activation=tf.nn.relu))
    # Output Layer: needs as many nodes as there are categories.
    model.add(keras.layers.Dense(3, activation='softmax'))

    print(model.summary())
    model.compile(optimizer=tf.train.AdamOptimizer(),
              loss='categorical_crossentropy',
              metrics=['accuracy']) # consider RMSE or MSE as metric for error
    return model
#  Train the model

estimator =KerasClassifier(build_fn=create_model, epochs=10, batch_size=1024, verbose=1)
kfold = KFold(n_splits=10, shuffle=True, random_state=7)
results = cross_val_score(estimator, input_data, encoded_labels, cv=kfold)
print("Baseline: %.2f%% (%.2f%%)" % (results.mean()*100, results.std()*100))
print(results)

# history = model.fit(x=train_data,
#                     y=train_labels,
#                     epochs=40,
#                     batch_size=512,
#                     validation_split=0.1,
#                     # validation_data=(validation_data, validation_labels),
#                     verbose=1)
# print(history)
# results = model.evaluate(test_data, test_labels)
#
# print(results)
def makePrediction(sentence):
    (indices, wordlist, poslist) = db_pull.in_pipe([sentence])
    id_list = pd.DataFrame.from_dict(keras.preprocessing.sequence.pad_sequences(indices, 10, padding='post'))
    pos_list = pd.DataFrame.from_dict(keras.preprocessing.sequence.pad_sequences(poslist, 10, padding='post'))
    input_data = pd.concat([id_list, pos_list], axis=1, ignore_index=True)
    prediction = model.predict(pd.DataFrame(data=input_data))
    print("-------")
    best=0
    best_i=0
    i=0
    print(prediction)
    for i in range(0,3):
        value = prediction[0][i]
        print(value)
        if (value >= best):
            best=value
            best_i=i
    print(best_i)
    if(best_i==0):
        return "variable"
    if(best_i==1):
        return "loop"
    if(best_i==2):
        return "print"
    return best_i