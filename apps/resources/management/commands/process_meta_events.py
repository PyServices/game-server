"""
Meta config: time-based and value-based events.
Run via cron: python manage.py process_meta_events

Config structure for Meta:
- events: [{type: "time"|"value", ...}]
- time: at specific time → reset/add/remove
- value: when value reaches X → remove owner from user

Stub: scans UserResources for Meta with events, processes time-based.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.resources.models import Resource, UserResource, ResourceType


class Command(BaseCommand):
    help = "Process Meta time-based events (reset, add, remove at scheduled time)"

    def handle(self, *args, **options):
        count = 0
        for r in Resource.objects.filter(type=ResourceType.META):
            events = (r.config or {}).get("events", [])
            for ev in events:
                if ev.get("type") == "time":
                    # Stub: check event time and act
                    # In production: parse ev["at"], ev["action"], etc.
                    count += 1
        self.stdout.write(self.style.SUCCESS(f"Processed {count} meta time events (stub)"))
