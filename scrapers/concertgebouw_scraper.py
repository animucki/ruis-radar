## Scraping Concertgebouw
import requests
from bs4 import BeautifulSoup

from config import dutch_months, venues
from utlis.date_utils import parse_dutch_date
from utlis.string_utils import add_separator


def scrape_concertgebouw(url=venues["Concertgebouw"], page=1, max_events=None):

    url = url + f"?page={page}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    events = []

    # Find each day section
    for day_section in soup.select("li.c-event-overview-list-item-day"):
        # Get the Dutch date string and parse it to ISO format
        date_str = day_section.select_one("h3.c-event-overview-list-item-day__title").get_text(strip=True)
        date = parse_dutch_date(date_str, dutch_months)

        # Find each event within this day
        for event_item in day_section.select("ul.mb-8 li.mb-6"):
            # Event link
            link = event_item.select_one("a")["href"]

            # Event name
            name = event_item.select_one("h3.c-content__title").get_text(strip=True)

            # Event time (if present)
            time_element = event_item.select_one("time")
            time = time_element.get_text(strip=True) if time_element else ""

            # Event image (if present)
            img_element = event_item.select_one("img")
            img_url = img_element["src"] if img_element else None

            # Description (list of pieces to be played)
            description = []
            description_element = event_item.select_one("div.text-xs.leading-tight ul")
            if description_element:
                # Extract each list item and add to description
                for item in description_element.select("li"):
                    description.append(add_separator(item.get_text(strip=True)))

            # Detect booking status
            booking_status = "Available"  # Default status
            status_element = event_item.select_one("footer p")
            if status_element:
                booking_status = status_element.get_text(strip=True)

            # Append the event data to the list
            events.append({
                "venue": "Concertgebouw",
                "date": date,
                "name": name,
                "time": time,
                "link": f"https://www.concertgebouw.nl{link}",
                "picture": img_url,
                "booking_status": booking_status,
                "description": "; ".join(description)
            })

            if (max_events is not None) and (len(events) >= max_events):
                return events

    return events
