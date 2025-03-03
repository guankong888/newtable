import requests
import datetime

# Airtable API Credentials
AIRTABLE_BASE_ID = "appJrWoXe5H2YZnmU"
AIRTABLE_API_KEY = "YOUR_KEY"
SOURCE_TABLE_ID = "tblZnkmYCBPNzv6rO"

TABLES_API_URL = f"https://api.airtable.com/v0/meta/bases/{AIRTABLE_BASE_ID}/tables"
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

def generate_table_name():
    """Generate table name in MM/DD-MM/DD/YYYY format for the current Monday and append 'Test'."""
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())  # Monday of current week
    sunday = monday + datetime.timedelta(days=6)               # Sunday of same week
    return f"{monday.strftime('%m/%d')}-{sunday.strftime('%m/%d/%Y')} Test"

def get_table_schema():
    """Retrieve schema from the 'Template' table, optionally excluding or converting MF/FAIRE Order."""
    response = requests.get(TABLES_API_URL, headers=HEADERS)
    if response.status_code == 200:
        tables = response.json().get("tables", [])
        for table in tables:
            if table.get("id") == SOURCE_TABLE_ID:
                fields = []
                for field in table.get("fields", []):
                    # ----------------------------
                    # APPROACH 1: EXCLUDE the field entirely
                    # if field["name"] == "MF/FAIRE Order":
                    #     continue
                    # ----------------------------
                    
                    # ----------------------------
                    # APPROACH 2: Convert MF/FAIRE Order to singleLineText
                    if field["name"] == "MF/FAIRE Order":
                        field_schema = {
                            "name": field["name"],
                            "type": "singleLineText"
                        }
                    else:
                        field_schema = {
                            "name": field["name"],
                            "type": field["type"]   # keep all other fields the same
                        }
                    # ----------------------------

                    fields.append(field_schema)
                return fields
    return []

def create_new_table():
    """Create a new table with the (modified) schema."""
    new_table_name = generate_table_name()
    fields = get_table_schema()

    if not fields:
        print("❌ No fields found. Table creation aborted.")
        return

    payload = {
        "name": new_table_name,
        "fields": fields
    }

    print(f"\n🔄 Sending table creation request for '{new_table_name}'...")
    resp = requests.post(TABLES_API_URL, json=payload, headers=HEADERS)

    print("\n📢 API Response:")
    print(resp.text)

    if resp.status_code == 200:
        new_table_id = resp.json().get("id")
        print(f"\n✅ Successfully created table: {new_table_name} (ID: {new_table_id})")
    else:
        print(f"\n❌ Error creating table: {resp.status_code}, {resp.text}")

# Run the script
create_new_table()
