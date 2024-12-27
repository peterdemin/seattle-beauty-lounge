import datetime

from api.slots import SlotsLoader


def test_slots_loader():
    slots = SlotsLoader()
    got = list(slots.iter_hours())
    assert got == [
        {"day": "Monday", "start": datetime.time(10, 0), "end": datetime.time(19, 0)},
        {"day": "Tuesday", "start": datetime.time(10, 0), "end": datetime.time(19, 0)},
        {
            "day": "Wednesday",
            "start": datetime.time(10, 0),
            "end": datetime.time(12, 30),
        },
        {
            "day": "Thursday",
            "start": datetime.time(10, 0),
            "end": datetime.time(19, 30),
        },
        {"day": "Friday", "start": datetime.time(10, 0), "end": datetime.time(19, 30)},
        {"day": "Saturday", "start": datetime.time(10, 0), "end": datetime.time(17, 0)},
    ]
