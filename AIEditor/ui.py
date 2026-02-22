# import from packages
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.tableview import Tableview

#import from different files
from AIEditor.settings.config import column_widths, FIELD_TYPES, FIELD_LAYOUT, GENERIC_MAP, CREDIT_MAP
from style import (
    SPACING,
    InitialWidth,
    TABLEVIEW_STYLE,
    TABLEVIEW_ROW_HEIGHT,
)
from AIEditor.logic.preset_utils import PRESET_CONFIG
from AIEditor.logic.tableview_editing import (
    cancel_tableview_cell_edit,
    start_tableview_cell_edit,
)
from AIEditor.logic.ui_utils import (
    compute_entry_widths,
    create_widget,
    sort_by_column,
    build_tableview_column_options,
    populate_company_tableview,
)

def CreateButtons(self, main_frame):
    btn_frame = ttk.Frame(main_frame)
    btn_frame.grid(row=0, column=0, padx=SPACING["sm"], pady=SPACING["sm"])

    self.add_button = ttk.Button(btn_frame, text="Add AI", command=self.add_new_company, state="disabled")
    self.add_button.pack(side="left", padx=SPACING["sm"])

    self.save_ai_btn = ttk.Button(btn_frame, text="Save AI", command=self.save_ai_company, state="disabled", bootstyle="success")
    self.save_ai_btn.pack(side="left", padx=SPACING["sm"])

    self.delete_ai_btn = ttk.Button(btn_frame, text="Delete AI", command=self.delete_ai_company, state="disabled", bootstyle="danger")
    self.delete_ai_btn.pack(side="left", padx=SPACING["sm"])

    self.generic_ai_btn = ttk.Button(btn_frame, text="Generic AI", command=self.generic_ai_company, state="disabled", bootstyle="secondary")
    self.generic_ai_btn.pack(side="left", padx=SPACING["sm"])

    self.switch_mode_btn = ttk.Button(btn_frame, text="Switch Mode", command=self.switch_mode, state="disabled", bootstyle="secondary")
    self.switch_mode_btn.pack(side="left", padx=SPACING["sm"])

def ActivateButton(self):
    if hasattr(self, "sync_editor_action_buttons"):
        self.sync_editor_action_buttons()
        return
    self.save_ai_btn.config(state="normal")
    self.add_button.config(state="normal")
    self.delete_ai_btn.config(state="normal")
    self.generic_ai_btn.config(state="normal")
    self.switch_mode_btn.config(state="normal")

# Creating table
def CreateTable(self, main_frame):
    table_frame = ttk.Frame(main_frame)
    table_frame.grid(row=0, column=0, sticky="nsew", padx=SPACING["md"], pady=SPACING["md"])
    self.table_container = table_frame

    self.table = ttk.Treeview(table_frame)
    self.table['columns'] = ("ID", "Name", "Owner", "HQ", "Founded", "Death", "Funds")

    self.table.heading("#0", text="", anchor="w")
    self.table.column("#0", width=0, stretch=False)

    for col in self.table['columns']:
        self.table.heading(
            col,
            text=col,
            command=lambda _col=col: sort_by_column(self.table, _col, False)
        )
        self.table.column(col, anchor="w", width=column_widths.get(col, 100))

    vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
    self.table.configure(yscrollcommand=vsb.set)

    self.table.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")

    self.table.bind("<<TreeviewSelect>>", self.show_details)

