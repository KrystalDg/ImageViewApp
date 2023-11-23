# import tkinter as tk
# from tkinter import filedialog, ttk

# root = tk.Tk()

# style = ttk.Style(root)
# style.theme_use("clam")
# style.configure("my.TButton", bordercolor="red")

# ttk_button = ttk.Button(root, text="Go UP", style="my.TButton")
# ttk_button.pack()

# root.mainloop()

# import tkinter as tk
# from tkinter import ttk

# master = tk.Tk()

# style = ttk.Style()
# style.theme_use("default")

# style.map(
#     "Mod.TButton",
#     background=[("active", "red"), ("!active", "blue")],
#     foreground=[("active", "yellow"), ("!active", "red")],
# )

# txt_btn = ttk.Button(master, text="Text", style="Mod.TButton").pack()

# master.mainloop()


# from tkinter import ttk
# import tkinter as tk
# root = tk.Tk()

# style = ttk.Style()
# style.configure('Custom.TLabel', background='red')

# slider = ttk.Button(root, text="Hello World", style='Custom.TLabel')
# slider.pack(pady=20)

# root.mainloop()      

import tkinter
from tkinter import ttk

import sv_ttk

root = tkinter.Tk()

button = ttk.Button(root, text="Click me!")
button.pack()

# This is where the magic happens
sv_ttk.set_theme("dark")

root.mainloop()