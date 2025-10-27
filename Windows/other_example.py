import tkinter as tk

root = tk.Tk()
canvas = tk.Canvas(root, bg="lightblue", width=300, height=200)
canvas.pack()
frame = tk.Frame(canvas, bg="red")
canvas.create_window(50, 50, window=frame, anchor="nw")
button = tk.Button(frame, text="Click Me")
button.pack()
root.mainloop()