import requests
import datetime

AIRTABLE_BASE_ID = "appJrWoXe5H2YZnmU"
AIRTABLE_API_KEY = "patkcqbpm4M0Z7WTg.676db3c4059059a9f74e2714bced3e09fbacabe05bb17bfa7b29aa792b9a80e0"
SOURCE_TABLE_ID = "tblZnkmYCBPNzv6rO"

TABLES_API_URL = f"https://api.airtable.com/v0/meta/bases/{AIRTABLE_BASE_ID}/tables"
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}


def list_all_tables():
    """Lists all tables for debugging."""
    print("\n===== LIST ALL TABLES IN BASE =====")
    resp = requests.get(TABLES_API_URL, headers=HEADERS)
    if resp.status_code == 200:
        data = resp.json().get("tables", [])
        if not data:
            print("No tables found in this base!")
        else:
            for tbl in data:
                tname = tbl.get("name", "UNKNOWN_NAME")
                tid = tbl.get("id", "UNKNOWN_ID")
                fields_data = tbl.get("fields", [])
                print(f"\nTABLE NAME: {tname}")
                print(f"TABLE ID:   {tid}")
                print("FIELDS:")
                for f in fields_data:
                    print(f"   - {f}")
    else:
        print(f"Error listing tables: {resp.status_code}, {resp.text}")


def generate_table_name():
    """Generate table name in MM/DD-MM/DD/YYYY format + 'Test'."""
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())
    sunday = monday + datetime.timedelta(days=6)
    return f"{monday.strftime('%m/%d')}-{sunday.strftime('%m/%d/%Y')} Test"


def get_table_schema():
    """Retrieve + fix any missing options for fields like 'checkbox' or 'select'."""
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
            print(f"🔎 RAW FIELDS from Template (count={len(raw_fields)}):")
            for rf in raw_fields:
                print(f"   → {rf}")

            fields = []
            for field in raw_fields:
                fname = field.get("name")
                ftype = field.get("type")
                print(f"Processing field → Name: {fname}, Type: {ftype}")

                # Build a minimal schema
                field_schema = {
                    "name": fname,
                    "type": ftype
                }

                # 1) Checkbox fields need {"icon": "check"} in "options"
                if ftype == "checkbox":
                    field_schema["options"] = {"icon": "check"}

                # 2) Single/Multi select fields need "choices" with color
                elif ftype in ["singleSelect", "multipleSelect"] and "options" in field:
                    choices = field["options"].get("choices", [])
                    if choices:
                        updated_choices = []
                        for choice in choices:
                            choice_color = choice.get("color", "blueLight")
                            updated_choices.append({
                                "name": choice["name"],
                                "color": choice_color
                            })
                        field_schema["options"] = {"choices": updated_choices}

                # 3) Number, currency, rating, etc. if needed
                elif ftype == "number":
                    field_schema["options"] = {"precision": field["options"].get("precision", 1)}
                elif ftype == "currency":
                    field_schema["options"] = {
                        "precision": field["options"].get("precision", 2),
                        "symbol": field["options"].get("symbol", "$")
                    }
                elif ftype == "rating":
                    field_schema["options"] = {"max": field["options"].get("max", 5)}

                fields.append(field_schema)

            print(f"Built a final fields list of length {len(fields)}!")
            return fields

    print(f"❌ Could not find table with ID={SOURCE_TABLE_ID} in the base!")
    return []


def create_new_table():
    new_table_name = generate_table_name()
    fields = get_table_schema()

    if not fields:
        print("\n❌ No fields found. Table creation aborted.")
        return

    payload = {
        "name": new_table_name,
        "fields": fields
    }

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
    list_all_tables()
    create_new_table()
