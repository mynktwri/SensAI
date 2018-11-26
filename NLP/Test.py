import Process
import csv

test = "This is a test."

# Getting the total length of a sentence: (Note that punctuations also count as a word)
# print(Process.getLength(test))
total = Process.getLength(test)
# Getting the tags list:
print(Process.getTag(test))

# Getting each words
# print(Process.getWord(test))
wordlist = []
POSlist = []
order = []
for x in range(0, total):
    wordlist.append(Process.getWord(test)[x])
    order.append(x+1)
POSlist = Process.getTag(test)
with open("output.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(order)
    writer.writerow(wordlist)
    writer.writerow(POSlist)
