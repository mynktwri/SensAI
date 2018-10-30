from bs4 import BeautifulSoup as BS
import requests
import json
from json import JSONDecoder
def parse_syn(json):
    # print (json["results"].items())
    if isinstance(json, str):
        print(json)
    else:
        for i in json:
            print(i)
            if (i =="synonyms"):
                print("synonym found")
                
            elif (len(i) < 2):
                continue
            else:
                if isinstance(i, str):
                    parse_syn(json[i])
                else:
                    parse_syn(i)

app_id = '7248bd1c'
app_key = 'c47f4d57c7c38204f8fd3846e6b725f9'

language = 'en'
word_id = 'create'

url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/' + language + \
 '/' + word_id.lower() + '/synonyms;antonyms'

# r = requests.get(url, headers = {'app_id': app_id, 'app_key': app_key}).json()

# print("code {}\n".format(r.status_code))
#print("text \n" + r.text)

with open('data.json') as file:
    r = json.load(file)
results = r["results"]
# print("json \n" + json.dumps(r))
parse_syn(results)
# print(results[0]["lexicalEntries"])

# with open('data.json', 'w') as outfile:
#     json.dump(r.json(), outfile)
#     print("data saved successfully.")
