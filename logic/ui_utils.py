# import from packages
import tkinter as tk
import ttkbootstrap as ttk
import tkinter.font as tkFont

# import from different files
from settings.style import SPACING, styleTable
from settings.config import max_widths, FIELD_TYPES, InitialWidth, RowWidth, CREDIT_MAP, GENERIC_MAP

# 🎛️ UI Utilities
def get_treeview_font(style):
    font_name = style.lookup("Treeview", "font")

    if not font_name:
        font_name = "TkDefaultFont"

    return tkFont.nametofont(font_name)

def auto_resize_columns(table, style):
    font_obj = get_treeview_font(style)
    for col in table['columns']:
        if col in max_widths:
            # Force fixed width
            table.column(col, width=max_widths[col], stretch=False)
        else:
            # Auto-resize with min/max
            max_width = font_obj.measure(col) + 20
            for row in table.get_children():
                text = str(table.set(row, col))
                width = font_obj.measure(text)
                if width > max_width:
                    max_width = width
            table.column(col, width=max_width, stretch=True)

def sort_by_column(tree, col, reverse):
    """Sort Treeview by given column, auto-detecting numeric values (like $1,000)."""
    try:
        data = [(tree.set(k, col), k) for k in tree.get_children('')]

        def convert(value):
            """Convert to number if it looks numeric or starts with $."""
            if isinstance(value, str):
                s = value.strip()

                # Detect currency-style strings
                if s.startswith("$"):
                    s = s.replace("$", "").replace(",", "")
                    try:
                        return float(s)
                    except ValueError:
                        return s.lower()

                # Otherwise, try normal number conversion
                try:
                    return float(s)
                except ValueError:
                    return s.lower()

            return value

        data.sort(key=lambda t: convert(t[0]), reverse=reverse)

        for index, (_, k) in enumerate(data):
            tree.move(k, '', index)

        tree.heading(
            col,
            command=lambda _col=col, _rev=not reverse: sort_by_column(tree, _col, _rev)
        )

        print(f"[DEBUG] Sorted by '{col}', reverse={reverse}")

    except Exception as e:
        print(f"[DEBUG] sort_by_column error on '{col}': {e}")

def load_company_map(self):
    """
    Parse the XML and return {ID: Name} dict.
    Example:
        {1: "Toyota", 2: "Honda", 3: "Renault"}
    """
    company_map = {}
    for company in self.xml_root.findall("Company"):  # adjust tag as needed
        cid = int(company.get("ID"))  # or however ID is stored
        cname = company.get("Name")  # <-- FIXED, use attribute not element
        company_map[cid] = cname
    return company_map

def populate_company_table(self):
    """
    Repopulate the company table with data from the XML file.
    """
    # 🧹 Clear old rows
    for row in self.table.get_children():
        self.table.delete(row)

    if not self.xml_root:
        return  # ⛔ No XML loaded yet → nothing to show

    # ➕ Insert updated company rows
    for idx, company in enumerate(self.xml_root.findall("Company")):
        cid = company.get("ID")
        cname = company.get("Name")
        owner_id = company.get("OwnerID")

        # Convert owner ID → owner name
        owner_name = self.company_map.get(int(owner_id), owner_id) if owner_id else ""

        # 🏙️ HQ: convert ID → "Name, Country"
        hq_id = company.get("HQ", "")
        if hq_id:
            try:
                hq_id_int = int(hq_id)
                hq_name = self.city_map.get(hq_id_int, hq_id)
            except ValueError:
                hq_name = self.city_map.get(hq_id, hq_id)
        else:
            hq_name = ""

        founded = company.get("Founded", "")
        death = company.get("Death", "")

        # 💰 Funds
        funds_elem = company.find("Funds")
        funds_raw = funds_elem.get("OnHand") if funds_elem is not None else "0"
        try:
            funds = f"${int(funds_raw):,}"
        except ValueError:
            funds = funds_raw

        # Insert row
        values = (cid, cname, owner_name, hq_name, founded, death, funds)

        styleTable(self)
        tag = "evenrow" if idx % 2 == 0 else "oddrow"
        self.table.insert("", tk.END, values=values, tags=(tag,))

    # 📏 Adjust column widths automatically
    auto_resize_columns(self.table, self.style)

