from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

client = MongoClient("mongodb://localhost:27017/")
db = client["webhookDB"]
collection = db["events"]

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    event_type = request.headers.get('X-GitHub-Event')
    ist_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
    timestamp = ist_time.strftime("%d %B %Y - %I:%M %p IST")

    if event_type == "ping":
        return "Ping received", 200

    if event_type == "push":
        author = data['pusher']['name']
        branch = data['ref'].split('/')[-1]
        message = f'"{author}" pushed to "{branch}" on {timestamp}'

    elif event_type == "pull_request":
        author = data['pull_request']['user']['login']
        from_branch = data['pull_request']['head']['ref']
        to_branch = data['pull_request']['base']['ref']
        message = f'"{author}" submitted a pull request from "{from_branch}" to "{to_branch}" on {timestamp}'

    else:
        return "Event not handled", 200

    collection.insert_one({"message": message})
    print("Message inserted into MongoDB:", message)
    return "OK", 200

# ✅ This is the route your frontend needs
@app.route('/events', methods=['GET'])
def get_events():
    events = list(collection.find({}, {"_id": 0}))
    return jsonify(events)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
