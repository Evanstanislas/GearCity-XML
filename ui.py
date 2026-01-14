# import from packages
import tkinter as tk
import tkinter.ttk as ttk

#import from different files
from settings.config import column_widths, InitialWidth, FIELD_TYPES, FIELD_LAYOUT, GENERIC_MAP, CREDIT_MAP
from settings.theme import SPACING
from logic.preset_utils import PRESET_CONFIG
from logic.ui_utils import compute_entry_widths, create_widget, sort_by_column

# Create Buttons
def CreateButtons(self, main_frame):
    # -------------------------
    # LEFT SIDE BUTTONS
    # -------------------------
    btn_frame_left = ttk.Frame(main_frame)
    btn_frame_left.grid(row=0, column=0, sticky="w", padx=SPACING["sm"], pady=SPACING["sm"])

    self.new_btn = ttk.Button(btn_frame_left, text="New AI XML", command=self.new_ai_xml)
    self.new_btn.pack(side="left", padx=SPACING["sm"])

    self.upload_btn = ttk.Button(btn_frame_left, text="Upload AI XML", command=self.upload_xml_file)
    self.upload_btn.pack(side="left", padx=SPACING["sm"])

    self.upload_city_btn = ttk.Button(btn_frame_left, text="Upload City XML", command=self.upload_city_xml)
    self.upload_city_btn.pack(side="left", padx=SPACING["sm"])

    self.save_btn = ttk.Button(btn_frame_left, text="Save", command=self.save_quick, state="disabled")
    self.save_btn.pack(side="left", padx=SPACING["sm"])

    self.saveAs_btn = ttk.Button(btn_frame_left, text="Save As", command=self.save_to_xml, state="disabled")
    self.saveAs_btn.pack(side="left", padx=SPACING["sm"])

    self.exportExcel_btn = ttk.Button(btn_frame_left, text="Export to Excel", command=self.export_excel, state="disabled")
    self.exportExcel_btn.pack(side="left", padx=SPACING["sm"])

    # -------------------------
    # RIGHT SIDE BUTTONS
    # -------------------------
    btn_frame_right = ttk.Frame(main_frame)
    btn_frame_right.grid(row=0, column=1, sticky="e", padx=SPACING["sm"], pady=SPACING["sm"])

    self.add_button = ttk.Button(btn_frame_right, text="Add AI", command=self.add_new_company, state="disabled")
    self.add_button.pack(side="left", padx=SPACING["sm"])

    self.save_ai_btn = ttk.Button(btn_frame_right, text="Save AI", command=self.save_ai_company, state="disabled", style="Accent.TButton")
    self.save_ai_btn.pack(side="left", padx=SPACING["sm"])

    self.delete_ai_btn = ttk.Button(btn_frame_right, text="Delete AI", command=self.delete_ai_company, state="disabled", style="Danger.TButton")
    self.delete_ai_btn.pack(side="left", padx=SPACING["sm"])

    self.generic_ai_btn = ttk.Button(btn_frame_right, text="Generic AI", command=self.generic_ai_company, state="disabled")
    self.generic_ai_btn.pack(side="left", padx=SPACING["sm"])

def ActivateButton(self):
    self.save_btn.config(state="normal")
    self.saveAs_btn.config(state="normal")
    self.save_ai_btn.config(state="normal")
    self.exportExcel_btn.config(state="normal")
    self.add_button.config(state="normal")
    self.delete_ai_btn.config(state="normal")
    self.generic_ai_btn.config(state="normal")

# Creating table
def CreateTable(self, main_frame):
    table_frame = ttk.Frame(main_frame)
    table_frame.grid(row=1, column=1, sticky="nsew", padx=SPACING["md"], pady=SPACING["md"])

    # 🌟 Create Treeview
    self.table = ttk.Treeview(table_frame)
    self.table['columns'] = ("ID", "Name", "Owner", "HQ", "Founded", "Death", "Funds")

    self.table.heading("#0", text="", anchor="w")
    self.table.column("#0", width=0, stretch=tk.NO)

    # 🌟 Create sortable headers
    for col in self.table['columns']:
        self.table.heading(
            col,
            text=col,
            command=lambda _col=col: sort_by_column(self.table, _col, False)
        )
        self.table.column(col, anchor="w", width=column_widths.get(col, 100))

    # 🌟 Create vertical scrollbar
    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
    self.table.configure(yscrollcommand=vsb.set)

    # 🌟 Pack table + scrollbar side by side
    self.table.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")

    # 🌟 Bind selection
    self.table.bind("<<TreeviewSelect>>", self.show_details)


