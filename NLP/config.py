import os

# We need to store the project root for testing reason. Also, it need to be absolute path.
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# MAIN_DIR = "./"
MAIN_DIR = ROOT_DIR
STANFORD_PARSER_HOME = os.path.join(MAIN_DIR, "..","/stanford/stanford-corenlp-full-2017-06-09/")

if __name__ == "__main__":
    print(ROOT_DIR)
