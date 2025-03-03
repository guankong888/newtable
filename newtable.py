import requests
import datetime

AIRTABLE_BASE_ID = "appJrWoXe5H2YZnmU"
AIRTABLE_API_KEY = "YOUR_KEY"
SOURCE_TABLE_ID = "tblZnkmYCBPNzv6rO"

TABLES_API_URL = f"https://api.airtable.com/v0/meta/bases/{AIRTABLE_BASE_ID}/tables"
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}

def generate_table_name():
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())
    sunday = monday + datetime.timedelta(days=6)
    return f"{monday.strftime('%m/%d')}-{sunday.strftime('%m/%d/%Y')} Test"

def get_table_schema():
    response = requests.get(TABLES_API_URL, headers=HEADERS)
    if response.status_code == 200:
        tables = response.json().get("tables", [])
        for table in tables:
            if table.get("id") == SOURCE_TABLE_ID:
                fields = []
                for field in table.get("fields", []):
                    # Skip the "MF/FAIRE Order" field entirely
                    if field["name"] == "MF/FAIRE Order":
                        continue

                    # Keep everything else the same
                    field_schema = {"name": field["name"], "type": field["type"]}
                    if field["type"] in ["singleSelect","multipleSelect"] and "options" in field:
                        # ...existing logic for choices...
                        # but we skip "MF/FAIRE Order" entirely, so it's never processed
                        pass

                    # or handle other fields...
                    fields.append(field_schema)
                return fields
    return []

def create_new_table():
    new_table_name = generate_table_name()
    fields = get_table_schema()
    if not fields:
        print("No fields found, aborting.")
        return
    payload = {"name": new_table_name,"fields": fields}
    resp = requests.post(TABLES_API_URL, json=payload, headers=HEADERS)
    print(resp.text)

create_new_table()
