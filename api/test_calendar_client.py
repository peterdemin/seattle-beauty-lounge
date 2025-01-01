import pytest

from api.calendar_client import DayBreaker


@pytest.mark.parametrize(
    "breaks,expected",
    [
        ([["12:00", "13:00"]], [["09:00", "12:00"], ["13:00", "17:00"]]),
        ([["07:00", "10:00"]], [["10:00", "17:00"]]),
        ([["13:00", "20:00"]], [["09:00", "13:00"]]),
        ([["00:00", "23:59"]], []),
        (
            [["12:00", "13:00"], ["14:00", "15:00"]],
            [["09:00", "12:00"], ["13:00", "14:00"], ["15:00", "17:00"]],
        ),
        (
            [["08:00", "11:00"], ["16:00", "18:00"]],
            [["11:00", "16:00"]],
        ),
        (
            [["09:00", "12:00"], ["12:00", "17:00"]],
            [],
        ),
    ],
)
def test_day_breaker_cases(breaks, expected):
    day_breaker = DayBreaker({"2014-04-14": breaks})
    got = day_breaker.break_availability("2014-04-14", "09:00", "17:00")
    assert got == expected
