from pprint import pprint

from backend.calendar_client import CalendarClient
from backend.google_auth import GoogleAuth

if __name__ == "__main__":
    calendar = CalendarClient(creds=GoogleAuth().get_local_credentials())
    pprint(calendar.parse_event_times(calendar.fetch_future_events(7)))
