import tkinter.font as tkFont

from settings.theme import (
    base_font, bold_font, header_font,
    TABLE_BG, TABLE_FG, TABLE_FIELD_BG, TABLE_SELECTION_BG,
    LABEL_FG, BUTTON_PADDING, ACCENT_BUTTON, SECONDARY_BUTTON, DANGER_BUTTON
)

def setup_styles(style):
    """Apply global ttk styles to the app."""

    # Initialize fonts
    font_obj = tkFont.Font(font=base_font)
    # Table
    style.configure(
        "Treeview",
        background=TABLE_BG,
        foreground=TABLE_FG,
        rowheight=25,
        fieldbackground=TABLE_FIELD_BG,
        font=base_font
    )
    style.map(
        "Treeview",
        background=[("selected", TABLE_SELECTION_BG)]
    )
    style.configure("Treeview.Heading", font=bold_font)

    # General
    style.configure("TLabel", font=base_font, foreground=LABEL_FG)
    style.configure("TButton", font=bold_font, padding=BUTTON_PADDING)
    style.configure("TLabelframe", font=header_font)
    style.configure("TLabelframe.Label", font=header_font)
    style.configure("TSpinbox", foreground=LABEL_FG, font=base_font)

    # 🌟 Accent button (for main actions like Save)
    style.configure(
        "Accent.TButton",
        font=bold_font,
        background=ACCENT_BUTTON,    # Blue
        foreground="white",
        padding=BUTTON_PADDING
    )
    style.map("Accent.TButton",
        background=[("active", "#005A9E"), ("disabled", "#444444")]
    )

    # 🌟 Danger button (for Delete AI)
    style.configure(
        "Danger.TButton",
        font=bold_font,
        background=DANGER_BUTTON,    # Red
        foreground="white",
        padding=BUTTON_PADDING
    )
    style.map("Danger.TButton",
        background=[("active", "#A52A00"), ("disabled", "#666666")]
    )

    # 🌟 Secondary button (neutral actions)
    style.configure(
        "Secondary.TButton",
        font=bold_font,
        background=SECONDARY_BUTTON,    # Light gray
        foreground="black",
        padding=BUTTON_PADDING
    )
    style.map("Secondary.TButton",
        background=[("active", "#C8C8C8"), ("disabled", "#AAAAAA")]
    )

    return font_obj