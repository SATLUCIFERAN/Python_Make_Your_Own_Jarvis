
import tkinter as tk

root = tk.Tk()
root.geometry("500x100")
root.title("Jarvis: Side-by-Side Layout")
# Create the container frame (The Wall)
time_frame = tk.Frame(root)
time_frame.pack(pady=20)
# Pack items INSIDE the frame from left to right
tk.Entry(time_frame, width=5).pack(side="left")
tk.Label(time_frame, text=" : ").pack(side="left")
tk.Entry(time_frame, width=5).pack(side="left")

root.mainloop()





