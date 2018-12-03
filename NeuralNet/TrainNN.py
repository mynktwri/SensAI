import os, sys
# sys.path.append(os.path.join(os.getcwd()))
import tensorflow.keras as keras
import DB_index_pull as db_pull
from tensorflow.keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_validate
from pandas import read_csv
import random
import data_collection as collect
import final_output as fo
random.seed(7)

collect.gather()

encoded_labels = read_csv("encoded_labels.csv")
input_data = read_csv("train_data.csv")

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
    model.add(keras.layers.Dense(64, activation='relu'))
    model.add(keras.layers.Dense(64, activation='relu'))
    model.add(keras.layers.Dense(64, activation='relu'))
    model.add(keras.layers.Dense(64, activation='relu'))
    model.add(keras.layers.Dense(64, activation='relu'))
    model.add(keras.layers.Dense(64, activation='relu'))
    model.add(keras.layers.Dense(64, activation='relu'))
    model.add(keras.layers.Dense(64, activation='relu'))
    # Output Layer: needs as many nodes as there are categories.
    model.add(keras.layers.Dense(4, activation='softmax'))

    print(model.summary())
    model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy']) # consider RMSE or MSE as metric for error
    return model
#  Train the model

estimator =KerasClassifier(build_fn=create_model, epochs=3, batch_size=2048, verbose=1)
kfold = KFold(n_splits=10, shuffle=True, random_state=7)
estimators = cross_validate(estimator, input_data, encoded_labels, cv=kfold, return_estimator=True,
                            return_train_score=True)
# print("Baseline: %.2f%% (%.2f%%)" % (results.mean()*100, results.std()*100))

# history = model.fit(x=train_data,
#                      y=train_labels,
#                      epochs=10,
#                      batch_size=512,
#                      validation_split=0.1,
#                      # validation_data=(validation_data, validation_labels),
#                      verbose=1)
# print(history)
# results = model.evaluate(test_data, test_labels)
max_score = 0
k = 0
for i in estimators["train_score"]:
    if i > max_score:
        model = estimators["estimator"][k].model
        max_score = i
    k+=1
# print(model.summary())

model.save('my_model.h5')  # creates a HDF5 file 'my_model.h5'
del model  # deletes the existing model
exit(0)
