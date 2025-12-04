from settings.preset import Funds_Preset, Skills_Preset, Design_Preset, Image_Preset, Behavior_Preset, Aggressions_Preset
from settings.config import CREDIT_MAP_REV, GENERIC_MAP_REV

def apply_funds_preset(editor, preset_name):
    """Apply a funds preset using formula with StartYear and Power."""
    preset = Funds_Preset.get(preset_name)
    if not preset:
        print(f"[DEBUG] Unknown preset: {preset_name}")
        return

    # --- Step 1: Calculate StartYear ---
    founded_raw = editor.detail_vars.get("Company_Founded", None)
    try:
        founded_val = int(founded_raw.get()) if founded_raw else 1850
    except Exception:
        founded_val = 1850  # fallback
    start_year = max(0, founded_val - 1850)

    print(f"[DEBUG] Preset={preset_name}, Founded={founded_val}, StartYear={start_year}")

    # --- Step 2: Extract preset values ---
    base_start = preset.get("Starting", 0)
    power = preset.get("Power", 1.0)
    credit_num = preset.get("Credit", 0)
    loan_coeff = preset.get("Loans", 0.0)

    # --- Step 3: Calculate Funds ---
    funds_onhand = int(base_start * (power ** start_year))
    funds_loans = int(funds_onhand * loan_coeff)

    # --- Step 4: Apply values ---
    # Funds_OnHand
    if "Funds_OnHand" in editor.detail_vars:
        editor.detail_vars["Funds_OnHand"].set(str(funds_onhand))
        print(f"[DEBUG] Funds_OnHand = {funds_onhand}")

    # Funds_Loans
    if "Funds_Loans" in editor.detail_vars:
        editor.detail_vars["Funds_Loans"].set(str(funds_loans))
        print(f"[DEBUG] Funds_Loans = {funds_loans}")

    # Funds_Credit
    if "Funds_Credit" in editor.detail_vars:
        credit_label = CREDIT_MAP_REV.get(credit_num, "D")
        editor.detail_vars["Funds_Credit"].set(credit_label)
        print(f"[DEBUG] Credit mapped {credit_num} → {credit_label}")

def apply_simple_preset(editor, preset_name, preset_dict, prefix=""):
    """
    Apply a simple preset: directly set values in detail_vars.
    Adds prefix automatically to match UI keys.
    """
    preset = preset_dict.get(preset_name)
    if not preset:
        print(f"[DEBUG] Unknown preset: {preset_name}")
        return

    print(f"[DEBUG] Applying simple preset={preset_name} with prefix={prefix}")

    for field, value in preset.items():
        key = f"{prefix}{field}" if prefix else field
        if key in editor.detail_vars:
            if field == "GenericDesigner":
                generic_num = preset.get("GenericDesigner",0)
                generic_label = GENERIC_MAP_REV.get(generic_num, "Random")
                editor.detail_vars[key].set(generic_label)
                print(f"[DEBUG] Generic Designer mapped {generic_num} → {generic_label}")
            else:
                editor.detail_vars[key].set(str(value))
                print(f"[DEBUG] {key} = {value}")
        else:
            print(f"[DEBUG] Skipped missing field: {key}")

PRESET_CONFIG = {
    "Funds_Preset": {
        "dict": Funds_Preset,
        "apply": apply_funds_preset,
    },
    "Skills_Preset": {
        "dict": Skills_Preset,
        "apply": lambda editor, chosen: apply_simple_preset(editor, chosen, Skills_Preset, prefix="Skills_")
    },
    "Design_Preset": {
        "dict": Design_Preset,
        "apply": lambda editor, chosen: apply_simple_preset(editor, chosen, Design_Preset, prefix="Design_")
    },
    "Image_Preset": {
        "dict": Image_Preset,
        "apply": lambda editor, chosen: apply_simple_preset(editor, chosen, Image_Preset, prefix="Image_")
    },
    "Behavior_Preset": {
        "dict": Behavior_Preset,
        "apply": lambda editor, chosen: apply_simple_preset(editor, chosen, Behavior_Preset, prefix="Behavior_")
    },
    "Aggressions_Preset": {
        "dict": Aggressions_Preset,
        "apply": lambda editor, chosen: apply_simple_preset(editor, chosen, Aggressions_Preset, prefix="Behavior_")
    },
}