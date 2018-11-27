from NLP import Process
import csv

test = "This isn't a test."

# Getting the total length of a sentence: (Note that punctuations also count as a word)
# print(Process.getLength(test))
total = Process.getLength(test)
# Getting the tags list:
print(Process.getTag(test))

# Getting each words
# print(Process.getWord(test))
wordlist = []
POSlist = []

POSlist = Process.getTag(test)
wordlist = Process.getWord(test)

with open("output.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(wordlist)
    writer.writerow(POSlist)
