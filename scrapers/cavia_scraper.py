from datetime import datetime

import requests
from bs4 import BeautifulSoup

from config import venues, dutch_months_long
from utlis.date_utils import parse_dutch_date


def scrape_cavia(url=venues["Filmhuis Cavia"]):
    # Fetch the front page
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the right program (whyyyy do they have to change the url every month)
    agenda_url = soup.select_one("a.mega-link-overlay")["href"]

    response = requests.get(agenda_url)
    soup = BeautifulSoup(response.text, "html.parser")
    events = []

    # Split the page content by <hr> tags
    event_sections = soup.select_one("div.col-content").select("hr")

    for section in event_sections:

        # Each section contains the details of an event
        event_content = section.find_next_sibling("p")

        # Extract date and time
        date_text = event_content.find("strong").get_text(strip=True)
        date_parts = date_text.split(", ")
        if len(date_parts) == 2:
            day_part, time_part = date_parts
        else:
            day_part, time_part = date_text, ""

        # Extract date in 'd MMMM' format if available
        try:
            date = parse_dutch_date(day_part, dutch_months_long)
        except ValueError:
            date = ""

        # this will happen if the date is a range
        if date == "":
            date = day_part

        # Extract event title
        title_element = event_content.find_next_sibling("h2")
        title = title_element.get_text(strip=True) if title_element else ""

        # Extract description, skipping links
        description_elements = [p.get_text(" ", strip=True) for p in event_content.find_next_siblings("p")]
        description = (" ".join(description_elements))[:40]

        # Extract image URL if available
        img_element = event_content.find_next("img")
        img_rel_url = img_element["src"] if img_element else None
        img_url = requests.compat.urljoin(agenda_url, img_rel_url)

        # Append event data to the list
        events.append({
            "venue": "Filmhuis Cavia",
            "date": date,
            "time": time_part,
            "name": title,
            "link": url,
            "picture": img_url,
            "description": description
        })

    return events