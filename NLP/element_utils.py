import sys, os
sys.path.append(os.path.join(os.getcwd()))
from lxml import etree
import os,copy, re
import logging
import pattern_lib
import os.path

def createFromXML(source="", path=None):
    """
    :param source: xml file to be parsed
    :return: element tree, each element being an item from the xml file
    """
    parser = etree.XMLParser(remove_blank_text=True)
    if path != None:
        element_tree = etree.parse(path, parser)
        # FIXME Not sure this can close the file open by element_tree.
        try:
            with open(path) as file:
                if not file.closed:
                    file.close()
        except:
            pass
    else:
        element_tree = etree.parse(source, parser)
        # FIXME Not sure this can close the file open by element_tree.
        try:
            with open(source) as file:
                if not file.closed:
                    file.close()
        except:
            pass
    logging.debug("element_utils::createFromXML:: Creating tree from source  " + source)
    return element_tree

def createFromString(source):
    """
    :param source: string source to parse into element tree
    :return: element tree, each element being an item from the string or list of strings
    """
    parser = etree.XMLParser(remove_blank_text=True)
    if type(source) == bytes:
        logging.debug("element_utils::createFromString:: Creating tree from String source")
        return etree.fromstring(source, parser)
    elif type(source) == str:
        # Grace: added this due to value error when source is a string
        logging.debug("element_utils::createFromString:: Creating tree from String")
        return etree.fromstring(source, parser)
    else:
        logging.debug("element_utils::createFromString:: Creating tree from String List")
        return etree.fromstringlist(source, parser)

def addAttribute(element, attribute, value):
    """
    :param element: an element from the element tree
    :param attribute: the attribute you would like to add
    :param value: the value for the new attribute
    :return: the element that has been manipulated
    """
    logging.debug("element_utils::addAttribute:: Adding "+ attribute + "="+str(value)+" to "+str(element))
    element.set(attribute, value)
    return element

def createNewElement(tag, *attributes):
    """
    :param tag: Tag for new element
    :param attributes: attributes to add to new element, (attrib, value)
    :return: the new element created
    """
    new_el = etree.Element(tag)
    try:
        if type(attributes[0]) is list:
            attributes = attributes[0]
    except:
        pass
    for attribute in attributes:
        addAttribute(new_el, attribute[0], attribute[1])

    logging.debug("element_utils::createNewElement:: Created new element with "
                  "tag "+ tag+" and attributes " + str(attributes))
    return new_el

def addElement(element, new_ele, pos="last"):
    """
    :param element: parent element
    :param new_ele: new child
    :param pos: position in children of parent element
    :return: the parent element
    """
    # print("in")
    if pos == "first":
        pos = 0
    elif pos == "last":
        pos = len(element.getchildren())
    element.insert(pos, new_ele)

    logging.debug("element_utils::addElement:: Added element")
    return element

def addNewElement(element, tag, pos="last", extend=False,*attributes):
    """
    :param element: parent element to new element
    :param tag: tag of new element
    :param pos: position in children of parent element
    :param extend: determine if element will adopt children of child previously in position
    :param attributes: tuples to add as attributes to the new element
    :return: returns the newly created element
    """
    if pos == "first":
        pos = 0
    elif pos == "last":
        pos = len(element.getchildren())
    new_element = etree.Element(tag)
    for attribute in attributes:
        new_element.set(str(attribute[0]), str(attribute[1]))
    #extend makes new element parent of children from previous element in this position
    if extend:
        new_element.extend(element)
    element.insert(pos, new_element)
    logging.debug("element_utils::addNewElement:: Added new element with extend value " + str(extend))
    return new_element

def convertToEtree(element):
    """
    :param element: element
    :return: element cast as etree
        Cast an element to an etree. Used mostly when needing to use getroot() on element.
    """
    logging.debug("element_utils::convertToEtree:: Element cast into element tree.")
    return etree.ElementTree(element)

def addCopyElement(element, ele_to_copy, pos="first",adopt=False):
    """
    :param element: parent element
    :param ele_to_copy: element to copy
    :param pos: position in children of parent element
    :param adopt: If false, delete children of copy
    :return: the copy that has been added
        Use when it is needed to add a copy of exisiting element to tree
    """
    if pos == "first":
        pos = 0
    elif pos == "last":
        pos = len(element.getchildren())

    clone_ele = copy.deepcopy(ele_to_copy)
    if not adopt:
        for child in clone_ele.getchildren():
            delElement(child)

    element.insert(pos, clone_ele)
    logging.debug("element_utils::addCopyElement:: Copying an element and adding it to tree.")
    return clone_ele
#TODO update to support depnodes
def getPatternToMatch(pattern, subkey=None):
    """
    :param pattern: pattern key
    :param subkey: subkey key in pattern
    :return:
        Gets pattern to search in etree
    """
    tree = pattern_lib.getSubData(pattern, "pattern_match", subkey)
    logging.debug("element_utils::patternToMatch:: Got matching pattern for " + pattern + " with subkey " + str(subkey))
    return tree
