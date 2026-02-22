# import from packages
import xml.etree.ElementTree as ET

# import from different files
from AIEditor.settings.config import (
    FIELD_LAYOUT,
    CREDIT_MAP,
    CREDIT_MAP_REV,
    GENERIC_MAP,
    GENERIC_MAP_REV,
)


def get_companies(self):
    """Return company elements from xml_root or an empty list."""
    if not hasattr(self, "xml_root") or self.xml_root is None:
        return []
    return list(self.xml_root.findall("Company"))


def build_company_rows(self):
    """Build normalized company rows used by both Treeview and Tableview."""
    rows = []
    company_map = getattr(self, "company_map", {}) or {}
    city_map = getattr(self, "city_map", {}) or {}

    for company in get_companies(self):
        cid = company.get("ID", "")
        cname = company.get("Name", "")
        owner_id = company.get("OwnerID")

        # Convert owner ID -> owner name
        owner_name = ""
        if owner_id:
            try:
                owner_name = company_map.get(int(owner_id), owner_id)
            except (TypeError, ValueError):
                owner_name = company_map.get(owner_id, owner_id)

        # Convert HQ ID -> city display
        hq_id = company.get("HQ", "")
        if hq_id:
            try:
                hq_name = city_map.get(int(hq_id), hq_id)
            except (TypeError, ValueError):
                hq_name = city_map.get(hq_id, hq_id)
        else:
            hq_name = ""

        founded = company.get("Founded", "")
        death = company.get("Death", "")

        funds_elem = company.find("Funds")
        funds_raw = funds_elem.get("OnHand") if funds_elem is not None else "0"
        try:
            funds_display = f"${int(funds_raw):,}"
        except (TypeError, ValueError):
            funds_display = funds_raw if funds_raw is not None else ""

        rows.append(
            {
                "id": str(cid) if cid is not None else "",
                "name": cname or "",
                "owner_name": owner_name or "",
                "hq_name": hq_name or "",
                "founded": founded or "",
                "death": death or "",
                "funds_display": funds_display or "",
            }
        )

    return rows


def build_tableview_column_options():
    """Build display_label -> field_key map from FIELD_LAYOUT, excluding preset rows."""
    options = {}
    seen_labels = set()

    for _, field_groups in FIELD_LAYOUT.items():
        for field_type, fields in field_groups:
            if field_type == "preset":
                continue
            for field_key, display_name in fields:
                label = display_name
                if label in seen_labels:
                    label = f"{display_name} ({field_key})"
                seen_labels.add(label)
                options[label] = field_key

    return options


def get_company_field_value(company, field_key, company_map, city_map):
    """Resolve raw XML value for a field key like Company_Name or Funds_OnHand."""
    if "_" not in field_key:
        return ""

    section, attr = field_key.split("_", 1)
    if section == "Company":
        raw = company.get(attr, "")
    else:
        elem = company.find(section)
        raw = elem.get(attr, "") if elem is not None else ""

    return format_tableview_value(field_key, raw, company_map, city_map)


def format_tableview_value(field_key, raw_value, company_map, city_map):
    """Format value for table display, mapping known IDs/codes to labels when possible."""
    raw = "" if raw_value is None else str(raw_value)

    if field_key == "Company_OwnerID":
        try:
            return str(company_map.get(int(raw), raw))
        except (TypeError, ValueError):
            return str(company_map.get(raw, raw))

    if field_key == "Company_HQ":
        try:
            return str(city_map.get(int(raw), raw))
        except (TypeError, ValueError):
            return str(city_map.get(raw, raw))

    if field_key == "Funds_Credit":
        try:
            return CREDIT_MAP_REV.get(int(raw), raw)
        except (TypeError, ValueError):
            return raw

    if field_key == "Behavior_GenericDesigner":
        try:
            return GENERIC_MAP_REV.get(int(raw), raw)
        except (TypeError, ValueError):
            return raw

    return raw


def build_tableview_rows(self, company_rows, extra_field_key):
    """Build Tableview row tuples in (ID, Name, extra) order."""
    rows = []
    companies = get_companies(self)
    company_map = getattr(self, "company_map", {}) or {}
    city_map = getattr(self, "city_map", {}) or {}
    pending_edits = getattr(self, "tableview_pending_edits", {}) or {}

    for idx, row in enumerate(company_rows):
        company_id = str(row["id"])
        pending_key = (company_id, extra_field_key)
        if pending_key in pending_edits:
            extra_value = pending_edits[pending_key]
            rows.append((row["id"], row["name"], extra_value))
            continue

        company = companies[idx] if idx < len(companies) else None
        if company is None:
            extra_value = ""
        else:
            extra_value = get_company_field_value(company, extra_field_key, company_map, city_map)

        rows.append((row["id"], row["name"], extra_value))

    return rows


def parse_tableview_input(field_key, text, company_map, city_map):
    """Parse tableview display input into raw XML-storable value."""
    raw = "" if text is None else str(text).strip()

    if field_key == "Company_OwnerID":
        for cid, cname in company_map.items():
            if str(cname) == raw:
                return str(cid)
        return raw

    if field_key == "Company_HQ":
        for cid, cname in city_map.items():
            if str(cname) == raw:
                return str(cid)
        return raw

    if field_key == "Funds_Credit":
        return str(CREDIT_MAP.get(raw, raw))

    if field_key == "Behavior_GenericDesigner":
        return str(GENERIC_MAP.get(raw, raw))

    return raw


def write_company_field(company, field_key, raw_value):
    """Write one field key (Company_X or Section_X) into XML."""
    if "_" not in field_key:
        return False, f"Invalid field key '{field_key}'."

    section, attr = field_key.split("_", 1)

    if section == "Company":
        if attr == "ID":
            return False, "Company ID is read-only."
        company.set(attr, str(raw_value))
        return True, ""

    elem = company.find(section)
    if elem is None:
        elem = ET.SubElement(company, section)
    elem.set(attr, str(raw_value))
    return True, ""


def validate_int(value):
    if value == "":
        return True
    if value == "-":
        return True
    return value.lstrip("-").isdigit()
