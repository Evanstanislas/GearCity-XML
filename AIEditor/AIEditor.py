#Import packages
import ttkbootstrap as ttk
from tkinter import filedialog
from ttkbootstrap.dialogs import Messagebox

# Import from files
from style import SPACING, TABLEVIEW_STYLE, TABLEVIEW_ROW_HEIGHT
from AIEditor.ui import CreateTable, CreateSecondaryTableview, CreateCompanyDetails, CreateButtons, ActivateButton
from AIEditor.logic.CRUD import (build_new_company, get_company_details, write_company_changes, 
                   delete_company_and_reindex, pick_new_selection, prepare_field_value, 
                   apply_generic_ai, get_selected_company, reselect_company)
from AIEditor.logic.xml_utils import (load_xml_file, save_xml_to_file, build_new_xml_with_company, 
                       build_city_map_from_xml, load_city_xml, ExportExcel, AnalyzeXML, has_xml)
from AIEditor.logic.ui_utils import refresh_editor_ui, save_tableview_edits, apply_tableview_row_colors

class AIEditor(ttk.Frame):
    # 🏗️ Initialization
    def __init__(self, app, master=None):
        super().__init__(master)
        self.app = app
        self.root = app.root
        self.style = app.style
        self.editor_mode = "table"
        self.table_available = True
        self.company_map = {}
        self.city_map = {}
        self.preset_vars = {}

        # Main container for layout
        main_frame = ttk.Frame(self, padding=SPACING["md"])
        main_frame.pack(fill="both", expand=True)

        # 2 columns: left = details, right = table
        main_frame.columnconfigure(0, weight=1, minsize=700)
        main_frame.columnconfigure(1, weight=3, minsize=400)
        main_frame.rowconfigure(0, weight=1)

        CreateCompanyDetails(self, main_frame)

        # RIGHT: container
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky="nsew")

        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)  # table expands
        CreateButtons(self, right_frame)
        self.right_content_frame = ttk.Frame(right_frame)
        self.right_content_frame.grid(row=1, column=0, sticky="nsew")
        self.right_content_frame.columnconfigure(0, weight=1)
        self.right_content_frame.rowconfigure(0, weight=1)

        CreateTable(self, self.right_content_frame)
        CreateSecondaryTableview(self, self.right_content_frame)
        self.tableview_container.grid_remove()
        self.sync_editor_action_buttons()

    def has_loaded_xml(self):
        return hasattr(self, "xml_root") and self.xml_root is not None

    def is_table_usable(self):
        if not getattr(self, "table_available", False):
            return False
        return hasattr(self, "table") and self.table is not None

    def set_editor_mode(self, mode):
        if mode == "table":
            if hasattr(self, "tableview_container"):
                self.tableview_container.grid_remove()
            if hasattr(self, "table_container"):
                self.table_container.grid()
            self.editor_mode = "table"
            self.table_available = True
            return

        if hasattr(self, "table_container"):
            self.table_container.grid_remove()
        if hasattr(self, "tableview_container"):
            self.tableview_container.grid()
        self.editor_mode = "tableview"
        self.table_available = False

    def refresh_ui_after_xml_change(self):
        refresh_editor_ui(self)
        ActivateButton(self)

    def save_xml_to_path(self, file_path):
        try:
            save_xml_to_file(self.xml_root, file_path)
            self.last_file = file_path
            self.show_info(f"XML saved successfully to:\n{file_path}", "Success")
            return True
        except Exception as e:
            self.show_error(f"Failed to save XML:\n{e}", "Error")
            return False

    def show_info(self, message, title="Info"):
        Messagebox.show_info(message, title)

    def show_error(self, message, title="Error"):
        Messagebox.show_error(message, title)

    def show_warning(self, message, title="Warning"):
        Messagebox.show_warning(message, title)

    def show_table_view(self):
        self.set_editor_mode("table")

    def show_tableview_mode(self):
        self.set_editor_mode("tableview")

    def sync_editor_action_buttons(self):
        has_xml = self.has_loaded_xml()
        table_mode = self.editor_mode == "table"

        if table_mode and has_xml:
            table_state = "normal"
        else:
            table_state = "disabled"

        self.save_ai_btn.config(state="normal" if has_xml else "disabled")
        self.add_button.config(state=table_state)
        self.delete_ai_btn.config(state=table_state)
        self.generic_ai_btn.config(state=table_state)
        self.switch_mode_btn.config(state="normal" if has_xml else "disabled")

    def refresh_tableview_style(self):
        if not hasattr(self, "secondary_tableview") or self.secondary_tableview is None:
            return
        self.style.configure(TABLEVIEW_STYLE, rowheight=TABLEVIEW_ROW_HEIGHT)
        self.secondary_tableview.view.configure(style=TABLEVIEW_STYLE)
        apply_tableview_row_colors(self)

    def checkXML(self):
        if not has_xml(getattr(self, "xml_root", None)):
            self.show_error("There's no XML yet", "Error")
            return False
        return True
    
    def overwriteXML(self):
        if hasattr(self, "xml_root") and self.xml_root is not None:
            return Messagebox.show_question(
                "This will erase the current XML. Continue?",
                "Confirm"
            )
        return True

    # 🎛️ UI Event Handlers
    def show_details(self, event):
        if not self.is_table_usable():
            return

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

    def new_ai_xml(self):
        # ⚠️ Confirm with the user before wiping
        if not self.overwriteXML():
            return

        # Build a brand-new XML
        self.xml_root = build_new_xml_with_company()

        # Reset last_file, so Save As is required
        self.last_file = None

        # Refresh UI
        self.refresh_ui_after_xml_change()

        self.show_info("A new AI XML has been created with 1 starter company.", "New XML")

    # Upload Files
    def upload_xml_file(self):
        """Open file dialog, load XML, refresh UI."""
        if not self.overwriteXML():
            return

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
            self.refresh_ui_after_xml_change()

            self.show_info(f"XML loaded successfully! 🎉\n{file_path}", "Success")

        except Exception as e:
            self.show_error(f"Something went wrong 😢\n\n{e}", "Unexpected Error")

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
                self.show_info(f"City XML uploaded!\n", "Success")
            except Exception as e:
                self.show_error(f"Failed to load City XML:\n{e}", "Error")

    # 📝 Company CRUD
    def add_new_company(self):
        new_company, _ = build_new_company(self.xml_root)
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
        if self.editor_mode == "tableview":
            if not self.checkXML():
                return

            applied, errors = save_tableview_edits(self)

            if applied > 0:
                refresh_editor_ui(self)

            if errors:
                self.show_warning(
                    "Some edits could not be saved:\n" + "\n".join(errors),
                    "Partial Save"
                )
                return

            if applied == 0:
                self.show_info("No table edits to save.", "Saved")
                return

            self.show_info(f"{applied} table edit(s) saved (in memory).", "Saved")
            return

        company, company_id, _ = get_selected_company(self)
        if company is None:
            return
        write_company_changes(company, self.detail_vars, self.field_types)

        refresh_editor_ui(self)
        reselect_company(self, company_id)
        self.show_info("AI company changes saved (in memory).", "Saved")

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
        self.show_info(f"Company {company_id} deleted and IDs reindexed.", "Deleted")

    def generic_ai_company(self):
        company, company_id, _ = get_selected_company(self)
        if company is None:
            return

        apply_generic_ai(company)

        refresh_editor_ui(self)
        reselect_company(self, company_id)
        self.show_info(f"Company {company_id} has it's value set to generic.", "Done")

    # 📂 File Handling (Load/Save/New)
    def save_to_xml(self):
        if not self.checkXML():
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

        self.save_xml_to_path(file_path)

    def save_quick(self):
        """Quick-save: overwrite last loaded/saved file directly."""
        if not self.checkXML():
            return
        # Fall back to Save As if no known file
        if not hasattr(self, "last_file") or not self.last_file:
            self.save_to_xml()
            return

        self.save_xml_to_path(self.last_file)

    # Export Excel
    def export_excel(self):
        if not self.checkXML():
            return
        file_path = filedialog.asksaveasfilename(
                    defaultextension=".xlsx",
                    filetypes=[("Excel Files", "*.xlsx")]
                )
        if not file_path:
            return
        ExportExcel(self.xml_root, file_path)
        self.show_info(f"XML has been exported as {file_path}", "Exported")

    def switch_mode(self):
        if self.editor_mode == "table":
            self.show_tableview_mode()
        else:
            self.show_table_view()
        self.sync_editor_action_buttons()
        
    def analyze_xml(self):
        if not self.checkXML():
            return
        AnalyzeXML(self.xml_root)
