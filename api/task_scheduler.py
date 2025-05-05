import threading
import time

import schedule
import sentry_sdk


class TaskScheduler:
    """Regular background task scheduler.

    Example usage::

        task_scheduler = TaskScheduler()
        stop = task_scheduler.start()
    """

    def __init__(self) -> None:
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run)

    def start(self) -> None:
        """Continuously execute pending jobs in background thread."""
        self._thread.start()

    def stop(self, timeout: float = 5) -> None:
        """Wait for task completion and stop."""
        self._stop_event.set()
        self._thread.join(timeout=timeout)

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                schedule.run_pending()
            except Exception as exc:  # pylint: disable=broad-exception-caught
                sentry_sdk.capture_exception(exc)
            if not self._stop_event.is_set():
                time.sleep(0.1)

    def every(self) -> schedule.Job:
        """Add regular task to run.

        Example usage::

            task_scheduler.every().second.do(background_job)
            task_scheduler.every(10).minutes.do(job)
            task_scheduler.every().hour.do(job)
            task_scheduler.every().day.at("10:30").do(job)
            task_scheduler.every().monday.do(job)
            task_scheduler.every().wednesday.at("13:15").do(job)
            task_scheduler.every().day.at("12:42", "Europe/Amsterdam").do(job)
            task_scheduler.every().minute.at(":17").do(job)
        """
        return schedule.every()
