import requests
import datetime

AIRTABLE_BASE_ID = "appJrWoXe5H2YZnmU"
AIRTABLE_API_KEY = "YOUR_KEY"
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
    """Retrieve the schema and forcibly set color for 'MF/FAIRE Order' to a single color for every choice."""
    print("\n🔄 Fetching table schema...")
    resp = requests.get(TABLES_API_URL, headers=HEADERS)
    if resp.status_code == 200:
        data = resp.json().get("tables", [])
        for table in data:
            if table.get("id") == SOURCE_TABLE_ID:
                fields = []
                for field in table.get("fields", []):
                    field_schema = {"name": field["name"], "type": field["type"]}

                    # If it's the MF/FAIRE Order field, forcibly treat it as a select with a single color for all choices
                    if field["name"] == "MF/FAIRE Order" and field["type"] in ["singleSelect", "multipleSelect"]:
                        original_choices = field["options"].get("choices", [])
                        forced_choices = []
                        for ch in original_choices:
                            forced_choices.append({
                                "name": ch["name"],  
                                # forcibly set color to "blueDark" for every single choice
                                "color": "blueDark"  
                            })
                        field_schema["options"] = {"choices": forced_choices}
                    else:
                        # handle other field types as usual
                        if field["type"] in ["singleSelect","multipleSelect"]:
                            choices = field["options"].get("choices", [])
                            if choices:
                                new_choices = []
                                for c in choices:
                                    new_choices.append({
                                        "name": c["name"],
                                        "color": c.get("color","blueLight")
                                    })
                                field_schema["options"] = {"choices": new_choices}
                        elif field["type"] == "number":
                            field_schema["options"] = {"precision": field["options"].get("precision", 1)}
                        elif field["type"] == "currency":
                            field_schema["options"] = {
                                "precision": field["options"].get("precision", 2),
                                "symbol": field["options"].get("symbol", "$")
                            }
                        elif field["type"] == "rating":
                            field_schema["options"] = {"max": field["options"].get("max", 5)}
                        elif field["type"] == "checkbox":
                            field_schema["options"] = {"icon": "check"}
                    
                    fields.append(field_schema)
                return fields
    return []

def create_new_table():
    new_table_name = generate_table_name()
    fields = get_table_schema()
    if not fields:
        print("❌ No fields found. Table creation aborted.")
        return
    payload = {"name": new_table_name,"fields": fields}
    print("\n🔄 Sending table creation request...")
    r = requests.post(TABLES_API_URL, json=payload, headers=HEADERS)
    print("\n📢 API Response:")
    print(r.text)
    if r.status_code == 200:
        new_table_id = r.json().get("id")
        print(f"✅ Successfully created table: {new_table_name} (ID: {new_table_id})")
    else:
        print(f"❌ Error creating table: {r.status_code}, {r.text}")

create_new_table()
