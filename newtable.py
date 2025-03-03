import requests

# Airtable API Credentials
AIRTABLE_BASE_ID = "appJrWoXe5H2YZnmU"  # Correct Airtable Base ID
AIRTABLE_API_KEY = "patNrsSsWF1NpOExt.7d405eb26f24695e8cb633bc7d61d057416e01e731dc872e108b3bc7f37fc5ab"
SOURCE_TABLE_NAME = "Template"  # Table to duplicate
TEST_TABLE_NAME = "Test"  # Fixed name for testing

# Airtable API URL
AIRTABLE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}"

# Headers for authentication
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

def get_table_structure():
    """Retrieve the structure (field names & types) from the 'Records' table."""
    url = f"{AIRTABLE_URL}/{SOURCE_TABLE_NAME}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        records = response.json().get("records", [])
        if records:
            return [{"name": field, "type": "singleLineText"} for field in records[0]["fields"].keys()]
        else:
            print("❌ No records found in 'Records' table. Using default structure.")
            return []
    else:
        print(f"❌ Error fetching table structure: {response.status_code}, {response.text}")
        return []

def get_blank_records():
    """Retrieve row names (primary field) and generate blank entries."""
    url = f"{AIRTABLE_URL}/{SOURCE_TABLE_NAME}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        records = response.json().get("records", [])
        blank_records = []
        if records:
            primary_field = list(records[0]["fields"].keys())[0]  # First field is usually the primary key
            for record in records:
                blank_records.append({"fields": {primary_field: record["fields"].get(primary_field, "Unnamed")}})
        return blank_records
    else:
        print(f"❌ Error fetching records: {response.status_code}, {response.text}")
        return []

def create_test_table():
    """Create a new table named 'Test' with the same structure as 'Records'."""
    fields = get_table_structure()

    if not fields:
        print("❌ No fields found. Table creation aborted.")
        return

    url = f"{AIRTABLE_URL}/meta/tables"
    payload = {
        "name": TEST_TABLE_NAME,
        "fields": fields
    }

    response = requests.post(url, json=payload, headers=HEADERS)

    if response.status_code == 200:
        print(f"✅ Successfully created test table: {TEST_TABLE_NAME}")
        blank_records = get_blank_records()
        if blank_records:
            insert_blank_records(TEST_TABLE_NAME, blank_records)
    else:
        print(f"❌ Error creating test table: {response.status_code}, {response.text}")

def insert_blank_records(table_name, blank_records):
    """Insert blank records into the new table, keeping row names only."""
    url = f"{AIRTABLE_URL}/{table_name}"
    payload = {"records": blank_records}

    response = requests.post(url, json=payload, headers=HEADERS)

    if response.status_code == 200:
        print(f"✅ Blank records inserted successfully into {table_name}")
    else:
        print(f"❌ Error inserting blank records: {response.status_code}, {response.text}")

# Run the test now
create_test_table()
