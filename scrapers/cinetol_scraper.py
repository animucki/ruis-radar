from datetime import datetime
import requests
from bs4 import BeautifulSoup
from config import venues
import re

def scrape_event_time(event_url):
    """Fetch and parse event-specific page to extract the start time from the description section."""
    response = requests.get(event_url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the description section
    description_section = soup.select_one("div.eventon_desc_in")
    if not description_section:
        return None  # Return None if description section isn't found

    # Search for 'Aanvang |' followed by time using regular expressions
    match = re.search(r"Aanvang\s*\|\s*([0-9]{2}:[0-9]{2})", description_section.get_text())
    if match:
        return match.group(1)  # Return the matched time in HH:MM format

    return None  # Return None if 'Aanvang' time isn't found

def scrape_cinetol(url=venues["Cinetol"], max_events=None):
    # Fetch the main events page
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # List to store events
    events = []

    # Find each month of events
    for n_events, month_div in enumerate(soup.select("div.sep_month_events")):
        for event in month_div.select("div.event"):
            # Event link and title
            link = event.select_one("a[itemprop='url']")["href"]
            title = event.select_one("span[itemprop='name']").get_text(strip=True)

            # Skip volunteer-related open calls
            if title.startswith("OPEN CALL"):
                continue

            # Basic metadata from main page
            start_date = event.select_one("meta[itemprop='startDate']")["content"]
            img_url = event.select_one("meta[itemprop='image']")["content"]
            description = event.select_one("meta[itemprop='description']")["content"]

            # Default date format
            date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y-%m-%d")

            # Attempt to fetch the exact start time from the event page
            start_time = scrape_event_time(link)

            # Fallback if 'Aanvang' isn't specified
            if not start_time:
                # Use Unix timestamp time as a fallback if no 'Aanvang' time found
                time_unix = int(event["data-time"].split("-")[0])
                start_time = datetime.fromtimestamp(time_unix).strftime("%H:%M")

            # Append to events list
            events.append({
                "venue": "Cinetol",
                "date": date,
                "name": title,
                "time": start_time,
                "link": link,
                "picture": img_url,
                "description": description
            })

            # Stop if max_events is reached
            if max_events is not None and len(events) >= max_events:
                return events

    return events
