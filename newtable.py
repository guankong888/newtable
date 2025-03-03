import requests
import datetime

# ----------------------------
# 1) CHANGE THESE TO YOUR ACTUAL VALUES
# ----------------------------
AIRTABLE_BASE_ID = "appJrWoXe5H2YZnmU"
AIRTABLE_API_KEY = "YOUR_API_KEY"
SOURCE_TABLE_ID = "tblZnkmYCBPNzv6rO"  # The Template table ID you're targeting

# ----------------------------
# 2) API URLs & HEADERS
# ----------------------------
TABLES_API_URL = f"https://api.airtable.com/v0/meta/bases/{AIRTABLE_BASE_ID}/tables"
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

# ----------------------------
# 3) UTILITY FUNCTIONS (List all tables for debugging)
# ----------------------------
def list_all_tables():
    """
    This function lists all tables in the base,
    printing their names, IDs, and RAW field data.
    """
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
                print(f"\nTABLE NAME: {tname}\nTABLE ID: {tid}\nFIELDS:")
                for f in fields_data:
                    print(f"   - {f}")
    else:
        print(f"Error listing tables: {resp.status_code}, {resp.text}")

# ----------------------------
# 4) MAIN SCRIPT: CREATE A NEW TABLE
# ----------------------------
def generate_table_name():
    """
    Generate table name in MM/DD-MM/DD/YYYY format for the current Monday,
    and append 'Test' so we can see it was created by our script.
    """
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())  # Monday of current week
    sunday = monday + datetime.timedelta(days=6)               # Sunday of same week
    return f"{monday.strftime('%m/%d')}-{sunday.strftime('%m/%d/%Y')} Test"

def get_table_schema():
    """
    Retrieve the schema for SOURCE_TABLE_ID from the base,
    then build a field list that we will use to create a new table.
    
    ADDED DEBUG LOGS to show RAW fields that we see.
    """
    print("\n===== FETCH TABLE SCHEMA =====")
    resp = requests.get(TABLES_API_URL, headers=HEADERS)
    if resp.status_code != 200:
        print(f"❌ Error {resp.status_code} fetching table info: {resp.text}")
        return []
    
    data = resp.json().get("tables", [])
    if not data:
        print("No tables found at all!")
        return []
    
    # Find the table by ID
    for tbl in data:
        tname = tbl.get("name", "NO_NAME")
        tid = tbl.get("id", "NO_ID")
        if tid == SOURCE_TABLE_ID:
            print(f"\n✅ Found Template Table: {tname} (ID: {tid})")
            
            # Here are the raw fields
            raw_fields = tbl.get("fields", [])
            print(f"🔎 RAW FIELDS from Template (count={len(raw_fields)}):")
            for rf in raw_fields:
                print(f"   → {rf}")
            
            # We'll keep this script super simple:
            # We won't exclude or convert anything automatically here,
            # just returning all fields as they are:
            fields = []
            for field in raw_fields:
                # For debugging, let's just print the name and type
                fname = field.get("name")
                ftype = field.get("type")
                print(f"Processing field → Name: {fname}, Type: {ftype}")
                
                field_schema = {
                    "name": fname,
                    "type": ftype
                }
                fields.append(field_schema)
            
            # Now we've built a fields list from RAW
            print(f"Built a final fields list of length {len(fields)}!")
            return fields
    
    print(f"❌ Could not find table with ID={SOURCE_TABLE_ID} in the base!")
    return []

def create_new_table():
    """
    Build a new table name, fetch the schema from the Template,
    then POST to create the new table, printing the API response.
    """
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

# ----------------------------
# 5) RUN THE DEBUGGING
# ----------------------------
if __name__ == "__main__":
    # 1) List all tables (for debugging)
    list_all_tables()
    
    # 2) Attempt to create new table from Template
    create_new_table()
