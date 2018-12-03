import string
translator=str.maketrans('','',string.punctuation)
printvar = open("print_var.txt").read().splitlines()
words = open("common_words.txt").read().splitlines()
output = open("script_out.csv", "w")

SIZEOUT = len(printvar)
SIZEIN = len(words)
output.write("sentence, cat, 0\n")

for i in range (0, SIZEOUT):
    for j in range (0, SIZEIN):
        line = printvar[i].translate(translator) + " " + words[j].translate(translator) + "," + "print" + "," + words[j].translate(translator) + "\n"
        output.write(line)

output.close()        
