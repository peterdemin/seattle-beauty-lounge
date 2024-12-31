import os
from pprint import pprint

from api.calendar_client import CalendarClient
from api.google_auth import GoogleAuth

if __name__ == "__main__":
    with open(os.path.expanduser("~/.gcp/credentials.json"), "rt", encoding="utf-8") as fobj:
        client_config = fobj.read()
    calendar = CalendarClient(creds=GoogleAuth(client_config).get_local_credentials())
    pprint(calendar.parse_event_times(calendar.fetch_future_events(7)))
