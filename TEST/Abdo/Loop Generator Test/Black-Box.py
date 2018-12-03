import sys
import os
import csv
os.system("loop_generator.py in1_1.txt in1_2.txt in1_3.txt in1_4.txt")

print("loop_generator.py in1_1.txt in1_2.txt in1_3.txt in1_4.txt")
print("\nSCRIPT OUTPUT:")
with open('script_out.csv', newline='') as csvfile:
    thingreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in thingreader:
        print(', '.join(row))
print("\nIDEAL OUTPUT:")
with open('ideal_out1.csv', newline='') as csvfile:
    thingreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in thingreader:
        print(', '.join(row))



