import requests
import datetime

# Airtable API Credentials
AIRTABLE_BASE_ID = "appJrWoXe5H2YZnmU"  # Correct Base ID
AIRTABLE_API_KEY = "patkcqbpm4M0Z7WTg.676db3c4059059a9f74e2714bced3e09fbacabe05bb17bfa7b29aa792b9a80e0"
SOURCE_TABLE_ID = "tblZnkmYCBPNzv6rO"  # Confirmed Table ID for "Template"

# Airtable API URL
TABLES_API_URL = f"https://api.airtable.com/v0/meta/bases/{AIRTABLE_BASE_ID}/tables"

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
    """Retrieve field types & options from the 'Template' table."""
    response = requests.get(TABLES_API_URL, headers=HEADERS)

    if response.status_code == 200:
        tables = response.json().get("tables", [])
        for table in tables:
            if table.get("id") == SOURCE_TABLE_ID:
                fields = []
                for field in table.get("fields", []):
                    field_schema = {
                        "name": field["name"],
                        "type": field["type"]
                    }

                    # **Handle Single Select & Multi Select Fields**
                    if field["type"] in ["singleSelect", "multipleSelect"] and "options" in field:
                        choices = field["options"].get("choices", [])
                        field_schema["options"] = {
                            "choices": [
                                {
                                    "name": choice["name"],
                                    "color": choice.get("color", "blueLight")  # Assign default color if missing
                                } 
                                for choice in choices
                            ]
                        }

                    # Handle other field types
                    elif field["type"] == "number":
                        field_schema["options"] = {"precision": field["options"].get("precision", 1)}

                    elif field["type"] == "currency":
                        field_schema["options"] = {
                            "precision": field["options"].get("precision", 2),
                            "symbol": field["options"].get("symbol", "$")
                        }

                    elif field["type"] == "rating":
                        field_schema["options"] = {"max": field["options"].get("max", 5)}

                    elif field["type"] == "checkbox":
                        field_schema["options"] = {"icon": "check"}

                    fields.append(field_schema)
                return fields
        print("❌ Table ID not found in base!")
        return []
    else:
        print(f"❌ Error fetching table schema: {response.status_code}, {response.text}")
        return []

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
        print(f"✅ Successfully created table: {new_table_name} with correct field types & options")
        new_table_id = response.json().get("id")  # Retrieve the new table ID
        return new_table_id
    else:
        print(f"❌ Error creating table: {response.status_code}, {response.text}")
        return None

# Run the script
new_table_id = create_new_table()
