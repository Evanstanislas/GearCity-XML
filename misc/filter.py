import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import xml.etree.ElementTree as ET

class XMLFilterApp:
    def __init__(self, root):
        """Initializes the main application window and its components."""
        self.root = root
        self.root.title("XML Company Filter")
        self.root.geometry("450x200")
        self.root.resizable(False, False)

        self.file_path = None
        self.setup_ui()

    def setup_ui(self):
        """Sets up the graphical user interface with buttons and inputs."""
        main_frame = ttk.Frame(self.root, padding="15 15 15 15")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # 1. File Selection Section
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=5)
        
        select_button = ttk.Button(file_frame, text="Select XML File", command=self.select_file)
        select_button.pack(side=tk.LEFT, padx=(0, 10))

        self.file_label = ttk.Label(file_frame, text="No file selected")
        self.file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 2. Founded Year Input
        year_frame = ttk.Frame(main_frame)
        year_frame.pack(fill=tk.X, pady=5)

        ttk.Label(year_frame, text="Founded Year <=:").pack(side=tk.LEFT)
        self.year_entry = ttk.Entry(year_frame, width=10)
        self.year_entry.insert(0, "1900")  # Default value
        self.year_entry.pack(side=tk.LEFT, padx=(5, 0))

        # 3. Execute Button
        execute_button = ttk.Button(main_frame, text="Execute Filter", command=self.execute_filter)
        execute_button.pack(pady=15)
        
    def select_file(self):
        """Opens a file dialog for the user to select an XML file."""
        self.file_path = filedialog.askopenfilename(
            defaultextension=".xml",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        if self.file_path:
            self.file_label.config(text=self.file_path)

    def execute_filter(self):
        """
        Executes the filtering logic using the selected file and entered year.
        Shows a pop-up message when complete.
        """
        if not self.file_path:
            messagebox.showwarning("Warning", "Please select an XML file first.")
            return

        try:
            max_founded_year = int(self.year_entry.get())
            output_file = f"{max_founded_year}_filtered_companies.xml"
            self.filter_and_reindex_companies(self.file_path, output_file, max_founded_year)
            messagebox.showinfo("Success", f"Filtering complete! The new file has been saved as:\n{output_file} 🎉")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for the year.")
        except Exception as e:
            messagebox.showerror("An Error Occurred", f"An unexpected error occurred:\n{e}")

    def filter_and_reindex_companies(self, input_file: str, output_file: str, max_founded_year: int):
        """
        Parses an XML file, filters companies based on a maximum 'Founded' year,
        and then re-indexes the ID and OwnerID attributes.
        """
        try:
            tree = ET.parse(input_file)
            root = tree.getroot()
            new_root = ET.Element("AINode")
            new_id = 1

            for company in root.findall('Company'):
                founded_year = int(company.get('Founded'))
                if founded_year <= max_founded_year:
                    company.set('ID', str(new_id))
                    company.set('OwnerID', str(new_id))
                    company.set('Founded', str(max_founded_year))
                    new_root.append(company)
                    new_id += 1

            new_tree = ET.ElementTree(new_root)
            new_tree.write(output_file, encoding='utf-8', xml_declaration=True)

        except ET.ParseError as e:
            raise Exception(f"Failed to parse XML file: {e}")
        except FileNotFoundError:
            raise Exception(f"File not found: '{input_file}'")

if __name__ == "__main__":
    root = tk.Tk()
    app = XMLFilterApp(root)
    root.mainloop()