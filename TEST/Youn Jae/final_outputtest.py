import os, sys
sys.path.append(os.path.join(os.getcwd(), "..", "..", "NeuralNet"))
sys.path.append(os.path.join(os.getcwd(), "..", "..", "NLP"))
import final_output as fo
# This section of code is the category seperation from evaluateNN.py in NeuralNet folder.
# Line 47 - 60
# This list contains all possible category numbers from the Neural Network and the 
# Sentences that could go along with the category given.
# best_i represents the "best" prediction that the model made.
sentencelist = [(0, "set x to 2"), (3, "if banana is greater than oreo"), (2, "for x greater than 2"),
                (1, "print x")]
#In the code, the results are usually returned. However, for the test's sake, we will
# print it instead.
for best_i, sentence in sentencelist:
    if best_i == 0:
        obj1, obj2 = fo.varObject(sentence)
        print(fo.varCode(obj1, obj2))
    elif best_i == 1:
        obj1 = fo.printObject(sentence)
        print(fo.printCode(obj1))
    elif best_i == 2:
        obj1 = fo.LoopObject(sentence)
        print(fo.loopCode(obj1))
    elif best_i == 3:
        obj1, opera, obj2 = fo.ifObject(sentence)
        print(fo.ifCode(obj1, opera, obj2))
    else:
        print(-1)