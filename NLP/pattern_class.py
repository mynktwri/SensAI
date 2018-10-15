#TODO update to support depnodes
import element_utils
#TODO update to support depnodes
class Pattern_Class():

    def __init__(self, key, max, prob):
        self.key = key #Key/name of hedgelist in template file.
        self.max = max #Max occurances of a class type.
        self.prob = prob #Probability of apperance for class, default 1
        self.sub_patterns = [] #List of all sub patterns of a pattern class

    def addPattern(self, element):
        """
        :param element: Pattern to add
        :return:
        """
        name = element_utils.getAttribute(element, "name")
        #gets the children of <insertion-point> tag
        insertion = element_utils.getElement(element, "insertion-point")
        #element tree with insertion-point data removed
        pattern_match = element_utils.delElementWithTag(element, "insertion-point")
        node = Pattern_Node(name, pattern_match, insertion)
        self.sub_patterns.append(node)
#TODO update to support depnodes
class Pattern_Node():
    def __init__(self, name, pattern_match, insertion):
        self.name = name #name/subkey
        self.insertion = insertion #data to insert into dsynt
        self.pattern_match = pattern_match #pattern to look for in dsynt

