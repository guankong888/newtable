import requests
import datetime
import time

# Airtable API Credentials
AIRTABLE_BASE_ID = "appJrWoXe5H2YZnmU"  # Correct Base ID
AIRTABLE_API_KEY = "patkcqbpm4M0Z7WTg.676db3c4059059a9f74e2714bced3e09fbacabe05bb17bfa7b29aa792b9a80e0"
SOURCE_TABLE_ID = "tblZnkmYCBPNzv6rO"  # Table ID for "Template"

# Columns to Exclude Values From (Headers will still be copied)
EXCLUDED_COLUMNS = ["MF/FAIRE Order", "N2G Water", "SUPP RESTOCK", "Notes"]

# Airtable API URL
AIRTABLE_URL = f"https://api.airtable.com/v0/meta/bases/{AIRTABLE_BASE_ID}/tables"

# Headers for authentication
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

def generate_table_name():
    """Generate table name in MM/DD-MM/DD/YYYY format for the current Monday and append 'Test'."""
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())  # Get Monday of the current week
    sunday = monday + datetime.timedelta(days=6)  # Get Sunday of the same week
    return f"{monday.strftime('%m/%d')}-{sunday.strftime('%m/%d/%Y')} Test"

def get_table_structure():
    """Retrieve all column names from the 'Template' table."""
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{SOURCE_TABLE_ID}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        records = response.json().get("records", [])
        if records:
            fields = []
            for field_name in records[0]["fields"].keys():
                fields.append({"name": field_name, "type": "singleLineText"})  # Defaulting all fields to text
            return fields
        else:
            print("❌ No records found in 'Template' table.")
            return []
    else:
        print(f"❌ Error fetching table structure: {response.status_code}, {response.text}")
        return []

def create_new_table():
    """Create a new table with the same structure as 'Template' and retrieve its ID."""
    new_table_name = generate_table_name()
    fields = get_table_structure()

    if not fields:
        print("❌ No fields found. Table creation aborted.")
        return None

    url = f"https://api.airtable.com/v0/meta/bases/{AIRTABLE_BASE_ID}/tables"
    payload = {
        "name": new_table_name,
        "fields": fields
    }

    response = requests.post(url, json=payload, headers=HEADERS)

    if response.status_code == 200:
        print(f"✅ Successfully created table: {new_table_name} with Template structure")
        new_table_id = response.json().get("id")  # Retrieve the new table ID
        return new_table_id
    else:
        print(f"❌ Error creating table: {response.status_code}, {response.text}")
        return None

def get_table_records():
    """Retrieve all records from the 'Template' table."""
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{SOURCE_TABLE_ID}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        return response.json().get("records", [])
    else:
        print(f"❌ Error fetching records: {response.status_code}, {response.text}")
        return []

def populate_table(new_table_id):
    """Duplicate all records from 'Template' to the newly created table while excluding specified columns."""
    records = get_table_records()

    if not records:
        print("❌ No records found to duplicate.")
        return

    new_records = []
    
    for record in records:
        new_record_fields = {}
        
        for field_name, field_value in record["fields"].items():
            if field_name in EXCLUDED_COLUMNS:
                new_record_fields[field_name] = ""  # Keep header, remove values
            else:
                new_record_fields[field_name] = field_value  # Copy values
                
        new_records.append({"fields": new_record_fields})

    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{new_table_id}"  # Use the new Table ID
    payload = {"records": new_records}

    response = requests.post(url, json=payload, headers=HEADERS)

    if response.status_code == 200:
        print(f"✅ Successfully populated table: {new_table_id}")
    else:
        print(f"❌ Error inserting records: {response.status_code}, {response.text}")

# Run the script
new_table_id = create_new_table()
if new_table_id:
    populate_table(new_table_id)
