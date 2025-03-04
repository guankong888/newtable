import requests
import datetime

# ---------------------------------------------------------------------------------
# 1) ACTUAL API CREDENTIALS (FROM YOU)
# ---------------------------------------------------------------------------------
AIRTABLE_BASE_ID = "appJrWoXe5H2YZnmU"
AIRTABLE_API_KEY = "patkcqbpm4M0Z7WTg.676db3c4059059a9f74e2714bced3e09fbacabe05bb17bfa7b29aa792b9a80e0"
SOURCE_TABLE_ID = "tblZnkmYCBPNzv6rO"
# ---------------------------------------------------------------------------------

TABLES_API_URL = f"https://api.airtable.com/v0/meta/bases/{AIRTABLE_BASE_ID}/tables"
HEADERS = {
    "Authorization": f"Bearer {AIRTABLE_API_KEY}",
    "Content-Type": "application/json"
}


def list_all_tables():
    """
    Lists all tables in the base, showing their names, IDs, and raw fields.
    This helps confirm the base and token are valid, and we see if MF/FAIRE
    Order is present.
    """
    print("\n===== LIST ALL TABLES IN BASE =====")
    resp = requests.get(TABLES_API_URL, headers=HEADERS)
    if resp.status_code == 200:
        data = resp.json().get("tables", [])
        if not data:
            print("No tables found in this base!")
        else:
            for tbl in data:
                tname = tbl.get("name", "UNKNOWN_NAME")
                tid = tbl.get("id", "UNKNOWN_ID")
                fields_data = tbl.get("fields", [])
                print(f"\nTABLE NAME: {tname}")
                print(f"TABLE ID:   {tid}")
                print("FIELDS:")
                for f in fields_data:
                    print(f"   - {f}")
    else:
        print(f"Error listing tables: {resp.status_code}, {resp.text}")


def generate_table_name():
    """
    Generate table name in MM/DD-MM/DD/YYYY format for the current Monday
    and append 'Test' so we can see it was created by our script.
    """
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())
    sunday = monday + datetime.timedelta(days=6)
    return f"{monday.strftime('%m/%d')}-{sunday.strftime