#TODO update to support depnodes
def addPattern(element, pattern, subkey=None, known_index = 0):
    """
    :param element: element that is the desired parent of the new pattern
    :param pattern: pattern key to load correct insertion data
    :param subkey: subkey to add specifically
    :param known_index: child index of element where you would like to
            insert the new element
    :return: element on success
    """
    try:
        temp = copy.deepcopy(pattern_lib.getSubData(pattern, "insertion", subkey))
        pattern_xml = temp
    except:
        logging.error("element_utils::addPattern:: Could not add pattern " + pattern + " with subkey " + str(subkey))
        return

    func = hasFunctionCall(pattern_xml)
    #if we need to calla function to handle insertion
    if func[0]:
        if pattern_xml.getchildren():
            pattern_str = pattern
            if subkey is not None:
                pattern_str += "_"+subkey
            getattr(importlib.import_module(func[1]),func[2])(element, pattern_xml, pattern_str)
        else:
            getattr(importlib.import_module(func[1]),func[2])(element)
        return element

    element.insert(len(element), pattern_xml)
    logging.debug("element_utils::addPattern:: Successfully adding pattern " + pattern + " with subkey " + str(subkey))
    return element
#TODO update to support depnodes
def hasFunctionCall(element):
    """
    :param element: insertion point dsynt
    :return: True: (module name, function name) False: (None,None)
        Determines if instead of just content insertion, we want to
        call a function to handle the insertion.
    """
    function_call = getAttribute(element, "function_call")
    module = getAttribute(element, "module")
    if function_call is "nil":
        logging.debug("element_utils::hasFunctionCall:: Pattern does not have function call.")
        return False, None, None
    logging.debug("element_utils::hasFunctionCall:: Function: " + function_call + " module: " + module)
    return True, module, function_call

def hasAttribute(element, attribute, similar=False):
    """
    :param element: element in element tree
    :param attribute: requested attribute. Valid attributes are any attributes in xml structure
    :param similar: if true, checks if element has similar entries.
    :return: Bool, true == yes
    """
    if similar:
        similar_attribs = re.findall(attribute+'\w*', str(element.attrib))
        if len(similar_attribs) > 0:
            logging.debug("element_utils::hasAttribute:: has attribute similar to " +attribute)
            return True
        else:
            logging.debug("element_utils::hasAttribute:: does not have attribute similar to " +attribute)
            return False
    try:
        logging.debug("element_utils::hasAttribute:: has attribute " +attribute)
        element.attrib[attribute]
        return True
    except:
        logging.debug("element_utils::hasAttribute:: does not have attribute " +attribute)
        return False

def getAttribute(element, attribute):
    """
    :param element: element in element tree
    :param attribute: requested attribute. Valid attributes are any attributes in xml structure
            example attribute == lexeme
    :return: value of attribute from element. If attribute not in element, return error
    """
    if hasAttribute(element, attribute):
        logging.debug("element_utils::getAttribute:: "+str(element)+" has attribute " +attribute + " has value " + element.attrib[attribute])
        return element.attrib[attribute]
    else:
        logging.debug("element_utils::getAttribute:: " +str(element)+" does not have attribute " +attribute)
        return "nil"

def getTag(element):
    """
    :param element: element in element tree
    :return: tag of element.
            example of tag === dsyntnode
    """
    logging.debug("element_utils::getTag:: element has tag " +str(element.tag))
    return element.tag

def getElement(element_tree, tag):
    """
    :param element_tree: tree of elements that tag element is in
    :param tag: tag to search for in tree
    :return:
    """
    tree = element_tree.xpath('.//' + tag)[0]
    if len(tree.getchildren()) > 0:
        tree = tree.getchildren()[0]
    return tree

def getAllElement(element_tree, tag):
    """
    :param element_tree: tree of elements that tag element is in
    :param tag: tag to search for in tree
    :return:
    """
    trees = element_tree.xpath('.//' + tag)[0]
    trees = [tree for tree in trees if len(tree.getchildren()) > 0]
    return trees

def setTag(element, value):
    """
    :param element: element in element tree
    :param value: new tag value for element
    :return: Nothing on success, on error returns error
    """
    try:
        element.tag = value
        logging.debug("element_utils::setTag:: set tag to " +str(value))
    except:
        logging.error("element_utils::setTag:: Could not set the elements tag correctly!")
        return

def setAttribute(element, attribute, value):
    """
    :param element: element in element tree
    :param attribute: attribute to change
            example of attribute == lexeme
    :param value: new attribute value
    :return: Original element
    """
    if hasAttribute(element, attribute):
        element.attrib[attribute] = str(value)
        logging.debug("element_utils::setAttribute:: "+str(element)+ " attribute " +str(attribute)+" set to "+str(value))
    else:
        addAttribute(element, attribute, value)
        # logging.warning("element_utils::setAttribute:: "+str(element)+ " attribute "+str(attribute)+" could not be set to "+str(value))
    return element

