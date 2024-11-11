from datetime import datetime
import requests
from bs4 import BeautifulSoup
from config import venues


def fetch_event_image(link):
    # Fetches the image URL from the event detail page.
    response = requests.get(link)
    detail_soup = BeautifulSoup(response.text, "html.parser")
    img_element = detail_soup.select_one("div.field-name-field-image img.image-style-none")
    return img_element["src"] if img_element else ""


def scrape_vondelbunker(url=venues["Vondelbunker"], max_events=None):
    # Fetch the main events page
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Locate the event table
    table = soup.select_one("table.views-table")
    if not table:
        print("No events found in the expected table.")
        return []

    # List to store events
    events = []

    # Loop through each row in the table's tbody
    for row in table.select("tbody tr"):
        # Date information
        date_text = row.select_one("div.date").get_text(strip=True)
        date_element = row.select_one("[property='schema:startDate']")
        date_iso = date_element["content"].split("T")[0] if date_element else ""
        time_start = datetime.fromisoformat(date_element["content"]).strftime("%H:%M") if date_element else ""

        # Handle events with end time
        date_end_element = row.select_one("[property='schema:endDate']")
        time_end = datetime.fromisoformat(date_end_element["content"]).strftime("%H:%M") if date_end_element else None

        time = time_start
        if time_end is not None:
            time += "-" + time_end

        # Event title and link
        title_element = row.select_one("a")
        title = title_element.get_text(strip=True) if title_element else ""
        link = "https://radar.squat.net" + title_element["href"] if title_element else "#"

        # Event categories
        categories = row.select_one("td:nth-of-type(3)").get_text(strip=True) if row.select_one("td:nth-of-type(3)") else ""

        # Fetch image URL from the event detail page
        img_url = fetch_event_image(link)

        # Append event data to the list
        events.append({
            "venue": "Vondelbunker",
            "date": date_iso,
            "name": title,
            "time": time,
            "link": link,
            "picture": img_url,
            "type": categories
        })

        # Stop if max_events is reached
        if (max_events is not None) and (len(events) >= max_events):
            return events

    return events
