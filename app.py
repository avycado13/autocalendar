from flask import Flask, request, redirect, url_for, jsonify, render_template
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os

app = Flask(__name__)

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
flow = Flow.from_client_secrets_file(
    'client_secrets.json',
    scopes=['https://www.googleapis.com/auth/calendar'],
    redirect_uri='http://localhost:5000/callback')

# This will store our events
events = []

@app.route('/')
def index():
    authorization_url, state = flow.authorization_url()
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    # ... existing code ...

@app.route('/events')
def get_events():
    # ... existing code ...

@app.route('/create_event', methods=['POST'])
def create_event():
    try:
        # Get the event details from the request
        event_details = request.get_json()

        # Only create the event if the checkbox was checked
        if event_details.get('addEvent', False):
            # Calculate the end time based on the start time and the duration
            start = datetime.strptime(event_details['start'], '%Y-%m-%dT%H:%M:%S')
            duration = timedelta(minutes=int(event_details['duration']))
            end = start + duration

            # Create the event
            event = {
                'summary': event_details['summary'],
                'description': event_details.get('description', ''),
                'start': {
                    'dateTime': start.isoformat(),
                    'timeZone': 'America/Los_Angeles',
                },
                'end': {
                    'dateTime': end.isoformat(),
                    'timeZone': 'America/Los_Angeles',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 10},
                    ],
                },
                'colorId': str(event_details.get('priority', 1))  # Use color to indicate priority
            }

            # Add the event to the primary calendar
            service = build('calendar', 'v3', credentials=flow.credentials)
            created_event = service.events().insert(calendarId='primary', body=event).execute()

            return jsonify(created_event)

        else:
            return jsonify({'message': 'Event not created because checkbox was not checked'})

    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run('localhost', 5000, debug=True)