def CreateSecondaryTableview(self, main_frame):
    tableview_frame = ttk.Frame(main_frame)
    tableview_frame.grid(row=0, column=0, sticky="nsew", padx=SPACING["md"], pady=SPACING["md"])
    self.tableview_container = tableview_frame
    tableview_frame.columnconfigure(0, weight=1)
    tableview_frame.rowconfigure(1, weight=1)

    control_frame = ttk.Frame(tableview_frame)
    control_frame.grid(row=0, column=0, sticky="ew", pady=(0, SPACING["sm"]))
    control_frame.columnconfigure(1, weight=1)

    ttk.Label(control_frame, text="Which column do you want to be available:").grid(
        row=0, column=0, sticky="w", padx=(0, SPACING["sm"])
    )

    self.tableview_column_options = build_tableview_column_options()
    self.tableview_column_var = ttk.StringVar()
    self.tableview_column_combo = ttk.Combobox(
        control_frame,
        textvariable=self.tableview_column_var,
        values=list(self.tableview_column_options.keys()),
        state="readonly",
        width=35,
    )
    self.tableview_column_combo.grid(row=0, column=1, sticky="ew")
    self.tableview_pending_edits = {}
    self.tableview_inline_editor = None
    self.tableview_edit_context = None

    self.tableview_selected_field_key = "Funds_OnHand"
    default_label = None
    for label, field_key in self.tableview_column_options.items():
        if field_key == self.tableview_selected_field_key:
            default_label = label
            break
    if default_label is None and self.tableview_column_options:
        default_label = next(iter(self.tableview_column_options.keys()))
        self.tableview_selected_field_key = self.tableview_column_options[default_label]
    if default_label is None:
        default_label = "Starting Funds"
    self.tableview_column_var.set(default_label)

    def on_column_change(event=None):
        cancel_tableview_cell_edit(self)
        selected_label = self.tableview_column_var.get()
        self.tableview_selected_field_key = self.tableview_column_options.get(selected_label, "Funds_OnHand")
        populate_company_tableview(self)

    self.tableview_column_combo.bind("<<ComboboxSelected>>", on_column_change)

    coldata = [
        {"text": "ID", "stretch": False},
        {"text": "Name", "stretch": True},
        {"text": default_label, "stretch": True},
    ]
    rowdata = []

    self.secondary_tableview = Tableview(
        master=tableview_frame,
        coldata=coldata,
        rowdata=rowdata,
        paginated=False,
        searchable=False,
        autofit=True,
        autoalign=False,
        stripecolor=None,
        yscrollbar=True
    )
    self.secondary_tableview.grid(row=1, column=0, sticky="nsew")
    self.style.configure(TABLEVIEW_STYLE, rowheight=TABLEVIEW_ROW_HEIGHT)
    self.secondary_tableview.view.configure(style=TABLEVIEW_STYLE)
    self.secondary_tableview.view.bind("<Double-1>", lambda e: start_tableview_cell_edit(self, e))

def CreateCompanyDetails(app, main_frame):
    """Build company detail frames and entries"""

    # Outer container (fixed area)
    detail_frame = ttk.Frame(main_frame)
    detail_frame.grid(
        row=0, column=0, sticky="nsew",
        padx=SPACING["md"], pady=SPACING["md"]
    )
    detail_frame.grid_propagate(False)

    content_frame = ScrolledFrame(
        detail_frame,
        autohide=True,
    )
    content_frame.pack(fill="both", expand=True)

    app.detail_labels = {}
    app.detail_vars = {}
    app.field_types = {}

    frames = {
        "Identity": ttk.LabelFrame(content_frame, text="Identity"),
        "Funds": ttk.LabelFrame(content_frame, text="Funds"),
        "Skills": ttk.LabelFrame(content_frame, text="Skills"),
        "Design": ttk.LabelFrame(content_frame, text="Design"),
        "Image": ttk.LabelFrame(content_frame, text="Image"),
        "Behavior": ttk.LabelFrame(content_frame, text="Behavior"),
        "Aggressions": ttk.LabelFrame(content_frame, text="Aggressions"),
    }

    for f in frames.values():
        f.pack(fill="x", padx=SPACING["s"], pady=SPACING["s"])

    for section, fields in FIELD_LAYOUT.items():
        frame = frames[section]
        for ftype, fdefs in fields:
            if ftype == "single":
                make_multi_entry(app, frame, [(fdefs[0][0], fdefs[0][1])])
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
            else:
                make_multi_entry(app, frame, fdefs)
    return detail_frame

def make_multi_entry(editor, frame, fields):
    row = ttk.Frame(frame)
    row.pack(fill="x", padx=SPACING["sm"], pady=SPACING["xs"])

    label_width, entry_width = compute_entry_widths(len(fields))

    for key, display_name in fields:
        subframe = ttk.Frame(row)
        subframe.pack(side="left", padx=(SPACING["xs"], SPACING["md"]))

        var = ttk.StringVar(value="")
        lbl = ttk.Label(subframe, text=f"{display_name}: ",
                        width=label_width, anchor="w")
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

    var = ttk.StringVar(value="")

    lbl = ttk.Label(
        subframe,
        text=f"{display_name}: ",
        width=InitialWidth, anchor="w",
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
        state="readonly"
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
