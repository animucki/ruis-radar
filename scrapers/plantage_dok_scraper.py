from datetime import datetime

import requests
from bs4 import BeautifulSoup

from config import venues


def scrape_plantage_dok(url=venues["Dokzaal"], month=None):
    if month is None:
        month = datetime.today().strftime("%Y-%m")

    try:
        datetime.strptime(month, "%Y-%m")
    except ValueError:
        raise ValueError("Incorrect format for month, should be YYYY-MM")

    # Fetch the webpage
    response = requests.get(url + month + "/")
    soup = BeautifulSoup(response.text, "html.parser")

    # List to store events
    events = []

    for event in soup.select("a.tribe-events-calendar-month__calendar-event-title-link"):
        link = event["href"]

        response = requests.get(link)
        soup = BeautifulSoup(response.text, "html.parser")

        picture_element = soup.select_one("img.wp-post-image")
        img_url = picture_element["src"] if picture_element is not None else ""

        title = soup.select_one("h1.tribe-events-single-event-title").get_text()

        datetime_str = soup.select_one("span.tribe-event-date-start").get_text()
        date_str, time_str = datetime_str.split(" @ ")

        # Infer year from calendar url (might bug out near New Year's but whatever)
        date_str = date_str + " " + month[:4]
        date = datetime.strptime(date_str, "%d %B %Y")

        # I refuse to believe anything here happens in the am
        time = datetime.strptime(time_str.replace("am", "pm"), "%I:%M %p")

        description = ""

        # Append event data to the list
        events.append({
            "venue": "Plantage Dok",
            "date": date,
            "name": title,
            "time": time,
            "link": link,
            "picture": img_url,
            "description": description
        })

    return events
