import tkinter.font as tkFont

# Fonts
base_font = ("Segoe UI", 8)
bold_font = ("Segoe UI", 8, "bold")
header_font = ("Segoe UI", 9, "bold")

ROW_COLORS = {
    "oddrow": "#363636",
    "evenrow": "#232323"
}
TABLE_SELECTION_BG = "#51AECA"

SPACING = {
    "xs": 2,
    "s": 3,
    "sm": 5,
    "md": 10,
}

def setup_styles(style):
    """Apply global ttk styles to the app."""

    # Initialize fonts
    font_obj = tkFont.Font(font=base_font)
    # Table
    style.configure("Treeview", rowheight=25, font=base_font)
    style.map("Treeview", background=[("selected", TABLE_SELECTION_BG)])
    style.configure("Treeview.Heading", font=bold_font)

    # General
    style.configure("TLabel", font=base_font)
    style.configure("TButton", font=bold_font)
    style.configure("TLabelframe", font=header_font)
    style.configure("TLabelframe.Label", font=header_font)
    style.configure("TSpinbox", font=base_font)
    return font_obj

def unbound(root):
    root.bind_class("TCombobox", "<MouseWheel>", lambda e: "break")
    root.bind_class("TCombobox", "<Button-4>", lambda e: "break")
    root.bind_class("TCombobox", "<Button-5>", lambda e: "break")
    root.bind_class("TSpinbox", "<MouseWheel>", lambda e: "break")
    root.bind_class("TSpinbox", "<Button-4>", lambda e: "break")
    root.bind_class("TSpinbox", "<Button-5>", lambda e: "break")
    return