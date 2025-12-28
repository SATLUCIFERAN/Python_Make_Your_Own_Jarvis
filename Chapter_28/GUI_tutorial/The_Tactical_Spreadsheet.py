
import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.geometry("500x100")
# Define columns
tree = ttk.Treeview(root, columns=("ID", "Task"), show="headings")
tree.heading("ID", text="ID")
tree.heading("Task", text="MISSION")
# Insert a sample row
tree.insert("", tk.END, values=("001", "Recharge Power Cells"))
tree.insert("", tk.END, values=("002", "Recharge Arc Reactors"))
tree.pack()
root.mainloop()










