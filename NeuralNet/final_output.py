import sys, os
import re
sys.path.append(os.path.join(os.getcwd(), "..", "NLP"))
sys.path.append(os.path.join(os.getcwd(), "..", "NeuralNet"))
import Process as p

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
        elif poslist[2] == "noun" or "numeral" or wordlist[2] == "to":
            objtwo = wordlist[2]
    elif poslist[0] == "noun" or "numeral":
        if wordlist[0] == "Set" or "set":
            objone = wordlist[1]
            objtwo = wordlist[3]
        else:
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
    total = ""
    for x in range(0, len(poslist)):
        if poslist[x] == "verb" or wordlist[x] == "print":
            if len(wordlist) == 1:
                return ""
            elif len(wordlist) == 2:
                return wordlist[1]
            elif len(wordlist) > 2:
                if len(wordlist) == 3 and wordlist[1] == "a":
                    return wordlist[2]
                else:
                    for x in range(2, len(wordlist)):
                        total = total + wordlist[x]
                    return total
    return ""


def LoopObject(sentence):
    wordlist = p.getWord(sentence)
    poslist = p.getTag(sentence)
    return ""


def ifObject(sentence):
    wordlist = p.getWord(sentence)
    poslist = p.getTag(sentence)
    objtwo = ""
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

        if x == len(wordlist) - 1:
            objtwo = wordlist[x]

    return objone, operator, objtwo


def varCode(obj1, obj2):
    return obj1 + "=" + obj2

def printCode(obj1):
    return "print(" + obj1 + ")"

def loopCode(obj1):
    return "for x in range ( , ):"

def ifCode(obj1, oper, obj2):
    return "if " + obj1 + " " + oper + " " + obj2 + ":"



