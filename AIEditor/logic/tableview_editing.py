# import from packages
import ttkbootstrap as ttk

# import from different files
from style import TABLEVIEW_ENTRY_PADDING_Y


def cancel_tableview_cell_edit(self):
    editor = getattr(self, "tableview_inline_editor", None)
    if editor is not None:
        try:
            editor.destroy()
        except Exception:
            pass
    self.tableview_inline_editor = None
    self.tableview_edit_context = None


def commit_tableview_cell_edit(self, iid, new_value):
    if not hasattr(self, "secondary_tableview") or self.secondary_tableview is None:
        cancel_tableview_cell_edit(self)
        return

    view = self.secondary_tableview.view
    values = list(view.item(iid, "values"))
    if len(values) < 3:
        cancel_tableview_cell_edit(self)
        return

    values[2] = new_value
    view.item(iid, values=values)

    row_obj = getattr(self.secondary_tableview, "iidmap", {}).get(str(iid))
    if row_obj is not None:
        row_obj.values = values

    company_id = str(values[0]) if values else ""
    field_key = getattr(self, "tableview_selected_field_key", "Funds_OnHand")
    if not hasattr(self, "tableview_pending_edits") or self.tableview_pending_edits is None:
        self.tableview_pending_edits = {}
    self.tableview_pending_edits[(company_id, field_key)] = str(new_value)

    cancel_tableview_cell_edit(self)


def start_tableview_cell_edit(self, event):
    if not hasattr(self, "secondary_tableview") or self.secondary_tableview is None:
        return

    view = self.secondary_tableview.view
    iid = view.identify_row(event.y)
    col = view.identify_column(event.x)
    if not iid or col != "#3":
        return

    bbox = view.bbox(iid, col)
    if not bbox:
        return

    x, y, w, h = bbox
    values = list(view.item(iid, "values"))
    if len(values) < 3:
        return

    cancel_tableview_cell_edit(self)

    entry = ttk.Entry(view)
    entry.insert(0, str(values[2]))
    entry.select_range(0, "end")
    pad_y = max(0, int(TABLEVIEW_ENTRY_PADDING_Y))
    entry_y = y + pad_y
    entry_h = max(1, h - (pad_y * 2))
    entry.place(x=x, y=entry_y, width=w, height=entry_h)
    entry.focus_set()

    self.tableview_inline_editor = entry
    self.tableview_edit_context = {"iid": iid}

    def commit_current(event=None):
        if getattr(self, "tableview_inline_editor", None) is not entry:
            return
        try:
            updated_value = entry.get()
        except Exception:
            return
        commit_tableview_cell_edit(self, iid, updated_value)

    entry.bind("<Return>", commit_current)
    entry.bind("<Escape>", lambda e: cancel_tableview_cell_edit(self))
    entry.bind("<FocusOut>", commit_current)
