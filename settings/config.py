# Set up columns with custom widths
column_widths = {
    "ID": 50,
    "Name": 150,
    "Owner": 100,
    "HQ": 120,
    "Founded": 70,
    "Death": 70,
    "Funds": 100
}

# For making certain columns staying the same in width
max_widths = {
    "ID": 50,        # lock ID at 50
    "Founded": 70,   # cap Founded
    "Death": 70      # cap Death
    # others will resize normally
}

# For the input fields
InitialWidth=22
TwoRowWidth=12
ThreeRowWidth=5

FIELD_LAYOUT = {
    "Identity": [
        ("single", [("Company_ID", "ID")]),
        ("single", [("Company_Name", "Company Name")]),
        ("single", [("Company_OwnerID", "Owner ID")]),
        ("single", [("Company_HQ", "Headquarters")]),
        ("double", [("Company_Founded", "Founded Year"), ("Company_Death", "Closure Year")]),
        ("single", [("Company_Logo", "Logo")]),
    ],

    "Funds": [
        ("preset", [("Funds_Preset", "Funds Preset")]),
        ("single", [("Funds_OnHand", "Starting Funds")]),
        ("double", [("Funds_Loans", "Loans"), ("Funds_Credit", "Credit Rating")]),
    ],

    "Skills": [
        ("preset", [("Skills_Preset", "Skills Preset")]),
        ("triple", [("Skills_Manufactoring", "Manufacturing"),
                    ("Skills_RnD", "RnD"),
                    ("Skills_Admin", "Administration")]),
        ("double", [("Skills_Marketing", "Marketing"),
                    ("Skills_Dealers", "Dealership")]),
    ],

    "Design": [
        ("preset", [("Design_Preset", "Design Preset")]),
        ("triple", [("Design_Engine", "Engine Design"),
                    ("Design_Chassis", "Chassis Design"),
                    ("Design_Transmission", "Transmission Design")]),
        ("triple", [("Design_Body", "Body Design"),
                    ("Design_Lux", "Luxury Design"),
                    ("Design_safety", "Safety Design")]),
    ],

    "Image": [
        ("preset", [("Image_Preset", "Image Preset")]),
        ("double", [("Image_GeneralGlobal", "Global Image"),
                    ("Image_Quality", "Quality Image")]),
        ("double", [("Image_Racing", "Racing Image"),
                    ("Image_Work", "Workmanship Image")]),
    ],

    "Behavior": [
        ("preset", [("Behavior_Preset", "Behavior Preset")]),
        ("triple", [("Behavior_GenericDesigner", "Generic Designs"),
                    ("Behavior_Rating_Performance", "Performance Rating"),
                    ("Behavior_Rating_Drivability", "Drivability Rating")]),
        ("triple", [("Behavior_Rating_Luxury", "Luxury Rating"),
                    ("Behavior_Rating_Safety", "Safety Rating"),
                    ("Behavior_Rating_Fuel", "Fuel Efficiency")]),
        ("triple", [("Behavior_Rating_Power", "Power Rating"),
                    ("Behavior_Rating_Cargo", "Cargo Rating"),
                    ("Behavior_Rating_Dependability", "Dependability")]),
    ],

    "Aggressions": [
        ("preset", [("Aggressions_Preset", "Aggressions Preset")]),
        ("triple", [("Behavior_DesignAggression", "Design Aggression"),
                    ("Behavior_SellAggression", "Sales Aggression"),
                    ("Behavior_BuildAggression", "Build Aggression")]),
        ("triple", [("Behavior_MarketingAggression", "Marketing Aggression"),
                    ("Behavior_CostAggression", "Cost Aggression"),
                    ("Behavior_QualityAggression", "Quality Aggression")]),
        ("triple", [("Behavior_PriceAggression", "Price Aggression"),
                    ("Behavior_ExpansionAggression", "Expansion Aggression"),
                    ("Behavior_ClusterSpace", "Clustering")]),
        ("double", [("Behavior_ExportDesigns", "Export Designs"),
                    ("Behavior_ImportDesigns", "Import Designs")]),
    ]
}

