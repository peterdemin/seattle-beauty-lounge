import base64
import datetime
import os
import re
import uuid
from unittest import mock

import pytest

from api.config import Settings
from api.linker import Linker
from api.models import Appointment
from api.service_catalog import ServiceCatalog
from api.smtp_client import SMTPClient, SMTPClientDummy
from api.tasks.emails import EmailTask
from lib.service import ImageInfo, ServiceInfo, load_content


def test_send_confirmation_email_example():
    smtp_client = mock.Mock(spec=SMTPClientDummy)
    content = load_content()
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
        email_template=content.get_snippet("7.04"),
        linker=Linker(base_url="http://site", admin_url="http://admin/a.html"),
    )
    email_task.on_appointment(
        Appointment(
            id=1,
            pubid=uuid.UUID("00000000-0000-0000-0000-000000000000"),
            serviceId="1.23",
            date=datetime.date(2014, 4, 4),
            time=datetime.time(13, 23, 45),
            clientName="clientName",
            clientPhone="clientPhone",
            clientEmail="clientEmail",
        )
    )
    assert smtp_client.send.call_count == 2
    # Confirmation to client:
    msg = smtp_client.send.call_args_list[0][0][0]
    email_body = msg.as_string()
    email_body = re.sub(r"==(=+[^=]+)==", "==boundary==", email_body)
    email_body = re.sub(r"(?m)^ *<!--.+?-->$", "", email_body)
    assert email_body.startswith(EMAIL_BODY)
    pp = msg.get_payload()
    ics_body = base64.b64decode(pp[1].get_payload()).decode("utf-8")
    ics_body = re.sub(r"(?m)^(DTSTAMP|UID):(\S+)$", r"\1:<scrambled>", ics_body)
    ics_body = ics_body.replace("UTC-08:00", "UTC-07:00")
    assert ics_body == ICS_BODY

    # Notification to owner:
    msg = smtp_client.send.call_args_list[1][0][0]
    email_body = msg.as_string()
    assert email_body == NOTIFICATION_BODY


@pytest.mark.skipif(
    os.environ.get("INTEGRATION") != "1",
    reason="Set INTEGRATION=1 to enable integration tests",
)
def test_send_confirmation_email_integration():
    settings = Settings()
    content = load_content()
    email_task = EmailTask(
        smtp_client=(
            SMTPClient(sender_email=settings.sender_email, sender_password=settings.sender_password)
            if settings.enable_emails
            else SMTPClientDummy()
        ),
        service_catalog=ServiceCatalog(
            [
                ServiceInfo(
                    source_path="1-cat/23-name.rst",
                    image=ImageInfo.dummy(),
                    title="in-and-out",
                    duration_min=3,
                )
            ]
        ),
        email_template=content.get_snippet("7.04"),
        linker=Linker(base_url="", admin_url="http://admin"),
    )
    email_task.on_appointment(
        Appointment(
            id=1,
            serviceId="1.23",
            date=datetime.date(2014, 4, 4),
            time=datetime.time(13, 23, 45),
            clientName="Peter Demin",
            clientPhone="2403421438",
            clientEmail="peterdemin@gmail.com",
        )
    )


EMAIL_BODY = """\
Content-Type: multipart/mixed; boundary="==boundary=="
MIME-Version: 1.0
Subject: Appointment with Seattle Beauty Lounge
From: kate@seattle-beauty-lounge.com
To: clientEmail

--==boundary==
Content-Type: multipart/alternative; boundary="==boundary=="
MIME-Version: 1.0

--==boundary==
Content-Type: text/plain; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit

Hello clientName,

Your appointment has been booked.

We'll see you on Friday, April 4 at 01:23 PM for service.

Thank you for choosing Seattle Beauty Lounge!

Address: 311 W Republican St, Seattle, WA 98119
Phone: 301-658-8708
Email: kate@seattle-beauty-lounge.com
--==boundary==
Content-Type: text/html; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit

<div class="p-6 font-light text-black">
 <span id="h-74q66fivwzmb">
 </span>
 <h1 class="py-2 text-2xl text-primary font-light">
  Appointment with Seattle Beauty Lounge
 </h1>

 <p class="py-2">
  Hello clientName,
 </p>
 <p class="py-2">
  Your appointment has been booked.
 </p>
 <p class="py-2">
  We'll see you on Friday, April 4 at 01:23 PM for service.
 </p>
 <p class="py-2">
  Thank you for choosing Seattle Beauty Lounge!
 </p>
 <div class="line-block">
  <div class="line">
   Address: 311 W Republican St, Seattle, WA 98119
  </div>
  <div class="line">
   Phone: 301-658-8708
  </div>
  <div class="line">
   Email:
   <a class="font-medium text-primary underline" href="mailto:kate@seattle-beauty-lounge.com">
    kate@seattle-beauty-lounge.com
   </a>
  </div>
 </div>
</div>

--==boundary==--

--==boundary==
Content-Type: text/calendar; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: base64
Content-Disposition: attachment; filename="invite.ics"
"""

ICS_BODY = (
    r"""BEGIN:VCALENDAR
PRODID:-//github.com/allenporter/ical//11.0.0//EN
VERSION:2.0
BEGIN:VEVENT
DTSTAMP:<scrambled>
UID:<scrambled>
DTSTART;TZID="UTC-07:00":20140404T132345
DTEND;TZID="UTC-07:00":20140404T132645
SUMMARY:service
CONTACT:301-658-8708
CONTACT:kate@seattle-beauty-lounge.com
DESCRIPTION:Seattle Beauty Lounge\n\nDetails: http://site/appointment.html?"""
    + "\n "
    + r"""app=00000000-0000-0000-0000-000000000000\nAddress: 311 W Republican St\,"""
    + " \n "
    + r"""Seattle\, WA 98119\nPhone: 301-658-8708\nEmail:"""
    + " "
    + r"""
 kate@seattle-beauty-lounge.com
LOCATION:311 W Republican St\, Seattle\, WA 98119
END:VEVENT
END:VCALENDAR
""".rstrip()
)

NOTIFICATION_BODY = """
Content-Type: text/plain; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: New appointment in Seattle Beauty Lounge
From: kate@seattle-beauty-lounge.com
To: kate@seattle-beauty-lounge.com

Seattle Beauty Lounge

Appointment: http://admin/a.html?app=1

Service: service
Date: Friday, April 4
Time: 01:23 PM

Name: clientName
Phone: clientPhone
Email: clientEmail
""".strip()
