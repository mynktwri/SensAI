import nltk
from nltk.tokenize import word_tokenize


def getTag(text):
    text = word_tokenize(text)
    pos_tags = nltk.pos_tag(text)
    return pos_tags



def getWord(text):
    text = word_tokenize(text)
    return text



def getLength(text):
    text = word_tokenize(text)
    pos_tags = nltk.pos_tag(text)
    return len(pos_tags)


def numVerbs(text):
    tokens = word_tokenize(text)
    pos_tags = nltk.pos_tag(tokens)
    verbs = ["MD", "TO", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]
    pos_list = [p for p in pos_tags if p[1] in verbs]
    return len(pos_list)