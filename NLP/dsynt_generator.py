import copy
import re
import os
import nltk
import inflect
import time
#TODO check if this module is needed to guarentee the pl param
import language_check
import sys
sys.path.append(os.path.join(os.getcwd(), "."))
import element_utils as eu
import stanford_tools as st

# FIXME if we are going to use this file in the future, PLEASE MAKE SURE WE CLOSE THE SQLITE_CONN.

    #
"""
FIXME known bugs:
< dsyntnode lexeme = "family" class ="common_noun" number="pl" article="no-art" gender="neut" rel="II" >
<dsyntnode lexeme = "locate" class ="verb" tense="past" mood="inf" rel="II" >

This causes a random "of" to be generated between these two words...
"""

def preprocessInput(split_char="\n"):
    debugsentences = []
    # with open("preprocessdebug.txt", "w") as outfile:
    folder = os.path.join(os.getcwd(), "data", "gen", "preprocessed_input")
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)

    for file in os.listdir(os.path.join(os.getcwd(), "data", "gen", "input")):
        t = time.time()
        file_txt_lines = open(os.path.join(os.getcwd(), "data", "gen", "input", file)).read().split(split_char)
        for line_num, file_txt in enumerate(file_txt_lines):
            # try:
                dep_parse, const_parse = st.parseSentence(file_txt, ["test"], expected_entities=[], both=True)
                # print(str(time.time() - t))
                dep_parse = st.putIntoDepTree(dep_parse)
                const_parse = st.putIntoDepTree(const_parse, case="const")
                dsynt_parse = convertToDsynts(dep_parse, const_parse)
                fileroot = file.split(".")[0] + "#" + str(line_num)
                filename = fileroot + ".xml"
                textfile = fileroot + ".txt"
                text_file = open(os.path.join(os.getcwd(), "data", "gen", "preprocessed_input", textfile), "w")
                text_file.write(file_txt)
                dev_file = (os.path.join(os.getcwd(), "data", "gen", "test", filename))
                dep_file = (os.path.join(os.getcwd(), "data", "gen", "dep", filename))
                eu.writeTree(eu.convertToEtree(eu.getRoot(dsynt_parse)), dev_file)
                eu.writeTree(eu.convertToEtree(eu.getRoot(dep_parse)), dep_file)
                # except Exception:
                #     debugsentences.append(str(file))
                #     debugsentences.append(str(line_num))
                #     debugsentences.append(str(file_txt))

    # outfile.write(str(debugsentences))

def main(dev=True, preprocess=False, run_realpro=True, brute_force=False):
    st.init()
    if dev:
        # The slimy bugs quietly entered my apartment.
        t = time.time()
        dep_parse, const_parse = st.parseSentence("""
             I recently momentarily opened my patio's door. The slimy bugs quietly
             entered my apartment. I did not initially notice that the slimy bugs
             quietly entered my apartment. I peacefully slept. I overnight awoke.
             I shockingly saw the slimy bugs was on my apartment's ceiling. I grabbed
             the reachable thing because the bugs scared me. The slimy bugs were
             my enemy. I smeared the greasy bugs's innards. I managed to kill every
            bug. I grazed the bugs's leader with the rolled comic book. I removed
            the tiny bugs's leader's limb. I angrily hit the bugs with the rolled
            comic book. The big bugs's leader now lurked in my apartment. The bugs's
            leader was the three-legged insect. The big bugs's leader escaped me.
            The big bugs's leader undoubtedly wanted to retaliate against me.
            I looked around every corner of my apartment. I checked my toilet seat
            I looked around every corner of my apartment. I checked my toilet seat
            for the big bugs's leader in order for me to sit down on my toilet seat.
            I in due course expected for the big bugs's leader to jump toward me.
            The cicadas did not even yet arrive to my apartment. Every action of my
            story notably happened.
            """, ["test"], expected_entities=[], both=True)
        # dep_parse, const_parse = st.parseSentence("""
        #     I in due course expected for the big bugs's leader to jump toward me.
        #     """, ["test"], expected_entities=[], both=True)
        print(str(time.time() - t))
        dep_parse = st.putIntoDepTree(dep_parse)
        dep_file = (os.path.join(os.getcwd(), "data", "gen", "dep", "dev_long.xml"))
        eu.writeTree(eu.convertToEtree(eu.getRoot(dep_parse)), dep_file)
        const_parse = st.putIntoDepTree(const_parse, case="const")
        dsynt_parse = convertToDsynts(dep_parse, const_parse)

        dev_file = (os.path.join(os.getcwd(), "data", "gen", "test", "dev_long.xml"))
        eu.writeTree(eu.convertToEtree(eu.getRoot(dsynt_parse)), dev_file)
    elif brute_force:
        #The Cotto is an Italian coffee shop with a moderate price range.
        gen = ["It is the portland arms in the city centre near.",
               "A 3 out of rating of 5."]
        for i, utterance in enumerate(["It is near The Portland Arms in the city centre.",
                          "A 3 out of 5 rating."]):
            dep_parse, const_parse = st.parseSentence(utterance, ["test"], expected_entities=[], both=True)
            dep_parse = st.putIntoDepTree(dep_parse)
            dep_file = (os.path.join(os.getcwd(), "data", "gen", "bf", "bf"+str(i)+".xml"))
            eu.writeTree(eu.convertToEtree(eu.getRoot(dep_parse)), dep_file)
            const_parse = st.putIntoDepTree(const_parse, case="const")
            dsynt_parse = convertToDsynts(dep_parse, const_parse)
            word_vector = sentenceMisMatchVector(utterance, gen[i])
            test_point = None
            for i, x in enumerate(word_vector):
                if x == 0:
                    test_point = i
                    break
            #first error
            lexeme = eu.getAttribute(eu.getRoot(dep_parse).xpath(".//*[@id='"+str(test_point+1)+"']")[0], "lexeme")
            lexeme = eu.getAttribute(eu.getRoot(dsynt_parse).xpath(".//*[@lexeme='" + lexeme + "']")[0], "lexeme")
            # dev_file = (os.path.join(os.getcwd(), "data", "gen", "test", "bf"+str(i)+".xml"))
            # eu.writeTree(eu.convertToEtree(eu.getRoot(dsynt_parse)), dev_file)
    else:
        if preprocess:
            preprocessInput()
        else:
            for file in os.listdir(os.path.join(os.getcwd(), "data", "gen", "input")):
                print("Processing " + str(file))
                t = time.time()
                file_txt = open(os.path.join(os.getcwd(), "data", "gen", "input", file)).read()
                dep_parse, const_parse = st.parseSentence(file_txt, ["test"], expected_entities=[], both=True)
                print(str(time.time() - t))
                dep_parse = st.putIntoDepTree(dep_parse)
                const_parse = st.putIntoDepTree(const_parse, case="const")
                dsynt_parse = convertToDsynts(dep_parse, const_parse)
                filename = file.split(".")[0]+".xml"

                dev_file = (os.path.join(os.getcwd(), "data", "gen", "test", filename))
                dep_file = (os.path.join(os.getcwd(), "data", "gen", "dep", filename))
                eu.writeTree(eu.convertToEtree(eu.getRoot(dsynt_parse)), dev_file)
                eu.writeTree(eu.convertToEtree(eu.getRoot(dep_parse)), dep_file)
    if run_realpro:
        import shutil
        folder = os.path.join(os.path.join(os.getcwd(), "..", "data", "xml", "kest"))
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        preprocess_dir = [x.split(".")[0]+".xml" for x in os.listdir(os.path.join(os.getcwd(), "data", "gen", "preprocessed_input"))]
        for file in os.listdir(os.path.join(os.getcwd(), "data", "gen", "test")):
            if preprocess and file not in preprocess_dir:
                continue
            shutil.copy2(os.path.join(os.getcwd(), "data", "gen", "test", file), os.path.join(os.getcwd(), "..", "data", "xml", "kest"))
        os.chdir("..")

