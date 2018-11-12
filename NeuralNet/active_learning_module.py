from NeuralNet import db_clean

#takes a new word and adds it to the database
def new_word(word, data_df):
    data_df.append([word, 0, 0, 0, 0])
    db_clean.db_clean(data_df)
