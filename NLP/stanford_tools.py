from pycorenlp import StanfordCoreNLP
import subprocess
import os
import time
import element_utils as eu
import re
from nltk.corpus import stopwords
from collections import defaultdict
import multiprocessing
import shutil
from config import STANFORD_PARSER_HOME
import requests
import copy
try:
    import gkg_ner
except:
    pass
from itertools import groupby

# sys.path.append(os.path.join(os.getcwd(), "m2d", "py_scripts"))
# import m2d.py_scripts.content_planner

# server_url = 'http://localhost:9000/?properties={"annotators":"pos,parse,depparse,dcoref,ner,sentiment","outputFormat":"xml"}'
server_url = 'http://localhost:9000'
global nlp
s_vers = None
global stop

#FIXME test GKG offset!!!!!!!

def has_server_setup(server_url):
    '''
    Check whether the server is already started, if it is, don't keep trying.
    :return:
    '''
    try:
        with requests.session() as req_session:
            req_session.get(server_url)
            return True
    except requests.exceptions.ConnectionError:
        pass
    return False

#TODO catch the case when it doesn't load correctly
def start_server(port=9000, timeout=4000):
    """
    Starts the server in a seperate terminal session. Only currently works with windows,
    need to add mac and linux (I guess?) support
    :param port: default port for Stanford Server is 9000
    :return:
    """
    # Use this absolute directory, so that it won't cause problem when stanford_tools is calling from other sub dir of the project.
    if not os.path.exists(STANFORD_PARSER_HOME):
        print("You don't have all of the stanford corenlp (3.7.0) source files in the proper place. Terminating.")
        exit()

    if not os.path.exists(os.path.join(STANFORD_PARSER_HOME,"stanford-corenlp-3.7.0-models.jar")):
        jarStanfordSource()

    stanford_dir = STANFORD_PARSER_HOME
    os.chdir(stanford_dir)
    if os.name == "nt":
        corenlp_cmdline = 'start java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer ' \
        '-preload tokenize, ssplit, pos, lemma, ner, parse, mention, depparse, dcoref, ner, sentiment, natlog, openie' \
        ' -timeout %s' \
        ' -port %s "\'' % (timeout, port)
        subprocess.call(corenlp_cmdline, shell=True)
    elif os.name == "posix":
        #pass
        # SORABY: changed this to cd into stanford_dir that we constructed above (original line commented below)
        #corenlp_cmdline = 'osascript -e \'tell application "Terminal" to do script "cd Desktop/dialogue_systems/stanford/stanford-corenlp-full-2015-12-09;java -mx4g -cp \\"*\\" edu.stanford.nlp.pipeline.StanfordCoreNLPServer"\''
        corenlp_cmdline = 'osascript -e \'tell application "Terminal" to do script "cd %s;' \
                          'java -mx4g -cp \\"*\\" edu.stanford.nlp.pipeline.StanfordCoreNLPServer ' \
                          ' -preload tokenize,ssplit,pos,lemma,ner,parse,mention,depparse,dcoref,ner,sentiment,natlog,openie ' \
                          ' -timeout %s' \
                          ' -port %s"\'' % (stanford_dir, timeout, port)
        # print(corenlp_cmdline)
        #corenlp_cmdline = 'open -a Terminal "`pwd`"; sleep 10; java -mx1000m -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer'
        subprocess.call(corenlp_cmdline, shell=True)
        #with tempfile.NamedTemporaryFile(suffix='.command') as f:
         #   f.write('#!/bin/sh\njava -mx1000m -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer\n')
          #  subprocess.call(['open', '-W', f.name])
    elif os.name == "mac":
        return False
        # Who even uses linux anyways?
    else:
        return False

def init_client(server_url):
    global nlp
    nlp = StanfordCoreNLP(server_url)
    return nlp

def check_tools():
    """
        Loads Stanford tools on server. This is all the annotators for use:
        quote, natlog, relation, dcoref, depparse, parse, truecase, sentiment, regexner, ner,
        lemma, pos, ssplit, cleanxml, tokenize
        http://stanfordnlp.github.io/CoreNLP/annotators.html
        :return:
            annotators broken up to make loading easier
        """
    # java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000
    # -preload tokenize,ssplit,pos,lemma,ner,parse,mention,depparse,dcoref,ner,sentiment
    # Now we preload the annotation in command, double confirm that the models are loaded
    # print("Check models.")
    nlp.annotate("load models", properties={
        'annotators': 'pos,parse,depparse,dcoref,ner,sentiment'
    })
    # print("Models are loaded.")

def init(server_url = 'http://localhost:9000', max_wait_for_server=600):
    """
    init, try to load tool, excecpt if server is not started start it, then load tools.
    The check_tools won't throw errors is the Stanford is fully start at the background.
    :param max_wait_for_server: Give up in max_wait_for_server seconds
    :return:
    """
    global stop
    stop = set(stopwords.words('english'))

    if not has_server_setup(server_url):
        p1 = multiprocessing.Process(target=start_server, name="start_server")
        p1.start()
        # Stanford could start within 30 seconds.
        count = 0
        while not has_server_setup(server_url):
            time.sleep(1)
            count += 1
            if count > 120:
                print("Warning: Couldn't start Stanford within " + str(120) + " second")
            if count > max_wait_for_server:
                raise Exception("Error: Couldn't start Stanford within " + str(max_wait_for_server) + " second")
        # Annotator works only after standford is fully started and listen to 9000.
        init_client(server_url)
        check_tools()
    else:
        init_client(server_url)

def correctText(text):
    text = re.sub(r" '", "'", text)
    return text

def dummyTree(speaker):
    #FIXME sentiment_value = 3 is Neutral?
    sub_root = eu.createNewElement("depnode", ("id", "0"), ("speaker", str(speaker.id)),
                                   ("sentiment_value","3"), ("sentiment","Neutral"), ("lexeme", "ROOT"))
    final_parse = putIntoDepTree([sub_root])
    return final_parse


def parse_sentences(text_list, speaker, full=True, num_new=None, expected_entities=None, core=None):
    p_list = []
    for text in text_list:
        p_list += parseSentence(text, speaker, full, num_new, expected_entities, core)
    return p_list


