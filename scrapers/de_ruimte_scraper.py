from datetime import datetime

import requests
from bs4 import BeautifulSoup

from config import venues


def scrape_de_ruimte(url=venues["De Ruimte"], max_events=None):
    # Fetch the webpage
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # List to store events
    events = []

    # Find each event in the events container
    for event in soup.select("a.vc_gitem-link"):
        # First get the link
        link = event["href"]

        # then parse the event page
        response = requests.get(link)
        event_soup = BeautifulSoup(response.text, "html.parser")

        title = event_soup.select_one("div.agenda_block_title").get_text()

        date = (datetime
                .strptime(event_soup.select_one("span._space_whole_date").get_text(), "%b %d, %Y")
                .strftime("%Y-%m-%d"))

        time = event_soup.select_one("div._space_time").get_text()



        # Append event data to the list
        events.append({
            "venue": "De Ruimte",
            "date": date,
            "name": title,
            "time": time,
            "link": link,
            "picture": "",
            "description": ""
        })

        if (max_events is not None) and (len(events) >= max_events):
                return events

    return events


