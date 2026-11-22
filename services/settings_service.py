
SETTING_COLUMNS = {
    "expense_categories": "A",
    "income_sources": "B",
    "payment_methods": "C"
}


def get_settings(service, spreadsheet_id):

    ranges = [
        "'Settings'!A2:A",
        "'Settings'!B2:B",
        "'Settings'!C2:C"
    ]

    response = service.spreadsheets().values().batchGet(
        spreadsheetId=spreadsheet_id,
        ranges=ranges
    ).execute()

    value_ranges = response.get("valueRanges", [])

    def extract_values(value_range):

        return [
            row[0].strip()
            for row in value_range.get("values", [])
            if row and row[0].strip()
        ]

    expense_categories = extract_values(value_ranges[0])
    income_sources = extract_values(value_ranges[1])
    payment_methods = extract_values(value_ranges[2])

    return {
        "expense_categories": expense_categories,
        "income_sources": income_sources,
        "payment_methods": payment_methods
    }


def add_setting_value(service, spreadsheet_id, setting_type, value):
    """Append a unique setting to its existing Settings worksheet column."""
    if setting_type not in SETTING_COLUMNS:
        raise ValueError(f"Unsupported setting type: {setting_type}")

    normalized_value = value.strip()
    if not normalized_value:
        raise ValueError("Setting value cannot be empty.")

    settings = get_settings(service, spreadsheet_id)
    if normalized_value.casefold() in {
        existing.casefold() for existing in settings[setting_type]
    }:
        raise ValueError("This value already exists.")

    column = SETTING_COLUMNS[setting_type]
    return service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=f"'Settings'!{column}:{column}",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": [[normalized_value]]}
    ).execute()