#FIXME this should be able to indicate which sentences don't require reprocessing for coref res with the GKG
def parseSentence(text, speaker, full=True, num_new=None, expected_entities=None, core=None, gcc=None, both=False):
    """
    :return:
        Dummy Parse function
    """
    #TODO replace this with slug_utils check/call for exisiting crawler
    if expected_entities != None and len(expected_entities) > 0:
        expected_entities = deleteListDuplicates(expected_entities)
    t = time.time()
    this = annotateText(text, "pos, parse, depparse, dcoref, ner, sentiment, openie", "xml").encode()
    text = correctSyntax(text)

    try:
        es = eu.createFromString(bytes(this))
    except:
        #FIXME put this into a log
        print(this)
        # print("Woah there cowboy, you tried to say '" + text + " ', which crashed. Probably this sentence has a lot of characters? Check the server log.")
        return []
    # eu.dumpElements(es)
    # print("===============================================")
    sentences = eu.getAllElement(es, "sentences")
    dep_trees = []
    parses = []

    if type(speaker) is not list:
        speaker = [speaker]*(len(sentences))

    ss_diff = len(sentences) - len(speaker)
    if ss_diff < 0 :
        print("ERROR: You've added more speakers than sentences!")
        return []

    elif ss_diff > 0:
        speaker += [speaker[-1]]*ss_diff


    #for weird error with empty tag a try except....
    try:

        for x, sentence in enumerate(sentences):
            sent_score = eu.getAttribute(sentence, "sentimentValue")
            sent_class = eu.getAttribute(sentence, "sentiment")
            p = eu.getElement(sentence, "parse")

            parse_string = eu.stringify_children(p)
            parse = convertParseToXML(parse_string)
            addidToParse(parse)
            parses.append(eu.convertToEtree(eu.convertToEtree(parse).getroot()))

            g = sentence.xpath(".//dependencies[@type='enhanced-plus-plus-dependencies']")[0]
            d = g.xpath(".//dep")
            dep_parse = convertDepParseToXML(d)

            if dep_parse is False:
                g = sentence.xpath(".//dependencies[@type='basic-dependencies']")[0]
                d = g.xpath(".//dep")
                dep_parse = convertDepParseToXML(d)

            triples = sentence.xpath(".//openie/triple")
            addOpenie(dep_parse, triples, x)
            pos_tokens = eu.getAllElement(sentence, "tokens")
            addPosTag(pos_tokens, dep_parse)
            #FIXME coref should probably be brought out on it's own somehow....
            unknownNameAssigner(dep_parse)
            dep_parse = eu.convertToEtree(dep_parse)
            dep_root = dep_parse.getroot()
            eu.addAttribute(dep_root, "sentiment_value", sent_score)
            eu.addAttribute(dep_root, "sentiment", sent_class)


            if type(speaker[x]) is str:
                s = speaker[x]
            else:
                s = str(speaker[x].id)

            eu.addAttribute(dep_root, "speaker", s)
            dep_trees.append(dep_parse)


        try:
            corefs = eu.getAllElement(es, "coreference")
        except:
            corefs = []
        corefStanford(text, corefs, speaker, dep_list=dep_trees)
        corefBasic(dep_trees, speaker)

        if expected_entities is not False:
            try:
                if num_new is not None:
                    gkg_ner.doGKGNER(text, parses[num_new:], dep_trees[num_new:], expected_entities, core, gcc)
                else:
                    gkg_ner.doGKGNER(text, parses, dep_trees, expected_entities, core, gcc)
            except:
                # import traceback
                # traceback.print_exc()
                pass

        corefCorrection(dep_trees, parses)
        if both:
            return dep_trees, parses
        elif full:
            return dep_trees
        return parses

    except:
        return []


def addOpenie(dep_parse, openie_triples, sent_id):
    oie_key = []
    for x, triple in enumerate(openie_triples):
        confidence = eu.getAttribute(triple, "confidence")
        triple_parts = [triple.xpath(".//"+part+"")[0] for part in ["subject", "relation", "object"]]
        temp_key = []
        for triple_part in triple_parts:
            bid = eu.getAttribute(triple_part, "begin")
            eid = eu.getAttribute(triple_part, "end")
            text = triple_part.xpath(".//text")[0].text

            # for did in range(int(bid), int(eid)):
                # curr_node = dep_parse.xpath(".//depnode[@id="+str(did)+"]")[0]
            temp_key.append(bid+":"+eid)
                # eu.addAttribute(curr_node, "oie", "True")
        temp_key = "-".join(temp_key)
        temp_key += "="+confidence
        oie_key.append(temp_key)
    oie_key = ";".join(oie_key)
    eu.addAttribute(dep_parse, "oie", oie_key)

def numNodes(root_node):
    """
    :param root_node: root node to iterate over
    :return: number of dsyntnode children
    """
    num_nodes = len(root_node.xpath(".//depnode"))
    return num_nodes

def addSentiment(token, curr_dep):
    try:
        sentiment = token.xpath(".//sentiment")[0].text
        eu.addAttribute(curr_dep, "sentiment", sentiment)
    except:
        pass

def addPosTag(pos_tokens, dep_parse, ner=True):
    for pos_token in pos_tokens:
        ptid = eu.getAttribute(pos_token, "id")
        curr_dep = eu.getRoot(dep_parse).xpath(".//depnode[@id="+ptid+"]")
        curr_dep = curr_dep[0]
        pos = pos_token.xpath(".//POS")[0].text
        eu.addAttribute(curr_dep, "pos", pos)
        addSentiment(pos_token, curr_dep)
        # if ner:
        #     ner = pos_token.xpath(".//NER")[0].text
        #     if ner != "O":
        #         eu.addAttribute(curr_dep, "ner", ner.title())

