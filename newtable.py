import requests

# Airtable API Credentials
AIRTABLE_BASE_ID = "appJrWoXe5H2YZnmU"
AIRTABLE_API_KEY = "patkcqbpm4M0Z7WTg.676db3c4059059a9f74e2714bced3e09fbacabe05bb17bfa7b29aa792b9a80e0"

# API URL to fetch all tables in the base
TABLES_API_URL = f"https://api.airtable.com/v0/meta/bases/{AIRTABLE_BASE_ID}/tables"

# Headers
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

def list_tables():
    """Retrieve all tables in the base to confirm Table ID."""
    response = requests.get(TABLES_API_URL, headers=HEADERS)

    if response.status_code == 200:
        tables = response.json()
        print("✅ Available Tables:", tables)
    else:
        print(f"❌ Error: {response.status_code}, {response.text}")

list_tables()
