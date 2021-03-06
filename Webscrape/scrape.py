import pandas as pd
import requests
import json
import time
from json import JSONDecoder
global synonyms

app_id = '7248bd1c'
app_key = 'c47f4d57c7c38204f8fd3846e6b725f9'

language = 'en'
word_id = 'create'
words = []


def get_syns(word):
    url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/' + language + \
          '/' + word.lower() + '/synonyms'
    r = requests.get(url, headers={'app_id': app_id, 'app_key': app_key})
    if(r.status_code ==200):
        print("200")
        senses = r.json()["results"][0]["lexicalEntries"][0]["entries"][0]["senses"]
        for i in senses:
            for j in i:
                if (j == "synonyms"):
                    for l in i[j]:
                        terms_df.loc[terms_df.index.max() + 1] = [l["text"], 0, 0, 0, 0]
                elif (j == "subsenses"):
                    for k in i[j]:
                        for l in k["synonyms"]:
                            terms_df.loc[terms_df.index.max() + 1] = [l["text"], 0, 0, 0, 0]


terms_df = pd.read_csv("terms.csv")
for i in terms_df["word"]:
    words.append(i)
print(len(words))
for i in words:
    get_syns(i)
    time.sleep(.1)
print(terms_df)
terms_df.to_csv("terms_synonyms.csv")
          # [0]["senses"]["synonyms"])
# results = r["results"]
# print print(j)
# print(results[0]["lexicalEntries"])
# with o("json \n" + json.dumps(r))
# # senseslist = parse_syn(results)
# # for i in senseslist:
# #     for j in i:
# #        pen('data.json', 'w') as outfile:
#     json.dump(r.json(), outfile)
#     print("data saved successfully.")