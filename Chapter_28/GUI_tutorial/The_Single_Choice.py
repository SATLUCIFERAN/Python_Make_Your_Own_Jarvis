
import tkinter as tk

root = tk.Tk()
root.geometry("500x100")
choice = tk.StringVar(value="A")
tk.Radiobutton(root, text="Option Alpha", variable=choice, value="A").pack()
tk.Radiobutton(root, text="Option Beta", variable=choice, value="B").pack()

root.mainloop()










