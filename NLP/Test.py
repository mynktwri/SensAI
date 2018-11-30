from NLP import Process
import csv

test = "This is a test."

# Getting the total length of a sentence: (Note that punctuations also count as a word)
# print(Process.getLength(test))
total = Process.getLength(test)
# Getting the tags list:

# Getting each words
# print(Process.getWord(test))
wordlist = []
POSlist = []

POSlist = Process.getTag(test)
wordlist = Process.getWord(test)

for i in range(len(wordlist)):
    if POSlist[i] == "punctuation":
        # remove it
        print("removing " + wordlist[i])
        wordlist.remove(wordlist[i])
        POSlist.remove(POSlist[i])
