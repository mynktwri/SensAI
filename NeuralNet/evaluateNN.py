import os, sys
# sys.path.append(os.path.join(os.getcwd()))
import keras
import DB_index_pull as db_pull
from tensorflow.keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_validate
import pandas as pd
import random
from keras.models import load_model
import data_collection as collect
import final_output as fo
random.seed(7)

model = load_model('my_model.h5')

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
    for i in range(0,4):
        value = prediction[0][i]
        print(value)
        if (value >= best):
            best=value
            best_i=i
    # print(best_i)
    if best_i == 0:
        obj1, obj2 = fo.varObject(sentence)
        print(fo.varCode(obj1, obj2))
    elif best_i == 1:
        obj1 = fo.printObject(sentence)
        print(fo.printCode(obj1))
    elif best_i == 2:
        obj1 = fo.LoopObject(sentence)
        print(fo.loopCode(obj1))
    elif best_i == 3:
        obj1, opera, obj2 = fo.ifObject(sentence)
        print(fo.ifCode(obj1, opera, obj2))
    else:
        return -1
