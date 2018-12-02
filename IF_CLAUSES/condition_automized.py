#!/usr/bin/python
# coding: latin-1
import os, sys


def getSentences(kind, variation):
	out = open("out.txt","a"); out_script = open("out_script.txt","a"); values = open("values.txt", "r"); variables = open("variables.txt", "r")

	#////////////////////////////////////COMMAND///////////////////////////////////////
	commandFile = ["if"];


	#////////////////////////////////////PREPOSITIONS///////////////////////////////////////

	#Prepositions further categoriation depending on sentence composition
	prep_to = ["to"]; prep_in = ["in"]; prep_as = ["as"]; prep_into = ["into"]; prep_may = ["may"]; prep_a =["a"]; prep_with =["with"];
	verb_is = ["is"]; verb_are = ["are"]; and_ =["and"];

	verb_are_not = ["are not"];
	verb_is_not = ["is not"];

	than = ["than"];

	#////////////////////////////////////COMPARE////////////////////////////////////////////
	#not ()
	negation_not = ["!", "not"];
	negation_doesnt = ["!"];

	equal_negation= ["equal", "match"];


	#v not compare v
	equal_prep_1_not = ["not same as", "not duplicate of", "not equal to", "not equivalent to", "not identical to"];
	is_equal_prep_1_not = ["is not same as", "is not duplicate of", "is not equal to", "is not equivalent to", "is not identical to"];



	#v compare v

	#IN ONE STATEMENT
	equal_prep_1 = ["corresponds to", "agrees with", "same as", "duplicate of", "equal to", "equivalent to", "identical to"];
	is_equal_prep_1 = ["is same as", "is duplicate of", "is equal to", "is equivalent to", "is identical to"];


	#FAGMENTED
	#unequal = ["unequal"];
	equal = ["equal", "matched", "matches", "equals", "matching", "balances", "=="];
	less = ["lower", "younger", "lighter", "less", "tinier", "smaller", "lower"]; #isn't, not, !
	greater = ["taller", "higher", "greater", "older","heavier","bigger"]; #isn't, not, !
	lessEqual = ["smaller equal", "less equal", "lower equal", "younger equal", "lighter equal"]; #isnt, not, !
	greaterEqual = ["greater equal", "higher equal", "older equal","heavier equal","bigger equal"]; #isnt, not, !


	#is_unequal_to = ["unequal"];
	is_less_than = ["lower", "younger", "lighter", "less","tinier","smaller","lower"]; #not, !
	is_greater_than = ["taller", "higher", "greater", "older","heavier","bigger"]; #not, !


	# v and v are (the) compare 
	equal_are = ["equivalent", "invariable", "balanced", "corresponding","agreeing","uniform","alike"]; #not
	unequal_are = ["differing", "dissimilar", "unalike", "vary", "diverge", "disagree", "clash"]; #not


	#////////////////////////////////////TEMPLATES///////////////////////////////////////
	#1 variable_compare_variable (x equals 5)
	if (kind == "variable_compare_variable"):
		firstFile = values; fourthFile = [""]; fifthFile = [""]; sixthFile = [""];
		posVariable = 1; posValue = 3; compare_symbol = "==";
		#if (variation == "1"): secondFile = unequal; thirdFile = variables; compare_symbol = "!=";
		if (variation == "2"): secondFile = equal; thirdFile = variables;
		if (variation == "3"): secondFile = equal_prep_1; thirdFile = variables; posValue = 4;
		if (variation == "4"): secondFile = is_equal_prep_1; thirdFile = variables; posValue = 5;

		if (variation == "5"): secondFile = less; thirdFile = variables; compare_symbol = "<";
		if (variation == "6"): secondFile = greater; thirdFile = variables; compare_symbol = ">";
		if (variation == "7"): secondFile = lessEqual; thirdFile = variables; posValue = 4; compare_symbol = "<=";
		if (variation == "8"): secondFile = greaterEqual; thirdFile = variables; posValue = 4; compare_symbol = ">=";

		if (variation == "9"): secondFile = verb_is; thirdFile = less; fourthFile = than; fifthFile = variables; posValue = 5; compare_symbol = "<";
		if (variation == "10"): secondFile = verb_is; thirdFile = greater; fourthFile = than; fifthFile = variables; posValue = 5; compare_symbol = ">";
		if (variation == "11"): secondFile = less; thirdFile = than; fourthFile = variables; posValue = 4; compare_symbol = "<";
		if (variation == "12"): secondFile = greater; thirdFile = than; fourthFile = variables; posValue = 4; compare_symbol = ">";


		if (variation == "13"): secondFile = and_; thirdFile = variables; fourthFile = verb_are; fifthFile = equal_are; posValue = 3; compare_symbol = "==";
		if (variation == "14"): secondFile = and_; thirdFile = variables; fourthFile = verb_are; fifthFile = unequal_are; posValue = 3; compare_symbol = "!=";

		#Negation
		if (variation == "15"): secondFile = equal_prep_1_not; thirdFile = variables; posValue = 5; compare_symbol = "!=";
		if (variation == "16"): secondFile = is_equal_prep_1_not; thirdFile = variables; posValue = 6; compare_symbol = "!=";

		if (variation == "17"): secondFile = negation_not; thirdFile = less; fourthFile = variables; posValue = 4; compare_symbol = ">=";
		if (variation == "18"): secondFile = negation_not; thirdFile = greater; fourthFile = variables; posValue = 4; compare_symbol = "<=";
		if (variation == "19"): secondFile = negation_not; thirdFile = lessEqual; fourthFile = variables; posValue = 5; compare_symbol = ">";
		if (variation == "20"): secondFile = negation_not; thirdFile = greaterEqual; fourthFile = variables; posValue = 5; compare_symbol = "<";

		if (variation == "21"): secondFile = verb_is_not; thirdFile = less; fourthFile = than; fifthFile = variables; posValue = 6; compare_symbol = ">=";
		if (variation == "22"): secondFile = verb_is_not; thirdFile = greater; fourthFile = than; fifthFile = variables; posValue = 6; compare_symbol = "<=";
		if (variation == "23"): secondFile = negation_not; thirdFile = less; fourthFile = than; fourthFile = variables; posValue = 4; compare_symbol = ">=";
		if (variation == "24"): secondFile = negation_not; thirdFile = greater; fourthFile = than; fourthFile = variables; posValue = 4; compare_symbol = "<=";

		if (variation == "25"): secondFile = and_; thirdFile = variables; fourthFile = verb_are_not; fifthFile = equal_are; posValue = 3; compare_symbol = "!=";
		if (variation == "26"): secondFile = and_; thirdFile = variables; fourthFile = verb_are_not; fifthFile = unequal_are; posValue = 3; compare_symbol = "==";


		#if (variation == "27"): secondFile = negation_not; thirdFile = unequal; fourthFile = variables; posValue = 4; compare_symbol = "==";
		if (variation == "27"): secondFile = negation_doesnt; thirdFile = equal_negation; fourthFile = variables; posValue = 4;  compare_symbol = "!=";



	#/////////////////////////////////////SENTENCE GENERATION//////////////////////////////////////

	arrOut = []; arrCommand = []; arrFirst = []; arrSecond = []; arrThird = []; arrFourth = []; arrFifth = []; arrSixth = [];

	for command in commandFile:
		arrCommand.append(command.strip())
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


	for command in commandFile:
		for first in arrFirst:
			for second in arrSecond:
				for third in arrThird:
					for fourth in arrFourth:
						for fifth in arrFifth:
							for sixth in arrSixth:
								line = command + " " + first + " " +second + " " + third + " " + fourth + " " + fifth + " " + sixth
								#line_p = command + " ( " + first + " " +second + " " + third + " " + fourth + " " + fifth + " " + sixth 
								line = line.strip()
								#line_p = line_p.strip() + " )"
								arrLine = line.split();
								#arrLine_p = line_p.split();
								lineScript = line + ", if, " + arrLine[posVariable] + ", "  + compare_symbol + ", " + arrLine[posValue]
								#lineScript_p = line_p + ", if, " + arrLine[posVariable ] + ", "  + compare_symbol + ", " + arrLine[posValue ]
								#out.write(line); out.write("\n"); out.write(line_p); out.write("\n")
								out_script.write(lineScript); out_script.write("\n"); 
								#out_script.write(lineScript_p); out_script.write("\n")

	#out_script.write(variation); out_script.write("\n\n\n");					
	out.close()
	out_script.close()





for i in range (2,28):
	v = str(i)
	getSentences("variable_compare_variable", v)
