import threading
from tkinter import *

started = False
def pop():
    new = Tk()

    l = Label(new,text='Loading')
    l.pack()

    new.protocol('WM_DELETE_WINDOW',lambda: new.destroy() if started else False) # Close the window only if main window has shown up
    new.mainloop()

threading.Thread(target=pop).start() # Use this before the heavy process starts

root = Tk()

text = Text(root , width = 65 , height = 20 , font = "consolas 14")
text.pack()

text.insert('1.0' , "hello\n"*5000000) # If you want to see real delay use time.sleep(5)

started = True
root.mainloop()