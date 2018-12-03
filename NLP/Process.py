import nltk
from nltk.tokenize import word_tokenize


def getTag(text):
    text = word_tokenize(text)
    pos_tags = nltk.pos_tag(text)
    verbs = ["MD", "TO", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]
    nouns = ["PRP", "PRP$", "POS", "NN", "NNS", "FW", "UH", "NNP", "NNPS"]
    adj = ["JJ", "JJR", "JJS", "PDT"]
    Adv = ["RB", "RBR", "RBS", "EX", "WDT", "WP", "WP$", "WRB"]
    prep = ["IN"]
    number = ["CD"]
    symbol = ["SYMBOL"]
    article = ["DT"]
    participle = ["RP"]
    quantifier = ["LS"]
    pos_map = {"adjective": ["JJ", "JJR", "JJS", "PDT"],
               "adverb": ["RB", "RBR", "RBS", "EX", "WDT", "WP", "WP$", "WRB"],
               "noun": ["PRP", "PRP$", "POS", "NN", "NNS", "FW", "UH", "NNP", "NNPS"],
               "verb": ["MD", "TO", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ"],
               "symbol": ["SYM"
                          "BOL", "<", ">", "=", ">=", "<=", "!=", "!"],
               "article": ["DT", ],
               "coordinating_conj": ["CC"],
               "demonstrative_pronoun": [],
               "numeral": ["CD", ],
               "participle": ["RP"],
               "indefinite_pronoun": [],
               "preposition": ["IN"],
               "quantifier": ["LS"],
               "subordinating_conj": [],
               "punctuation": [".", ",", "\"", "\'", "`", "?", "(", ")", "``", "\""]}
    simple_tags = []
    for p in pos_tags:
        for k, v in pos_map.items():
            if p[1] in v:
                simple_tags.append(k)
            else:
                pass
# The code does not take words that are not in the nltk dictionary.
    return simple_tags



def getWord(text):
    return word_tokenize(text)


def getLength(text):
    text = word_tokenize(text)
    pos_tags = nltk.pos_tag(text)
    return len(pos_tags)


