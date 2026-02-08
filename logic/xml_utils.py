import xml.etree.ElementTree as ET
import pandas as pd

from logic.CRUD import build_new_company

def importExcel(file_path):
    pass

# 📂 XML Load & Save
def load_xml_file(file_path):
    """Return parsed XML root or raise a friendly error."""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        if root is None:
            raise ValueError("Empty XML file (no root element).")

        # --- Minimal structure check for AI/Company XML ---
        companies = root.findall(".//Company")
        if not companies:
            raise ValueError("XML does not contain any <Company> elements.")

        for comp in companies[:5]:  # spot check first few
            if "ID" not in comp.attrib or "Name" not in comp.attrib:
                raise ValueError("Company element missing required 'ID' or 'Name' attributes.")

        return root

    except ET.ParseError as e:
        raise ET.ParseError(f"Malformed XML: {e}")
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(*e.args)  # preserve details
    except (FileNotFoundError, PermissionError, OSError) as e:
        raise e

def save_xml_to_file(xml_root, file_path):
    """Save the given xml_root to a file. Raises exception if fails."""
    indent_xml(xml_root)   # ⭐ make it pretty before writing
    tree = ET.ElementTree(xml_root)
    tree.write(file_path, encoding="utf-8", xml_declaration=True)

def indent_xml(elem, level=0):
    """
    Pretty-print XML by adding indents and newlines recursively.
    Modifies the element tree in place.
    """
    i = "\n" + level * "\t"   # tab-based indent
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "\t"
        for child in elem:
            indent_xml(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = i
    if level and (not elem.tail or not elem.tail.strip()):
        elem.tail = i

def build_new_xml_with_company():
    """
    Create a brand-new XML root with one starter company.
    Reuses build_new_company() so default company definition is in one place.
    """
    root = ET.Element("AINode")

    # 🚀 Reuse the helper, pass root so it knows the next ID
    starter_company, _ = build_new_company(root)
    root.append(starter_company)

    return root

def build_city_map_from_xml(self):
    """
    Build a dictionary mapping city IDs → "Name, Country" labels from the City XML.

    - Expects self.city_xml_root to be set (from upload_city_xml).
    - Reads <City><ID id="..."/><NAME name="..."/><COUNTRY nation="..."/>.
    - Keeps IDs as int when possible.
    - Saves into self.city_map as {id: "Name, Country"}.
    """
    # 🧹 Start fresh
    self.city_map = {}

    root = getattr(self, "city_xml_root", None)
    if root is None:
        print("🚫 No City XML loaded yet")
        return

    # ➕ Loop through all City elements
    for city in root.findall(".//City"):
        id_elem = city.find("ID")
        name_elem = city.find("NAME")
        country_elem = city.find("COUNTRY")

        if id_elem is None or name_elem is None or country_elem is None:
            print("⚠️ Skipped one city (missing ID/NAME/COUNTRY)")
            continue

        cid_raw = id_elem.get("id")
        cname = name_elem.get("name")
        country = country_elem.get("nation")

        if cid_raw is None or cname is None or country is None:
            print("⚠️ Skipped one city (broken attributes)")
            continue

        # 🔢 Convert ID into int (if possible)
        try:
            cid = int(cid_raw)
        except ValueError:
            cid = cid_raw  # fallback → keep as string

        # 🏷️ Build label → "Name, Country"
        label = f"{cname}, {country}"

        # Save to map
        self.city_map[cid] = label

def load_city_xml(file_path):
    tree = ET.parse(file_path)
    cities = tree.findall(".//City")
    if not cities:
        raise ValueError("XML does not contain any <Cities> elements.")
    return tree.getroot()

def numericCheck(col):
    try:
        return pd.to_numeric(col)
    except Exception:
        print(f"Skipped non-numeric column: {col.name}")
        return col
    
def XMLtoDF(xml_root):
    rows = []
    for company in xml_root.findall("Company"):
        row = {}
        for key, value in company.attrib.items():
            row[key] = value
        for child in company:
            for key, value in child.attrib.items():
                row[f"{child.tag}_{key}"] = value
        rows.append(row)

    df = pd.DataFrame(rows)
    df = df.apply(numericCheck)
    return df

def AnalyzeXML(xml_root):
    df = XMLtoDF(xml_root)
    pd.set_option("display.float_format", "{:.2f}".format)
    print(df.describe().transpose())

def ExportExcel(xml_root, file_path):
    if not xml_root:
        return
    df = XMLtoDF(xml_root)

    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Companies")

        ws = writer.book.active

        for column_cells in ws.columns:
            max_length = 0
            column_letter = column_cells[0].column_letter

            for cell in column_cells:
                if cell.value is not None:
                    max_length = max(max_length, len(str(cell.value)))

            ws.column_dimensions[column_letter].width = max_length + 2