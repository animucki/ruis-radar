from datetime import datetime


def parse_dutch_date(date_str, months):
    """Parse a Dutch date string into an ISO date string (YYYY-MM-DD)."""
    parts = date_str.split()  # e.g., ["za", "9", "nov", "2024"]
    day = parts[1]
    month = months[parts[2].lower()]  # Convert month abbreviation

    # Determine the year
    if len(parts) == 4:  # Year is specified
        year = parts[3]
    else:  # Year is not specified
        current_year = datetime.now().year
        current_month = datetime.now().month

        # Default to next year if currently Q4 and event is in Q1
        if current_month >= 10 and month in ["01", "02", "03"]:
            year = str(current_year + 1)
        else:
            year = str(current_year)
    return f"{year}-{month}-{day.zfill(2)}"