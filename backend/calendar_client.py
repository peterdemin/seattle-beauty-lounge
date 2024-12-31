import datetime

from googleapiclient.discovery import build


class CalendarClient:
    LIMIT_DAYS = 7 * 7  # 7 weeks
    CALENDAR_ID = "primary"

    def __init__(self, creds) -> None:
        self._service = build("calendar", "v3", credentials=creds)

    def fetch_future_events(self, limit_days: int = LIMIT_DAYS):
        now = datetime.datetime.utcnow()
        time_max = now + datetime.timedelta(days=limit_days)
        return (
            self._service.events()
            .list(
                calendarId=self.CALENDAR_ID,
                timeMin=now.isoformat() + "Z",  # 'Z' indicates UTC
                timeMax=time_max.isoformat() + "Z",
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
            .get("items", [])
        )

    def parse_event_times(self, events):
        return [self.parse_event(event) for event in events]

    def parse_event(self, event):
        start = event["start"].get("dateTime", event["start"].get("date"))
        end = event["end"].get("dateTime", event["end"].get("date"))
        # If start/end are dateTimes, parse them into datetime objects
        if "T" in start:
            start_dt = datetime.datetime.fromisoformat(start.rstrip("Z"))
        else:
            # All-day event (just a date)
            start_dt = datetime.datetime.fromisoformat(start + "T00:00:00")
        if "T" in end:
            end_dt = datetime.datetime.fromisoformat(end.rstrip("Z"))
        else:
            end_dt = datetime.datetime.fromisoformat(end + "T23:59:59")
        return (start_dt, end_dt)
