#Import packages
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import xml.etree.ElementTree as ET

# Import from files
from settings.style import setup_styles
from settings.theme import SPACING
from ui import CreateTable, CreateCompanyDetails, CreateButtons, ActivateButton
from logic.CRUD import (build_new_company, get_company_details, write_company_changes, 
                   delete_company_and_reindex, pick_new_selection, prepare_field_value)
from logic.xml_utils import (load_xml_file, save_xml_to_file, build_new_xml_with_company, 
                       build_city_map_from_xml, load_city_xml, ExportExcel)
from logic.ui_utils import refresh_editor_ui

class XMLEditor:
    # ================================
    # 🏗️ Initialization
    # ================================
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Gearcity XML Editor")
        self.root.geometry("1400x800")

        # Apply external styles 🎨
        self.font_obj = setup_styles(self.root)
        self.company_map = {}
        self.city_map = {}
        self.preset_vars = {}

        # -------------------------
        # Main container for layout
        # -------------------------
        main_frame = ttk.Frame(self.root, padding=SPACING["md"])
        main_frame.pack(fill="both", expand=True)

        # 2 columns: left = details, right = table
        main_frame.columnconfigure(0, weight=0, minsize=600)
        main_frame.columnconfigure(1, weight=3, minsize=400)
        main_frame.rowconfigure(1, weight=1)  # row=1 is the big content row

        # -------------------------
        # Buttons row
        # -------------------------
        CreateButtons(self, main_frame)

        # -------------------------
        # Left: Company details
        # -------------------------
        CreateCompanyDetails(self, main_frame)  # will go row=1, col=0

        # -------------------------
        # Right: Table
        # -------------------------
        CreateTable(self, main_frame)           # will go row=1, col=1

    # ================================
    # 🎛️ UI Event Handlers
    # ================================

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

    # ================================
    # 📝 Company CRUD
    # ================================
    def add_new_company(self):
        new_company = build_new_company(self.xml_root)
        self.xml_root.append(new_company)
        refresh_editor_ui(self)
        return new_company
    
    def upload_xml_file(self):
        """Open file dialog, load XML, refresh UI."""
        file_path = filedialog.askopenfilename(
            title="Select XML File",
            filetypes=[("XML files", "*.xml")]
        )
        if not file_path:
            return  # user cancelled

        try:
            self.xml_root = load_xml_file(file_path)   # validated for Company XML
            self.last_file = file_path   # ⭐ remember last file

            # 🔄 Update everything
            refresh_editor_ui(self)
            ActivateButton(self)

            messagebox.showinfo("Success", f"XML loaded successfully! 🎉\n{file_path}")

        except ET.ParseError as e:
            messagebox.showerror("XML Error", f"Invalid or malformed XML 😢\n\n{e}")
        except ValueError as e:
            messagebox.showerror("Structure Error", f"XML structure not valid for AI XML 😭\n\n{e}")
        except UnicodeDecodeError as e:
            messagebox.showerror("Encoding Error", f"File encoding problem 😭\n\n{e}")
        except FileNotFoundError:
            messagebox.showerror("File Error", "File not found. Did it move?")
        except PermissionError:
            messagebox.showerror("File Error", "Permission denied. Try running as admin.")
        except OSError as e:
            messagebox.showerror("OS Error", f"Could not read file 😢\n\n{e}")
        except Exception as e:
            # final fallback
            messagebox.showerror("Unexpected Error", f"Something went wrong 😢\n\n{e}")

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
                    messagebox.showinfo("Success", f"City XML uploaded!\n")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load City XML:\n{e}")
    
    # CRUD Companies
    def save_ai_company(self):
        sel = self.table.selection()
        if not sel:
            messagebox.showwarning("No selection", "Please select a company row to save.")
            return

        iid = sel[0]
        item = self.table.item(iid)
        company_id = str(item['values'][0])

        company = self.xml_root.find(f"Company[@ID='{company_id}']")
        if company is None:
            messagebox.showerror("Error", "Selected company not found in XML.")
            return

        # 👉 hand off the logic part
        write_company_changes(company, self.detail_vars, self.field_types)

        refresh_editor_ui(self)

        for iid in self.table.get_children():
            vals = self.table.item(iid)['values']
            if str(vals[0]) == company_id:
                self.table.selection_set(iid)
                self.table.see(iid)
                self.show_details(None)
                break

        messagebox.showinfo("Saved", "AI company changes saved (in memory).")

    def delete_ai_company(self):
        """Delete the selected company, reindex IDs and OwnerIDs, refresh UI."""
        # 0) basic pre-check
        if not hasattr(self, "xml_root") or self.xml_root is None:
            messagebox.showwarning("No XML Loaded", "Please load an XML before deleting a company.")
            return

        sel = self.table.selection()
        if not sel:
            messagebox.showwarning("No selection", "Please select a company row to delete.")
            return

        selected_iid = sel[0]
        selected_index = self.table.index(selected_iid)  # index in the tree (for re-selection afterwards)
        item = self.table.item(selected_iid)
        company_id = str(item['values'][0])

        # confirm destructive action
        ok = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete Company ID {company_id}?\n\n"
            "This will remove the company and reindex ALL company IDs and OwnerIDs."
        )
        if not ok:
            return

        # perform deletion + reindex (logic.py helper)
        try:
            delete_company_and_reindex(self.xml_root, company_id)
        except KeyError:
            messagebox.showerror("Error", f"Company ID {company_id} not found in XML.")
            return
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete company:\n{e}")
            return

        # refresh UI
        refresh_editor_ui(self)

        # choose a sensible selection: same index (or the last one)
        children = self.table.get_children()
        new_iid = pick_new_selection(children, selected_index)
        if new_iid:
            self.table.selection_set(new_iid)
            self.table.see(new_iid)
            self.show_details(None)
        else:
            for k, var in self.detail_vars.items():
                try:
                    var.set("")
                except Exception:
                    pass

        messagebox.showinfo("Deleted", f"Company {company_id} deleted and IDs reindexed.")

    # ================================
    # 📂 File Handling (Load/Save/New)
    # ================================

    def save_to_xml(self):
        if not hasattr(self, "xml_root") or self.xml_root is None:
            messagebox.showwarning("No XML Loaded", "Please load or create an XML before saving.")
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
            messagebox.showinfo("Success", f"XML saved successfully to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save XML:\n{e}")

    def save_quick(self):
        """Quick-save: overwrite last loaded/saved file directly."""
        if not hasattr(self, "xml_root") or self.xml_root is None:
            messagebox.showwarning("No XML Loaded", "Please load or create an XML before saving.")
            return

        # Fall back to Save As if no known file
        if not hasattr(self, "last_file") or not self.last_file:
            self.save_to_xml()
            return

        try:
            save_xml_to_file(self.xml_root, self.last_file)   # 👉 use the same helper
            messagebox.showinfo("Success", f"XML saved successfully to:\n{self.last_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save XML:\n{e}")

    def new_ai_xml(self):
        # ⚠️ Confirm with the user before wiping
        if hasattr(self, "xml_root") and self.xml_root is not None:
            if not messagebox.askyesno("Confirm", "This will erase the current XML. Continue?"):
                return

        # Build a brand-new XML
        self.xml_root = build_new_xml_with_company()

        # Reset last_file, so Save As is required
        self.last_file = None

        # Refresh UI
        refresh_editor_ui(self)

        ActivateButton(self)

        messagebox.showinfo("New XML", "A new AI XML has been created with 1 starter company.")

    # Export Excel
    def export_excel(self):
        file_path = filedialog.asksaveasfilename(
                    defaultextension=".xlsx",
                    filetypes=[("Excel Files", "*.xlsx")]
                )
        if not file_path:
            return
        ExportExcel(self.xml_root, file_path)

        messagebox.showinfo("Exported", f"XML has been exported as {file_path}")
        

    # ================================
    # ▶️ Run
    # ================================
    def run(self):
        self.root.mainloop()