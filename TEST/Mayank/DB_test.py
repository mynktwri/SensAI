import os, sys
sys.path.append(os.path.join(os.getcwd(), "..", "..", "..", "SensAI"))
from NeuralNet import DB_index_pull as db_func
import pandas as pd
clean_db = "../../NeuralNet/clean_terms_saved.csv"


df = pd.read_csv(clean_db)

new_df, indices, wordlist, poslist = db_func.parse_input(["this is a sentence"], df, False)
print(len(new_df))
print(db_func.get_db_len(filename=clean_db))
print(wordlist)
print(poslist)

print("print looked up in database is 2578: ", 2578 == db_func.db_get("print", df))
