from datetime import datetime
import requests
from bs4 import BeautifulSoup
from config import venues


def scrape_munganga(url=venues["Munganga"], max_events=None):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    # Fetch the webpage
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # List to store events
    events = []

    # Loop through each event item
    for event in soup.select("li.product"):
        # Event link and title
        link_element = event.select_one("a.woocommerce-LoopProduct-link")
        link = link_element["href"] if link_element else "#"

        # Image URL
        img_element = event.select_one("img.attachment-woocommerce_thumbnail")
        img_url = img_element["src"] if img_element else None

        title_element = event.select_one("h2.woocommerce-loop-product__title")
        title_raw = title_element.get_text(strip=True) if title_element else ""

        # zap all the gremlins (this will break the second someone makes yet another nonstandard title)
        title_raw = (title_raw
                     .replace(",", "")
                     .replace("–", "")
                     .replace("  ", " ")
                     .replace("Zo", "Sun")
                     .strip())

        # Extract date, time, and title
        # This will break one day I can feel it
        date_str = title_raw[:21]
        title = title_raw[22:]

        time = date_str[-5:]
        date = datetime.strptime(date_str, "%a %d %b %Y %H:%M").strftime("%Y-%m-%d") if date_str else ""

        # Fetch the event page for description
        description = ""
        if link != "#":
            event_response = requests.get(link, headers=headers)
            event_soup = BeautifulSoup(event_response.text, "html.parser")

            # Extract a brief description from <h4> tags, excluding text in <a> tags
            description_elements = event_soup.select("div.et_pb_tab_content h4")
            description_text = " ".join(
                element.get_text(strip=True) for element in description_elements if not element.select_one("a")
            )
            description = description_text[:40].rsplit(" ", 1)[0] + "..." if len(
                description_text) > 40 else description_text

        # Append event data to the list
        events.append({
            "venue": "Munganga",
            "date": date,
            "time": time,
            "name": title,
            "link": link,
            "picture": img_url,
            "description": description
        })

        # Stop if max_events is reached
        if (max_events is not None) and (len(events) >= max_events):
            return events

    return events
