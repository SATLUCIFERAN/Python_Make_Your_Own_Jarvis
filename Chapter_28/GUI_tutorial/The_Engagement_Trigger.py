
import tkinter as tk
from tkinter import messagebox

def start_mission():
    messagebox.showinfo("Jarvis", "Mission Started!")

root = tk.Tk()
root.geometry("500x100")
btn = tk.Button(root, text="ENGAGE", command=start_mission, bg="blue", fg="white")
btn.pack(pady=20)
root.mainloop()