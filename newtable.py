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
    resp = requests.get(TABLES_API_URL, headers=HEADERS)
    if resp.status_code == 200:
        data = resp.json().get("tables", [])
        for tbl in data:
            if tbl.get("id") == SOURCE_TABLE_ID:
                raw_fields = tbl.get("fields", [])
                fields = []
                for field in raw_fields:
                    fname = field["name"]
                    ftype = field["type"]
                    
                    field_schema = {"name": fname, "type": ftype}
                    
                    # If it's a checkbox, see if there's a color in the metadata
                    if ftype == "checkbox":
                        # Check if the metadata provided any color
                        # Usually it might be "options": { "icon":"check", "color":"blueDark" } 
                        meta_options = field.get("options", {})
                        icon = meta_options.get("icon", "check")
                        color = meta_options.get("color", "blueBright")  # fallback color
                        
                        field_schema["options"] = {
                            "icon": icon,
                            "color": color
                        }
                    
                    # Single/multi select logic, rating, currency, etc. can go here if needed
                    fields.append(field_schema)
                return fields
    return []

def create_new_table():
    new_table_name = generate_table_name()
    fields = get_table_schema()
    if not fields:
        print("No fields found, aborting.")
        return
    
    payload = {"name": new_table_name, "fields": fields}
    resp = requests.post(TABLES_API_URL, json=payload, headers=HEADERS)
    print(resp.text)

create_new_table()
