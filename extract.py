import json
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Session:
    id: str
    title: str
    description: Optional[str]
    date: str
    time: str
    room: Optional[str]
    session_type: Optional[str]
    speakers: List[str]


@dataclass
class Day:
    date: str
    sessions: List[Session]


def parse_html(html_content: str) -> List[Day]:
    soup = BeautifulSoup(html_content, "html.parser")
    days: List[Day] = []

    for day_div in soup.find_all("div", class_="wp-block-tc23-event-agenda-day"):
        date = day_div.find(
            "h2", class_="wp-block-tc23-event-agenda-day__title"
        ).text.strip()
        sessions: List[Session] = []

        for session_div in day_div.find_all(
            "div", class_="wp-block-tc23-event-agenda-session"
        ):
            session_id = session_div.get("id", "").replace("session-", "")
            title = session_div.find(
                "h3", class_="wp-block-tc23-event-agenda-session__title"
            ).text.strip()

            description_elem = session_div.find(
                "p", class_="wp-block-tc23-event-agenda-session__description"
            )
            description = description_elem.text.strip() if description_elem else None

            time_elem = session_div.find(
                "span", class_="wp-block-tc23-event-agenda-session__time"
            )
            time = time_elem.text.strip() if time_elem else ""

            room_elem = session_div.find(
                "span", class_="wp-block-tc23-event-agenda-session__room"
            )
            room = room_elem.text.strip() if room_elem else None

            session_type_elem = session_div.find(
                "span", class_="wp-block-tc23-event-agenda-session__type"
            )
            session_type = session_type_elem.text.strip() if session_type_elem else None

            speakers = [
                speaker.text.strip()
                for speaker in session_div.find_all(
                    "span", class_="wp-block-tc23-event-agenda-session__speaker-name"
                )
            ]

            sessions.append(
                Session(
                    id=session_id,
                    title=title,
                    description=description,
                    date=date,
                    time=time,
                    room=room,
                    session_type=session_type,
                    speakers=speakers,
                )
            )

        days.append(Day(date=date, sessions=sessions))

    return days


def main():
    with open("Agenda.html", "r", encoding="utf-8") as file:
        html_content = file.read()

    agenda = parse_html(html_content)

    # Convert to JSON-serializable format
    agenda_dict = [asdict(day) for day in agenda]

    # Write to JSON file
    with open("agenda.json", "w", encoding="utf-8") as json_file:
        json.dump(agenda_dict, json_file, indent=2, ensure_ascii=False)

    print("Agenda extracted and saved to agenda.json")


if __name__ == "__main__":
    main()
