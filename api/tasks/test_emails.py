import base64
import datetime
import re
from unittest import mock

from api.models import Appointment
from api.service_catalog import ServiceCatalog
from api.smtp_client import SMTPClientDummy
from api.tasks.emails import EmailTask
from lib.service import ImageInfo, ServiceInfo

RE_BOUNDARY = re.compile(r"==(=+[^=]+)==")
RE_NON_DETERMINISTIC = re.compile(r"(?m)^(DTSTAMP|UID):(\S+)$")


def test_send_confirmation_email_example():
    smtp_client = mock.Mock(spec=SMTPClientDummy)
    email_task = EmailTask(
        smtp_client=smtp_client,
        service_catalog=ServiceCatalog(
            [
                ServiceInfo(
                    source_path="1-cat/23-name.rst",
                    image=ImageInfo.dummy(),
                    title="service",
                    duration_min=3,
                )
            ]
        ),
    )
    email_task.send_confirmation_email(
        Appointment(
            id=1,
            serviceId="1.23",
            date=datetime.date(2014, 4, 14),
            time=datetime.time(1, 10, 20),
            clientName="clientName",
            clientPhone="clientPhone",
            clientEmail="clientEmail",
        )
    )
    smtp_client.send.assert_called_once()
    msg = smtp_client.send.call_args_list[0][0][0]
    email_body = RE_BOUNDARY.sub("==boundary==", msg.as_string())
    assert email_body.startswith(EMAIL_BODY)
    pp = msg.get_payload()
    ics_body = base64.b64decode(pp[1].get_payload()).decode("utf-8")
    ics_body = RE_NON_DETERMINISTIC.sub(r"\1:<scrambled>", ics_body)
    ics_body = ics_body.replace("UTC-08:00", "UTC-07:00")
    assert ics_body == ICS_BODY


EMAIL_BODY = """\
Content-Type: multipart/mixed; boundary="==boundary=="
MIME-Version: 1.0
Subject: Appointment with Seattle Beauty Lounge
From: kate@seattle-beauty-lounge.com
To: clientEmail

--==boundary==
Content-Type: text/plain; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit

Hello clientName,

Your appointment has been booked.

We'll see you on Monday, April 14 at 01:10 for service.

Thank you for choosing Seattle Beauty Lounge!

Address: 311 W Republican St, Seattle, WA 98119
Phone: 301-658-8708
Email: kate@seattle-beauty-lounge.com
"""

ICS_BODY = (
    r"""
BEGIN:VCALENDAR
PRODID:-//github.com/allenporter/ical//9.0.2//EN
VERSION:2.0
BEGIN:VEVENT
DTSTAMP:<scrambled>
UID:<scrambled>
DTSTART;TZID="UTC-07:00":20140414T011020
DTEND;TZID="UTC-07:00":20140414T011320
SUMMARY:service
CONTACT:301-658-8708
CONTACT:kate@seattle-beauty-lounge.com
DESCRIPTION:Seattle Beauty Lounge\n\nAddress: 311 W Republican St\,""".lstrip()
    + " "
    + r"""
 Seattle\, WA 98119\nPhone: 301-658-8708\nEmail:"""
    + " "
    + r"""
 kate@seattle-beauty-lounge.com
LOCATION:311 W Republican St\, Seattle\, WA 98119
END:VEVENT
END:VCALENDAR
""".rstrip()
)
