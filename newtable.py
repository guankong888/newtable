import requests

# Airtable API Credentials
AIRTABLE_BASE_ID = "appJrWoXe5H2YZnmU"  # Your Base ID
AIRTABLE_API_KEY = "patkcqbpm4M0Z7WTg.676db3c4059059a9f74e2714bced3e09fbacabe05bb17bfa7b29aa792b9a80e0"

# API URL for Creating Tables (Meta API)
AIRTABLE_URL = f"https://api.airtable.com/v0/meta/bases/{AIRTABLE_BASE_ID}/tables"

# Headers for authentication
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

def create_test_table():
    """Attempt to create a test table with correct schema."""
    payload = {
        "name": "TestTableCreation",
        "fields": [
            {"name": "TestField1", "type": "singleLineText"},
            {"name": "TestField2", "type": "number", "options": {"precision": 1}}  # Fixed number field
        ]
    }

    response = requests.post(AIRTABLE_URL, json=payload, headers=HEADERS)

    if response.status_code == 200:
        print("✅ Successfully created table: TestTableCreation")
    else:
        print(f"❌ Error creating table: {response.status_code}, {response.text}")

create_test_table()
