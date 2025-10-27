from tkinter import *
from tkinter import ttk

# obtener resolución de pantalla en Windows
import ctypes

user32 = ctypes.windll.user32
WIDTH = user32.GetSystemMetrics(0)
HEIGHT = user32.GetSystemMetrics(1)

def calculate(*args):
    try:
        value = float(feet.get())
        meters.set(round(0.3048 * value, 4))
    except ValueError:
        pass
# GUI setup padding=(3,3,12,12)
root = Tk()
root.title("Feet to Meters")
mainframe = ttk.Frame(root, width=WIDTH/3, height=HEIGHT/2)
mainframe.pack()
feet = StringVar()
feet_entry = ttk.Entry(mainframe, width=7, textvariable=feet)
feet_entry.grid(column=2, row=1, sticky=(W, E))

meters = StringVar()
ttk.Label(mainframe, textvariable=meters).grid(column=2, row=2, sticky=(W, E))

ttk.Button(mainframe, text="Calculate", command=calculate).grid(column=3, row=3, sticky=W)

ttk.Label(mainframe, text="feet").grid(column=3, row=1, sticky=W)
ttk.Label(mainframe, text="is equivalent to").grid(column=1, row=2, sticky=E)
ttk.Label(mainframe, text="meters").grid(column=3, row=2, sticky=W)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
mainframe.columnconfigure(2, weight=1)
for child in mainframe.winfo_children(): 
    child.grid_configure(padx=5, pady=5)

feet_entry.focus()
root.bind("<Return>", calculate)

root.mainloop()