def convertParseToXML(parse_string):
    """
    :param parse_string: string text parse tree
    :return:
        root of parse tree
    """
    tree = None
    #preprocessing stanford output
    parse_string = re.sub(r"&#13;", "", parse_string)
    tag_stack = []
    for ps in parse_string.split("\n"):
        #preprocessing steps
        splits = ps[(len(ps) - len(ps.lstrip(" "))):].split(" ", 1)
        tag = splits[0].rstrip("\r")
        if len(splits) == 1:
            attribute = " "
        else:
            attribute = splits[1]
        attribute = attribute.rstrip("\r")
        tag = tag.lstrip("(")
        if tag in ["\n", " ", ""]:
            continue
        #cases like punct are under the SYMBOL class
        elif not tag.isalpha():
            tag = "SYMBOL"
        num_paren = ps.count("(") - ps.count(")")
        #This node indicates that it is the parent of the following nodes
        #since there is parens mismatch in favor of (
        if num_paren > 0:
            tag_stack.append(tag)
            node = createParseNode(tag, attribute)
            if tree is None:
                tree = node
                root = node
            else:
                eu.addElement(tree, node)
                tree = node
        #this is the case in which we are popping up a level in our dependencies
        elif num_paren < 0:
            # attribute = attribute[:-1]
            change_tag = False
            if attribute.count("(") == 0:
                attribute = attribute[:-1]
            elif not attribute.startswith("("):
                attribute = "("+tag+" "+attribute
                change_tag = True
            curr_tree = tree
            while num_paren <= -1:
                attribute = attribute[:-1]
                tree = tree.getparent()
                num_paren += 1
                tag_stack.pop()
            if change_tag:
                tag = curr_tree
                createParseNode(tag, attribute)
            else:
                node = createParseNode(tag, attribute)
                eu.addElement(curr_tree, node)

        #this is a standalone node with no children nodes
        else:
            tag_stack.append(tag)
            attribute = attribute[:-1]
            node = createParseNode(tag, attribute)
            if tree is None:
                tree = node
            else:
                eu.addElement(tree, node)
    return root

def createParseNode(tag, attribute):
    """
    :param tag: tag, generally elements like NP, VP, NN
    :param attribute: either list of nodes to be added, or lexeme, or nothing
    :return:
        root of parse tree
    """
    res = re.findall(r"\(.*?\)", attribute)
    attrs = []
    if attribute != " ":
        attrs.append(("lexeme", attribute))
    if type(tag) is str:
        if tag.endswith("$"):
            tag = tag.rstrip("$")
            attrs.append(("possessive", "True"))
        node = eu.createNewElement(tag, attrs)
    else:
        node = tag
    addParseChildren(node, res)
    if len(res) > 0:
        eu.delAttribute(node, "lexeme")

    return node

def addParseChildren(node, nodes):
    """
    :param node: root node
    :param nodes: the nodes that are part of the root node:
        ex: (NP (JJ fat) (NN cat))
        NP = root node
        nodes = (JJ fat), (NN cat)
    :return:
    """
    x = 0

    for x, ns in enumerate(nodes):
        try:
            poss = False
            ns = ns[1:-1]
            tag, attribute = ns.split(" ", 1)
            if tag:
                if tag.endswith("$"):
                    poss = True
                    tag = tag.rstrip("$")
                elif not tag.isalpha():
                    tag = "SYMBOL"
                n = eu.createNewElement(tag, ("lexeme", attribute))
                if poss:
                    eu.addAttribute(n, "poss", "True")
                eu.addElement(node, n)
        except:
            # FIXME add log here.
            print("Something bad happened with the parse node for " + str(ns))
            pass

    return x

def convertDepParseToXML(dep_parse_xml):
    t = time.time()
    ids_done = {}

    for dep_node in dep_parse_xml:
        type = eu.getAttribute(dep_node, "type")
        gov, dep = dep_node.getchildren()
        gov_id = eu.getAttribute(gov, "idx")
        dep_id = eu.getAttribute(dep, "idx")
        if gov_id in ids_done.keys():
            gov_node = ids_done[gov_id]
        else:
            gov_node = eu.createNewElement("depnode", ("id", gov_id),("lexeme", gov.text))
            ids_done[gov_id] = gov_node

        if dep_id in ids_done.keys():
            dep_node = ids_done[dep_id]
            tsplit = type.split(":")
            eu.addAttribute(dep_node, tsplit[0], gov_id)
            addGovParent(dep_node, tsplit[0])
            for x in range(1, len(tsplit)):
                if "'" in tsplit[x]:
                    tsplit[x] = tsplit[x].replace("'", "")
                    eu.addAttribute(dep_node, "apos", "True")
                eu.addAttribute(dep_node, tsplit[x], gov_id)
                addGovParent(dep_node, tsplit[x])

        else:
            tsplit = type.split(":")
            dep_node = eu.createNewElement("depnode", ("id", dep_id),("lexeme", dep.text)
                                          ,(tsplit[0],gov_id))
            addGovParent(dep_node, tsplit[0])
            for x in range(1,len(tsplit)):
                eu.addAttribute(dep_node, tsplit[x], gov_id)
                addGovParent(dep_node, tsplit[x])
            ids_done[dep_id] = dep_node
        #FIXME.... This try except handles a wierd case
        try:
            par = dep_node.getparent()
            if par is not None:
                eu.addElement(par, gov_node)
            eu.addElement(gov_node, dep_node)
        except:
            # print("WARNING: The tree structure was so complex, we had to run simple deps not enhanced.")
            return False

    root = eu.convertToEtree(ids_done["0"]).getroot()

    return root

def addGovParent(dep_node, gov_type):
    if eu.hasAttribute(dep_node, "gov_type"):
        curr_gov = eu.getAttribute(dep_node, "gov_type")
        eu.setAttribute(dep_node, "gov_type", curr_gov + ";" + gov_type)
    else:
        eu.addAttribute(dep_node, "gov_type", gov_type)

def annotateText(text, annotators, outputFormat):
    """
    :param text:
    :param annotators:
        Possible args:
        'quote, natlog, relation, dcoref, depparse, parse, truecase, sentiment, regexner, ner, lemma, pos, ssplit, cleanxml, tokenize'
    :param outputFormat:
        Possible args:
    :return:
        api docs:
        http://stanfordnlp.github.io/CoreNLP/corenlp-server.html#api-documentation
    """
    if type(text) is bytes:
        text = text.decode("utf-8")

    return nlp.annotate(text, properties={
        'annotators': annotators,
        'outputFormat': outputFormat
    })

