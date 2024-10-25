from flask import Flask, send_from_directory, request, jsonify, send_file
import json
from datetime import datetime
import pytz
from dateutil import parser
import io

app = Flask(__name__)

SELECTED_EVENTS_FILE = "selected_events.json"


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/<path:path>")
def serve_file(path):
    return send_from_directory(".", path)


@app.route("/get_selected_events")
def get_selected_events():
    try:
        with open(SELECTED_EVENTS_FILE, "r") as f:
            return jsonify(json.load(f))
    except FileNotFoundError:
        return jsonify([])


@app.route("/save_selected_events", methods=["POST"])
def save_selected_events():
    selected_events = request.json
    with open(SELECTED_EVENTS_FILE, "w") as f:
        json.dump(selected_events, f, indent=2)
    return jsonify({"message": "Events saved successfully"})


@app.route("/download_calendar", methods=["GET"])
def download_calendar():
    try:
        with open(SELECTED_EVENTS_FILE, "r") as f:
            selected_events = json.load(f)
    except FileNotFoundError:
        return jsonify({"error": "No selected events found"}), 404

    ical_content = generate_ical_content(selected_events)
    buffer = io.BytesIO(ical_content.encode())
    buffer.seek(0)
    return send_file(
        buffer,
        mimetype="text/calendar",
        as_attachment=True,
        download_name="techcrunch_disrupt_events.ics",
    )


def generate_ical_content(events):
    ical_content = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//TechCrunch Disrupt Planner//EN",
    ]

    current_year = datetime.now().year
    pt_tz = pytz.timezone("America/Los_Angeles")

    for event in events:
        # Parse the date and time strings
        date_str = f"{event['date']} {current_year}"
        start_datetime = parser.parse(f"{date_str} {event['startTime']}")
        end_datetime = parser.parse(f"{date_str} {event['endTime']}")

        # Localize the datetimes to Pacific Time
        start_date = pt_tz.localize(start_datetime)
        end_date = pt_tz.localize(end_datetime)

        ical_content.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{event['id']}@techcrunchdisrupt.com",
                f"DTSTAMP:{datetime.now(pytz.utc).strftime('%Y%m%dT%H%M%SZ')}",
                f"DTSTART:{start_date.astimezone(pytz.utc).strftime('%Y%m%dT%H%M%SZ')}",
                f"DTEND:{end_date.astimezone(pytz.utc).strftime('%Y%m%dT%H%M%SZ')}",
                f"SUMMARY:{event['title']}",
                f"LOCATION:{event['room']}",
                f"DESCRIPTION:{event.get('description', '')}",
                "END:VEVENT",
            ]
        )

    ical_content.append("END:VCALENDAR")
    return "\r\n".join(ical_content)


if __name__ == "__main__":
    app.run(debug=True)
