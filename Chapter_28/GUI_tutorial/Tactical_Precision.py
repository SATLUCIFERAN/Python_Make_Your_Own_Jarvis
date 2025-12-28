
import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.geometry("500x100")
tk.Label(root, text="Set Hour (0-23):").pack()
spin = ttk.Spinbox(root, from_=0, to=23, format="%02.0f", width=5)
spin.pack()
root.mainloop()


