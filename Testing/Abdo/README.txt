Black Box Tests for each of these two sentence generators, ideally run in command line.

Output for Print generator test:
RUNNING print_generator.py in1_1.txt in1_2.txt

SCRIPT OUTPUT:
sen,cat,0
print, word1,print,word1
print, word2,print,word2
print, word3,print,word3
output, word1,print,word1
output, word2,print,word2
output, word3,print,word3

IDEAL OUTPUT:
sen,cat,0
print, word1,print,word1
print, word2,print,word2
print, word3,print,word3
output, word1,print,word1
output, word2,print,word2
output, word3,print,word3

=========================================
Output for Loop generator test:
loop_generator.py in1_1.txt in1_2.txt in1_3.txt in1_4.txt

SCRIPT OUTPUT:
sen, cat, 0
iterate , loop, 
iterate a[] , loop, a[] 
iterate a , loop, a 
iterate x in , loop, 
iterate x in a[] , loop, a[] 
iterate x in a , loop, a 
iterate for , loop, 
iterate for a[] , loop, a[] 
iterate for a , loop, a 
iterate for x in , loop, 
iterate for x in a[] , loop, a[] 
iterate for x in a , loop, a 
iterate through , loop, 
iterate through a[] , loop, a[] 
iterate through a , loop, a 
iterate through x in , loop, 
iterate through x in a[] , loop, a[] 
iterate through x in a , loop, a 
loop , loop, 
loop a[] , loop, a[] 
loop a , loop, a 
loop x in , loop, 
loop x in a[] , loop, a[] 
loop x in a , loop, a 
loop for , loop, 
loop for a[] , loop, a[] 
loop for a , loop, a 
loop for x in , loop, 
loop for x in a[] , loop, a[] 
loop for x in a , loop, a 
loop through , loop, 
loop through a[] , loop, a[] 
loop through a , loop, a 
loop through x in , loop, 
loop through x in a[] , loop, a[] 
loop through x in a , loop, a 

IDEAL OUTPUT:
sen, cat, 0
iterate , loop, 
iterate a[] , loop, a[] 
iterate a , loop, a 
iterate x in , loop, 
iterate x in a[] , loop, a[] 
iterate x in a , loop, a 
iterate for , loop, 
iterate for a[] , loop, a[] 
iterate for a , loop, a 
iterate for x in , loop, 
iterate for x in a[] , loop, a[] 
iterate for x in a , loop, a 
iterate through , loop, 
iterate through a[] , loop, a[] 
iterate through a , loop, a 
iterate through x in , loop, 
iterate through x in a[] , loop, a[] 
iterate through x in a , loop, a 
loop , loop, 
loop a[] , loop, a[] 
loop a , loop, a 
loop x in , loop, 
loop x in a[] , loop, a[] 
loop x in a , loop, a 
loop for , loop, 
loop for a[] , loop, a[] 
loop for a , loop, a 
loop for x in , loop, 
loop for x in a[] , loop, a[] 
loop for x in a , loop, a 
loop through , loop, 
loop through a[] , loop, a[] 
loop through a , loop, a 
loop through x in , loop, 
loop through x in a[] , loop, a[] 
loop through x in a , loop, a