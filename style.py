# Fonts
base_font = ("Segoe UI", 8)
bold_font = ("Segoe UI", 8, "bold")
header_font = ("Segoe UI", 9, "bold")

ROW_COLORS = {
    "oddRowDark": "#363636",
    "evenRowDark": "#232323",
    "oddRowLight": "#E8E8E8",
    "evenRowLight": "#D6D6D6"
}

TABLEVIEW_ROW_HEIGHT = 30
TABLEVIEW_ENTRY_PADDING_Y = 2
TABLEVIEW_STYLE = "TableviewEditable.Treeview"

TABLE_SELECTION_BG = {
    "Dark": "#51AECA",
    "Light": "#004D79"
}

SPACING = {
    "xs": 2,
    "s": 3,
    "sm": 5,
    "md": 10,
}

# For the input fields
InitialWidth=22
RowWidth=6

def setup_styles(self):
    self.root.option_add("*Font", base_font)
    self.style.configure("Treeview", rowheight=25)
    self.style.configure("Treeview.Heading", font=bold_font)
    self.style.configure("TButton", font=bold_font)
    self.style.configure("TLabelframe.Label", font=header_font)
    if self.mode.get() == 0: # DarkMode
        self.style.map("Treeview", background=[('selected', TABLE_SELECTION_BG["Dark"])])
    else: #LightMode
        self.style.map("Treeview", background=[('selected', TABLE_SELECTION_BG["Light"])])
    if hasattr(self, "table"):   # 🛡️ safety guard
        styleTable(self)
    if hasattr(self, "editor") and hasattr(self.editor, "refresh_tableview_style"):
        self.editor.refresh_tableview_style()
    
def styleTable(self):
    if self.mode.get() == 0:
        self.table.tag_configure("evenrow", background=ROW_COLORS["evenRowDark"])
        self.table.tag_configure("oddrow", background=ROW_COLORS["oddRowDark"])
    else:
        self.table.tag_configure("evenrow", background=ROW_COLORS["evenRowLight"])
        self.table.tag_configure("oddrow", background=ROW_COLORS["oddRowLight"])

def unbound(root):
    root.bind_class("TCombobox", "<MouseWheel>", lambda e: "break")
    root.bind_class("TCombobox", "<Button-4>", lambda e: "break")
    root.bind_class("TCombobox", "<Button-5>", lambda e: "break")
    root.bind_class("TSpinbox", "<MouseWheel>", lambda e: "break")
    root.bind_class("TSpinbox", "<Button-4>", lambda e: "break")
    root.bind_class("TSpinbox", "<Button-5>", lambda e: "break")
    return
