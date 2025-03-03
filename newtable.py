import requests
import datetime

# Airtable API Credentials
AIRTABLE_BASE_ID = "appJrWoXe5H2YZnmU"
AIRTABLE_API_KEY = "patkcqbpm4M0Z7WTg.676db3c4059059a9f74e2714bced3e09fbacabe05bb17bfa7b29aa792b9a80e0"
SOURCE_TABLE_ID = "tblZnkmYCBPNzv6rO"

# Airtable API URL
TABLES_API_URL = f"https://api.airtable.com/v0/meta/bases/{AIRTABLE_BASE_ID}/tables"

# Headers for authentication
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

# Default color fallback
DEFAULT_COLOR = "blueLight"

def generate_table_name():
    """Generate table name in MM/DD-MM/DD/YYYY format for the current Monday and append 'Test'."""
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())
    sunday = monday + datetime.timedelta(days=6)
    return f"{monday.strftime('%m/%d')}-{sunday.strftime('%m/%d/%Y')} Test"

def get_table_schema():
    """Retrieve field types & options (including colors) from the 'Template' table."""
    print("\n🔄 Fetching table schema...")
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

                    # **Fix: Ensure Select Fields Retain Colors from Template**
                    if field["type"] in ["singleSelect", "multipleSelect"] and "options" in field:
                        choices = field["options"].get("choices", [])
                        
                        # **Ensure choices array is not empty**
                        if choices:
                            updated_choices = []
                            for choice in choices:
                                choice_color = choice.get("color", DEFAULT_COLOR)
                                updated_choices.append({
                                    "name": choice["name"],
                                    "color": choice_color
                                })
                            field_schema["options"] = {"choices": updated_choices}

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
                print("✅ Table schema retrieved successfully!")
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

    print("\n🔄 Sending table creation request to Airtable...")
    response = requests.post(TABLES_API_URL, json=payload, headers=HEADERS)

    print("\n📢 API Response:")
    print(response.text)

    if response.status_code == 200:
        new_table_id = response.json().get("id")
        print(f"\n✅ Successfully created table: {new_table_name} (ID: {new_table_id})")
        return new_table_id
    else:
        print(f"\n❌ Error creating table: {response.status_code}, {response.text}")
        return None

# Run the script
new_table_id = create_new_table()
