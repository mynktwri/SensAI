import tkinter
import evaluateNN as enn
from tkinter import *

root = Tk()
top = Frame(root)
top.pack(side = TOP)
L1 = Label(top, text="Enter a sentence to feed to neural net.")
L1.pack( side = LEFT)
E1 = Entry(top, bd =5)
E1.pack(side = RIGHT)

output = StringVar()

def callNN():
    output.set(E1.get())
    L2.pack()
    sentence = E1.get()
    prediction = enn.makePrediction(sentence)
    output.set(prediction)
bottom = Frame(root)
bottom.pack(side = BOTTOM)
B = Button(bottom, text ="Evaluate", command = callNN)
B.pack(side = TOP)
L2 = Label(bottom, textvariable=output, relief=RAISED)
L2.pack(side = BOTTOM)

root.mainloop()
