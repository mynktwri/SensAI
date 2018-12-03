#!/usr/bin/python
# coding: latin-1
import os, sys

def getSentences(v):

	out_script = open("loop_data.csv","a"); values = open("array.txt", "r"); variables = open("variable.txt", "r")

	#////////////////////////////////////COMMAND///////////////////////////////////////
	command_for = ["for"];
	command = ["go", "loop", "pass", "walk", "flip", "move", "iterate", "scan", "check", "browse", "skim", "look"];
	command_loop = ["loop"];
	command_count = ["check", "investigate", "consider"];

	#////////////////////////////////////PREPOSITIONS///////////////////////////////////////

	position = ["through", "over", "along"];
	position_loop = ["the"];
	position_in = ["in"];

	preposition= ["with", "using", "utilizing", "for", "as"];
	preposition_of = ["of"];

	objects= ["scope", "spectrum", "area"];

	count= ["all", "every", "each"];



	#////////////////////////////////////TEMPLATES///////////////////////////////////////

	#command position array
	if (v == "1"):
		firstFile = command; secondFile = position; thirdFile = values; fourthFile = [""]; fifthFile = [""]; sixthFile = [""];
		posVariable = -1; posValue = 2;

	#command the array
	if (v == "2"):
		firstFile = command_loop; secondFile = position_loop; thirdFile = values; fourthFile = [""]; fifthFile = [""]; sixthFile = [""];
		posVariable = -1; posValue = 2;

	#command position array preposition variable
	if (v == "3"):
		firstFile = command; secondFile = position; thirdFile = values; fourthFile = preposition; fifthFile = variables; sixthFile = [""];
		posVariable = 4; posValue = 2;

	#for variable in verb object array: for i in range of array
	if (v == "4"):
		firstFile = command_for; secondFile = variables; thirdFile = position_in; fourthFile = objects; fifthFile = preposition_of; sixthFile = values;
		posVariable = 1; posValue = 5;

	#for variable in array
	if (v == "5"):
		firstFile = command_for; secondFile = variables; thirdFile = position_in; fourthFile = values; fifthFile = [""]; sixthFile = [""];
		posVariable = 1; posValue = 3;

	#for count variable in array
	if (v == "6"):
		firstFile = command_for; secondFile = count; thirdFile = variables; fourthFile = position_in; fifthFile = values; sixthFile = [""];
		posVariable = 2; posValue = 4;

	#command position count element in array
	if (v == "7"):
		firstFile = command; secondFile = position; thirdFile = count; fourthFile = variables; fifthFile = position_in; sixthFile = values;
		posVariable = 3; posValue = 5;


	#command count element in array
	if (v == "8"):
		firstFile = command_count; secondFile = count; thirdFile = variables; fourthFile = position_in; fifthFile = values; sixthFile = [""];
		posVariable = 2; posValue = 4;

	#/////////////////////////////////////SENTENCE GENERATION//////////////////////////////////////

	arrOut = []; arrFirst = []; arrSecond = []; arrThird = []; arrFourth = []; arrFifth = []; arrSixth = [];

	for first in firstFile:
		arrFirst.append(first.strip())
	for second in secondFile:
		arrSecond.append(second.strip())
	for third in thirdFile:
		arrThird.append(third.strip())
	for fourth in fourthFile:
		arrFourth.append(fourth.strip())
	for fifth in fifthFile:
		arrFifth.append(fifth.strip())
	for sixth in sixthFile:
		arrSixth.append(sixth.strip())



	for first in arrFirst:
		for second in arrSecond:
			for third in arrThird:
				for fourth in arrFourth:
					for fifth in arrFifth:
						for sixth in arrSixth:
							line = first + " " +second + " " + third + " " + fourth + " " + fifth + " " + sixth
							line = line.strip()
							arrLine = line.split();
							if(posVariable < 0):
								lineScript = line + ",loop," + arrLine[posValue] + ","
							else:
								lineScript = line + ",loop," + arrLine[posValue] + "," + arrLine[posVariable]
							out_script.write(lineScript); out_script.write("\n"); 
	
	out_script.close()



for i in range (1,9):
	v = str(i)
	getSentences(v)




