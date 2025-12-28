
import tkinter as tk

root = tk.Tk()
root.title("Jarvis: Foundation")
root.geometry("500x100")
wall_frame = tk.Frame(root, bg="gray", padx=10, pady=10)
wall_frame.pack(pady=20) 
tk.Label(wall_frame, text="I am inside a Frame").pack()

root.mainloop()



