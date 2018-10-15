#TODO update to support depnodes
import sys, os
sys.path.append(os.path.join("."))

import element_utils
import re
import logging
import os
import copy
patterns_table = {}
#TODO update to support depnodes
def loadLib():
    """
    :return:
        Loads database with insertion pattern templates from the
        markers-templates.xml file. Can be used to sanatize database
    """
    doc = element_utils.createFromXML(path=os.path.join(os.getcwd(), "tools", "M2D", "data", "xml", "markers-templates.xml"))

    #Creates a list of trees based on children of hedgelist items
    for node in doc.xpath('.//hedgelist'):
        #get data
        name = element_utils.getAttribute(node, "name")
        max = element_utils.getAttribute(node, "max")
        prob = element_utils.getAttribute(node, "prob-coef")
        if prob is "nil":
            prob = 1.0
        pattern = pattern_class.Pattern_Class(name, max, prob)

        #Another sublist of items that start with the "dsynts" tag
        #Creates a new pattern_node for each sub node of a node.
        for subnode in node.xpath('.//dsynts'):
            newnode = subnode
            pattern.addPattern(newnode)

        patterns_table[name] = pattern
    logging.info("pattern_lib::loadLib:: Pattern library loaded.")
#TODO update to support depnodes
def setClassData(key, *data):
    """
    :param key: key of dict entry that has required data
    :return: tuple (max uses per dsynt, prob of it appearing)
        This returns the data from the class entry in the dict.
        Essentially the information presented in the hedgelist section
        of the template file.
    """
    if not isKey(key):
        return
    for d in data:
        if d[0] == "max":
            patterns_table[key].max = d[1]
        if d[0] == "prob":
            patterns_table[key].max = d[1]
        logging.debug("pattern_lib::setClassData:: setting data for " + key +
                     ", "+ d[0]+": "+ str(d[1]))
#TODO update to support depnodes
def isKey(key):
    """
    :param key: key to check
    :return: True if in table, False is not in table
        Determines if given key is in patterns table
    """
    try:
        patterns_table[key]
        return True
    except:
        return False
#TODO update to support depnodes
def getClassData(key):
    """
    :param key: key of dict entry that has required data
    :return: tuple (max uses per dsynt, prob of it appearing)
        This returns the data from the class entry in the dict.
        Essentially the information presented in the hedgelist section
        of the template file.
    """
    max = patterns_table[key].max
    prob = patterns_table[key].prob
    logging.debug("pattern_lib::getClassData:: getting data for " + key +
                 ", max: " + str(int(max)) + " prob: " + str(float(prob)))
    return (int(max), float(prob))
#TODO update to support depnodes
def getPatternNode(key, subkey = None):
    """
    :param key: Desired key in dict of pattern classes
    :param subkey: Subkey to subindex if there are multiple subelements.
        Example: "expletives" key has "bloody", "damn" and "oh_god" subkeys.
        By default, just returns first pattern node, as most templates
        only have one pattern node, and don't require the subkey.
    :return:
    """
    if subkey != None:
        for subs in patterns_table[key].sub_patterns:
            if subs.name == subkey:
                return subs
    logging.debug("pattern_lib::getPatternNode:: Getting pattern node for " + key + " with subkey " + str(subkey))
    return patterns_table[key].sub_patterns[0]
#TODO update to support depnodes
def getSubData(key, data, subkey = None):
    """
    :param key: key from original dict to use
    :param data: keyword to determine which data you want to return
        Possible entries: "insertion", "pattern_match", "name"
    :param subkey: Subkey to subindex if there are multiple subelements.
        Example: "expletives" key has "bloody", "damn" and "oh_g+od" subkeys.
    :return:
    """
    logging.debug("pattern_lib::getSubData:: Getting " + data + " for " + key + "with subkey " + str(subkey))
    if data == "insertion":
        return copy.deepcopy(getPatternNode(key, subkey).insertion)
    elif data == "pattern_match":
        return getPatternNode(key, subkey).pattern_match
    elif data == "name":
        return getPatternNode(key, subkey).name
    else:
        logging.warning("pattern_lib::getSubData:: " + data + " is not a valid data entry.")
        return
#TODO update to support depnodes
def hasSubkeys(key):
    """
    :param key: key in hash you would like to see if children exist.
        note, there will always be one child
    :return: bool
    """
    if len(patterns_table[key].sub_patterns) > 1:
        logging.debug("pattern_lib::hasSubkeys:: " + key + " has subkeys key.")
        return True
    else:
        logging.debug("pattern_lib::hasSubkeys:: " + key + " has no subkeys key.")
        return False
#TODO update to support depnodes
def possibleKeys(regex=None, supress=False):
    """
    :param regex: expression to match and return given keys based on.
        Example good regex arg is "ack", to return acknowledgements keys
    :return: list of ether all keys, or specifc keys based on regex
    """
    all_keys = patterns_table.keys()
    if regex is None:
        if not supress: print(all_keys)
        logging.debug("pattern_lib::possibleKeys:: Getting possible keys...")
        logging.debug("      " + str(all_keys))
        return all_keys
    else:
        specific_keys = re.findall(regex+'\w*', str(all_keys))
        if not supress: print(specific_keys)
        logging.debug("pattern_lib::possibleKeys:: Getting possible keys...")
        logging.debug("      " + str(specific_keys))
        return specific_keys
#TODO update to support depnodes
def possibleSubKeys(key, supress=False):
    """
    :return: Dump all possible subkeys to stdout
    """
    subby = []
    for subkey in patterns_table[key].sub_patterns:
        if not supress: print(subkey.name)
        subby.append(subkey.name)
    logging.debug("pattern_lib::possibleSubKeys:: Getting possible subkeys...")
    logging.debug("      " + str(subby))
    return subby
#TODO update to support depnodes
if __name__ == '__main__':
    loadLib()