#!/usr/bin/python
# coding: latin-1
import os, sys


out = open("out.txt","a"); out_script = open("out_script.txt","a"); variables = open("variables.txt", "r"); values = open("values.txt", "r")

#////////////////////////////////////PREPOSITIONS///////////////////////////////////////

#Prepositions further categoriation depending on sentence composition
prep_to = ["to"]; prep_in = ["in"]; prep_as = ["as"]; prep_into = ["into"]; prep_may = ["may"]; prep_a =["a"];


#7
prep_symbols7 = ["=", "->", "equal", "equalto", "be", "is", "contains"]

#8
prep_symbols8 = ["=", "<-", "equal", "equals", "equalto", "be", "is", "contains"]

#////////////////////////////////////VERBS///////////////////////////////////////

#1Verb_Variable_Preposition_Value (set x to 5)
verbs_to_1 = ["point","turn","set"];
verbs_as_1 = ["safe"];
verbs_a_1 = ["make"];

#2Verb_Value_Preposition_Variable (insert 5 into x)
verbs_to_2= ["designate","change","appoint","schedule","direct","orientate","realize","write","allocate"];
verbs_into_2 = ["change","deposit","put"];
verbs_in_2 = ["place","store","insert","deposit","put","safe"];

#3Value_Verb_Preposition_Variable (5 stored in x)
verbs_to_3 = ["designated","appointed","directed","written","allocated"];
verbs_into_3 = ["deposited","put", "inserted"];
verbs_in_3 = ["placed","stored","inserted","deposited","put","safed","realized"];

#4Preposition_Variable_Verb_Value (may x be 5)
verbs_may_4 = ["be", "have", "take"];

#5Variable_Verb_Preposition_Value (x changed to 5)
verbs_to_5 = ["designated","changed","appointed","scheduled","directed","orientated","realized","directed"];

#6Verb_Variable_Value (assign x 5)
verbs_6 = ["assign","make","give","designate","appoint"];

#7Value_Preposition_Variable (5 -> x)
#8Variable_Preposition_Value (x equal 5)
#9 Variable_Value (x 5)

#////////////////////////////////////TEMPLATES///////////////////////////////////////
#1
if (sys.argv[1] == "Verb_Variable_Preposition_Value"):
	secondFile = variables; fourthFile = values;
	posVariable = 1; posValue = 3;
	if (sys.argv[2] == "to"): firstFile = verbs_to_1; thirdFile = prep_to;
	if (sys.argv[2] == "as"): firstFile = verbs_as_1; thirdFile = prep_as;
	if (sys.argv[2] == "a"): firstFile = verbs_a_1; thirdFile = prep_a;
#2
if (sys.argv[1] == "Verb_Value_Preposition_Variable"):
	secondFile = values; fourthFile = variables;
	posVariable = 3; posValue = 1;
	if (sys.argv[2] == "to"): firstFile = verbs_to_2; thirdFile = prep_to;
	if (sys.argv[2] == "into"): firstFile = verbs_into_2; thirdFile = prep_into;
	if (sys.argv[2] == "in"): firstFile = verbs_in_2; thirdFile = prep_in;
#3
if (sys.argv[1] == "Value_Verb_Preposition_Variable"):
	firstFile = values; fourthFile = variables;
	posVariable = 3; posValue = 0;
	if (sys.argv[2] == "to"): secondFile = verbs_to_3; thirdFile = prep_to;
	if (sys.argv[2] == "into"): secondFile = verbs_into_3; thirdFile = prep_into;
	if (sys.argv[2] == "in"): secondFile = verbs_in_3; thirdFile = prep_in;
#4
if (sys.argv[1] == "Preposition_Variable_Verb_Value"):
	secondFile = variables; fourthFile = values;
	posVariable = 1; posValue = 3;
	if (sys.argv[2] == "may"): thirdFile = verbs_may_4; firstFile = prep_may;
#5
if (sys.argv[1] == "Variable_Verb_Preposition_Value"):
	firstFile = variables; fourthFile = values;
	posVariable = 0; posValue = 3;
	if (sys.argv[2] == "to"): secondFile = verbs_to_5; thirdFile = prep_to;
#6
if (sys.argv[1] == "Verb_Variable_Value"):
	firstFile = verbs_6; secondFile = variables; thirdFile = values; fourthFile = [" "];
	posVariable = 1; posValue = 2;
#7
if (sys.argv[1] == "Value_Preposition_Variable"):
	firstFile = values; secondFile = prep_symbols7; thirdFile = variables; fourthFile = [" "]; 
	posVariable = 2; posValue = 0;
#8
if (sys.argv[1] == "Variable_Preposition_Value"):
	firstFile = variables; secondFile = prep_symbols8; thirdFile = values; fourthFile = [" "]; 
	posVariable = 0; posValue = 2;
#9
if (sys.argv[1] == "Variable_Value"):
	firstFile = variables; secondFile = values; thirdFile = [" "]; fourthFile = [" "]; 
	posVariable = 0; posValue = 1;
#/////////////////////////////////////SENTENCE GENERATION//////////////////////////////////////

arrOut = []; arrFirst = []; arrSecond = []; arrThird = []; arrFourth = [];
for first in firstFile:
	arrFirst.append(first.strip())
for second in secondFile:
	arrSecond.append(second.strip())
for third in thirdFile:
	arrThird.append(third.strip())
for fourth in fourthFile:
	arrFourth.append(fourth.strip())


for first in arrFirst:
	for second in arrSecond:
		for third in arrThird:
			for fourth in arrFourth:
				line = first + " " +second + " " + third + " " + fourth
				arrLine = line.split();
				tempTuple = (line, [arrLine[posVariable], arrLine[posValue]])
				arrOut.append(tempTuple) #Array of tuples containing the script information
				lineScript = line + ", variable, " + arrLine[posVariable] + ", " + arrLine[posValue]
				out.write(line); out.write("\n")
		   		out_script.write(lineScript); out_script.write("\n")


out.close()
out_script.close()




