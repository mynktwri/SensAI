import sys

sys.path.insert(0, '../../NeuralNet')
sys.path.insert(0, '../../NLP')

import evaluateNN as enn

testsPassed = 0
testsFailed = 0

output = enn.makePrediction("iterate over a")
if output == "for item in a:":
        testsPassed = testsPassed + 1
else:
        testsFailed = testsFailed + 1
        print('expected "for item in a:", got')
        print(output)

output = enn.makePrediction("if i = banana")
if output == "if i == banana:":
        testsPassed = testsPassed + 1
else:
        testsFailed = testsFailed + 1
        print('expected "if i == banana:", got')
        print(output)

print('testsPassed = ')
print(testsPassed)
print('testsFailed = ')
print(testsFailed)
print('Percent passed = ')
print((testsPassed/(testsPassed+testsFailed))*100)
