## Scraping Muziekgebouw
import re

import requests
from bs4 import BeautifulSoup

from config import dutch_months, venues
from utlis.date_utils import parse_dutch_date
from utlis.string_utils import add_separator


# Helper to extract background-image URL from inline CSS in <style> tags
def _extract_image_url(style_content):
    match = re.search(r"background-image: url\('([^']+)'\);", style_content)
    return match.group(1) if match else None

def scrape_muziekgebouw(url=venues["Muziekgebouw"], page=1, max_events=None):

    url = url + f"?page={page}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    events = []

    # Find each event listing in the <ul class="listItems variant-normal">
    for n_events, event_item in enumerate(soup.select("ul.listItems.variant-normal li.eventCard")):
        # Check for Bimhuis venue and skip if found
        venue_element = event_item.select_one("div.venue")
        if venue_element and "Bimhuis" in venue_element.get_text(strip=True):
            continue  # Skip this event if venue is Bimhuis

        # Event name
        name = event_item.select_one("h2.title").get_text(strip=True)

        # Event subtitle and concatenation with the name
        subtitle = ""
        subtitle_element = event_item.select_one("div.subtitle")
        if subtitle_element:
            subtitle = subtitle_element.get_text(strip=True)
        if subtitle != "":
            name = f"{name} : {subtitle}"

        # Event link
        link = event_item.select_one("a.desc")["href"]

        # Event date
        date_str = event_item.select_one("span.start").get_text(strip=True)
        date = parse_dutch_date(date_str, dutch_months)

        # Event time
        time = event_item.select_one("span.time").get_text(strip=True)

        # Extract the background image URL from <style> tag
        style_content = event_item.find("style").string
        img_url = _extract_image_url(style_content)

        # Description (tagline)
        tagline_element = event_item.select_one("div.tagline p")
        if tagline_element:
            description = add_separator(tagline_element.get_text(strip=True))
        else:
            description = ""

        # Detect booking status
        booking_status = "Available"  # Default status
        status_element = event_item.select_one("a.status-info .label")
        if status_element:
            booking_status = status_element.get_text(strip=True)

        # Append the event data to the list
        events.append({
            "venue": "Muziekgebouw",
            "date": date,
            "name": name,
            "time": time,
            "link": f"https://www.muziekgebouw.nl{link}",
            "picture": img_url,
            "booking_status": booking_status,
            "description": description
        })

        if (max_events is not None) and (n_events >= max_events):
            return events

    return events
