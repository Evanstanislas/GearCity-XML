import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Alternating Row Colors in Treeview")

style = ttk.Style()
style.configure("oddrow", background="#AAAAAA")  # Light gray
style.configure("evenrow", background="#FFFFFF") # White

tree = ttk.Treeview(root, columns=("col1", "col2"), show="headings")
tree.heading("col1", text="Data Column 1")
tree.heading("col2", text="Data Column 2")
tree.pack(expand=True, fill="both")

data = [
    ("Apple", 10),
    ("Banana", 25),
    ("Orange", 15),
    ("Grape", 30),
    ("Strawberry", 20),
]

for i, row_data in enumerate(data):
    tag = "evenrow" if i % 2 == 0 else "oddrow"
    tree.insert("", "end", values=row_data, tags=(tag,))

root.mainloop()