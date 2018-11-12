#!/usr/bin/python
# coding: latin-1
import os, sys


filename = "out.txt"
out = open(filename,"w")

filename1 = "variables.txt"
variables = open(filename1, "r")

filename2 = "verbs.txt"
verbs = open(filename2, "r")

filename3 = "assignments.txt"
assign = open(filename3, "r")

filename4 = "values.txt"
values = open(filename4, "r")


arrVerbs = [];
for verb in verbs:
	arrVerbs.append(verb.strip())

arrVariables = [];
for var in variables:
	arrVariables.append(var.strip())

arrAssign = [];
for ass in assign:
	arrAssign.append(ass.strip())

arrValues = [];
for val in values:
	arrValues.append(val.strip())


arrOut = []

for verb in arrVerbs:
	for var in arrVariables:
		for ass in arrAssign:
			for val in arrValues:
				line = verb + " " +var + " " + ass + " " + val
				tempTuple = (line, [var, val])
				arrOut.append(tempTuple)
				#print(line)
				out.write(line)
		   		out.write("\n")

out.close()





