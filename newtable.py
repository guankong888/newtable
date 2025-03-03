import requests
import datetime
import time

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

# List of Airtable supported colors for Select fields
AIRTABLE_COLORS = [
    "blueLight", "blueBright", "blueDark",
    "cyanLight", "cyanBright", "cyanDark",
    "tealLight", "tealBright", "tealDark",
    "greenLight", "greenBright", "greenDark",
    "yellowLight", "yellowBright", "yellowDark",
    "orangeLight", "orangeBright", "orangeDark",
    "redLight", "redBright", "redDark",
    "pinkLight", "pinkBright", "pinkDark",
    "purpleLight", "purpleBright", "purpleDark",
    "grayLight", "grayBright", "grayDark"
]

def generate_table_name():
    """Generate table name in MM/DD-MM/DD/YYYY format for the current Monday and append 'Test'."""
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())
    sunday = monday + datetime.timedelta(days=6)
    return f"{monday.strftime('%m/%d')}-{sunday.strftime('%m/%d/%Y')} Test"

def get_table_schema():
    """Retrieve field types & options from the 'Template' table."""
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

                    if field["type"] in ["singleSelect", "multipleSelect"] and "options" in field:
                        choices = field["options"].get("choices", [])
                        field_schema["options"] = {
                            "choices": [
                                {
                                    "name": choice["name"],
                                    "color": choice.get("color", AIRTABLE_COLORS[i % len(AIRTABLE_COLORS)])
                                } 
                                for i, choice in enumerate(choices)
                            ]
                        }

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

def confirm_table_exists():
    """Check if the newly created table actually exists."""
    print("\n🔄 Confirming if the table was created successfully...")
    response = requests.get(TABLES_API_URL, headers=HEADERS)

    if response.status_code == 200:
        tables = response.json().get("tables", [])
        table_names = [table["name"] for table in tables]
        print("\n📋 Current Tables in Base:")
        for table in table_names:
            print(f"   - {table}")
        
        new_table_name = generate_table_name()
        if new_table_name in table_names:
            print(f"\n✅ The table '{new_table_name}' was successfully created!")
        else:
            print(f"\n⚠️ Table '{new_table_name}' does NOT exist. Something went wrong!")
    else:
        print(f"❌ Error confirming table existence: {response.status_code}, {response.text}")

# Run the script
new_table_id = create_new_table()
if new_table_id:
    confirm_table_exists()
