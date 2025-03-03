import requests
import datetime
import time

# Airtable API Credentials
AIRTABLE_BASE_ID = "appJrWoXe5H2YZnmU"  # Correct Base ID
AIRTABLE_API_KEY = "patkcqbpm4M0Z7WTg.676db3c4059059a9f74e2714bced3e09fbacabe05bb17bfa7b29aa792b9a80e0"
SOURCE_TABLE_ID = "tblZnkmYCBPNzv6rO"  # Confirmed Table ID for "Template"

# Columns to Exclude Values From (Headers will still be copied)
EXCLUDED_COLUMNS = ["MF/FAIRE Order", "N2G Water", "SUPP RESTOCK", "Notes", "Last Modified By"]

# Airtable API URLs
TABLES_API_URL = f"https://api.airtable.com/v0/meta/bases/{AIRTABLE_BASE_ID}/tables"
VIEWS_API_URL = f"https://api.airtable.com/v0/meta/bases/{AIRTABLE_BASE_ID}/tables/{SOURCE_TABLE_ID}/views"

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

def get_table_schema():
    """Retrieve field types from the 'Template' table using metadata API."""
    response = requests.get(TABLES_API_URL, headers=HEADERS)

    if response.status_code == 200:
        tables = response.json().get("tables", [])
        for table in tables:
            if table.get("id") == SOURCE_TABLE_ID:
                fields = []
                for field in table.get("fields", []):
                    fields.append({"name": field["name"], "type": field["type"]})
                return fields
        print("❌ Table ID not found in base!")
        return []
    else:
        print(f"❌ Error fetching table schema: {response.status_code}, {response.text}")
        return []

def get_view_settings():
    """Retrieve grid view & grouping settings from the 'Template' table."""
    response = requests.get(VIEWS_API_URL, headers=HEADERS)

    if response.status_code == 200:
        views = response.json().get("views", [])
        if views:
            return views[0]  # Assuming first view is the default grid view
        else:
            print("⚠️ No views found in 'Template'. Using default settings.")
            return None
    else:
        print(f"⚠️ Could not fetch view settings: {response.status_code}, {response.text}")
        return None

def create_new_table():
    """Create a new table with the same schema as 'Template' and retrieve its ID."""
    new_table_name = generate_table_name()
    fields = get_table_schema()

    if not fields:
        print("❌ No fields found. Table creation aborted.")
        return None

    payload = {
        "name": new_table_name,
        "fields": fields
    }

    response = requests.post(TABLES_API_URL, json=payload, headers=HEADERS)

    if response.status_code == 200:
        print(f"✅ Successfully created table: {new_table_name} with correct field types")
        new_table_id = response.json().get("id")  # Retrieve the new table ID
        return new_table_id
    else:
        print(f"❌ Error creating table: {response.status_code}, {response.text}")
        return None

def apply_view_settings(new_table_id):
    """Apply grouping and sorting from 'Template' to the new table."""
    view_settings = get_view_settings()
    if not view_settings:
        print("⚠️ No view settings applied.")
        return

    view_payload = {
        "name": view_settings.get("name", "Grid view"),
        "fields": view_settings.get("fields", []),
        "grouping": view_settings.get("grouping", []),
        "sorting": view_settings.get("sorting", []),
        "layout": view_settings.get("layout", "grid"),
    }

    url = f"https://api.airtable.com/v0/meta/bases/{AIRTABLE_BASE_ID}/tables/{new_table_id}/views"

    response = requests.post(url, json=view_payload, headers=HEADERS)

    if response.status_code == 200:
        print(f"✅ Applied view settings from Template to new table: {new_table_id}")
    else:
        print(f"❌ Error applying view settings: {response.status_code}, {response.text}")

# Run the script
new_table_id = create_new_table()
if new_table_id:
    apply_view_settings(new_table_id)
