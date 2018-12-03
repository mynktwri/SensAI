
# This section of code is the category seperation from evaluateNN.py in NeuralNet folder.
# Line 47 - 60
test = [0, 3, 2, 1]
if best_i == 0:
    obj1, obj2 = fo.varObject(sentence)
    return (fo.varCode(obj1, obj2))
elif best_i == 1:
    obj1 = fo.printObject(sentence)
    return (fo.printCode(obj1))
elif best_i == 2:
    obj1 = fo.LoopObject(sentence)
    return (fo.loopCode(obj1))
elif best_i == 3:
    obj1, opera, obj2 = fo.ifObject(sentence)
    return (fo.ifCode(obj1, opera, obj2))
else:
    return -1