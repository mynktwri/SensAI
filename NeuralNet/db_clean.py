
def db_clean(data_df, save=False):
    # data_df = data_df.drop(data_df.columns[:1], axis=1)
    data_df["word"] = data_df["word"].str.lower()
    data_df = data_df.drop_duplicates(["word"])
    data_df = data_df.sort_values(by="word", axis=0)
    data_df.reset_index(drop=True, inplace=True)
    if save:
        data_df.to_csv("clean_terms.csv")