def corefStanford(text, corefs, speakers, dep_parse_single=None, dep_list=None):
    if dep_list is None:
        dep_list = [dep_parse_single]
    for x, dep_parse in enumerate(dep_list):
        prp_list = dep_parse.xpath('.//depnode[@pos="PRP$" or @ner="Person"]')
        for prp in prp_list:
            if not eu.hasAttribute(prp, "ref"):
                if eu.getAttribute(prp, "lexeme") == "your":
                    eu.addAttribute(prp, "ref", "$your$")
                    #TODO XXX this is maybe not needed
                    # eu.addAttribute(prp, "ner", "Person")
                else:
                    eu.addAttribute(prp, "ref", "???")
                eu.setAttribute(prp, "ref_type", "actors")
        #handles the I and My case
        actor_nodes = dep_parse.xpath('.//depnode[@lexeme="I" or @lexeme="my" or @lexeme="My" or @lexeme="Me" or @lexeme="me"]')
        for actor_node in actor_nodes:
            sid = speakers[x]
            if type(speakers[x]) is not str:
                sid = speakers[x].id
            eu.setAttribute(actor_node, "ref", str(sid))
            eu.setAttribute(actor_node, "ref_type", "actors")
            # TODO XXX this is maybe not needed
            # eu.addAttribute(actor_node, "ner", "Person")

    for x, coref in enumerate(corefs):
        ele_list = [c for c in coref.iter() if eu.getTag(c) == "text"]
        #The nodes in a given text set:
        text_list = [c.text for c in ele_list]
        # print(text_list)
        dep_nodes = []
        bias = []
        curr_refs = []
        skip_var = False
        for ele in ele_list:
            if ele.text.lower() in ["i", "my", "me"]:
                skip_var = True
                continue
            sent = int(ele.getparent().xpath(".//sentence")[0].text)
            cid = ele.getparent().xpath(".//start")[0].text
            eid = str(int(ele.getparent().xpath(".//end")[0].text) -1)

            """
                For some reason there is a case where stuff like 'My name' and 'my friend' or 'his friend'
                get lumped in by dcoref. Not sure how to use this parsed_data, doesn't seem very reliable. Catches
                cases where it's like 'a boat', we probably only want the 'boat' node, so drop DT.
            """
            curr_ids = []
            if int(eid) - int(cid) > 0:
                mid = cid
                while True:
                    if int(eid) - int(mid) == -1:
                        break
                    node = dep_list[sent-1].xpath(".//depnode[@id=" + str(mid) + "]")[0]
                    # if eu.hasAttribute(node, "ner"):
                    #     if "NN" in eu.getAttribute(node, "pos"):
                    #         curr_ids.append(mid)
                    # elif int(eid) - int(mid) == 0:
                    curr_ids.append(mid)
                    mid = int(mid) + 1
                else:
                    continue
            else:
                curr_ids.append(cid)
            for curr_id in curr_ids:
                curr_dep = dep_list[sent-1].xpath(".//depnode[@id=" + str(curr_id) + "]")[0]
                curr_ref = eu.getAttribute(curr_dep, "ref")
                cur_ref_type = "actors"
                if eu.getAttribute(curr_dep,"ref_type") == "objects":
                    cur_ref_type = "objects"

                if curr_ref != "???" and curr_ref != "nil":
                    bias.append(curr_ref)
                else:
                    bias.append(-1)
                dep_nodes.append(curr_dep)
        if skip_var is True:
            continue
        bias = deleteListDuplicates(bias)
        if bias.count(-1) > 0:
            bias.remove(-1)

        if len(bias) == 0:
            # new_ref = "$"+cur_ref_type[0]+"$" + str(x)
            new_ref = "$"+"a"+"$" + str(x)
        else:
            new_ref = bias[0]

        for dn in dep_nodes:
            eu.setAttribute(dn, "ref_type", cur_ref_type)
            eu.setAttribute(dn, "ref", new_ref)

def unknownNameAssigner(dep_parse):
    unknown_actors = dep_parse.xpath(".//depnode[@ref='???' and @ner='PERSON']")
    known_actors = dep_parse.xpath(".//depnode[@ref_type='actors' and @poss]")
    found_node = None
    for ka in known_actors:
        poss = eu.getAttribute(ka,"poss")
        parent_poss = dep_parse.xpath(".//depnode[@id="+poss+"]")[0]
        if parent_poss in unknown_actors:
            found_node = parent_poss
        elif eu.hasAttribute(parent_poss, "nsubj"):
            nsubj = eu.getAttribute(parent_poss, "nsubj")
            pp_poss = dep_parse.xpath(".//depnode[@id=" + nsubj + "]")[0]
            if pp_poss in unknown_actors:
                found_node = pp_poss
        if found_node is not None:
            curr_id = eu.getAttribute(ka, "ref")
            curr_type = eu.getAttribute(ka, "ref_type")
            eu.setAttribute(found_node, "ref", curr_id)
            eu.setAttribute(found_node, "ref_type", curr_type)
            unknown_actors.remove(found_node)

    for uk in unknown_actors:
        if eu.hasAttribute(uk, "compound"):
            comp_node = dep_parse.xpath(".//depnode[@id=" + eu.getAttribute(uk,"compound") + "]")[0]
            curr_id = eu.getAttribute(comp_node, "ref")
            curr_type = eu.getAttribute(comp_node, "ref_type")
            eu.setAttribute(uk, "ref", curr_id)
            eu.setAttribute(uk, "ref_type", curr_type)
        else:
            eu.setAttribute(uk, "ref_type", "actors")
            eu.setAttribute(uk, "ref", str(numNodes(eu.convertToEtree(uk).getroot())+int(eu.getAttribute(uk,"id"))))

def corefBasic(dep_trees, speakers):
    # FIXME this needs to hand the case of PRP "it" and noun references
    # FIXME handle NNP and NNPS
    """
    :param text:
    :param corefs:
    :param speaker:
    :param dep_parse:
    :return:
     NN = noun
     NNP = proper noun
     NNS = plural noun
     NNPS = plural proper noun
    """
    for x, dep_parse in enumerate(dep_trees):
        noun_list = dep_parse.xpath('.//depnode[(starts-with(@pos,"NN") and not(@ref)) or (starts-with(@pos,"PRP") and not(@ref))]')
        for x, noun in enumerate(noun_list):
            # r_type = "objects"

            r_type = "actors"
            if eu.getAttribute(noun, "lexeme") in ["you"]:
                r_type = "actors"
                # TODO XXX this is maybe not needed
                # eu.addAttribute(noun, "ner", "Person")
            if eu.getAttribute(noun, "pos").endswith("S"):
                eu.addAttribute(noun, "pl",str(1))
            eu.addAttribute(noun, "ref", "$"+r_type[0]+"$" + str((x+1) + eu.lenTreeObject(dep_parse, "depnode")))
            eu.addAttribute(noun, "ref_type", r_type)

def getEntityFromScore(dep_parse, ner, score):
    nodes = dep_parse.xpath(".//depnode[@"+ner+"='"+str(score)+"']")
    # nodes = listNodesInOrder(nodes)
    text = makeSentFromNodes(nodes)
    return text

