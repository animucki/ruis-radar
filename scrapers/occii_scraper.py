from datetime import datetime

import requests
from bs4 import BeautifulSoup

from config import venues


def _parse_occ_date(date_str):
    # Parse OCCII date format like "Saturday, November 9" into an ISO date (YYYY-MM-DD).
    try:
        return datetime.strptime(date_str.strip(), "%A, %B %d").replace(year=datetime.now().year).strftime("%Y-%m-%d")
    except ValueError:
        return None  # Handle parsing errors if any

def scrape_occii(url=venues["Occii"], max_events=None):
    # Fetch the webpage
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # List to store events
    events = []

    # Find each event in the OCCII events container
    for n_events, event in enumerate(soup.select("div.occii-event-display")):
        # Event image URL
        img_element = event.select_one("div.occii-event-display-image img")
        img_url = img_element["src"] if img_element else None

        # Event title and link
        title_element = event.select_one("h3.occii-event-link a")
        title = title_element.get_text(strip=True) if title_element else ""
        link = title_element["href"] if title_element else "#"

        # Event date and time
        date_time_element = event.select_one("p.occii-event-times")
        date_str, *time_parts = date_time_element.get_text().splitlines()
        date = _parse_occ_date(date_str)
        time = time_parts[0].replace("Doors open: ", "").strip() if time_parts else ""

        # Event description
        description_element = event.select_one("p.occii-events-description")
        description = description_element.get_text(strip=True) if description_element else ""

        # Append event data to the list
        events.append({
            "venue": "OCCII",
            "date": date,
            "name": title,
            "time": time,
            "link": link,
            "picture": img_url,
            "description": description
        })

        if (max_events is not None) and (n_events >= max_events):
            return events

    return events
