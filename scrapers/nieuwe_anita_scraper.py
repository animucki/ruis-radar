from datetime import datetime
import requests
from bs4 import BeautifulSoup
from config import venues


def _parse_nieuwe_anita_date(date_str):
    # Convert date format like 'November 9' into ISO date format
    try:
        date = datetime.strptime(date_str, "%B %d")
        current_year = datetime.now().year
        current_month = datetime.now().month
        # Assign year based on the current month and event month convention
        if current_month >= 7 and date.month <= 6:
            year = current_year + 1
        else:
            year = current_year
        return date.replace(year=year).strftime("%Y-%m-%d")
    except ValueError:
        return None


def _get_event_details(event_url):
    """Fetch event page details such as image and description."""
    response = requests.get(event_url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract the first event image
    img_element = soup.select_one("img.wp-post-image")
    img_url = img_element["src"] if img_element else None

    # Extract the first paragraph within the description container, excluding <strong> text
    description_element = soup.select_one("div.wpb_wrapper")

    if description_element:
        # Gather text excluding <strong> tags
        description_text = ""
        for elem in description_element.descendants:
            if elem.name != "strong" and isinstance(elem, str):
                description_text += elem.strip() + " "
        description_text = description_text.strip()
    else:
        description_text = ""

    # Limit description to 40 characters, ending cleanly
    short_description = (description_text[:40].rsplit(" ", 1)[0] + "...") if len(description_text) > 40 else description_text

    return img_url, short_description


def scrape_nieuwe_anita(url=venues["Nieuwe Anita"], max_events=None):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Select only the events inside the `scrolling1` container
    container = soup.select_one("div.vc_col-sm-6.wpb_column.vc_column_container.scrolling1")
    if not container:
        print("No events found in the expected container.")
        return []

    events = []

    for n_events, event in enumerate(container.select("div.vc_grid-item")):
        title_element = event.select_one("h6 a")
        title = title_element.get_text(strip=True) if title_element else ""
        link = title_element["href"] if title_element else "#"
        date_element = event.select_one("div.date-agenda")
        date_str = date_element.get_text(strip=True) if date_element else ""
        date = _parse_nieuwe_anita_date(date_str)
        time_element = event.select_one("div.time-agenda")
        time_str = time_element.get_text(strip=True) if time_element else ""
        time = datetime.strptime(time_str, "%I:%M %p").strftime("%H:%M") if time_str else ""

        # Fetch additional details from event page
        img_url, short_description = _get_event_details(link)

        if title == "Cinemanita":
            short_description = "Jeffrey Babcock"

        events.append({
            "venue": "Nieuwe Anita",
            "date": date,
            "name": title,
            "time": time,
            "link": link,
            "picture": img_url,
            "description": short_description
        })

        if max_events is not None and len(events) >= max_events:
            return events

    return events