FIELD_TYPES = {
    # --- Company ---
    "Company_ID": {"type": "text", "readonly": True},
    "Company_Name": {"type": "text"},
    "Company_OwnerID": {"type": "spinbox", "min": 1, "max": 99999, "step": 1, "with_dropdown": True, "dropdown_map": "company_map"},
    "Company_HQ": {"type": "spinbox", "min": 1, "max": 99999, "step": 1, "with_dropdown": True, "dropdown_map": "city_map"},
    "Company_Founded": {"type": "spinbox", "min": 1800, "max": 2100, "step": 1},
    "Company_Death": {"type": "spinbox", "min": 1800, "max": 2100, "step": 1},
    "Company_Logo": {"type": "text"},

    # --- Funds ---
    "Funds_OnHand": {"type": "number"},
    "Funds_Loans": {"type": "number"},
    "Funds_Credit": {"type": "Creditdropdown"},

    # --- Skills ---
    "Skills_Manufactoring": {"type": "spinbox", "min": 0, "max": 100, "step": 1},
    "Skills_RnD": {"type": "spinbox", "min": 0, "max": 100, "step": 1},
    "Skills_Admin": {"type": "spinbox", "min": 0, "max": 100, "step": 1},
    "Skills_Marketing": {"type": "spinbox", "min": 0, "max": 100, "step": 1},
    "Skills_Dealers": {"type": "spinbox", "min": 0, "max": 100, "step": 1},

    # --- Design ---
    "Design_Engine": {"type": "spinbox", "min": 0, "max": 100, "step": 1},
    "Design_Chassis": {"type": "spinbox", "min": 0, "max": 100, "step": 1},
    "Design_Transmission": {"type": "spinbox", "min": 0, "max": 100, "step": 1},
    "Design_Body": {"type": "spinbox", "min": 0, "max": 100, "step": 1},
    "Design_Lux": {"type": "spinbox", "min": 0, "max": 100, "step": 1},
    "Design_safety": {"type": "spinbox", "min": 0, "max": 100, "step": 1},

    # --- Image ---
    "Image_GeneralGlobal": {"type": "spinbox", "min": 0, "max": 100, "step": 1},
    "Image_Quality": {"type": "spinbox", "min": 0, "max": 100, "step": 1},
    "Image_Racing": {"type": "spinbox", "min": 0, "max": 100, "step": 1},
    "Image_Work": {"type": "spinbox", "min": 0, "max": 100, "step": 1},

    # --- Behavior ---
    "Behavior_GenericDesigner": {"type": "Genericdropdown"},
    "Behavior_Rating_Performance": {"type": "spinbox", "min": 0, "max": 1, "step": 0.05},
    "Behavior_Rating_Drivability": {"type": "spinbox", "min": 0, "max": 1, "step": 0.05},
    "Behavior_Rating_Luxury": {"type": "spinbox", "min": 0, "max": 1, "step": 0.05},
    "Behavior_Rating_Safety": {"type": "spinbox", "min": 0, "max": 1, "step": 0.05},
    "Behavior_Rating_Fuel": {"type": "spinbox", "min": 0, "max": 1, "step": 0.05},
    "Behavior_Rating_Power": {"type": "spinbox", "min": 0, "max": 1, "step": 0.05},
    "Behavior_Rating_Cargo": {"type": "spinbox", "min": 0, "max": 1, "step": 0.05},
    "Behavior_Rating_Dependability": {"type": "spinbox", "min": 0, "max": 1, "step": 0.05},

    # --- Aggression ---
    "Behavior_DesignAggression": {"type": "spinbox", "min": 0, "max": 1, "step": 0.05},
    "Behavior_SellAggression": {"type": "spinbox", "min": 0, "max": 1, "step": 0.05},
    "Behavior_BuildAggression": {"type": "spinbox", "min": 0, "max": 1, "step": 0.05},
    "Behavior_MarketingAggression": {"type": "spinbox", "min": 0, "max": 1, "step": 0.05},
    "Behavior_CostAggression": {"type": "spinbox", "min": 0, "max": 1, "step": 0.05},
    "Behavior_QualityAggression": {"type": "spinbox", "min": 0, "max": 1, "step": 0.05},
    "Behavior_PriceAggression": {"type": "spinbox", "min": 0, "max": 1, "step": 0.05},
    "Behavior_ExpansionAggression": {"type": "spinbox", "min": 0, "max": 1, "step": 0.05},
    "Behavior_ClusterSpace": {"type": "spinbox", "min": 0, "max": 1, "step": 0.05},
    "Behavior_ExportDesigns": {"type": "spinbox", "min": 0, "max": 1, "step": 0.05},
    "Behavior_ImportDesigns": {"type": "spinbox", "min": 0, "max": 1, "step": 0.05},
}

CREDIT_MAP = {
    "AAA": 9,
    "AA": 8,
    "A": 7,
    "BBB": 6,
    "BB": 5,
    "B": 4,
    "CCC": 3,
    "CC": 2,
    "C": 1,
    "D": 0,
    "Random": -1,
}

CREDIT_MAP_REV = {v: k for k, v in CREDIT_MAP.items()}

GENERIC_MAP = {
    "True": 1,
    "False": 0,
    "Random": -1
}

GENERIC_MAP_REV = {v: k for k, v in GENERIC_MAP.items()}