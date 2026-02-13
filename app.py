import ttkbootstrap as ttk

from style import setup_styles, unbound
from AIEditor.AIEditor import AIEditor

class App:
    def __init__(self):
        self.root = ttk.Tk()
        self.style = ttk.Style("cyborg")
        self.root.title("Gearcity XML Editor")
        self.root.geometry("1400x800")
        self.mode = ttk.IntVar()

        # Unbound the scroll wheel from SpinBox and ComboBox
        unbound(self.root)

        # Build UI screen
        self.editor = AIEditor(self, master=self.root)
        self.editor.pack(fill="both", expand=True)

        self.CreateMenuBar()

        # Expose table for styling helpers
        self.table = self.editor.table

        # Apply external styles 🎨
        setup_styles(self)

    def CreateMenuBar(self):
        menubar = ttk.Menu(self.root)

        # FILE MENU
        file_menu = ttk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New AI XML", command=self.editor.new_ai_xml)
        file_menu.add_command(label="Upload AI XML", command=self.editor.upload_xml_file)
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self.editor.save_quick)
        file_menu.add_command(label="Save As", command=self.editor.save_to_xml)
        file_menu.add_separator()
        file_menu.add_command(label="Export to Excel", command=self.editor.export_excel)
        menubar.add_cascade(label="File", menu=file_menu)

        # TOOLS MENU
        tools_menu = ttk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Upload City XML", command=self.editor.upload_city_xml)
        tools_menu.add_command(label="Analyze XML", command=self.editor.analyze_xml)
        menubar.add_cascade(label="Tools", menu=tools_menu)

        # VIEW MENU
        view_menu = ttk.Menu(menubar, tearoff=0)
        self.change_theme = view_menu.add_checkbutton(label="Light Mode", variable=self.mode, onvalue=0, offvalue=1, command=self.changeTheme)
        menubar.add_cascade(label="View", menu=view_menu)

        self.root.config(menu=menubar)

    def changeTheme(self):
        if self.mode.get() == 0:
            self.style.theme_use("cyborg")
            setup_styles(self)
        else:
            self.style.theme_use("flatly")
            setup_styles(self)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = App()
    app.run()