from flask import Flask, send_from_directory, request, jsonify
import json

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


if __name__ == "__main__":
    app.run(debug=True)