def getStanfordNer(dep_parse):
    entities = []
    seen = []
    nodes = dep_parse.xpath('.//depnode[@ner and not(@gkg)]')
    for node in nodes:
        ner = eu.getAttribute(node, "ner")
        gkglex = eu.getAttribute(node, "lexeme")
        score = 0
        key = ner + ":" + str(score)
        if key not in seen:
            seen.append(key)
            entities.append((ner, float(score), gkglex))
    return entities

def getEntitiesForDB(dep_parse, keys=False):
    entities = []
    seen = []
    nodes = dep_parse.xpath('.//depnode[@ner and @gkg="True"]')
    for node in nodes:
        #FIXME xxx this is place one
        ner = eu.getAttribute(node, "ner")
        gkglex = eu.getAttribute(node, "gkglex")
        score = eu.getAttribute(node, ner)
        key = ner + ":" + score
        if key not in seen:
            seen.append(key)
            entities.append((ner, float(score), gkglex))
    if keys:
        return seen
    return entities

def makeSentFromNodes(dep_parse):
    if type(dep_parse) is not list:
        list_root = eu.getRoot(dep_parse, False)
        dep_roots = list_root.xpath(".//deps")
    else:
        dep_roots = dep_parse
    sents = []
    for dep_root in dep_roots:
        depnodes = listNodesInOrder(dep_root)
        curr_sent = ""
        for depnode in depnodes:
            if eu.getAttribute(depnode, "id") != "0":
                curr_sent += " " + eu.getAttribute(depnode, "lexeme")
        curr_sent = curr_sent.strip()
        curr_sent = curr_sent.replace(" 's", "'s")
        sents.append(curr_sent)
    return sents

def corefAddDetCorrection(dep_list):
    for dep_parse in dep_list:
        for candidate in dep_parse.xpath(".//depnode[@det]"):
            det = eu.getAttribute(candidate, "det")
            det_root = dep_parse.xpath(".//depnode[@id='" + det + "']")[0]
            ref = eu.getAttribute(det_root, "ref")
            ref_type = eu.getAttribute(det_root, "ref_type")
            if ref is not "nil":
                eu.setAttribute(candidate, "ref", ref)
                eu.setAttribute(candidate, "ref_type", ref_type)

def corefINCorrection(dep_list):
    for dep_parse in dep_list:
        candidates = dep_parse.xpath(".//depnode[@pos='IN']")
        for candidate in candidates:
            lex_IN = eu.getAttribute(candidate, "lexeme")
            try:
                node_IN = dep_parse.xpath(".//depnode[@"+lex_IN+"]")
            except:
                continue
            if len(node_IN) == 0:
                continue
            list_IN = dep_parse.xpath(".//depnode[@" + lex_IN + "]")
            if len(list_IN) == 0:
                continue
            node_IN = list_IN[0]
            id_IN = eu.getAttribute(node_IN, lex_IN)


            root_IN = dep_parse.xpath(".//depnode[@" + "id" + "='"+id_IN+"']")
            if len(root_IN) == 0:
                continue
            root_IN = root_IN[0]

            ref = eu.getAttribute(root_IN, "ref")
            ref_type = eu.getAttribute(root_IN, "ref_type")
            if ref != "nil":
                for r in root_IN.iter():
                    if eu.getAttribute(r, "lexeme") == lex_IN:
                        eu.setAttribute(r, "ref", ref)
                        eu.setAttribute(r, "ref_type", ref_type)

                old_ref = eu.getAttribute(node_IN, "ref")

                eu.setAttribute(node_IN, "ref", ref)
                eu.setAttribute(node_IN, "ref_type", ref_type)

                id_dict = {"minus":"-", "plus":"+"}

                id_minus = id_IN
                for mode in ["minus", "plus"]:
                    while True:
                        id_minus = str(eval(id_minus + id_dict[mode] + "1"))
                        node_minus = dep_parse.xpath(".//depnode[@id='" + id_minus + "']")
                        if len(node_minus) == 0:
                            break
                        node_minus = node_minus[0]
                        if eu.getAttribute(node_minus, "ref") == old_ref:
                            eu.setAttribute(node_minus, "ref", ref)
                            eu.setAttribute(node_minus, "ref_type", ref_type)
                        else:
                            break

def corefVerifyActorNER(dep_list):
    for y, dep_parse in enumerate(dep_list):
        candidates = dep_parse.xpath(".//depnode[@ref='1' or @ref='0']")
        for candidate in candidates:
            if not eu.hasAttribute(candidate, "ner"):
                pass
                # TODO XXX this is maybe not needed
                # eu.setAttribute(candidate, "ner", "Person")

def corefPossCorrection(dep_list):
    for y, dep_parse in enumerate(dep_list):
        candidates = dep_parse.xpath(".//depnode[@ref and @poss]")
        for x, candidate in enumerate(candidates):
            poss = eu.getAttribute(candidate, "poss")
            ref = eu.getAttribute(candidate, "ref")
            ref_type = eu.getAttribute(candidate, "ref_type")
            new_ref = ref + "." + str(y) + str(x)

            poss_root = dep_parse.xpath(".//depnode[@id='" + poss + "']")[0]
            eu.setAttribute(poss_root, "ref", new_ref)
            eu.setAttribute(poss_root, "ref_type", ref_type)

            # TODO test this functionality
            for poss_child in poss_root.getchildren():
                pos = eu.getAttribute(poss_child, "pos")
                if (pos.startswith("RB") or pos.startswith("JJ")) and poss_child is not candidate:
                    eu.setAttribute(poss_child, "ref", new_ref)
                    eu.setAttribute(poss_child, "ref_type", ref_type)

def corefCompoundCorrection(dep_list):
    for dep_parse in dep_list:
        candidates = dep_parse.xpath(".//depnode[@ref and @compound]")
        for x, candidate in enumerate(candidates):
            compound = eu.getAttribute(candidate, "compound")
            compound_root = dep_parse.xpath(".//depnode[@id='" + compound + "']")[0]
            ref = eu.getAttribute(compound_root, "ref")
            ref_type = eu.getAttribute(compound_root, "ref_type")
            if ref != "nil":
                eu.setAttribute(candidate, "ref", ref)
                eu.setAttribute(candidate, "ref_type", ref_type)