def convertToDsynts(dep_parse, const_parse=None, full=True):
    #TODO there is an assumption if a node can be killed, it never really mattered. Need to test and very this.
    dsynt_parse = copy.deepcopy(dep_parse)
    convertListRoot(dsynt_parse)
    dsynts = dsynt_parse.xpath(".//deps")
    for dsynt_node in dsynts:
        # dc_map = zipDepAndConst(dsynt_parse, const_parse)
        nodes = [eu.getRoot(dsynt_node)] + dsynt_node.xpath(".//depnode")
        for dsynt in nodes:
            convertSpecialCases(dsynt)
        nodes = [eu.getRoot(dsynt_node)] + dsynt_node.xpath(".//depnode")
        for dsynt in nodes:
            convertTag(dsynt)
            convertRoot(dsynt)
            convertLexeme(dsynt)
            convertPOS(dsynt)
            convertPro(dsynt)
            convertTense(dsynt)
            convertVoice(dsynt)
            convertArticle(dsynt)
            convertNumber(dsynt)
            convertPerson(dsynt)
            convertForm(dsynt)
            convertGender(dsynt)
            convertMood(dsynt)
            convertRel(dsynt)
            convertPosition(dsynt)
            convertPolarity(dsynt)
            convertAspect(dsynt)
            # convertQuestion(dsynt)
            # convertCase(dsynt)
            # convertAspect(dsynt)
            # convertExtrapo(dsynt)
            # convertCaps(dsynt)
    # todo make a flag for both strip functions
        stripKillNodes(dsynt_node)
    for dsynt in dsynt_parse.iter():
        convertPunct(dsynt)
        convertCompound(dsynt)
        verifyINodes(dsynt)
        verifyConjNodes(dsynt)
        verifyAttrNodes(dsynt)
    for dsynt in dsynt_parse.iter():
        stripDefaults(dsynt)
        stripExtraAttrs(dsynt)
    for dsynt in dsynt_parse.iter():
        convertCompound(dsynt)

    dsynt_parse = eu.convertToEtree(eu.getRoot(dsynt_parse))
    # adjustIdNumbers(dsynt_parse)
    return dsynt_parse

def convertListRoot(dsynt_parse):
    dsynt_parse[0].getparent().tag = "dsynts-list"

def convertTag(dsynt):
        tag = eu.getTag(dsynt)
        tag = tag.replace("dep","dsynt")
        eu.setTag(dsynt, tag)

def convertRoot(dsynt):
    if eu.getAttribute(dsynt, "lexeme") == "ROOT" and eu.getAttribute(dsynt, "id") == "0":
        eu.delElement(dsynt, True)

def convertLexeme(dsynt):
    if eu.hasAttribute(dsynt, "lexeme"):
        if "'" in eu.getAttribute(dsynt, "lexeme"):
            eu.delElement(dsynt, True)
        else:
            eu.setAttribute(dsynt, "lexeme", eu.getAttribute(dsynt, "lexeme").replace(" ", "_").lower())

