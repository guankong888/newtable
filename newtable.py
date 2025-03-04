import requests
import datetime

AIRTABLE_BASE_ID = "appJrWoXe5H2YZnmU"
AIRTABLE_API_KEY = "YOUR_API_KEY"
SOURCE_TABLE_ID = "tblZnkmYCBPNzv6rO"

TABLES_API_URL = f"https://api.airtable.com/v0/meta/bases/{AIRTABLE_BASE_ID}/tables"
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

def generate_table_name():
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())
    sunday = monday + datetime.timedelta(days=6)
    return f"{monday.strftime('%m/%d')}-{sunday.strftime('%m/%d/%Y')} Test"

def get_table_schema():
    """Retrieve all fields (no skipping) and forcibly set missing options for checkboxes/selects."""
    print("\n===== FETCH TABLE SCHEMA =====")
    resp = requests.get(TABLES_API_URL, headers=HEADERS)
    if resp.status_code != 200:
        print(f"❌ Error {resp.status_code} fetching table info: {resp.text}")
        return []

    data = resp.json().get("tables", [])
    if not data:
        print("No tables found at all in base!")
        return []

    for tbl in data:
        tname = tbl.get("name", "NO_NAME")
        tid = tbl.get("id", "NO_ID")
        if tid == SOURCE_TABLE_ID:
            print(f"\n✅ Found Template Table: {tname} (ID: {tid})")

            raw_fields = tbl.get("fields", [])
            print(f"🔎 RAW FIELDS (count={len(raw_fields)}):")
            for rf in raw_fields:
                print(f"   → {rf}")

            fields = []
            for field in raw_fields:
                fname = field.get("name")
                ftype = field.get("type")
                print(f"\nProcessing Field: '{fname}' → type '{ftype}'")

                field_schema = {"name": fname, "type": ftype}

                # 1) If it's a checkbox, forcibly set 'icon' + 'color' in options
                if ftype == "checkbox":
                    meta_options = field.get("options", {})
                    # If the UI has a 'style' or 'color' property, it might appear as meta_options["color"]
                    # We'll fallback to "blueDark" if missing.
                    color = meta_options.get("color", "blueDark")
                    icon = meta_options.get("icon", "check")
                    field_schema["options"] = {
                        "icon": icon,
                        "color": color
                    }

                # 2) If it's singleSelect or multipleSelect, forcibly set choices with colors
                elif ftype in ["singleSelect", "multipleSelect"]:
                    meta_options = field.get("options", {})
                    choices = meta_options.get("choices", [])
                    if choices:
                        forced_choices = []
                        for c in choices:
                            forced_choices.append({
                                "name": c["name"],
                                "color": c.get("color", "blueDark")
                            })
                        field_schema["options"] = {"choices": forced_choices}

                # 3) If it's a number, rating, or currency, forcibly set minimal 'options'
                elif ftype == "number":
                    field_schema["options"] = {"precision": field["options"].get("precision", 1)}
                elif ftype == "currency":
                    field_schema["options"] = {
                        "precision": field["options"].get("precision", 2),
                        "symbol": field["options"].get("symbol", "$")
                    }
                elif ftype == "rating":
                    field_schema["options"] = {"max": field["options"].get("max", 5)}

                # For everything else (singleLineText, formula, etc.),
                # no special options needed unless the metadata says otherwise.

                fields.append(field_schema)

            print(f"\nBuilt a final fields list of length {len(fields)}:")
            for fs in fields:
                print("   ", fs)

            return fields

    print(f"\n❌ Could not find table with ID={SOURCE_TABLE_ID} in the base!")
    return []

def create_new_table():
    new_table_name = generate_table_name()
    fields = get_table_schema()
    if not fields:
        print("\n❌ No fields found. Table creation aborted.")
        return

    payload = {"name": new_table_name, "fields": fields}
    print(f"\n===== CREATE NEW TABLE: {new_table_name} =====")
    resp = requests.post(TABLES_API_URL, json=payload, headers=HEADERS)

    print("\n📢 API Response:")
    print(resp.text)

    if resp.status_code == 200:
        new_table_id = resp.json().get("id")
        print(f"\n✅ Successfully created table: {new_table_name} (ID: {new_table_id})")
    else:
        print(f"\n❌ Error creating table: {resp.status_code}, {resp.text}")

if __name__ == "__main__":
    create_new_table()
