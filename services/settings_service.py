
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
