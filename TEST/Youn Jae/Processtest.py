import os, sys
sys.path.append(os.path.join(os.getcwd(), "..", "..", "NLP"))
import Process as p

test = ["This is a test.", "if x is equal to 2", "for x bigger than 3", "if x is smaller than 2", "if banana is four",
        "print x", "print h", "Tomorrow will be a monday.", "Yesterday was a thursday.",
        "for banana not equal to apples", "Bananas will always be loved by humans.", "8 is a number.",
        "You have been warned.", "This project is called SensAI."]
checklist = []
for sentence in test:
    # This prints the sentences in the test list as a list.
    checklist = p.getWord(sentence)
    print("Sentence: ")
    print(checklist)
    # This prints the Part of speech tags from the sentences.
    checklist = p.getTag(sentence)
    print("Part of Speech: ")
    print(checklist)
    # This prints the length of each sentences.
    print("Sentence Length: ")
    print(p.getLength(sentence))
    print(" \n")
    checklist = []