def corefGKGCorrection(dep_list):
    ref = 100
    for dep_parse in dep_list:
        keys = getEntitiesForDB(dep_parse)
        for key in keys:
            ner, score = key[0], key[1]
            nodes = dep_parse.xpath('.//depnode[@'+ner+'="'+str(score)+'"]')
            ref_to_replace = []
            for node in nodes:
                    r = eu.getAttribute(node, "ref")
                    if r != "nil":
                        ref_to_replace.append(r)
                    eu.setAttribute(node, "ref", "$a$"+str(ref))
                    eu.setAttribute(node, "ref_type", "actors")
            for r in ref_to_replace:
                r_nodes = dep_parse.xpath('.//depnode[@ref="'+r+'"]')
                for rn in r_nodes:
                    eu.setAttribute(rn, "ref", str(ref))
                    eu.setAttribute(rn, "ref_type", "actors")
            ref += 1

def corefPOSConstCorrection(dep_list, const_list):
    for x, dep in enumerate(dep_list):
        for d in dep.iter():
            if eu.hasAttribute(d, "ref"):
                if "NN" in eu.getAttribute(d, "pos") and not eu.hasAttribute(d, "gkg"):
                    curr_id = eu.getAttribute(d, "id")
                    const_node = const_list[x].xpath(".//*[@id="+str(int(curr_id)-1)+"]")
                    if len(const_node) == 0:
                        continue
                    const_node = const_node[0]
                    const_pos = eu.getTag(const_node)
                    if "NN" not in const_pos:
                        eu.setAttribute(d, "pos", const_pos)
                        eu.setAttribute(d, "const_pos", "True")
                        eu.delAttribute(d, "ref")
                        eu.delAttribute(d, "ref_type")

def corefCorrection(dep_list, const_list):
    corefPOSConstCorrection(dep_list, const_list)
    corefPossCorrection(dep_list)
    corefGKGCorrection(dep_list)
    corefAddDetCorrection(dep_list)
    corefINCorrection(dep_list)
    corefCompoundCorrection(dep_list)
    corefVerifyActorNER(dep_list)

def deleteListDuplicates(seq):
    """
    :param seq: list
    :return: list with no duplicates
    """
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def writeToFile(parse, filename):
    eu.writeTree(eu.convertToEtree(parse), filename)

def listNodesInOrder(dep_parse, root="dep"):
    node_list = []
    if type(dep_parse) is not list:
        dep_root = eu.getRoot(dep_parse)
        deps = dep_root.xpath(".//"+root+"s")
        if len(deps) == 0:
            deps = dep_root
        for dep in deps:
            # We need to use the "root" instead of "dep" which id = 0 because the .//depnode will ignore the root.
            node_list += sorted(eu.getRoot(dep).xpath(".//"+root+"node"), key=lambda x: int(eu.getAttribute(x, "id")))
            # node_list += sorted(dep.xpath(".//depnode"), key=lambda x: int(eu.getAttribute(x, "id")))
        # node_list = eu.convertToEtree(eu.getRoot(dep_parse)).xpath(".//depnode")
    else:
        node_list = dep_parse
        node_list = sorted(node_list, key=lambda x: int(eu.getAttribute(x, "id")))
    return node_list

def dupIndicies(seq):
    tally = defaultdict(list)
    for i,item in enumerate(seq):
        tally[item].append(i)
    return ((key,locs) for key,locs in tally.items()
                            if len(locs)>1)

def replaceWordsWithNer(dep_parse, condense_nodes=False, ret_str=False, correct=True, print_NER=True):
    ner_groups = {}
    ordered_dep = listNodesInOrder(dep_parse)
    for ner_node in ordered_dep:
        # FIXME xxx this is place one
        if eu.hasAttribute(ner_node, "ner"):
            ner_type = eu.getAttribute(ner_node, "ner")
            ner_group = eu.getAttribute(ner_node, ner_type)
            if ner_group == "nil":
                ner_id = eu.getAttribute(ner_node, "id")
                old_key = str(ner_type) + "%%" + str(int(ner_id) - 1)
                key = str(ner_type) + "%%" + ner_id
                if old_key in ner_groups:
                    curr_contents = ner_groups[old_key]
                    ner_groups.pop(old_key)
                    ner_groups[key] = curr_contents
            else:
                key = str(ner_type) + "_" + str(ner_group)
            if key not in list(ner_groups.keys()):
                ner_groups[key] = []
            ner_groups[key].append(ner_node)
    if print_NER:
        print("ORIGINAL: ", end= " ")
        for od in ordered_dep:
            print(eu.getAttribute(od, "lexeme"), end=" ")
        print()
    for ner in list(ner_groups.items()):
        ner_key, ner_to_replace = ner
        rep_str = None
        ner_val = ner[0].split("_")[0]
        if "%%" in ner_key:
            ner_val = ner[0].split("%%")[0]
            rep_str = " ".join(eu.getAttribute(x, "lexeme") for x in ner_to_replace)
        for x, ntr in enumerate(ner_to_replace):
            curr_val = "#e:"+ner_val
            if condense_nodes:
                if x != 0:
                    curr_val = ""
            eu.setAttribute(ntr, "lexeme", curr_val)
            if rep_str is not None:
                eu.setAttribute(ntr, ner_val, rep_str)
    if print_NER:
       print("REPLACEMENT: ", end=" ")
    new_str = " ".join([eu.getAttribute(od,"lexeme") for x, od in enumerate(ordered_dep) if not eu.hasAttribute(od, "speaker")])
    if print_NER:
        print(new_str)
    if correct:
        new_str = correctSyntax(new_str, inc_hash=False)
        if print_NER:
            print("TEXT_CORRECTION: " + str(new_str))
    if ret_str:
        return new_str

def condenseNERDups(s, c):
    return ''.join(c if a == c else ''.join(b) for a, b in groupby(s))


def refsPhrases(dep_parse):
    list_root = eu.getRoot(dep_parse, False)
    dep_roots = list_root.xpath(".//deps")
    refs = {}
    ref_deps = {}
    curr_deps = []
    curr_ref_deps = []
    curr_ref = None
    for dep_root in dep_roots:
        depnodes = listNodesInOrder(dep_root.xpath(".//depnode"))
        for depnode in depnodes:
            ref = eu.getAttribute(depnode, "ref")
            if ref == curr_ref:
                if "PRP" not in eu.getAttribute(depnode, "pos"):
                    curr_deps.append(eu.getAttribute(depnode, "lexeme"))
                curr_ref_deps.append(depnode)
            else:
                if curr_ref not in ["nil", None]:
                    if curr_ref not in refs.keys():
                        refs[curr_ref] = []
                        ref_deps[curr_ref] = []
                    refs[curr_ref].append(" ".join(curr_deps))
                    ref_deps[curr_ref].append(curr_ref_deps)
                curr_ref = ref
                if "PRP" not in eu.getAttribute(depnode, "pos"):
                    curr_deps = [eu.getAttribute(depnode, "lexeme")]
                else:
                    curr_deps = []
                curr_ref_deps = [depnode]
        if curr_ref is not None:
            if curr_ref not in ["nil", None]:
                if curr_ref not in refs.keys():
                    refs[curr_ref] = []
                    ref_deps[curr_ref] = []
                refs[curr_ref].append(" ".join(curr_deps))
                ref_deps[curr_ref].append(curr_ref_deps)

    return refs, ref_deps

