printvar = open("print_var.txt").read().splitlines()
words = open("common_words.txt").read().splitlines()
output = open("script_out.txt", "w")

SIZEOUT = len(printvar)
SIZEIN = len(words)

for i in range (0, SIZEOUT):
    for j in range (0, SIZEIN):
        line = printvar[i] + " " + words[j] + "," + "print" + "," + words[j] + "\n"
        output.write(line)

output.close()        
