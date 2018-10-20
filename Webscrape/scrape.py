from bs4 import BeautifulSoup as BS
import requests
import json
from json import JSONDecoder
url = 'https://www.thesaurus.com/browse/%s'
url_offline = 'Webscrape\offline_content.html'
response = requests.get(url % 'create')
decoder = JSONDecoder()
# response_offine = BS(url_offline, "html.parser")
url_content = BS(response.content, "html.parser")
scripts = url_content.find_all('script')
synonyms = scripts[11]
wordlists = []
j = 0
for i in synonyms:
    print(type(i))
    wordlists.append(i)
    j+=1
uni_str = str(wordlists[0].string)
print(type(uni_str))


# print(wordlists[0].string)
json_str = uni_str[23:70340]
a = decoder.decode(json_str)
for i in a:
    print(i)
print(a["posTabs"])
# print(json.dumps(json_str, sort_keys=True, indent=4))
#window.INITIAL_STATE