def refresh_editor_ui(self):
    """
    Refresh all UI elements after the XML data changes:
    - Rebuilds all maps (company_map, city_map, etc.).
    - Repopulates the company table.
    - Updates all dropdowns (company/city/etc.) with the latest values.
    """

    if not hasattr(self, "xml_root"):
        print("⚠️ No Company XML loaded yet — skipping company table.")

    # 🔄 Rebuild maps
    if hasattr(self, "xml_root") and self.xml_root is not None:
        self.company_map = load_company_map(self)  # from Company XML
    else:
        self.company_map = {}

    # 🖼️ Repopulate the company table (only if company data exists)
    if hasattr(self, "xml_root") and self.xml_root is not None:
        populate_company_table(self)

    # ⬇️ Refresh dropdown values dynamically
    for key, widget in self.detail_labels.items():
        if isinstance(widget, ttk.Combobox) and key.endswith("_dropdown"):
            # Find the base key before "_dropdown"
            base_key = key.replace("_dropdown", "")
            field_cfg = FIELD_TYPES.get(base_key, {})

            # Look up which map to use (default → company_map)
            dropdown_source = field_cfg.get("dropdown_map", "company_map")
            map_dict = getattr(self, dropdown_source, {}) or {}

            # Update dropdown values with latest map values
            widget["values"] = list(map_dict.values())

            # If the current var is set to a valid ID, sync it
            var = self.detail_vars.get(base_key)
            if var is not None:
                try:
                    cid = int(var.get())
                    cname = map_dict.get(cid, "")
                    self.detail_vars[key].set(cname if cname else "")
                except Exception:
                    self.detail_vars[key].set("")

def compute_entry_widths(count):
    if count == 1:
        return InitialWidth, InitialWidth
    elif count == 2 or count == 3:
        return InitialWidth, RowWidth
    else:
        # fallback for 4+ entries
        label_width = max(5, InitialWidth - (count * 2))
        entry_width = max(5, RowWidth - (count - 3))
        return label_width, entry_width

def create_widget(editor, subframe, key, var, field_cfg, entry_width):
    field_type = field_cfg.get("type", "text")

    if field_type == "text":
        return ttk.Entry(subframe, textvariable=var, width=entry_width), var

    elif field_type == "number":
        vcmd = editor.root.register(validate_int)
        entry = ttk.Entry(subframe, textvariable=var, width=entry_width, 
                          validate="key", validatecommand=(vcmd, "%P"))
        return entry, var

    elif field_type == "Creditdropdown":
        entry = ttk.Combobox(subframe, textvariable=var, values=list(CREDIT_MAP.keys()), width=RowWidth)
        entry.current(0)
        return entry, var
    
    elif field_type == "Genericdropdown":
        entry = ttk.Combobox(subframe, textvariable=var, values=list(GENERIC_MAP.keys()), width=entry_width)
        return entry,var

    elif field_type == "checkbox":
        bool_var = ttk.BooleanVar(value=False)
        entry = ttk.Checkbutton(subframe, variable=bool_var, width=entry_width)
        return entry, bool_var

    else:
        return create_spinbox_with_optional_dropdown(editor, subframe, key, var, field_cfg, entry_width)

def create_spinbox_with_optional_dropdown(editor, subframe, key, var, field_cfg, entry_width):
    min_val = field_cfg.get("min", 0)
    max_val = field_cfg.get("max", 999999)
    step = field_cfg.get("step", 1)
    fmt = "%.2f" if isinstance(step, float) else None

    entry = ttk.Spinbox(
        subframe,
        textvariable=var,
        from_=min_val, to=max_val,
        increment=step,
        width=entry_width,
        format=fmt
    )

    if field_cfg.get("with_dropdown"):
        dropdown_var = ttk.StringVar()
        dropdown_source = field_cfg.get("dropdown_map", "city_map")

        # initial values (may be empty) — will be refreshed when combobox opens
        dropdown = ttk.Combobox(
            subframe,
            textvariable=dropdown_var,
            values=list(getattr(editor, dropdown_source, {}).values()),
            width=entry_width
        )
        dropdown.pack(side="left", padx=(SPACING["xs"], SPACING["sm"]))

        # use dynamic lookup inside bind function
        bind_spinbox_dropdown_sync(editor, var, dropdown_var, dropdown, dropdown_source, key)

        # Save dropdown separately for UI refreshes
        editor.detail_labels[f"{key}_dropdown"] = dropdown
        editor.detail_vars[f"{key}_dropdown"] = dropdown_var

    return entry, var

