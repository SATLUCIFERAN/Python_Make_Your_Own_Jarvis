
import tkinter as tk

root = tk.Tk()
root.geometry("500x100")
# x=50 (pixels from left), y=50 (pixels from top)
label = tk.Label(root, text="Surgical Precision", bg="yellow")
label.place(x=50, y=20)
# Placing another gadget exactly below it
btn = tk.Button(root, text="Target Locked")
btn.place(x=50, y=60)

root.mainloop()











