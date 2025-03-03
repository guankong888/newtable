import requests

# Airtable API Credentials
AIRTABLE_BASE_ID = "appJrWoXe5H2YZnmU"  # Ensure this is correct
AIRTABLE_API_KEY = "patkcqbpm4M0Z7WTg.676db3c4059059a9f74e2714bced3e09fbacabe05bb17bfa7b29aa792b9a80e0"

# Airtable API URL
AIRTABLE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}"

# Headers for authentication
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

def check_airtable_access():
    """Check if the API key has access to the correct base and list available tables."""
    response = requests.get(AIRTABLE_URL, headers=HEADERS)

    if response.status_code == 200:
        print("✅ Airtable connection successful!")
        print("Available Tables:", response.json())
    else:
        print(f"❌ Error: {response.status_code}, {response.text}")

check_airtable_access()
