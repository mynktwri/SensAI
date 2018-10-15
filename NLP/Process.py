import stanford_tools as st
import dsynt_generator as dg
import element_utils as eu
import config as config
import subprocess

def NLP(text):
    st.init()
    texttree = st.parse_sentences([text], "test")
    texttree = st.putIntoDepTree(texttree)
    text_dsynt = dg.convertToDsynts(texttree)
    print(type(text_dsynt))
    eu.writeTree(text_dsynt, "output.xml")
    return text_dsynt