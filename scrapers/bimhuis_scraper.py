import requests
from bs4 import BeautifulSoup

from config import dutch_months_long, venues
from utlis.date_utils import parse_dutch_date


def _get_event_time(event_url):
    # Navigate to the event's ticket page to retrieve start and end times.
    response = requests.get(event_url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find start and end times from the table
    start_time, end_time = None, None
    for row in soup.select("table.price-table tr"):
        label = row.select_one("td").get_text(strip=True)
        time = row.select_one("td b").get_text(strip=True) if row.select_one("td b") else None
        if "Aanvang" in label:
            start_time = time.replace("u", "")

    return start_time


def scrape_bimhuis(url=venues["Bimhuis"], max_events=None):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # List to store events
    events = []

    # Find each event item in the main agenda
    for event_item in soup.select("ul.items li.maand"):
        # Event title
        name = event_item.select_one("h3").get_text(strip=True)

        # Event link
        link = event_item.select_one("a")["href"]

        # Event date
        date_str = event_item.select_one("div.date").get_text(strip=True)
        date = parse_dutch_date(date_str, dutch_months_long)

        # Event description (sub-title)
        description_element = event_item.select_one("div.sub-title")
        description = description_element.get_text(strip=True) if description_element else ""

        # Image URL (optional)
        img_element = event_item.select_one("img.load-img")
        img_url = img_element["data-src"] if img_element else None

        # Fetch start and end times from the event's ticket page
        time = _get_event_time(link)

        # past event, don't ned to scraped
        if time is None:
            continue

        # Append event data to the list
        events.append({
            "venue": "Bimhuis",
            "date": date,
            "name": name,
            "time": time,
            "link": link,
            "picture": img_url,
            "description": description
        })

        if (max_events is not None) and (len(events) >= max_events):
            return events

    return events