#FIXME need to check for repeated words - see .xml file
def replaceWordsWithCoref(dep_parse, core=None):
    dep_parse = copy.deepcopy(dep_parse)
    refs, ref_deps = refsPhrases(dep_parse)
    for k,v in refs.items():
        ref_type = None
        breaker = False
        for nodes in ref_deps[k]:
            for node in nodes:
                r = eu.getAttribute(node, "ref_type")
                if r != "nil":
                    ref_type = r
                    breaker = True
                    break
            if breaker:
                break
        if ref_type is None:
            ref_type = "actors"
        rep_lex = getRepresentativeCorefLex(k, v, core, ref_type)
        if rep_lex is None:
            continue
        deps_to_change = ref_deps[k]
        for deps in deps_to_change:
            curr_text = " ".join([eu.getAttribute(d, "lexeme") for d in deps])
            curr_pos = eu.getAttribute(deps[0], "pos")
            if curr_text != rep_lex and len(deps) == 1 and "NN" not in curr_pos:
                isPoss = eu.hasAttribute(deps[0], "poss")
                rep = rep_lex
                #FIXME Only insert if it doesn't already have it
                if isPoss:
                    rep = rep_lex + "'s"
                eu.setAttribute(deps[0], "lexeme", rep)
                poss_nodes = deps[0].xpath('.//depnode[@lexeme="\'s"]')
                for poss_node in poss_nodes:
                    try:
                        del poss_node
                    except:
                        print("couldn't delete:")

                for i in range(1, len(deps)):
                    try:
                        del deps[i]
                    except:
                        print("couldn't delete:")
    return dep_parse

def getRepresentativeCorefLex(coref_id=None, list_of_lexs=None, core=None, coref_type=None):
    if core is None:
        for x in range(len(list_of_lexs) - 1, -1, -1):
            if list_of_lexs[x] != "":
                return list_of_lexs[x]
    else:
        if type(coref_id) is int:
            coref_id = str(coref_id)
        csplit = coref_id.split(".")
        cid = csplit[0]
        cprop = None
        if len(csplit) > 1:
            cprop = csplit[1]
        return core.getCorefLex(cid, coref_type, coref_prop=cprop)

def jarStanfordSource():
    jar_path = os.path.join(os.getcwd(), "stanford", "stanford-corenlp-full-2016-10-31", "stanford-corenlp-3.7.0-models")
    shutil.make_archive(jar_path, "zip", jar_path)
    thisFile = jar_path + ".zip"
    base = os.path.splitext(thisFile)[0]
    os.rename(thisFile, base + ".jar")

def putIntoDepTree(parses, case="dep"):
    root = eu.createNewElement(case+"s-list")
    for x, parse in enumerate(parses):
        sub_root = eu.createNewElement(case+"s", ("id", str(x)))
        par_root = eu.getRoot(parse)
        if case == "dep":
            speaker = eu.getAttribute(par_root, "speaker")
            sentiment = eu.getAttribute(par_root, "sentiment")
            sentiment_value = eu.getAttribute(par_root, "sentiment_value")
            eu.addAttribute(sub_root, "speaker", speaker)
            eu.addAttribute(sub_root, "sentiment", sentiment)
            eu.addAttribute(sub_root, "sentiment_value", sentiment_value)
        eu.addElement(sub_root, par_root)
        eu.addElement(root, sub_root)
    return root

def extractFromDepTree(parses):
    extracted_parses = []
    for dep in parses.xpath(".//deps"):
        children = dep.getchildren()
        if len(children) > 0:
            extracted_parses.append(copy.deepcopy(children[0]))
    return extracted_parses

def addidToParse(parse):
    parse = eu.getRoot(parse)
    x = 0
    for p in parse.iter():
        if eu.hasAttribute(p, "lexeme"):
            eu.setAttribute(p, "id", str(x))
            x += 1

def deleteOldParses(dep_parse, his):
    for x in range(0, his):
        old = dep_parse.xpath(".//deps[@id='"+str(x)+"']")[0]
        old.getparent().remove(old)
    for dep in dep_parse.xpath(".//deps"):
        eu.setAttribute(dep, "id", str(int(eu.getAttribute(dep, "id")) - his))

def correctSyntax(text, inc_hash=True):
    #FIXME this should be more robust
    # Fix bugs like 50% to 50 %
    text = re.sub(r"\b(\d+)([^\d]+)\b", r"\1 \2 ", text)
    text = re.sub(r"%", "PERCENT", text)
    text = re.sub(r"\\", " ", text)
    text = re.sub(r"/", " ", text)
    text = re.sub(r"(\s)*\.", ".", text)
    text = re.sub(r"\.+", ".", text)
    text = re.sub(r"\b(\w)\.(\w)\b", "\1. \2", text)
    text = re.sub(r"(\s)*,", ",", text)
    text = re.sub(r"(\s)*!", "!", text)
    text = re.sub(r"(\s)*\?", "?", text)
    text = re.sub(r"(\s)*'", "'", text)
    text = re.sub(r"(\s)+ ", " ", text)
    text = re.sub(r"\b(the\s+){2,}\b", "the ", text,flags=re.IGNORECASE)
    if inc_hash:
        text = re.sub(r'[^\w\s\.,!\?\']', '', text)
    else:
        text = re.sub(r'[^\w\s\.,!\?#\']', '', text)
    text = re.sub(r"(\w+)\.(\w+)", r"\1. \2", text)
    text = text.strip()
    return text

