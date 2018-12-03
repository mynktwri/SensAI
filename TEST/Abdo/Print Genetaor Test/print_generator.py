import string
import sys
import getopt
translator=str.maketrans('','',string.punctuation)
#printvarfile = input("Enter print variables file name: ")
#wordsfile = input("Enter words file name: ")
printvarfile = sys.argv[1]
wordsfile = sys.argv[2]
#print(printvarfile)
#print(wordsfile)

printvar = open(printvarfile).read().splitlines()
words = open(wordsfile).read().splitlines()
output = open("script_out.csv", "w")

SIZEOUT = len(printvar)
SIZEIN = len(words)
output.write("sen,cat,0\n")

for i in range (0, SIZEOUT):
    for j in range (0, SIZEIN):
        line = printvar[i].translate(translator) + " " + words[j].translate(translator) + "," + "print" + "," + words[j].translate(translator) + "\n"
        output.write(line)

output.close()        
