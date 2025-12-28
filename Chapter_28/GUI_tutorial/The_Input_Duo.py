
import tkinter as tk

root = tk.Tk()
root.geometry("500x100")
tk.Label(root, text="Mission Name:", font=("Arial", 10)).pack()
task_box = tk.Entry(root)
task_box.pack()

root.mainloop()