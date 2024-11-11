from datetime import datetime

import requests
from bs4 import BeautifulSoup

from config import venues

def scrape_ot301(url=venues["OT301"], max_events=None):
    # Fetch the webpage
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # List to store events
    events = []

    # Find each event in the OCCII events container
    for event in soup.select("a.event-item"):
        # First get the link
        link = requests.compat.urljoin(url, event["href"])

        # then parse the event page
        response = requests.get(link)
        event_soup = BeautifulSoup(response.text, "html.parser")

        # Extract the date and title from the event page
        date_text = event_soup.select_one("div.head.bg-dark.light").get_text(strip=True)
        date = (datetime
                .strptime(date_text.split(" ", 1)[1], "%d %B")
                .replace(year=datetime.now().year)
                .strftime("%Y-%m-%d"))

        title_element = event_soup.select_one("strong")
        title = title_element.get_text(strip=True) if title_element else ""

        # Extract the time
        time_element = event_soup.select_one("div.meta")
        time_text = time_element.get_text(strip=True) if time_element else ""
        time = time_text.split(" // ")[1].strip() if " // " in time_text else ""

        # Extract the image URL
        img_element = event_soup.select_one("div.media")
        img_url = img_element["style"].split("url(")[-1].strip(")") if img_element else None

        # Extract a short description
        description_element = event_soup.select_one("div.text p")
        description = description_element.get_text(strip=True)[:40] if description_element else ""

        # Append event data to the list
        events.append({
            "venue": "OT301",
            "date": date,
            "name": title,
            "time": time,
            "link": link,
            "picture": img_url,
            "description": description
        })

        if (max_events is not None) and (len(events) >= max_events):
                return events

    return events