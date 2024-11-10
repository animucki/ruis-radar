from datetime import datetime

import requests
from bs4 import BeautifulSoup

from config import venues

def _get_image_url(event_url):
    """Fetch the event page and extract the featured image URL."""
    response = requests.get(event_url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the main image within the featured-image-container
    img_element = soup.select_one("div.featured-image img")
    if img_element:
        return img_element["src"]
    return ""  # Return empty if no image is found

def scrape_zaal301(url=venues["Zaal 100"], max_events=None):
    # Fetch the webpage
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # List to store events
    events = []

    # Find each event
    for n_events, event in enumerate(soup.select("article.agenda-item")):

        link_element = event.select_one("a")
        if link_element:
            link = link_element["href"]
        else:
            link = ""

        # Get the image URL from the event page
        img_url = _get_image_url(link) if link else ""

        month = int(event.select_one("span.maand").get_text())
        if month == 100: # this is the case for expositions apparently. fuck expositions i want EVENTS
            continue

        day = int(event.select_one("span.datum").get_text())

        current_year = datetime.now().year
        current_month = datetime.now().month

        # Default to next year if currently H2 and event is in H1
        if current_month >= 7 and month in ["01", "02", "03", "04", "05", "06"]:
            year = current_year + 1
        else:
            year = current_year

        date = f"{year:04d}-{month:02d}-{day:02d}"

        title = event.select_one("h2.titel").get_text()

        pretitle_element = event.select_one("h4.voor-titel")
        aftertitle_element = event.select_one("h5.na-titel")

        description = ""
        if pretitle_element is not None:
            description += pretitle_element.get_text()
        if aftertitle_element is not None:
            description += " " + aftertitle_element.get_text()

        description = description.strip()

        time = event.select_one("div.tijd.floatleft").get_text()

        events.append({
            "venue": "Zaal 100",
            "date": date,
            "name": title,
            "time": time,
            "link": link,
            "picture": img_url,
            "description": description
        })

        # Stop if max_events is reached
        if max_events is not None and len(events) >= max_events:
            return events

    return events