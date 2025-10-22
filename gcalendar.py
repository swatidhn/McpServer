import datetime
import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def get_calendar_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('calendar', 'v3', credentials=creds)
    return service
def create_event(title: str, start_time: datetime.datetime, duration_minutes=20, recurrence: str = None) -> str:
    service = get_calendar_service()
    event = {
        'summary': title,
        'start': {'dateTime': start_time.isoformat(), 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': (start_time + datetime.timedelta(minutes=duration_minutes)).isoformat(), 'timeZone': 'Asia/Kolkata'},
    }
    if recurrence:
        event['recurrence'] = [recurrence]

    created_event = service.events().insert(calendarId='primary', body=event).execute()
    return created_event.get('htmlLink')