def bind_spinbox_dropdown_sync(editor, var, dropdown_var, dropdown, dropdown_source, key):
    """
    Keep spinbox 'var' and combobox 'dropdown_var' in sync.
    Always fetch the current mapping via getattr(editor, dropdown_source) so it
    reacts to maps populated after the widget was created.
    """

    def get_map():
        # always fetch the current map from editor (company_map or city_map)
        return getattr(editor, dropdown_source, {}) or {}

    def on_dropdown_change(event=None):
        """Dropdown → Spinbox (name → ID)."""
        name = dropdown_var.get()
        map_dict = get_map()
        print(f"[DEBUG] on_dropdown_change: key={key} selected_name={name!r} map_size={len(map_dict)}")
        for cid, cname in map_dict.items():
            if cname == name:
                print(f"[DEBUG] on_dropdown_change: match found {cid} -> {cname!r}")
                var.set(str(cid))
                return
        print(f"[DEBUG] on_dropdown_change: no match for {name!r}")

    def on_spinbox_change(*args):
        """Spinbox → Dropdown (ID → label)."""
        raw = var.get()
        map_dict = get_map()
        print(f"[DEBUG] on_spinbox_change: key={key} raw_var={raw!r} map_size={len(map_dict)}")
        try:
            cid = int(raw)
            cname = map_dict.get(cid, "")
            if cname:
                print(f"[DEBUG] on_spinbox_change: found {cid} -> {cname!r}; setting dropdown_var")
                dropdown_var.set(cname)
            else:
                print(f"[DEBUG] on_spinbox_change: id {cid} not in map -> clearing dropdown_var")
                dropdown_var.set("")
        except Exception:
            print(f"[DEBUG] on_spinbox_change: cannot parse {raw!r} -> clearing dropdown_var")
            dropdown_var.set("")

    def refresh_dropdown_values(event=None):
        """Refresh combobox values from the live map before user sees it."""
        map_dict = get_map()
        vals = list(map_dict.values())
        dropdown.configure(values=vals)
        print(f"[DEBUG] refresh_dropdown_values: key={key} refreshed values (count={len(vals)})")

    def on_dropdown_keyrelease(event):
        """Filter dropdown values dynamically, open list only when pressing Enter."""
        value = dropdown_var.get().lower()
        map_dict = get_map()
        all_names = list(map_dict.values())

        if not value:
            filtered = all_names
        else:
            filtered = [name for name in all_names if value in name.lower()]

        dropdown.configure(values=filtered)

        # Only open dropdown when Enter is pressed
        if event.keysym == "Return":
            dropdown.event_generate("<Down>")
            # keep cursor focused in entry so user can still type or press down arrow again
            dropdown.after(0, lambda: (dropdown.focus_set(), dropdown.icursor(len(value))))

        print(f"[DEBUG] on_dropdown_keyrelease: key={event.keysym} filter='{value}' matches={len(filtered)}")

    # Bind handlers
    dropdown.bind("<<ComboboxSelected>>", on_dropdown_change)
    dropdown.bind("<Button-1>", refresh_dropdown_values)   # user clicking to open
    dropdown.bind("<FocusIn>", refresh_dropdown_values)    # focus shows updated values
    dropdown.bind("<KeyRelease>", on_dropdown_keyrelease)

    # trace_add expects a callback that accepts (name, index, op) — use *args
    var.trace_add("write", on_spinbox_change)

def validate_int(value):
    if value == "":
        return True
    if value == "-":
        return True
    return value.lstrip("-").isdigit()