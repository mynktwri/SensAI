from bs4 import BeautifulSoup as BS
import requests
import json
from json import JSONDecoder
global synonyms

app_id = '7248bd1c'
app_key = 'c47f4d57c7c38204f8fd3846e6b725f9'

language = 'en'
word_id = 'create'

url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/' + language + \
 '/' + word_id.lower() + '/synonyms;antonyms'

r = requests.get(url, headers = {'app_id': app_id, 'app_key': app_key})

print("code {}\n".format(r.status_code))
#print("text \n" + r.text)

# with open('data.json') as file:
#     r = json.load(file)
senses = r.json()["results"][0]["lexicalEntries"][0]["entries"][0]["senses"]

for i in senses:
    for j in i:
        if (j == "synonyms"):
            print(i[j])
        elif(j == "subsenses"):
            for k in i[j]:
                print(k["synonyms"])
          # [0]["senses"]["synonyms"])
# results = r["results"]
# print("json \n" + json.dumps(r))
# senseslist = parse_syn(results)
# for i in senseslist:
#     for j in i:
#         print(j)

# print(results[0]["lexicalEntries"])

# with open('data.json', 'w') as outfile:
#     json.dump(r.json(), outfile)
#     print("data saved successfully.")