def getAssociatedVerb(dep_parse):
    entities = []
    seen = []
    nodes = dep_parse.xpath('.//depnode[@ner and @gkg="True"]')
    for node in nodes:
        ner = eu.getAttribute(node, "ner")
        score = eu.getAttribute(node, ner)
        key = ner + ":" + score
        if key not in seen:
            seen.append(key)
            entities.append(node)

    final_entity = []
    for entity in entities:
        final_node = None
        par = entity.getparent()
        while par is not None:
            if eu.getAttribute(par, "pos") == "VB":
                final_node = par
                break
            par.getparent()
        if final_node is None:
            final_entity.append(None)
        else:
            final_entity.append(final_node)

    final = list(zip(entities, final_entity))
    for e, v in final:
        print(eu.getAttribute(e, "gkglex") + " :: " + eu.getAttribute(v, "lexeme"))
    return final


if __name__ == "__main__":
        # jarStanfordinit()Source()
    init()

    t = time.time()
    print("start")
    # print(str(nltk.word_tokenize("my favorite Star Wars movie is probably revenge of the sith ")))
    # sm.getRootObjects()

    f = True
    ptype = "const"
    if f:
        ptype = "dep"

    shawshank_review = """\
    I have never seen such an amazing film since I saw The Shawshank Redemption. Shawshank encompasses friendships, hardships, hopes, and dreams.  And what is so great about the movie is that it moves you, it gives you hope.
    """

    """Even though the circumstances between the characters and the viewers are quite different, you don't feel that far removed from what the characters are going through.
    It  is a simple film, yet it has an everlasting message.  Frank Darabont didn't need to put any kind of outlandish special effects to get us to love this film, the narration and the acting does that for him.  Why this movie didn't win all seven Oscars is beyond me, but don't let that sway you to not see this film, let its ranking on the IMDb's top 250 list sway you, let your friends recommendation about the movie sway you.
    Se  t aside a little over two hours tonight and rent this movie.  You will finally understand what everyone is talking about and you will understand why this is my all time favorite movie.
    """

    s = """
    Yea, I like Inception. What do you think about Inception?
    """

    parses = [
        parseSentence("I removed the tiny bugs's leader's limb.", ["shawshank_review"], expected_entities=[]),

        '''
        parseSentence("What is the capital city of Mexico? What is its population? What is its geographical location?", ["test"],
                              expected_entities=["Movie"], full=f),
        parseSentence("What is the capital city of Mexico? Mexico's capital city is Mexico City. What is its population?", ["test"],
                              expected_entities=["Movie"], full=f),
        parseSentence(
            "my favorite Star Wars movie is probably revenge of the sith", ["test"],
            expected_entities=None, full=f),
        parseSentence(
            "Barack Obama was born in Hawaii. Steve Rogers was born in New York.", ["0"],
            expected_entities=None, full=f),
        parseSentence(
        "Yeah, I think it's likely, like over 50%, that a cat who lives long enough will get some type of cancer.", ["0"],
        expected_entities=None, full=f),
        parseSentence(
            "Unless they're going to foist 8k on us between now and the day when we're all wearing VR entertainment headsets.", ["0"],
            expected_entities=None, full=f),
        parseSentence(
            "An advisory opinion is an opinion issued"
            " by a court or a commission like an election commision that does not have the effect of adjudicating a specific"
            " legal case, but merely advises on the constitutionality or interpretation of law.", ["test"],
            expected_entities=["Movie"], full=f),
        parseSentence(
            "Elk Grove", ["test"],
            expected_entities=["City"], full=f),
        parseSentence(
            "Big Bang Theory", ["test"],
            expected_entities=["Basketball team"], full=f)
        '''

    ]


    parse = parses[0]
    #print('parse=', parse)

    parse = putIntoDepTree(parse, ptype)
    # getAssociatedVerb(parse)

    sent = parse[0]
    print('p=', sent)
    print('p.tag=', sent.tag)
    print('p.attrib=', sent.attrib)
    print()

    '''
    for child in sent.iter('depnode'):
        id = child.get('id')
        lexeme = child.get('lexeme')
        sentiment = child.get('sentiment')
        if lexeme == 'ROOT':
            parent,rel, parent_word, children = None, None, None, None
        else:
            rel = child.get('gov_type')
            # check if there are multiple parents
            if rel.find(';') > -1:
                parents = rel.split(';')
                rel = parents[0]
            parent = child.get(rel)
            parent_node = child.getparent()
            parent_word = parent_node.get('lexeme')
            children = child.getchildren()
        print(id, (parent_word, rel), '\t', lexeme, '\t',  sentiment, '\t', children)
    '''

    #replaceWordsWithNer(parse, condense_nodes=True, ret_str=True)



    # dep_parse = replaceWordsWithCoref(parse)
    # list_root = eu.getRoot(dep_parse, False)
    # dep_roots = list_root.xpath(".//deps")
    # for dep_root in dep_roots:
    #     depnodes = listNodesInOrder(eu.convertToEtree(dep_root))
    #     print()
    #     for depnode in depnodes:
    #         print(eu.getAttribute(depnode, "lexeme"), end= " ")
    # if ptype == "const":
    #     addidToParse(parse)
    #parse = parseSentence("I saw superbad", ["test"])

    print('run time: ',t - time.time())


    # parse = m2d.py_scripts.content_planner.callOnExistingTrees(parse, tag=True, adj_mod=True, ack=True)

    filename = os.path.join(os.getcwd(),"test_"+ptype+".xml")
    writeToFile(parse, filename)

    # f = open(os.path.join(os.getcwd(), "data", "schema_entities.txt")).read()
    # schema_entities = []
    # for line in f.split("\n"):
    #     text = re.sub(r"(?P<name>[A-Z]+[a-z]*)", r"\1 ", line)
    #     text.strip()
    #     schema_entities.append(text)
    # f2 = open(os.path.join(os.getcwd(), "data", "schema_entities.txt"), mode="w")
    # f2.write("\n".join(schema_entities))
        # re_match = re.compile(r"^\A|(?P<name>[A-Z]+[a-z]*)").search(line)
        # while re_match:
        #     group_dict = re_match.groupdict()
        #     print(str(group_dict.items()))

            # match = group_dict["opinion_object"]
            # has_pat = True
            # if match is not None:
            #     match = match.strip()
            # break
            #
    # filename = os.path.join(os.getcwd(), "test_test_" + ptype + ".xml")
    # writeToFile(dep_parse, filename)

    # print(t - time.time())
    # blah = annotateText("This is a test of how well this can work with decent sized sentences.", "pos", "text")
    # print(blah)
    # print(t - time.time())

    # print("now we try and use content_planner:")