import sys, os
import re
sys.path.append(os.path.join(os.getcwd(), "..", "NLP"))
sys.path.append(os.path.join(os.getcwd(), "..", "NeuralNet"))
import Process as p

#This is the action.
def categoryconvert(categorynum):
    categorynum = int(categorynum)
    if categorynum == 1:
        return "variable"
    elif categorynum == 2:
        return "print"
    elif categorynum == 3:
        return "loop"
    elif categorynum == 4:
        return "if"
    else:
        return -1


# Get Object for variable statements
def varObject(sentence):
    wordlist = p.getWord(sentence)
    poslist = p.getTag(sentence)
    objone = ""
    objtwo = ""
    if poslist[0] == "verb":
        objone = wordlist[1]
        if poslist[2] == "article":
            if len(poslist)-1 == 2:
                objtwo = wordlist[2]
            else:
                objtwo = wordlist[3]
        elif poslist[2] == "noun" or "numeral":
            objtwo = wordlist[2]
    elif poslist[0] == "noun" or "numeral":
        objone = wordlist[0]
        objtwo = wordlist[2]
    elif wordlist[1] == "=" or "->":
        objone = wordlist[0]
        objtwo = wordlist[2]
    else:
        pass

    return objone, objtwo


# This one is for the print statements
def printObject(sentence):
    wordlist = p.getWord(sentence)
    poslist = p.getTag(sentence)
    for x in range(0, len(poslist)):
        if poslist[x] == "verb":
            if poslist[x + 1] == "article":
                return wordlist[x + 2]
            else:
                return wordlist[x + 1]
        else:
            pass
    return ""


def LoopObject(sentence):
    wordlist = p.getWord(sentence)
    poslist = p.getTag(sentence)
    return ""


def ifObject(sentence):
    wordlist = p.getWord(sentence)
    poslist = p.getTag(sentence)
    objone = wordlist[1]
    operator = ""
    lessthan = ["light", "less", "tin", "small", "lower", "young"]
    greaterthan = ["great", "old", "tall", "big", "high", "heav"]
    wrong = ["unequal", "un", "not", "!"]
    lessflag = False
    moreflag = False
    wrongFlag = False
    equalFlag = False
    for x in range(2, len(wordlist)):
        for y in lessthan:
            if y in wordlist[x]:
                if "equal" in wordlist[x]:
                    equalFlag = True
                    lessflag = True
                else:
                    lessflag = True
        for y in greaterthan:
            if y in wordlist[x]:
                if "equal" in wordlist[x]:
                    equalFlag = True
                    moreflag = True
                else:
                    moreflag = True
        for y in wrong:
            if y in wordlist[x]:
                wrongFlag = True
        if "equal" in wordlist[x]:
            equalFlag = True

        if lessflag:
            if equalFlag:
                operator = "<="
            else:
                operator = "<"
        elif moreflag:
            if equalFlag:
                operator = ">="
            else:
                operator = ">"
        elif wrongFlag:
            operator = "!="

        else:
            operator = "=="

    objtwo = wordlist(len(wordlist)-1)
    return objone, operator, objtwo