def CreateCompanyDetails(app, parent):
    """Build company detail frames and entries"""
    detail_frame = ttk.Frame(parent)
    detail_frame.grid(row=1, column=0, sticky="nsew", padx=SPACING["md"], pady=SPACING["md"])
    detail_frame.grid_propagate(False)

    app.detail_labels = {}
    app.detail_vars = {}
    app.field_types = {}

    frames = {
        "Identity": ttk.LabelFrame(detail_frame, text="Identity"),
        "Funds": ttk.LabelFrame(detail_frame, text="Funds"),
        "Skills": ttk.LabelFrame(detail_frame, text="Skills"),
        "Design": ttk.LabelFrame(detail_frame, text="Design"),
        "Image": ttk.LabelFrame(detail_frame, text="Image"),
        "Behavior": ttk.LabelFrame(detail_frame, text="Behavior"),
        "Aggressions": ttk.LabelFrame(detail_frame, text="Aggressions"),
    }

    for f in frames.values():
        f.pack(fill="x", padx=SPACING["s"], pady=SPACING["s"])

    for section, fields in FIELD_LAYOUT.items():
        frame = frames[section]
        for ftype, fdefs in fields:
            if ftype == "single":
                make_single_entry(app, frame, fdefs[0][0], fdefs[0][1])
            elif ftype == "double":
                make_double_entry(app, frame, fdefs)
            elif ftype == "triple":
                make_triple_entry(app, frame, fdefs)
            elif ftype == "preset":
                key, label = fdefs[0]
                cfg = PRESET_CONFIG.get(key)
                if cfg:
                    make_preset_dropdown(
                        app,
                        frame,
                        key,
                        label,
                        cfg["dict"],
                        cfg["apply"],
                    )

    return detail_frame

def make_single_entry(editor, frame, key, display_name):
    make_multi_entry(editor, frame, [(key, display_name)])

def make_double_entry(editor, frame, fields):
    make_multi_entry(editor, frame, fields)

def make_triple_entry(editor, frame, fields):
    make_multi_entry(editor, frame, fields)

def make_multi_entry(editor, frame, fields):
    row = ttk.Frame(frame)
    row.pack(fill="x", padx=SPACING["sm"], pady=SPACING["xs"])

    label_width, entry_width = compute_entry_widths(len(fields))

    for key, display_name in fields:
        subframe = ttk.Frame(row)
        subframe.pack(side="left", padx=(SPACING["xs"], SPACING["md"]))

        var = tk.StringVar(value="")
        lbl = ttk.Label(subframe, text=f"{display_name}: ",
                        width=label_width, anchor="w", font=editor.font_obj)
        lbl.pack(side="left")

        field_cfg = FIELD_TYPES.get(key, {"type": "text"})
        
        if field_cfg.get("loans"):
            entry_width = InitialWidth

        entry, var = create_widget(editor, subframe, key, var, field_cfg, entry_width)

        entry.pack(side="left")

        if field_cfg.get("readonly"):
            try: entry.state(["readonly"])
            except Exception: entry.config(state="readonly")

        editor.detail_vars[key] = var
        editor.detail_labels[key] = entry
        editor.field_types[key] = field_cfg.get("type", "text")

def make_preset_dropdown(editor, frame, key, display_name, presets_dict, apply_func):
    """
    Create a dropdown for selecting presets (e.g. Funds).
    Aligns with multi_entry rows so UI looks consistent.
    """
    row = ttk.Frame(frame)
    row.pack(fill="x", padx=SPACING["sm"], pady=SPACING["xs"])

    # --- mimic multi_entry layout ---
    subframe = ttk.Frame(row)
    subframe.pack(side="left", padx=(SPACING["xs"], SPACING["md"]))

    var = tk.StringVar(value="")

    lbl = ttk.Label(
        subframe,
        text=f"{display_name}: ",
        width=InitialWidth, anchor="w",
        font=editor.font_obj
    )
    lbl.pack(side="left")

    # --- Build dropdown values ---
    if key.lower().endswith("credit"):
        values = list(CREDIT_MAP.keys())
    else:
        values = list(presets_dict.keys())

    dropdown = ttk.Combobox(
        subframe,
        textvariable=var,
        values=values,
        width=InitialWidth,
        state="readonly",
        font=editor.font_obj
    )
    dropdown.pack(side="left")

    # --- Event binding ---
    def on_select(event=None):
        chosen = var.get()
        print(f"[DEBUG] Preset selected: {chosen}")

        if key.lower().endswith("credit"):
            raw_value = CREDIT_MAP[chosen]   # map label back to number
            print(f"[DEBUG] Credit '{chosen}' mapped to {raw_value}")
            apply_func(editor, raw_value)
        elif key.lower().endswith("genericdesigner"):
            raw_value = GENERIC_MAP[chosen]   # map label back to number
            print(f"[DEBUG] Generic Designer '{chosen}' mapped to {raw_value}")
            apply_func(editor, raw_value)
        else:
            apply_func(editor, chosen)

    dropdown.bind("<<ComboboxSelected>>", on_select)

    # Save vars like the others
    editor.preset_vars[key] = var
    editor.detail_labels[key] = dropdown
    editor.field_types[key] = "preset"