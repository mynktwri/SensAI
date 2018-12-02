#!/usr/bin/python
# coding: latin-1
import os, sys


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
negation_not = ["!", "isn't", "not"];
negation_doesnt = ["doesn't", "!"];

equal_negation= ["equal", "match"];


#v not compare v
equal_prep_1_not = ["not same as", "not duplicate of", "not equal to", "not equivalent to", "not identical to"];
is_equal_prep_1_not = ["is not same as", "is not duplicate of", "is not equal to", "is not equivalent to", "is not identical to"];



#v compare v

#IN ONE STATEMENT
equal_prep_1 = ["corresponds to", "agrees with", "same as", "duplicate of", "equal to", "equivalent to", "identical to"];
is_equal_prep_1 = ["is same as", "is duplicate of", "is equal to", "is equivalent to", "is identical to"];


#FAGMENTED
unequal = ["unequal"];
equal = ["equal", "matched", "equals", "matching", "balances", "=="];
less = ["lower", "younger", "lighter", "less", "tinier", "smaller", "lower"]; #isn't, not, !
greater = ["taller", "higher", "greater", "older","heavier","bigger","taler"]; #isn't, not, !
lessEqual = ["smallerEqual", "lessEqual", "lowerEqual", "youngerEqual", "lighterEqual"]; #isnt, not, !
greaterEqual = ["greaterEqual", "higherEqual", "olderEqual","heavierEqual","biggerEqual"]; #isnt, not, !


is_unequal_to = ["unequal"];
is_less_than = ["lower", "younger", "lighter", "less","tinier","smaller","lower"]; #not, !
is_greater_than = ["taller", "higher", "greater", "older","heavier","bigger","taler"]; #not, !


# v and v are (the) compare 
equal_are = ["equivalent", "invariable", "balanced", "corresponding","agreeing","uniform","alike"]; #not
unequal_are = ["unequal", "differing", "dissimilar", "unalike", "vary", "diverge", "disagree", "clash"]; #not


#////////////////////////////////////TEMPLATES///////////////////////////////////////
#1 variable_compare_variable (x equals 5)
if (sys.argv[1] == "variable_compare_variable"):
	firstFile = values; fourthFile = [""]; fifthFile = [""]; sixthFile = [""];
	posVariable = 1; posValue = 3; compare_symbol = "==";
	if (sys.argv[2] == "unequal"): secondFile = unequal; thirdFile = variables; compare_symbol = "!=";
	if (sys.argv[2] == "equal"): secondFile = equal; thirdFile = variables;
	if (sys.argv[2] == "equal_prep_1"): secondFile = equal_prep_1; thirdFile = variables; posValue = 4;
	if (sys.argv[2] == "is_equal_prep_1"): secondFile = is_equal_prep_1; thirdFile = variables; posValue = 5;

	if (sys.argv[2] == "less"): secondFile = less; thirdFile = variables; compare_symbol = "<";
	if (sys.argv[2] == "greater"): secondFile = greater; thirdFile = variables; compare_symbol = ">";
	if (sys.argv[2] == "lessEqual"): secondFile = lessEqual; thirdFile = variables; compare_symbol = "<=";
	if (sys.argv[2] == "greaterEqual"): secondFile = greaterEqual; thirdFile = variables; compare_symbol = ">=";

	if (sys.argv[2] == "is_less_than"): secondFile = verb_is; thirdFile = less; fourthFile = than; fifthFile = variables; posValue = 5; compare_symbol = "<";
	if (sys.argv[2] == "is_greater_than"): secondFile = verb_is; thirdFile = greater; fourthFile = than; fifthFile = variables; posValue = 5; compare_symbol = ">";
	if (sys.argv[2] == "less_than"): secondFile = less; thirdFile = than; fourthFile = variables; posValue = 4; compare_symbol = "<";
	if (sys.argv[2] == "greater_than"): secondFile = greater; thirdFile = than; fourthFile = variables; posValue = 4; compare_symbol = ">";


	if (sys.argv[2] == "equal_are"): secondFile = and_; thirdFile = variables; fourthFile = verb_are; fifthFile = equal_are; posValue = 3; compare_symbol = "==";
	if (sys.argv[2] == "unequal_are"): secondFile = and_; thirdFile = variables; fourthFile = verb_are; fifthFile = unequal_are; posValue = 3; compare_symbol = "!=";

	#Negation
	if (sys.argv[2] == "equal_prep_1_not"): secondFile = equal_prep_1_not; thirdFile = variables; posValue = 5; compare_symbol = "!=";
	if (sys.argv[2] == "is_equal_prep_1_not"): secondFile = is_equal_prep_1_not; thirdFile = variables; posValue = 6; compare_symbol = "!=";

	if (sys.argv[2] == "less_not"): secondFile = negation_not; thirdFile = less; fourthFile = variables; posValue = 4; compare_symbol = ">=";
	if (sys.argv[2] == "greater_not"): secondFile = negation_not; thirdFile = greater; fourthFile = variables; posValue = 4; compare_symbol = "<=";
	if (sys.argv[2] == "lessEqual_not"): secondFile = negation_not; thirdFile = lessEqual; fourthFile = variables; posValue = 4; compare_symbol = ">";
	if (sys.argv[2] == "greaterEqual_not"): secondFile = negation_not; thirdFile = greaterEqual; fourthFile = variables; posValue = 4; compare_symbol = "<";

	if (sys.argv[2] == "is_less_than_not"): secondFile = verb_is_not; thirdFile = less; fourthFile = than; fifthFile = variables; posValue = 6; compare_symbol = ">=";
	if (sys.argv[2] == "is_greater_than_not"): secondFile = verb_is_not; thirdFile = greater; fourthFile = than; fifthFile = variables; posValue = 6; compare_symbol = "<=";
	if (sys.argv[2] == "less_than_not"): secondFile = negation_not; thirdFile = less; fourthFile = than; fourthFile = variables; posValue = 4; compare_symbol = ">=";
	if (sys.argv[2] == "greater_than_not"): secondFile = negation_not; thirdFile = greater; fourthFile = than; fourthFile = variables; posValue = 4; compare_symbol = "<=";

	if (sys.argv[2] == "equal_are_not"): secondFile = and_; thirdFile = variables; fourthFile = verb_are_not; fifthFile = equal_are; posValue = 3; compare_symbol = "!=";
	if (sys.argv[2] == "unequal_are_not"): secondFile = and_; thirdFile = variables; fourthFile = verb_are_not; fifthFile = unequal_are; posValue = 3; compare_symbol = "==";


	if (sys.argv[2] == "unequal_not"): secondFile = negation_not; thirdFile = unequal; fourthFile = variables; posValue = 4; compare_symbol = "==";
	if (sys.argv[2] == "equal_not"): secondFile = negation_doesnt; thirdFile = equal_negation; fourthFile = variables; posValue = 4;  compare_symbol = "!=";



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
							out.write(line); out.write("\n"); out.write(line_p); out.write("\n")
							out_script.write(lineScript); out_script.write("\n"); 
							#out_script.write(lineScript_p); 
							#out_script.write("\n")


out.close()
out_script.close()