def writeTree(element_tree, filename):
    """
    :param element_tree: element tree to write to file
    :param filename: filename of output file
    :return:
    """
    try:
        element_tree.write(filename, pretty_print=True)
        logging.debug("element_utils::writeTree:: tree written to " + filename )
    except:
        import traceback
        traceback.print_exc()
        logging.warning("element_utils::writeTree:: tree write failure, verify etree and valid filename provided.")

def delElementsFromPath(element_tree, tag, attr, val):
    """
    :param element_tree: tree to traverse and look for elements to delete
    :param tag: target tag
    :param attr: target attribute
    :param val: target value for attribute
    :return:
    Used to delete an element inside of a path specified. Can also set a
    specific attribute with a value to narrow deletion targets as well.
    """
    for elem in element_tree.xpath("//"+tag+"[@"+attr+"=\'"+val+"\']"):
        elem.getparent().remove(elem)
    logging.debug("element_utils::delElementsFromPath:: elements deleted with path  " + "//"+tag+"[@"+attr+"=\'"+val+"\']" )

def delElementWithTag(element_tree, tag):
    """
    :param element_tree: Tree to remove from
    :param tag: Target tag to remove
    :return:
    """
    etree.strip_elements(element_tree, tag)
    logging.debug("element_utils::delElementWithTag:: elements deleted with tag "+ tag)
    return element_tree

def delElement(element, save_children=False):
    """
    :param element: Element to remove
    :return:
    """
    parent = element.getparent()
    if save_children:
        for child in element.getchildren():
            parent.append(child)
    parent.remove(element)
    logging.debug("element_utils::delElement:: element deleted correctly.")

def delAttribute(element, attribute):
    """
    :param element: element in element tree
    :param attribute: attribute to change
            example of attribute == lexeme
    :return: Success of failure message of operation
    """
    if hasAttribute(element, attribute):
        del element.attrib[attribute]
        logging.debug("element_utils::delAttribute:: deleted attribute: " + attribute)
        return element
    else:
        pass
        # logging.warning("element_utils::delAttribute:: didn't delete attribute: " + attribute+" correctly.")

def lenTreeObject(element_tree, tree_tag):
    """
    :param element_tree: A source element tree
    :param tree_tag: Tag for which to find instances of
    :return: len of total entries
    """
    uses = len(element_tree.findall(".//"+str(tree_tag)))
    logging.debug("element_utils::lenTreeObject:: There are " + str(uses) + " of tree tag " + str(tree_tag))
    return uses

def spk_id_bool(s):
    """
    :param s: speaker id value
    :return: BOOL related to string value
        Return bool for given string value stored in speaker_id attribute of dsynts node.
    """
    if s == 'True':
         return True
    elif s == 'False':
         return False
    return None

def increment_attr_val(dsynt, attribute, value):
    """
    :param dsynt: dsynt to check the value of
    :param attribute: attribute to update
    :param value: value to sum
    :return: dsynt
        Checks if an attribute has an int attribute to add values to
    """
    curr_val = getAttribute(dsynt, attribute)
    if curr_val == "nil":
        addAttribute(dsynt, attribute, str(value))
        return dsynt
    if curr_val == "+":
        setAttribute(dsynt, attribute, curr_val + "+")
    if type(value) is int:
        setAttribute(dsynt, attribute, str(int(value)+int(curr_val)))
    else:
        setAttribute(dsynt, attribute, str(curr_val)+","+str(value))
    return dsynt

def stringify_children(node):
    from lxml.etree import tostring
    from itertools import chain
    parts = ([node.text] +
            list(chain(*([c.text, tostring(c), c.tail] for c in node.getchildren()))) +
            [node.tail])
    # filter removes possible Nones in texts and tails
    return ''.join(filter(None, parts)).rstrip("\n").rstrip("")

def dumpElements(elements):
    """
    :param elements: element in element tree, or full element tree/subtree
    :return: prints data tree to stdout.
    Method used for debug
    """
    if type(elements) == etree._Element:
        etree.dump(elements)
    else:
        etree.dump(elements.getroot())

def getRoot(element, prune_list=True):
    if type(element) is etree._ElementTree:
        element = element.getroot()
    r = element.getparent()
    while r is not None:
        if prune_list:
            if atListRoot(r):
                break
        element = r
        r = element.getparent()
    return element

def atListRoot(element):
    if "-list" in getTag(element):
        return True
    return False

if __name__ == "__main__":
    import config
    element = createFromXML(path=os.path.join(config.FLOW_DATA, "books_flow.xml"))
    dumpElements(element)
    element = createFromXML(source=os.path.join(config.FLOW_DATA, "books_flow.xml"))
    dumpElements(element)