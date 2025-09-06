#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_events.settings')
django.setup()

from events.models import Event

print("=== Event Status Check ===")
events = Event.objects.all()
for event in events:
    print(f"Event: {event.title}")
    print(f"  Status: {event.status}")
    print(f"  Is Registration Open: {event.is_registration_open}")
    print("---")
