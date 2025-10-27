# entrypoint
import tkinter as tk
from src import EyeControlApp_TK
def main():
    root = tk.Tk()
    app = EyeControlApp_TK(root)
    root.configure(bg='lightblue')
    root.mainloop()

if __name__ == "__main__":
    main()