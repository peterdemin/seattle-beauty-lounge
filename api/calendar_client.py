import datetime
from typing import Iterable

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from api.constants import TIMEZONE


class CalendarServiceDummy:

    def fetch(self, limit_days: int) -> list[dict]:
        del limit_days
        return []

    def insert(self, body: dict) -> dict:
        del body
        return {}


class CalendarService(CalendarServiceDummy):
    CALENDAR_ID = "primary"

    def __init__(self, creds: Credentials) -> None:
        self._service = build("calendar", "v3", credentials=creds)

    def fetch(self, limit_days: int) -> list[dict]:
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        time_max = now + datetime.timedelta(days=limit_days)
        return (
            self._service.events()  # pylint: disable=no-member
            .list(
                calendarId=self.CALENDAR_ID,
                timeMin=now.isoformat(),
                timeMax=time_max.isoformat(),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
            .get("items", [])
        )

    def insert(self, body: dict) -> dict:
        return (
            self._service.events()  # pylint: disable=no-member
            .insert(calendarId=self.CALENDAR_ID, body=body)
            .execute()
        )


class CalendarEventParser:

    def __call__(self, event: dict) -> tuple[datetime.datetime, datetime.datetime]:
        if start := event["start"].get("dateTime"):
            start_dt = datetime.datetime.fromisoformat(start)
        else:
            start = event["start"].get("date")
            start_dt = TIMEZONE.localize(
                datetime.datetime.combine(
                    datetime.date.fromisoformat(start),
                    datetime.time(0, 0),
                )
            )

        if end := event["end"].get("dateTime"):
            end_dt = datetime.datetime.fromisoformat(end)
        else:
            end = event["end"].get("date")  # Next day after the event
            end_dt = TIMEZONE.localize(
                datetime.datetime.combine(
                    datetime.date.fromisoformat(end),
                    datetime.time(0, 0),
                )
            ) - datetime.timedelta(seconds=1)

        return (start_dt, end_dt)


class DayBreakerInterface:
    def break_availability(self, date: str, start: str, end: str) -> list[list[str]]:
        del date, start, end
        raise NotImplementedError()


class DayBreaker(DayBreakerInterface):
    def __init__(self, breaks: dict[str, list[list[str]]]) -> None:
        self._breaks = breaks

    def break_availability(self, date: str, start: str, end: str) -> list[list[str]]:
        result = []
        for break_start, break_end in self._breaks.get(date, []):
            if start <= break_start <= end:
                if start < break_start:
                    result.append([start, break_start])
                start = break_end
            elif start <= break_end <= end:
                start = break_end
            elif break_start <= start < end <= break_end:
                start = break_end
        if start < end:
            result.append([start, end])
        return result

    @staticmethod
    def group_time_ranges(
        time_ranges: Iterable[tuple[datetime.datetime, datetime.datetime]],
    ) -> dict[str, list[list[str]]]:
        result = {}
        for start, end in time_ranges:
            if start.date() == end.date():
                result.setdefault(start.date().isoformat(), []).append(
                    [start.time().isoformat("minutes"), end.time().isoformat("minutes")]
                )
            else:
                # Multi-day event
                result.setdefault(start.date().isoformat(), []).append(
                    [start.time().isoformat("minutes"), "23:59"]
                )
                result.setdefault(end.date().isoformat(), []).append(
                    ["00:00", end.time().isoformat("minutes")]
                )
                for days_offset in range(1, (end - start).days):
                    date = start + datetime.timedelta(days=days_offset)
                    result.setdefault(date.date().isoformat(), []).append(["00:00", "23:59"])
        for date, ranges in result.items():
            prev_start, prev_end = "", ""
            non_overlapping = []
            for start, end in sorted(ranges):
                if start > prev_start and end < prev_end:
                    continue
                non_overlapping.append([start, end])
                prev_start, prev_end = start, end
            result[date] = non_overlapping
        return result


class CalendarClient:
    LIMIT_DAYS = 7 * 7  # 7 weeks

    def __init__(
        self, calendar_service: CalendarService, calendar_event_parser: CalendarEventParser
    ) -> None:
        self._calendar_service = calendar_service
        self._calendar_event_parser = calendar_event_parser

    def __call__(
        self, limit_days: int = LIMIT_DAYS
    ) -> list[tuple[datetime.datetime, datetime.datetime]]:
        return [
            self._calendar_event_parser(event) for event in self._calendar_service.fetch(limit_days)
        ]
