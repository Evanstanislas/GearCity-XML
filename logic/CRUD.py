# import from packages
import xml.etree.ElementTree as ET

#import from different files
from settings.config import CREDIT_MAP, CREDIT_MAP_REV, GENERIC_MAP, GENERIC_MAP_REV, FIELD_TYPES

def pick_new_selection(children, old_index):
    if not children:
        return None
    new_index = min(old_index, len(children) - 1)
    return children[new_index]

def prepare_field_value(key, val, field_types, dropdown_sources):
    """Return (main_value, dropdown_value) for a given field."""
    field_type = field_types.get(key, "entry")

    if field_type == "Creditdropdown":
        return CREDIT_MAP_REV.get(int(val), "D"), None
    elif field_type == "checkbox":
        return (val == "1"), None
    elif field_type == "Genericdropdown":
        return GENERIC_MAP_REV.get(int(val), "Random"), None
    else:
        # normal value
        main_value = val
        dropdown_var = None
        field_cfg = FIELD_TYPES.get(key, {})
        dropdown_source = field_cfg.get("dropdown_map", "company_map")
        map_dict = dropdown_sources.get(dropdown_source, {})
        try:
            cid = int(val)
        except ValueError:
            cid = val
        cname = map_dict.get(cid, "")
        dropdown_var = cname if cname else ""
        return main_value, dropdown_var

# ================================
# 📝 Company CRUD Helpers
# ================================
def get_company_details(xml_root, company_id):
    company = xml_root.find(f"Company[@ID='{company_id}']")
    if company is None:
        return {}
    details = {}
    for attr, val in company.attrib.items():
        details[f"Company_{attr}"] = val
    for section in ["Funds", "Skills", "Design", "Image", "Behavior"]:
        elem = company.find(section)
        if elem is not None:
            for attr, val in elem.attrib.items():
                details[f"{section}_{attr}"] = val
    return details

def build_new_company(xml_root):
    """
    Create a new <Company> element with default values and add it to the XML.
    - Generates a unique ID (max existing ID + 1).
    - Initializes all required child elements with zero/default values.
    - Refreshes the UI to show the new company.
    """

    # 🆔 Find next available company ID
    max_id = 0
    max_id = max((int(c.get("ID", 0)) for c in xml_root.findall("Company")), default=0)
    new_id = max_id + 1

    # 🏗️ Build new company skeleton
    new_company = ET.Element("Company", {
        "ID": str(new_id),
        "Name": "",
        "Active": "1",
        "OwnerID": str(new_id),
        "HQ": "",
        "Founded": "1900",
        "Death": "1900",
        "Logo": ""
    })

    # Add child nodes
    ET.SubElement(new_company, "Funds", {"OnHand": "-1", "Credit": "-1", "Loans": "0"})
    ET.SubElement(new_company, "Skills", {
        "Manufactoring": "-1", "RnD": "-1", "Admin": "-1", 
        "Marketing": "-1", "Dealers": "-1"
    })
    ET.SubElement(new_company, "Design", {
        "Engine": "-1", "Chassis": "-1", "Transmission": "-1", 
        "Body": "-1", "Lux": "-1", "safety": "-1"
    })
    ET.SubElement(new_company, "Image", {
        "GeneralGlobal": "-1", "Quality": "-1", "Racing": "-1", "Work": "-1"
    })
    ET.SubElement(new_company, "Behavior", {
        "GenericDesigner": "-1", "Rating_Performance": "-1", "Rating_Drivability": "-1", "Rating_Luxury": "-1",
        "Rating_Safety": "-1", "Rating_Fuel": "-1", "Rating_Power": "-1", "Rating_Cargo": "-1", "Rating_Dependability": "-1",
        "DesignAggression": "-1", "SellAggression": "-1", "BuildAggression": "-1", "MarketingAggression": "-1",
        "CostAggression": "-1", "QualityAggression": "-1", "PriceAggression": "-1", "ExpansionAggression": "-1",
        "ClusterSpace": "-1", "ExportDesigns": "-1", "ImportDesigns": "-1"
    })

    return new_company

def write_company_changes(company, detail_vars, field_types):
    """Take the UI values and write them back into the given <Company> element."""

    company_id = company.get("ID")

    for key, var in detail_vars.items():
        # 🚫 skip UI-only helpers
        if key.endswith("_dropdown") or key.endswith("_Preset"):
            continue

        try:
            val = var.get()
        except Exception:
            val = var

        if key.startswith("Company_"):
            attr = key.split("_", 1)[1]
            if attr == "ID":
                continue
            company.set(attr, str(val))
            continue

        if "_" in key:
            section, attr = key.split("_", 1)
            elem = company.find(section)
            if elem is None:
                elem = ET.SubElement(company, section)

            field_type = field_types.get(key, "entry")

            if field_type == "Creditdropdown":
                num = CREDIT_MAP.get(val, 0)
                elem.set(attr, str(num))
            elif field_type == "Genericdropdown":
                num = GENERIC_MAP.get(val, 0)
                elem.set(attr, str(num))
            elif field_type == "checkbox":
                elem.set(attr, "1" if bool(val) else "0")
            else:
                elem.set(attr, str(val))

    # 🆕 Ensure Active flag is consistent
    owner_id = company.get("OwnerID")
    company.set("Active", "1" if owner_id == company_id else "0")

def delete_company_and_reindex(xml_root, company_id_to_delete):
    """
    Delete the <Company> element with ID == company_id_to_delete (str or int),
    then renumber remaining companies' ID attributes sequentially (1..N),
    and update OwnerID attributes to the new numbering.

    Returns the mapping {old_id (int): new_id (int)}.

    Raises KeyError if the company to delete was not found.
    """
    cid_str = str(company_id_to_delete)
    # find the company to remove
    company_elem = xml_root.find(f"Company[@ID='{cid_str}']")
    if company_elem is None:
        raise KeyError(f"Company ID {cid_str} not found")

    # remove the element
    xml_root.remove(company_elem)

    # gather remaining companies in document order
    remaining = xml_root.findall("Company")

    # build old->new mapping and reassign new IDs
    mapping = {}
    for new_idx, comp in enumerate(remaining, start=1):
        old_id_str = comp.get("ID", "")
        try:
            old_id = int(old_id_str)
        except Exception:
            # if the old id is not integer-ish, still assign sequential new id
            old_id = None

        if old_id is not None:
            mapping[old_id] = new_idx
        # set new ID attribute
        comp.set("ID", str(new_idx))

    # update OwnerID for every remaining company
    for comp in remaining:
        owner = comp.get("OwnerID")
        if owner is None or owner == "":
            continue
        try:
            owner_int = int(owner)
        except Exception:
            # non numeric owner, skip
            continue

        if owner_int in mapping:
            comp.set("OwnerID", str(mapping[owner_int]))
        else:
            # owner pointed to deleted company (or unknown) → clear/zero it
            comp.set("OwnerID", "0")

    return mapping