def convertPOS(dsynt):
    if eu.hasAttribute(dsynt, "pos") and not eu.hasAttribute(dsynt, "class"):
        pos_map = {"adjective": ["JJ", "JJR", "JJS", "PDT"],
                   "adverb": ["RB", "RBR", "RBS", "EX", "WDT", "WP", "WP$", "WRB"],
                   "common_noun": ["PRP", "PRP$", "POS", "NN", "NNS", "FW", "UH"],
                   "proper_noun": ["NNP", "NNPS"],
                   "verb": ["MD", "TO", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ"],
                   "symbol": ["SYMBOL"],
                   "article": ["DT", ],
                   "coordinating_conj": ["CC"],
                   "demonstrative_pronoun": [],
                   "numeral": ["CD", ],
                   "participle": ["RP"],
                   "indefinite_pronoun": [],
                   "preposition": ["IN"],
                   "quantifier": ["LS"],
                   "subordinating_conj": []}
        pos = eu.getAttribute(dsynt, "pos")
        realpro_pos = ""
        for k,v in pos_map.items():
            if pos in v:
                realpro_pos = k
        if realpro_pos == "":
            realpro_pos = "symbol"
        #this is a weird special case I've noticed in our data
        elif realpro_pos == "verb" and eu.getAttribute(dsynt, "lexeme") == "to":
            realpro_pos = "preposition"
        eu.setAttribute(dsynt, "class", realpro_pos)

#FIXME be verbs are wierd, around line 1500 in the en-verbs.csv
def convertTense(dsynt):
    if eu.getAttribute(dsynt, "class") == "verb":
        with open(os.path.join(os.getcwd(), "data", "en-verbs.csv")) as f:
            verbs = f.read().split("\n")
        verbs = {verb.split(",")[-1]:verb.split(",")[0] for verb in verbs}
        dep_pos = eu.getAttribute(dsynt, "pos")
        if dep_pos in ["VBN", "VBD"]:
            eu.setAttribute(dsynt, "tense", "past")
            curr_lex = eu.getAttribute(dsynt, "lexeme")
            if curr_lex.lower() in verbs:
                eu.setAttribute(dsynt, "lexeme", verbs[curr_lex])
        elif dep_pos in ["MD"]:
            eu.setAttribute(dsynt, "tense", "future")
            if eu.hasAttribute(dsynt, "mood"):
                eu.delAttribute(dsynt, "mood")
        else:
            eu.setAttribute(dsynt, "tense", "pres")

def convertVoice(dsynt):
    if eu.getAttribute(dsynt, "pos").startswith("V"):
        # be,am,are,is,are,being,was,were,was,were,were,been,am not,aren't,isn't,aren't,wasn't,weren't,wasn't,weren't
        if eu.getAttribute(dsynt, "lexeme") in ["be", "am", "is", "are", "was", "were", "been", "being"]:
            curr_id = int(eu.getAttribute(dsynt, "id"))
            curr_dsynt_tree = getCurrentDsynt(dsynt)
            next_dsynt = curr_dsynt_tree.xpath(".//*[@id='"+str(curr_id+1)+"']")
            if len(next_dsynt) > 0:
                next_pos = eu.getAttribute(next_dsynt[0], "pos")
                if next_pos.startswith("V") and not next_pos.startswith("VBG"):
                    eu.setAttribute(next_dsynt[0], "voice", "pass")
                    eu.setAttribute(dsynt, "voice", "pass")

def convertNumber(dsynt):
    if "noun" in eu.getAttribute(dsynt, "class"):
        lexeme = eu.getAttribute(dsynt, "lexeme")
        #FIXME edge case bug
        if lexeme.lower() in ["express"]:
            eu.setAttribute(dsynt, "number", "sg")
        else:
            p = inflect.engine()
            if eu.hasAttribute(dsynt, "pl"):
                eu.setAttribute(dsynt, "number", "pl")
                singularized = p.singular_noun(lexeme)
                if type(singularized) is str:
                    # if lang_check.check(lexeme) == lang_check.check(singularized):
                    eu.setAttribute(dsynt, "lexeme", singularized)
            else:
                singularized = p.singular_noun(lexeme)
                if type(singularized) is str and singularized != lexeme:
                    # if lang_check.check(lexeme) == lang_check.check(singularized):
                    eu.setAttribute(dsynt, "number", "pl")
                    eu.setAttribute(dsynt, "lexeme", singularized)
                else:
                    eu.setAttribute(dsynt, "number", "sg")

def convertPro(dsynt):
    #pro:rel is mentioned in the docs but never in our data, so we don't handle it
    if "PRP" in eu.getAttribute(dsynt, "pos"):
        if eu.hasAttribute(dsynt, "poss"):
            eu.setAttribute(dsynt, "pro", "poss")
            #fixme special case
            if eu.getAttribute(dsynt, "lexeme") == "its":
                eu.setAttribute(dsynt, "lexeme", "it")
        else:
            eu.setAttribute(dsynt, "pro", "pro")

def convertPerson(dsynt):
    #pro:rel is mentioned in the docs but never in our data, so we don't handle it
    if "PRP" in eu.getAttribute(dsynt, "pos"):
        lex = eu.getAttribute(dsynt, "lexeme").lower()
        if lex in ["i", "my", "mine", "me", "myself", "we", "us", "our", "ours"]:
            eu.setAttribute(dsynt, "person", "1st")
        elif "you" in lex:
            eu.setAttribute(dsynt, "person", "2nd")
        else:
            eu.setAttribute(dsynt, "person", "3rd")

def convertForm(dsynt):
    """
    word twelve
    roman XII
    arabic 12
    """
    if eu.getAttribute(dsynt, "pos") == "CD":
        try:
            int(eu.getAttribute(dsynt, "lexeme"))
            eu.setAttribute(dsynt, "form", "arabic")
        except:
            eu.setAttribute(dsynt, "form", "word")
    elif eu.getAttribute(dsynt, "pos") == "SYMBOL":
        if isRomanNumeral(eu.getAttribute(dsynt, "lexeme")):
            eu.setAttribute(dsynt, "form", "roman")
            eu.setAttribute(dsynt, "class", "numeral")

#todo does commenting out the "that" case break sentence 2 or is it fine?
def convertArticle(dsynt):
    if eu.getAttribute(dsynt, "class") == "article":
        article_map = {"indef": ["a", "an"],
                       "def": ["the"],
                       # "dem-prox":["this", "these"], not in data
                       # "dem-pist": ["that", "those"], not in data
                       }
        article_dsynt = dsynt
        ids = []
        while True:
            par = dsynt.getparent()
            if par is None or eu.getTag(par) == "dsynts" or "noun" not in eu.getAttribute(par, "class"):
                break
            par_id = int(eu.getAttribute(par, "id"))
            isValid = False
            if len(ids) == 0:
                isValid = True
            else:
                for i in ids:
                    if par_id in [i-1, i+1]:
                        isValid = True
                        break
            if not isValid:
                break
            ids.append(par_id)
            dsynt = par
        if len(ids) == 0:
            det_id = eu.getAttribute(article_dsynt, "det")
            ids.append(int(det_id))
        lexeme = eu.getAttribute(article_dsynt, "lexeme").lower()
        realpro_article = ""
        for k, v in article_map.items():
            if lexeme in v:
                realpro_article = k
        if realpro_article == "":
            #FIXME this is a weird special case where it's like "Twenty Two" the fictional place, well this is a numeral noun.
            if "noun" not in eu.getAttribute(dsynt, "class"):
                eu.setAttribute(article_dsynt, "class", "common_noun")
                if eu.hasAttribute(article_dsynt, "form"):
                    eu.delAttribute(article_dsynt, "form")
            eu.setAttribute(article_dsynt, "class", "ATTR")
        else:
            root = eu.getRoot(dsynt)
            node = root.xpath(".//*[@id='"+str(ids[-1])+"']")[0]
            # FIXME this is a weird special case where it's like "Twenty Two" the fictional place, well this is a numeral noun.
            if "noun" not in eu.getAttribute(dsynt, "class"):
                eu.setAttribute(node, "class", "common_noun")
                if eu.hasAttribute(node, "form"):
                    eu.delAttribute(node, "form")
            eu.setAttribute(node, "article", realpro_article)
            eu.delElement(article_dsynt, True)

    elif "noun" in eu.getAttribute(dsynt, "class"):
        if not eu.hasAttribute(dsynt, "article"):
            eu.setAttribute(dsynt, "article", "no-art")

def convertRel(dsynt):
    """
    :param dsynt:
    :return:
        Rel notes:
            I
            II is a root - verb primarily
            III
            VI
            ATTR - adj or adverb primarily or pro=poss and is noun
    """
    if eu.hasAttribute(dsynt, "class"):
        curr_class = eu.getAttribute(dsynt, "class")
        if curr_class == "verb":
            curr_par = dsynt.getparent()
            if curr_par is not None and eu.getTag(curr_par) == "dsyntnode":
                par = curr_par
                while par != None:
                    if eu.getAttribute(par, "class") == "verb":
                        break
                    par = par.getparent()
                #there is no root verb
                if par is None:
                    root = eu.getRoot(dsynt)
                    root_node = root.getchildren()[0]
                    eu.setAttribute(dsynt, "rel", "II")
                    eu.setAttribute(root_node, "rel", "II")
                    eu.setAttribute(root_node, "verb_swap", "True")
                    new_element = eu.addCopyElement(root, dsynt)
                    for child in root_node.getchildren():
                        eu.addElement(new_element,child)
                    eu.addElement(new_element, root_node)
                    eu.delElement(dsynt, True)
                #there is a root verb
                else:
                # if eu.getAttribute(par, "class") == "verb" and eu.getAttribute(par, "rel") == "II":
                    if eu.getAttribute(par, "class") in ["common_noun", "verb"] and eu.getAttribute(par, "rel") == "II" and \
                            (eu.getAttribute(dsynt, "lexeme") == "be" or eu.getAttribute(dsynt, "mood") == "inf-to"):
                        eu.setAttribute(dsynt, "rel", "III")
                    else:
                        eu.setAttribute(dsynt, "rel", "II")
            else:
                eu.setAttribute(dsynt, "rel", "II")
            if eu.getAttribute(dsynt, "lexeme") == "be" and eu.getAttribute("dsynt", "rel") == "III":
                curr = dsynt
                break_tag_loop = False
                while curr is not None and eu.getTag(curr) != "dsynts":
                    for child in curr.getchildren():
                        if eu.getAttribute(child, "class") == "verb":
                            break_tag_loop = True
                            break
                    if break_tag_loop:
                        break
                    curr = curr.getparent()

                bubble_node = curr
                new_element = eu.addCopyElement(bubble_node.getparent(), dsynt)
                eu.addElement(new_element, bubble_node)
                eu.delElement(dsynt, True)
        elif curr_class in ["participle", "numeral"]:
            eu.setAttribute(dsynt, "rel", "II")
        elif "noun" in curr_class:
            #fixme idk if this is going to work
            if "proper_noun" in curr_class:
                eu.setAttribute(dsynt, "rel", "II")
            if eu.getAttribute(dsynt, "pro") == "poss":
                eu.setAttribute(dsynt, "rel", "ATTR")
            else:
                par = dsynt.getparent()
                curr_id = int(eu.getAttribute(dsynt, "id"))
                if par is None or eu.getTag(par) == "dsynts":
                    par_id = 0
                else:
                    par_id = int(eu.getAttribute(par, "id"))
                #word is after parent
                if curr_id - par_id > 0:
                    eu.setAttribute(dsynt, "rel", "II")
                #word is before parent
                else:
                    root_id = int(eu.getAttribute(par, "id"))
                    curr_id = int(eu.getAttribute(dsynt, "id"))
                    if curr_id > root_id:
                        eu.setAttribute(dsynt, "III")
                    else:
                        eu.setAttribute(dsynt, "rel", "I")
                    cans = []
                    for sibling in par.getchildren():
                        if eu.getAttribute(sibling, "rel") == "I":
                            cans.append(sibling)
                    if len(cans) > 1:
                        min_val = None
                        bubble_node = None
                        for can in cans:
                            curr_val = par_id - int(eu.getAttribute(can, "id"))
                            if min_val is None or curr_val > min_val:
                                min_val = curr_val
                                bubble_node = can
                        eu.setAttribute(bubble_node, "rel", "II")
                        par = bubble_node.getparent()
                        while par is not None:
                            tmp_par = par.getparent()
                            break_while_loop = False
                            for sibling in tmp_par.getchildren():
                                if eu.getAttribute(sibling, "rel") == "II" or \
                                        (eu.getAttribute(sibling, "rel") == "ATTR" and len(tmp_par.getchildren()) == 1):
                                    break_while_loop = True
                                    break
                            if not break_while_loop:
                                break
                            par = tmp_par
                        #fixme this is causing the i problem
                        new_element = eu.addCopyElement(par.getparent(), bubble_node)
                        for child in bubble_node.getchildren():
                            eu.addElement(new_element, child)
                        eu.delElement(bubble_node, True)
        #fixme unsafe catch all
        else:
            eu.setAttribute(dsynt, "rel", "ATTR")
            # heuristic learned from sentence 21 of bug out for blood (of)
            if eu.getAttribute(dsynt, "class") == "preposition":
                par = dsynt.getparent()
                #special case
                if par is not None:
                    grandparent = par.getparent()
                    #todo test elif
                    if grandparent is not None:
                        siblings = grandparent.getchildren()
                        b = False
                        for sibling in siblings:
                            if eu.getAttribute(sibling, "class") == "ATTR":
                                eu.delElement(dsynt, True)
                                b = True
                                break
                        #special case from line 16 of bug out for blood
                        if not b:
                            curr_id = eu.getAttribute(dsynt, "id")
                            par_id = eu.getAttribute(par, "id")
                            if int(curr_id) < int(par_id):
                                new_element = eu.addCopyElement(grandparent, dsynt)
                                eu.addElement(new_element, par)
                                eu.delElement(dsynt, True)
                                dsynt = new_element
                    if eu.getAttribute(dsynt.getparent(), "lexeme") == "in_order":
                        eu.delElement(dsynt, True)
                    #todo is this true? a preposition should only be a child of verb? we shall see.
                    # elif eu.getAttribute(dsynt.getparent(), "class") != "verb":
                    #     eu.delElement(dsynt, True)
            elif eu.getAttribute(dsynt, "class") == "adjective":
                par = dsynt.getparent()
                if par is not None:
                    correct_parent = None
                    for sibling in par.getchildren():
                        if eu.getAttribute(sibling, "verb_swap") == "True":
                            correct_parent = sibling
                            break
                    if correct_parent is not None:
                        eu.addElement(correct_parent, dsynt)
        par = dsynt.getparent()
        if par is not None:
            subj_nodes = [child for child in par.getchildren() if eu.getAttribute(child, "rel") == "II"]
            if len(subj_nodes) > 1:
                correctSubjNodes(subj_nodes, dsynt.getchildren())
            noun_nodes = [child for child in par.getchildren() if eu.getAttribute(child, "rel") == "I" and "noun" in eu.getAttribute(child, "class")]
            if len(noun_nodes) > 1:
                correctNounNodes(noun_nodes, dsynt.getchildren())
            #todo this is likely useful, but not now
            # if eu.getAttribute(dsynt, "lexeme") == "pasta":
            #     if eu.getAttribute(dsynt, "rel") == "I":
            #         par = dsynt.getparent()
            #         if par is not None:
            #             correct_parent = None
            #             for sibling in par.getchildren():
            #                 if eu.getAttribute(sibling, "verb_swap") == "True":
            #                     correct_parent = sibling
            #                     break
            #             if correct_parent is not None:
            #                 eu.addElement(correct_parent, dsynt)

#fixme very likely this needs to be improved
def correctSubjNodes(subj_nodes, nodes):
    comp_nodes = sorted(subj_nodes, key=lambda x: int(eu.getAttribute(x, "id")))
    # root_id = int(eu.getAttribute(comp_nodes[-1].getparent(), "id"))
    for x, comp_node in enumerate(comp_nodes):
        if x < len(comp_nodes)-1:
            # curr_id = int(eu.getAttribute(comp_nodes[-1].getparent(), "id"))
            # if root_id > curr_id:
            eu.setAttribute(comp_node, "rel", "I")
            # else:
            #     eu.setAttribute(comp_node, "rel", "III")

def correctNounNodes(noun_nodes, nodes):
    comp_nodes = sorted(noun_nodes, key=lambda x: int(eu.getAttribute(x, "id")))
    for x, comp_node in enumerate(comp_nodes):
        if x < len(comp_nodes) - 1:
            eu.setAttribute(comp_node, "rel", "ATTR")
            par = comp_node.getparent()
            if par is not None:
                correct_parent = None
                for sibling in par.getchildren():
                    if eu.getAttribute(sibling, "verb_swap") == "True":
                        correct_parent = sibling
                        break
                cans = par.getchildren()
                if correct_parent is not None:
                    curr_id = int(eu.getAttribute(comp_node, "id"))
                    for can in cans:
                        can_id = int(eu.getAttribute(can, "id"))
                        if curr_id in [can_id - 1, can_id+1]:
                            eu.addElement(correct_parent, comp_node)
                            break

def verifyAttrNodes(dsynt):
    par = dsynt.getparent()
    if par is not None:
        attr_nodes = [child for child in par.getchildren() if
                      eu.getAttribute(child, "rel") == "ATTR" and "noun" in eu.getAttribute(child, "class") or
                      "adjective" in eu.getAttribute(child, "class")]
        if len(attr_nodes) > 0:
            comp_nodes = sorted(attr_nodes, key=lambda x: int(eu.getAttribute(x, "id")))
            comp_sets = []
            new_set = []
            curr_id = int(eu.getAttribute(comp_nodes[0], "id"))
            for comp_node in comp_nodes:
                tmp_id = int(eu.getAttribute(comp_node, "id"))
                if curr_id == tmp_id or tmp_id == curr_id+1:
                    new_set.append(comp_node)
                else:
                    comp_sets.append(new_set)
                    new_set = []
                    new_set.append(comp_node)
                curr_id = tmp_id
            else:
                comp_sets.append(new_set)
            for comp_set in comp_sets:
                nouns = [c for c in comp_set if "noun" in eu.getAttribute(c, "class")]
                adjs = [c for c in comp_set if eu.getAttribute(c, "class") == "adjective"]
                if len(nouns) > 0 and len(adjs) > 0:
                    a_id = int(eu.getAttribute(adjs[0], "id"))
                    for noun in nouns:
                        n_id = int(eu.getAttribute(noun, "id"))
                        if n_id < a_id:
                            eu.addElement(adjs[0], noun)


                    # if eu.getAttribute(dsynt, "class") == "preposition" and eu.getAttribute(dsynt, "rel") == "ATTR":
    #     case = eu.getAttribute(dsynt, "case")
    #
    #     if case != "nil":
    #         if case != eu.getAttribute(dsynt.getparent(), "id"):
    #             root_node = eu.getRoot(dsynt)
    #             nodes = root_node.xpath(".//dsyntnode[@id='" + case + "']")
    #             if len(nodes) > 0:
    #                 # eu.dumpElements(root_node)
    #                 # print(case)
    #                 # print(eu.getAttribute(nodes[0], "lexeme"))
    #                 # print(eu.getAttribute(dsynt, "lexeme"))
    #                 eu.setAttribute(dsynt, "rel", "I")
    #                 new_node = copy.deepcopy(dsynt)
    #                 eu.addElement(nodes[0], new_node)
    #                 eu.delElement(dsynt)

def verifyINodes(dsynt):
    par = dsynt.getparent()
    if par is not None:
        noun_nodes = [child for child in par.getchildren() if
                      eu.getAttribute(child, "rel") == "I" and "noun" in eu.getAttribute(child, "class") or
                      "adjective" in eu.getAttribute(child, "class")]
        if len(noun_nodes) > 0:
            comp_nodes = sorted(noun_nodes, key=lambda x: int(eu.getAttribute(x, "id")))
            root_id = int(eu.getAttribute(comp_nodes[-1].getparent(), "id"))
            for x, comp_node in enumerate(comp_nodes):
                curr_id = int(eu.getAttribute(comp_node, "id"))
                if root_id < curr_id:
                    eu.setAttribute(comp_node, "rel", "III")

def verifyConjNodes(dsynt):
    if eu.getAttribute(dsynt, "class") == "coordinating_conj":
        par = dsynt.getparent()
        curr_id = int(eu.getAttribute(dsynt, "id"))
        if par is not None:
            new_child_nodes = [child for child in par.getchildren() if int(eu.getAttribute(child, "id")) > curr_id]
            if len(new_child_nodes) > 0:
                for new_child in new_child_nodes:
                    eu.addElement(dsynt, new_child)

def convertGender(dsynt):
    if "noun" in eu.getAttribute(dsynt, "class"):
        with open(os.path.join(os.getcwd(), "data", "male_names.txt")) as f:
            male_names = f.read().split("\n")
        with open(os.path.join(os.getcwd(), "data", "female_names.txt")) as f:
            female_names = f.read().split("\n")

        masc = ["his", "he", "hisself", "him", "himself"]
        fem = ["her", "she", "herself", "herself"]
        curr_lex = eu.getAttribute(dsynt, "lexeme")
        ref = eu.getAttribute(dsynt, "ref")
        if curr_lex in fem or curr_lex.upper() in female_names:
            eu.setAttribute(dsynt, "gender", "fem")
            if ref != "nil":
                root_node = eu.getRoot(dsynt)
                nodes = root_node.xpath(".//dsyntnode[@ref='" + ref + "']")
                for node in nodes:
                    eu.setAttribute(node, "gender", "fem")
        #fixme - removed or convertPro(dsynt), need to test if this works
        elif curr_lex in masc or curr_lex.upper() in male_names:
            eu.setAttribute(dsynt, "gender", "masc")
            if ref != "nil":
                root_node = eu.getRoot(dsynt)
                nodes = root_node.xpath(".//dsyntnode[@ref='" + ref + "']")
                for node in nodes:
                    eu.setAttribute(node, "gender", "masc")
        else:
            if ref != "nil" and eu.hasAttribute(dsynt, "gender"):
                return
            eu.setAttribute(dsynt, "gender", "neut")

# todo need to add other punctuation
def convertPunct(dsynt):
    if eu.getAttribute(dsynt, "class") == "symbol":
        #realpro will add a . by default
        if eu.getAttribute(dsynt, "lexeme") == ".":
            eu.delElement(dsynt, True)
        elif eu.getAttribute(dsynt, "lexeme") == ",":
            curr_id = eu.getAttribute(dsynt, "id")
            root = eu.getRoot(dsynt)
            next_node = root.xpath(".//*[@id='"+str(int(curr_id)+1)+"']")
            if len(next_node) > 0:
                eu.addElement(next_node[0], dsynt)

def convertPosition(dsynt):
    """
    :param dsynt:
    :return:
    for adverbs mostly
    sent-initial (starting_point = +)
    pre-verbal
    post-verbal
    sent-final (rheme = +)
    """
    if eu.getAttribute(dsynt, "class") == "adverb":
        root = eu.getRoot(dsynt)
        curr_id = int(eu.getAttribute(dsynt, "id"))

        par = dsynt.getparent()
        while par != None:
            if eu.getAttribute(par, "class") == "verb":
                break
            par = par.getparent()
        if par is None:
            grandparent = dsynt.getparent()
            if grandparent is not None:
                par_siblings = grandparent.getchildren()
                for par_sibling in par_siblings:
                    if eu.getAttribute(par_sibling, "class") == "verb":
                        par = par_sibling
                        break
        if par is None:
            prev = root.xpath(".//dsyntnode[@id='" + str(curr_id + 1) + "']")
            next = root.xpath(".//dsyntnode[@id='" + str(curr_id - 1) + "']")
            if len(prev) > 0 and eu.getAttribute(prev[0], "class") == "verb":
                eu.setAttribute(dsynt, "position", "pre-verbal")
            elif len(next) > 0 and eu.getAttribute(next[0], "class") == "verb":
                eu.setAttribute(dsynt, "position", "post-verbal")
            elif curr_id == 1:
                eu.setAttribute(dsynt, "position", "sent-initial")
            elif curr_id == len(root.xpath(".//dsyntnode")):
                eu.setAttribute(dsynt, "position", "sent-final")
        else:
            par_id = int(eu.getAttribute(par, "id"))
            if par_id - curr_id > 0:
                eu.setAttribute(dsynt, "position", "pre-verbal")
            elif par_id - curr_id < 0:
                eu.setAttribute(dsynt, "position", "post-verbal")
            elif curr_id == 1:
                eu.setAttribute(dsynt, "position", "sent-initial")
            elif curr_id == len(root.xpath(".//dsyntnode")):
                eu.setAttribute(dsynt, "position", "sent-final")

def convertMood(dsynt):
    """(default) ind: likes
        cond: would like (never seen)
        imp (never seen)
        inf: like
        inf-to: to like
        pres-part (never seen)
        past-part (never seen)"""
    if eu.getAttribute(dsynt, "lexeme") == "to":
        root = eu.getRoot(dsynt)
        curr_id = int(eu.getAttribute(dsynt, "id"))
        prev = root.xpath(".//dsyntnode[@id='" + str(curr_id + 1) + "']")
        if len(prev) > 0 and eu.getAttribute(prev[0], "class") == "verb":
            eu.setAttribute(prev[0], "mood", "inf-to")
            par = prev[0].getparent()
            if eu.getAttribute(par, "class") == "preposition":
                grandparent = par.getparent()
                if grandparent is not None:
                    for sibling in grandparent.getchildren():
                        eu.addElement(grandparent, sibling)
                    eu.delElement(par, True)
            eu.delElement(dsynt, True)
    else:
        if eu.getAttribute(dsynt, "class") == "verb" and not eu.hasAttribute(dsynt, "mood"):
            with open(os.path.join(os.getcwd(), "data", "en-verbs.csv")) as f:
                verbs = f.read().split("\n")

            inf_verbs = {verb.split(",")[0] for verb in verbs}
            ind_verbs = {verb.split(",")[1]:verb.split(",")[0] for verb in verbs if len(verb.split(",")) > 1}
            curr_lex = eu.getAttribute(dsynt, "lexeme")
            root = eu.getRoot(dsynt)
            curr_id = int(eu.getAttribute(dsynt, "id"))
            prev = root.xpath(".//*[@id='" + str(curr_id - 1) + "']")

            if len(prev) > 0 and eu.getAttribute(prev[0], "class") == "verb" and eu.getAttribute(prev[0], "lexeme") in ["would"]:
                par = prev[0].getparent()
                rel = eu.getAttribute(prev[0], "rel")
                eu.setAttribute(dsynt, "mood", "cond")
                eu.setAttribute(dsynt, "rel", rel)

                new_dsynt = copy.deepcopy(dsynt)
                eu.delElement(dsynt)
                dsynt = new_dsynt

                children = prev[0].getchildren()

                eu.delElement(prev[0], True)

                eu.addElement(par, dsynt)
                for child in children:
                    eu.addElement(dsynt, child)

            # FIXME this needs to be fixed somehow, totally unpredictable when have will be has
            elif curr_lex in ["is", "has"]:
                eu.setAttribute(dsynt, "mood", "imp")
            elif curr_lex in inf_verbs:
                eu.setAttribute(dsynt, "mood", "inf")
            else:
                eu.setAttribute(dsynt, "mood", "ind")
                if curr_lex in ind_verbs:
                    eu.setAttribute(dsynt, "lexeme", ind_verbs[curr_lex])

def convertPolarity(dsynt):
    #Note that I believe it's possible for adj and adv to share this functionality, though not in our data
    if eu.getAttribute(dsynt, "lexeme") == "not" and len(dsynt.getchildren()) == 0:
        par = dsynt.getparent()
        if eu.getAttribute(par, "class") == "verb":
            do_verb = None
            tense = "pres"
            for child in par.getchildren():
                child_lex = eu.getAttribute(child, "lexeme")
                if child_lex in ["did", "do"] and len(child.getchildren()) == 0:
                    if child_lex == "did":
                        tense = "past"
                    do_verb = child
                    break
            if do_verb is not None:
                eu.setAttribute(par, "tense", tense)
                eu.setAttribute(par, "polarity", "neg")
                eu.delElement(dsynt, True)
                eu.delElement(do_verb, True)

def convertSpecialCases(dsynt):
    if eu.getAttribute(dsynt, "lexeme") == "order":
        par = dsynt.getparent()
        if eu.getAttribute(par, "lexeme") == "in":
            eu.setAttribute(par, "lexeme", "in_order")
            eu.delElement(dsynt, True)
    in_node = None
    due_node = None
    if eu.getAttribute(dsynt, "lexeme") == "course":
        for child in dsynt.getchildren():
            if eu.getAttribute(child, "lexeme") == "in":
                in_node = child
            elif eu.getAttribute(child, "lexeme") == "due":
                due_node = child
            if in_node is not None and due_node is not None:
                eu.setAttribute(dsynt, "lexeme", "in due course")
                eu.setAttribute(dsynt, "class", "adverb")
                eu.delElement(in_node, True)
                eu.delElement(due_node, True)
                break

#todo enhance for when compound is not reliable, such as 'comic books'
def convertCompound(dsynt):
    if eu.hasAttribute(dsynt, "compound"):
        #FIXME XXX
        # print(eu.getAttribute(dsynt, "lexeme"))
        par = dsynt.getparent()
        if par is not None:
            # FIXME XXX
            # print("in the if one")
            if eu.hasAttribute(par, "compound") or (eu.getAttribute(par, "id") == eu.getAttribute(dsynt, "compound")):
                # FIXME XXX
                # print("the first if")
                eu.setAttribute(dsynt, "rel", "ATTR")
                if "noun" in eu.getAttribute(par, "class") and "noun" not in eu.getAttribute(dsynt, "class"):
                    # FIXME XXX
                    # print("the second if")
                    eu.setAttribute(dsynt, "class", eu.getAttribute(par, "class"))
            else:
                # FIXME XXX
                # print("the first else")
                #TODO check if this needs to account for the id number/location
                if eu.getAttribute(dsynt, "rel") == "ATTR":
                    # FIXME XXX
                    # print("the if in the else")
                    root = eu.getRoot(dsynt)
                    comp_node = root.xpath(".//*[@id='" + eu.getAttribute(dsynt, "compound") + "']")[0]

                    new_element = copy.deepcopy(dsynt)
                    eu.delElement(dsynt)
                    eu.addElement(comp_node, new_element)

            # elif eu.getAttribute(dsynt, "compound"):
            #     new_par = eu.getRoot(dsynt).xpath(".//*[@id='" + eu.getAttribute(dsynt, "compound") + "']")[0]
            #     eu.setAttribute(dsynt, "rel", "ATTR")
            #     eu.addElement(new_par, dsynt)
            #     if "noun" in eu.getAttribute(new_par, "class") and "noun" not in eu.getAttribute(dsynt, "class"):
            #         eu.setAttribute(dsynt, "class", eu.getAttribute(new_par, "class"))
    elif eu.hasAttribute(dsynt, "compound") and False == True:
        root = eu.getRoot(dsynt)
        comp_nodes = root.xpath(".//*[@id='" + eu.getAttribute(dsynt, "compound") + "']")
        comp_nodes += [dsynt]
        comp_nodes = sorted(comp_nodes, key=lambda x: int(eu.getAttribute(x, "id")))
        if len(comp_nodes) > 0:
            root_comp_lex = "_".join([eu.getAttribute(l, "lexeme") for l in comp_nodes])
            root_comp = comp_nodes[0]
            eu.setAttribute(root_comp, "lexeme", root_comp_lex)
            for x, c in enumerate(comp_nodes):
                if x == 0:
                    continue
                eu.delElement(c, True)
    elif eu.getAttribute(dsynt, "class") == "preposition":
        children = dsynt.getchildren()
        if eu.hasAttribute(dsynt, "id") and len(children) == 1 and eu.getAttribute(children[0], "class") == "preposition":
            curr_id = int(eu.getAttribute(dsynt, "id"))
            child_id = int(eu.getAttribute(children[0], "id"))
            #TODO test this, is this only needed for sequential cases?
            if abs(curr_id - child_id) == 1:
                child_lex = eu.getAttribute(children[0], "lexeme")
                eu.setAttribute(dsynt, "lexeme", eu.getAttribute(dsynt, "lexeme") + "_" + child_lex)
                eu.delElement(dsynt.getchildren()[0], True)

def convertAspect(dsynt):
    if eu.getAttribute(dsynt, "class") == "verb":
        with open(os.path.join(os.getcwd(), "data", "en-verbs.csv")) as f:
            verbs = f.read().split("\n")

        cont_verbs = {verb.split(",")[2]: verb.split(",")[0] for verb in verbs if len(verb.split(",")) > 2}
        curr_lex = eu.getAttribute(dsynt, "lexeme")
        if curr_lex in cont_verbs:
            eu.setAttribute(dsynt, "aspect", "cont")
        else:
            eu.setAttribute(dsynt, "aspect", "simple")

# todo low priority actually
def convertExtrapo(dsynt):
    pass

# todo low priority actually
def convertCaps(dsynt):
    pass

# todo low priority actually
def convertTaxis(dsynt):
    pass

def stripDefaults(dsynt):
    defaults = {"tense":"pres", "number":"sg",
                "gender":"masc", "case":"nom",
                "form":"arabic", "voice":"act",
                "aspect":"simple", "mood":"ind",
                "polarity":"nil", "question":"-",
                "extrapo":"-"}
    for k,v in defaults.items():
        if eu.getAttribute(dsynt, k) == v:
            eu.delAttribute(dsynt, k)
    for attrib in dsynt.attrib:
        if eu.getAttribute(dsynt, attrib) == "":
            eu.delAttribute(dsynt, attrib)

def stripExtraAttrs(dsynt):
    dsynt_attributes = ["class", "tense", "number", "lexeme", "voice", "number", "pro", "person", "form",
                        "article", "rel", "gender", "position", "mood", "polarity", "punct"]
    if eu.getTag(dsynt) == "dsynts":
        dsynt_attributes.append("id")
    del_attribs = [attrib for attrib in dsynt.attrib if attrib not in dsynt_attributes]
    for del_attrib in del_attribs:
        eu.delAttribute(dsynt, del_attrib)

def stripKillNodes(dsynt_parse):
    for dsynt in dsynt_parse.xpath(".//dsyntnode[@kill='true']"):
        eu.delElement(dsynt)

def zipDepAndConst(dsynt_parse, const_parse):
    dep_dict = {}
    for depnode in dsynt_parse.xpath(".//depnode"):
        curr_id = eu.getAttribute(depnode, "id")
        if curr_id == "0":
            continue
        const_node = const_parse.xpath(".//*[@id='"+curr_id+"']")[0]
        dep_dict[const_node] = depnode
    return dep_dict

def adjustIdNumbers(dsynt_parse):
    dsynt_list = sorted(dsynt_parse.xpath(".//dsyntnode"), key=lambda x: int(eu.getAttribute(x, "id")))
    for x, dsynt in enumerate(dsynt_list):
        eu.setAttribute(dsynt, "id", str(x))

def findBestMatch(ref_node, can_nodes):
    stats = {}
    for can_node in can_nodes:
        stats[can_node] = 0
        for attrib in ref_node.attrib:
            if eu.getAttribute(ref_node, attrib).lower() == eu.getAttribute(can_node, attrib).lower():
                stats[can_node] += 1
    return max(stats, key=stats.get)

def compareDsynts():
    #TODO this needs to write to a file once there is a dev case
    gold_dir = os.listdir(os.path.join("data", "gen", "gold"))
    gen_dir = os.listdir(os.path.join("data", "gen", "test"))
    for index, file in enumerate(gold_dir):
        gold_dsynts = eu.createFromXML(os.path.join(os.getcwd(), "data", "gen", "gold", file))
        gen_dsynts = eu.createFromXML(os.path.join(os.getcwd(), "data", "gen", "test", gen_dir[index]))

        with open(os.path.join(os.getcwd(), "data", "gen", "comp", str(file.split(".")[0])+".txt"), "w") as comp_file:
            gold_dsynts = gold_dsynts.xpath("dsynts")
            gen_dsynts = gen_dsynts.xpath("dsynts")
            total_errors = {"lexeme":0, "number":0, "class":0, "gender":0, "article":0, "form":0, "rel":0,
            "pro":0, "tense":0, "voice":0, "mood":0, "question":0, "person":0, "position":0,
            "case":0, "aspect":0, "polarity":0, "extrapo":0, "caps":0, "punct":0}

            if len(gold_dsynts) == len(gen_dsynts):
                for x in range(0, len(gold_dsynts)):
                    gold_nodes = gold_dsynts[x].xpath(".//dsyntnode")
                    comp_file.write("SENTENCE %s:\n" % x)
                    z = len(gold_nodes)
                    y = len(gen_dsynts[x].xpath(".//dsyntnode"))
                    if z != y:
                        comp_file.write("MISMATCH IN #OF NODES GOLD:%s GEN:%s\n" % (z, y))
                    for line,curr_gold_node in enumerate(gold_nodes):
                        comp_file.write("LINE %s:\n" % line)
                        curr_lex = eu.getAttribute(curr_gold_node, "lexeme")
                        can_nodes = gen_dsynts[x].xpath(".//dsyntnode[@lexeme='" + curr_lex + "']")
                        stripDefaults(curr_gold_node)
                        stripExtraAttrs(curr_gold_node)
                        if len(can_nodes) == 0:
                            comp_file.write("Mismatch in file %s for lexeme attribute. #Gold=%s\n" % (
                                file, curr_lex))
                            total_errors["lexeme"] += 1
                            continue
                        elif len(can_nodes) > 1:
                            can_node = findBestMatch(curr_gold_node, can_nodes)
                        else:
                            can_node = can_nodes[0]
                        for attrib in curr_gold_node.attrib:
                            if eu.getAttribute(curr_gold_node, attrib).lower() != eu.getAttribute(can_node, attrib).lower():
                                comp_file.write("Mismatch in file %s for attrib %s in line #%s (lexeme = %s), Gold: %s, Test: %s\n"%
                                      (file, attrib, line, eu.getAttribute(can_node, "lexeme"), eu.getAttribute(curr_gold_node, attrib), eu.getAttribute(can_node, attrib)))
                                total_errors[attrib] += 1
            else:
                comp_file.write("When comparing Dsynts file %s did not have the same number of nodes. #Gold=%s , #Test=%s\n" % (
                file, len(gold_dsynts), len(gen_dsynts)))

            comp_file.write("ANALYTICS (MISMATCH PER ATTRIBUTE):\n")
            comp_file.write("\n".join([str(k)+":"+str(v) for k,v in total_errors.items()]))

def compareText(ignore_special_chars=True):
    gold_dir = os.listdir(os.path.join("data", "gen", "gold_out"))
    gen_dir = os.listdir(os.path.join("data", "gen", "test_out"))
    for index, file in enumerate(gen_dir):
        if file not in gold_dir:
            print("WARNING: I could not find a gold file for " + file + " . Make sure the name is the same please. "
                                                                        "This file has been skipped for comparison.")
            continue

        with open(os.path.join(os.getcwd(), "data", "gen", "gold_out", file)) as f:
            gold_text = f.read()
        with open(os.path.join(os.getcwd(), "data", "gen", "test_out", file)) as f:
            gen_text = f.read()

        with open(os.path.join(os.getcwd(), "data", "gen", "comp_out", file), "w") as comp_file:
            if ignore_special_chars:
                gold_text = re.sub(r'[^\w\s\.,!\?]', '', gold_text)
                gen_text = re.sub(r'[^\w\s\.,!\?]', '', gen_text)

            gold_samples = gold_text.split("\n")
            gen_samples = gen_text.split("\n")
            total_bleu = 0
            total_sents = 0
            if len(gold_samples) != len(gen_samples):
                comp_file.write(
                    "When comparing surface text file %s did not have the same number of samples. #Gold=%s , #Test=%s\n" % (
                        file, len(gold_samples), len(gen_samples)))
                comp_file.write("GOLD: " + gold_text + "\n")
                comp_file.write("GEN: " + gen_text + "\n")
            for sample in range(0, len(gold_samples)):
                comp_file.write("========================================================\n")
                comp_file.write("SAMPLE: %s \n" % str(sample))

                gold_text = gold_samples[sample]
                gen_text = gen_samples[sample]

                gold_sents = nltk.tokenize.sent_tokenize(gold_text)
                gen_sents = nltk.tokenize.sent_tokenize(gen_text)
                total_sents += len(gold_sents)

                if len(gold_sents) != len(gen_sents):
                    comp_file.write("When comparing surface text file %s did not have the same number of sentences. #Gold=%s , #Test=%s\n" % (
                    file, len(gold_sents), len(gen_sents)))
                    comp_file.write("GOLD: " + gold_text+"\n")
                    comp_file.write("GEN: " + gen_text+"\n")
                else:
                    for x in range(0, len(gold_sents)):
                        comp_file.write("-------------------------------------------------------------------\n")
                        comp_file.write("SENTENCE: %s \n"%str(x))
                        gold_text = gold_sents[x].replace("\n"," ")
                        gen_text = gen_sents[x].replace("\n"," ")
                        gold_text = re.sub(r" ( )+", " ", gold_text)
                        gen_text = re.sub(r" ( )+", " ", gen_text)
                        bleu_score = sentenceScore(gold_text, gen_text)
                        comp_file.write("GOLD: " + gold_text+"\n")
                        comp_file.write("GEN: " + gen_text+"\n")
                        comp_file.write("OVERLAP: " + str(bleu_score)+"\n")
                        total_bleu += bleu_score
            comp_file.write("AVERAGE OVERLAP: " + str(total_bleu/total_sents) + "\n")

def sentenceMisMatchVector(gold_text, gen_text, ignore_special_chars=True):
    if ignore_special_chars:
        gold_text = re.sub(r'[^\w\s\.,!\?]', '', gold_text)
        gen_text = re.sub(r'[^\w\s\.,!\?]', '', gen_text)
    gold_text = re.sub(r" ( )+", " ", gold_text)
    gen_text = re.sub(r" ( )+", " ", gen_text)
    word_vector = sentenceVector(gold_text, gen_text)
    return word_vector

def sentenceVector(gold, test):
    gold_tok = nltk.word_tokenize(gold)
    test_tok = nltk.word_tokenize(test)
    print(str(gold_tok))
    print(str(test_tok))
    word_vector = []
    for x, g in enumerate(gold_tok):
        if x < len(test_tok) and test_tok[x].lower() == g.lower():
            word_vector.append(1)
        else:
            word_vector.append(0)
    return word_vector

def sentenceScore(gold, test):
    gold_tok = nltk.word_tokenize(gold)
    test_tok = nltk.word_tokenize(test)
    score = 0
    for x, g in enumerate(gold_tok):
        if x < len(test_tok) and test_tok[x].lower() == g.lower():
            score += 1
    return score/len(gold_tok)

def test(comp_dsynts=True):
    if comp_dsynts:
        compareDsynts()
    compareText()

def isRomanNumeral(lexeme):
    romanNumeralPattern = re.compile("""
        ^                   # beginning of string
        M{0,4}              # thousands - 0 to 4 M's
        (CM|CD|D?C{0,3})    # hundreds - 900 (CM), 400 (CD), 0-300 (0 to 3 C's),
                            #            or 500-800 (D, followed by 0 to 3 C's)
        (XC|XL|L?X{0,3})    # tens - 90 (XC), 40 (XL), 0-30 (0 to 3 X's),
                            #        or 50-80 (L, followed by 0 to 3 X's)
        (IX|IV|V?I{0,3})    # ones - 9 (IX), 4 (IV), 0-3 (0 to 3 I's),
                            #        or 5-8 (V, followed by 0 to 3 I's)
        $                   # end of string
        """, re.VERBOSE)
    if not romanNumeralPattern.search(lexeme):
        return False
    return True

def getCurrentDsynt(dsynt):
    while eu.getTag(dsynt) != "dsynts":
        dsynt = dsynt.getparent()
    return dsynt

def cleanGold():
    # TODO this needs to write to a file once there is a dev case
    gold_dir = os.listdir(os.path.join("data", "gen", "gold"))
    for index, file in enumerate(gold_dir):
        gold_dsynts = eu.createFromXML(os.path.join(os.getcwd(), "data", "gen", "gold", file))
        tree = gold_dsynts
        gold_dsynts = gold_dsynts.xpath("dsynts")
        for x in range(0, len(gold_dsynts)):
            gold_nodes = gold_dsynts[x].xpath(".//dsyntnode")
            for line, curr_gold_node in enumerate(gold_nodes):
                stripDefaults(curr_gold_node)
                stripExtraAttrs(curr_gold_node)
        eu.writeTree(tree, os.path.join(os.getcwd(), "data", "gen", "gold", file))
#TODO these realpro classes:
"""
realpro params:
lexeme (done)
class (done)
number (done)
gender
article
form (done)
rel
pro (done)
tense (done)
voice (done)
mood
question
person (done)
position

case (low-priority)
aspect (low-priority)
polarity (low-priority)
extrapo (low-priority)
caps (low-priority)
punct (low-priority)

m2d params:
wordnet id
ref
"""


"""
Realpro open class POS:
# adjective small, disastrous
# adverb really, maybe, surprisingly
# common_noun table, map
# proper_noun John, Poona, Socks
# verb disintegrate, indulge
# symbol
Realpro closed class POS:
article those, the, a
coordinating_conj AND, BUT, OR
(NEVER SEEN IN OUR DATA) demonstrative_pronoun THIS, THAT, THESE, THOSE
numeral TWELVE
particle not
(NEVER SEEN IN OUR DATA) indefinite_pronoun ANYTHING
preposition ABOUT
(NEVER SEEN IN OUR DATA) quantifier ALL
(NEVER SEEN IN OUR DATA) subordinating_conj IF

Stanford POS:
http://www.comp.leeds.ac.uk/amalgam/tagsets/upenn.html
CC Coordinating conjunction
CD Cardinal number
DT Determiner
EX Existential there
FW Foreign word
IN Preposition or subordinating conjunction
JJ Adjective
JJR Adjective, comparative
JJS Adjective, superlative
LS List item marker
MD Modal
NN Noun, singular or mass
NNS Noun, plural
NNP Proper noun, singular
NNPS Proper noun, plural
PDT Predeterminer
POS Possessive ending
PRP Personal pronoun
PRP$ Possessive pronoun
RB Adverb
RBR Adverb, comparative
RBS Adverb, superlative
RP Particle
SYM Symbol
TO to
UH Interjection
VB Verb, base form
VBD Verb, past tense
VBG Verb, gerund or present participle
VBN Verb, past participle
VBP Verb, non­3rd person singular present
VBZ Verb, 3rd person singular present
WDT Wh­determiner
WP Wh­pronoun
WP$ Possessive wh­pronoun
WRB Wh­adverb
"""

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

def clusterFile():
    for file in os.listdir(os.path.join(os.getcwd(), "data", "gen", "input")):
        with open(os.path.join(os.getcwd(), "data", "gen", "input", file)) as f:
            file_txt_lines = f.read().split("\n")

        file_txt_lines = list(chunks(file_txt_lines, 5))
        for x, file_txt in enumerate(file_txt_lines):
            with open(os.path.join(os.getcwd(), "data", "gen", "input", file.split(".")[0]+"_batch_"+str(x)), "w") as batch_file:
                batch_file.write("\n".join(file_txt))

if __name__ == '__main__':
    # clusterFile()
    lang_check = language_check.LanguageTool('en-US')
    # cleanGold()
    # main(False, True, True, False)
    # test(False)
    main(False, True)

