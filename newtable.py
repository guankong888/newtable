import requests

# Airtable API Credentials
AIRTABLE_BASE_ID = "appJrWoXe5H2YZnmU"  # Correct Airtable Base ID
AIRTABLE_API_KEY = "patkcqbpm4M0Z7WTg.676db3c4059059a9f74e2714bced3e09fbacabe05bb17bfa7b29aa792b9a80e0"
SOURCE_TABLE_NAME = "Template"  # Table to duplicate
TEST_TABLE_NAME = "Test"  # Fixed name for testing

# Airtable API URL
AIRTABLE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}"

# Headers for authentication
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

def get_table_records():
    """Retrieve all records from the 'Template' table."""
    url = f"{AIRTABLE_URL}/{SOURCE_TABLE_NAME}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        records = response.json().get("records", [])
        if records:
            return records
        else:
            print("❌ No records found in 'Template' table.")
            return []
    else:
        print(f"❌ Error fetching records: {response.status_code}, {response.text}")
        return []

def duplicate_table():
    """Automatically create a test table and copy structure from 'Template'."""
    new_table_name = TEST_TABLE_NAME  # Fixed table name for testing
    records = get_table_records()

    if not records:
        print("❌ No records found. Table duplication aborted.")
        return

    blank_records = []
    primary_field = list(records[0]["fields"].keys())[0]  # First field (usually primary key)

    for record in records:
        blank_records.append({"fields": {primary_field: record["fields"].get(primary_field, "Unnamed")}})

    url = f"{AIRTABLE_URL}/{new_table_name}"  # Target table
    payload = {"records": blank_records}

    response = requests.post(url, json=payload, headers=HEADERS)

    if response.status_code == 200:
        print(f"✅ Successfully duplicated 'Template' into {new_table_name}")
    else:
        print(f"❌ Error inserting blank records: {response.status_code}, {response.text}")

# Run the test now
duplicate_table()
