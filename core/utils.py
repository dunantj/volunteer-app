from icalendar import Calendar, Event
from datetime import datetime, timedelta
from django.utils import timezone

def create_ics_for_slot(slot):
    match = slot.match

    # Combine match date + start_time into a full datetime
    start_dt = datetime.combine(match.date, match.start_time)
    start_dt = timezone.make_aware(start_dt, timezone.get_current_timezone())

    start_dt = start_dt - timedelta(minutes=90)
    end_dt = start_dt + timedelta(hours=2)

    cal = Calendar()
    cal.add('prodid', '-//Volunteering App//example.com//')
    cal.add('version', '2.0')

    event = Event()
    event.add('summary', f"Volunteering for {match.home_team} vs {match.guest_team}")
    event.add('dtstart', start_dt)
    event.add('dtend', end_dt)
    event.add('dtstamp', timezone.now())
    event.add('location', match.location or "")
    event.add('description', f"You’re volunteering for the match {match}.")

    cal.add_component(event)
    return cal.to_ical()