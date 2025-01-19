import json

from api.calendar_client import CalendarEventParser, CalendarServiceDummy, DayBreaker
from api.kv import KiwiStore
from api.task_scheduler import TaskScheduler


class AvailabilityTask:
    def __init__(
        self,
        key: str,
        kv: KiwiStore,
        calendar_service: CalendarServiceDummy,
        calendar_event_parser: CalendarEventParser,
        day_breaker: DayBreaker,
    ) -> None:
        self._key = key
        self._kv = kv
        self._calendar_service = calendar_service
        self._calendar_event_parser = calendar_event_parser
        self._day_breaker = day_breaker

    def __call__(self, limit: int = 7 * 7) -> None:
        try:
            events = self._calendar_service.fetch(limit)
        except Exception:
            # Whatever, next attempt is in one minute
            return
        self._kv.set(
            self._key,
            json.dumps(
                self._day_breaker.group_time_ranges(
                    map(
                        self._calendar_event_parser,
                        events,
                    )
                )
            ),
        )

    def register(self, task_scheduler: TaskScheduler) -> None:
        task_scheduler.every().minute.do(self)
