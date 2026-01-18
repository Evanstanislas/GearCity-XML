#Import packages
import ttkbootstrap as ttk
from tkinter import filedialog
import xml.etree.ElementTree as ET
from ttkbootstrap.dialogs import Messagebox

# Import from files
from settings.style import setup_styles, SPACING
from ui import CreateTable, CreateCompanyDetails, CreateButtons, ActivateButton
from logic.CRUD import (build_new_company, get_company_details, write_company_changes, 
                   delete_company_and_reindex, pick_new_selection, prepare_field_value, 
                   apply_generic_ai, get_selected_company, reselect_company)
from logic.xml_utils import (load_xml_file, save_xml_to_file, build_new_xml_with_company, 
                       build_city_map_from_xml, load_city_xml, ExportExcel)
from logic.ui_utils import refresh_editor_ui

class XMLEditor:
    # 🏗️ Initialization
    def __init__(self):
        self.root = ttk.Tk()
        self.style = ttk.Style("cyborg")
        self.root.title("Gearcity XML Editor")
        self.root.geometry("1400x800")

        # Apply external styles 🎨
        self.font_obj = setup_styles(self.style)
        self.company_map = {}
        self.city_map = {}
        self.preset_vars = {}

        # Main container for layout
        main_frame = ttk.Frame(self.root, padding=SPACING["md"])
        main_frame.pack(fill="both", expand=True)

        # 2 columns: left = details, right = table
        main_frame.columnconfigure(0, weight=1, minsize=700)
        main_frame.columnconfigure(1, weight=3, minsize=400)
        main_frame.rowconfigure(1, weight=1)

        CreateButtons(self, main_frame)
        CreateCompanyDetails(self, main_frame)
        CreateTable(self, main_frame)

    # 🎛️ UI Event Handlers
    def show_details(self, event):
        selected_item = self.table.selection()
        if not selected_item:
            return

        item = self.table.item(selected_item)
        company_id = item['values'][0]

        details = get_company_details(self.xml_root, company_id)

        for key, val in details.items():
            if key in self.detail_vars:
                main_val, dropdown_val = prepare_field_value(
                    key, val, self.field_types,
                    {"company_map": self.company_map, "city_map": self.city_map}  # pass sources
                )
                self.detail_vars[key].set(main_val)
                if dropdown_val is not None:
                    dropdown_var = self.detail_vars.get(f"{key}_dropdown")
                    if dropdown_var is not None:
                        dropdown_var.set(dropdown_val)

    # Upload Files
    def upload_xml_file(self):
        """Open file dialog, load XML, refresh UI."""
        file_path = filedialog.askopenfilename(
            title="Select XML File",
            filetypes=[("XML files", "*.xml")]
        )
        if not file_path:
            return  # user cancelled

        try:
            self.xml_root = load_xml_file(file_path)
            self.last_file = file_path   # ⭐ remember last file

            # 🔄 Update everything
            refresh_editor_ui(self)
            ActivateButton(self)

            Messagebox.show_info(f"XML loaded successfully! 🎉\n{file_path}", "Success")

        except Exception as e:
            Messagebox.show_error(f"Something went wrong 😢\n\n{e}", "Unexpected Error")

    def upload_city_xml(self):
        # Open file dialog to select XML
        file_path = filedialog.askopenfilename(
            title="Select City XML",
            filetypes=[("XML Files", "*.xml")]
        )
        if file_path:
            try:
                self.city_xml_root = load_city_xml(file_path)
                build_city_map_from_xml(self)
                refresh_editor_ui(self)
                Messagebox.show_info(f"City XML uploaded!\n", "Success")
            except Exception as e:
                Messagebox.show_error(f"Failed to load City XML:\n{e}", "Error")

    # 📝 Company CRUD
    def add_new_company(self):
        new_company, new_id = build_new_company(self.xml_root)
        self.xml_root.append(new_company)

        refresh_editor_ui(self)
        # 🔑 reselect last row
        children = self.table.get_children()
        if children:
            last_iid = children[-1]
            item = self.table.item(last_iid)
            company_id = str(item["values"][0])
            reselect_company(self, company_id)
            return new_company

    def save_ai_company(self):
        company, company_id, _ = get_selected_company(self)
        if company is None:
            return
        write_company_changes(company, self.detail_vars, self.field_types)

        refresh_editor_ui(self)
        reselect_company(self, company_id)
        Messagebox.show_info("AI company changes saved (in memory).", "Saved")

    def delete_ai_company(self):
        company, company_id, index = get_selected_company(self)
        if company is None:
            return
        delete_company_and_reindex(self.xml_root, index+1)
        refresh_editor_ui(self)

        # choose a sensible selection: same index (or the last one)
        children = self.table.get_children()
        new_iid = pick_new_selection(children, index)
        if new_iid:
            item = self.table.item(new_iid)
            new_company_id = str(item["values"][0])
            reselect_company(self, new_company_id)
        else:
            for k, var in self.detail_vars.items():
                try:
                    var.set("")
                except Exception:
                    pass
        Messagebox.show_info(f"Company {company_id} deleted and IDs reindexed.", "Deleted")

    def generic_ai_company(self):
        company, company_id, _ = get_selected_company(self)
        if company is None:
            return

        apply_generic_ai(company)

        refresh_editor_ui(self)
        reselect_company(self, company_id)
        Messagebox.show_info(f"Company {company_id} has it's value set to generic.", "Done")

    # 📂 File Handling (Load/Save/New)
    def save_to_xml(self):
        if not hasattr(self, "xml_root") or self.xml_root is None:
            Messagebox.show_warning("Please load or create an XML before saving.", "No XML Loaded")
            return

        initial_file = getattr(self, "last_file", "companies.xml")

        file_path = filedialog.asksaveasfilename(
            title="Save XML File",
            defaultextension=".xml",
            initialfile=initial_file,
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )

        if not file_path:
            return  # user cancelled

        try:
            save_xml_to_file(self.xml_root, file_path)   # 👉 hand off logic
            self.last_file = file_path
            Messagebox.show_info(f"XML saved successfully to:\n{file_path}", "Success")
        except Exception as e:
            Messagebox.show_error(f"Failed to save XML:\n{e}", "Error")

    def save_quick(self):
        """Quick-save: overwrite last loaded/saved file directly."""
        if not hasattr(self, "xml_root") or self.xml_root is None:
            Messagebox.show_warning("Please load or create an XML before saving.", "No XML Loaded")
            return

        # Fall back to Save As if no known file
        if not hasattr(self, "last_file") or not self.last_file:
            self.save_to_xml()
            return

        try:
            save_xml_to_file(self.xml_root, self.last_file)
            Messagebox.show_info(f"XML saved successfully to:\n{self.last_file}", "Success")
        except Exception as e:
            Messagebox.show_error(f"Failed to save XML:\n{e}", "Error")

    def new_ai_xml(self):
        # ⚠️ Confirm with the user before wiping
        if hasattr(self, "xml_root") and self.xml_root is not None:
            if not Messagebox.show_question("This will erase the current XML. Continue?", "Confirm"):
                return

        # Build a brand-new XML
        self.xml_root = build_new_xml_with_company()

        # Reset last_file, so Save As is required
        self.last_file = None

        # Refresh UI
        refresh_editor_ui(self)
        ActivateButton(self)

        Messagebox.show_info("A new AI XML has been created with 1 starter company.", "New XML")

    # Export Excel
    def export_excel(self):
        file_path = filedialog.asksaveasfilename(
                    defaultextension=".xlsx",
                    filetypes=[("Excel Files", "*.xlsx")]
                )
        if not file_path:
            return
        ExportExcel(self.xml_root, file_path)

        Messagebox.show_info(f"XML has been exported as {file_path}", "Exported")

    def run(self):
        self.root.mainloop()