import requests

# Airtable API Credentials
AIRTABLE_BASE_ID = "appJrWoXe5H2YZnmU"  # Correct Base ID
AIRTABLE_API_KEY = "patkcqbpm4M0Z7WTg.676db3c4059059a9f74e2714bced3e09fbacabe05bb17bfa7b29aa792b9a80e0"
SOURCE_TABLE_ID = "tblZnkmYCBPNzv6rO"  # Correct Table ID for "Template"

# Airtable API URL (Using Table ID Instead of Name)
AIRTABLE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{SOURCE_TABLE_ID}"

# Headers for authentication
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

def test_table_access():
    """Check if API Key can access the table using Table ID."""
    response = requests.get(AIRTABLE_URL, headers=HEADERS)

    if response.status_code == 200:
        print("✅ API Key can access 'Template' using Table ID. Sample Data:")
        print(response.json())
    else:
        print(f"❌ Error: {response.status_code}, {response.text}")

test_table_access()
