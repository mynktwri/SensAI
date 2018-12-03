import string
translator=str.maketrans('','',string.punctuation)
loopvar = open("loop_var.txt").read().splitlines()
filler = open("filler_words.txt").read().splitlines()
var1 = open("var1.txt").read().splitlines()
array_vars = open("array_vars.txt").read().splitlines()
output = open("script_out.csv", "w")

SIZE1 = len(loopvar)
SIZE2 = len(filler)
SIZE3 = len(var1)
SIZE4 = len(array_vars)

output.write("sen,cat,0\n")

for i in range (0, SIZE1):
    for j in range (0, SIZE2):
        for k in range (0, SIZE3):
            for l in range (0, SIZE4):
                line = loopvar[i]+ filler[j].translate(translator) + var1[k] + array_vars[l]+ "," + "loop" +"," +array_vars[l]+"\n" 
                output.write(line)

output.close()        
