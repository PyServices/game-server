"""
EventService per .cursor/docs/core/event/user-event.md

SendEvent(event|eventId, userId, value?, metaData?, requestEntityId?, targetEntityId?)
GetAll(event|id, userId, requestEntityId, targetEntityId, type:EventCalculate, start, end)
GetCount(id, TimeSpan?)
GetLatest(event_id, requestEntityId, targetEntityId, user_id, start?, end?)
"""
from datetime import datetime

from .models import Event, UserEvent


class EventCalculate:
    COUNT = "Count"
    HIGH_VALUE = "HighValue"
    SUM_VALUE = "SumValue"


class EventService:
    """Public API for event operations. Other modules use this, not models."""

    _observers = []  # Observer pattern: [(event_id, callback), ...]

    @classmethod
    def register_observer(cls, event_id: int, callback):
        """Register callback for event. Called when UserEvent is created."""
        cls._observers.append((event_id, callback))

    @classmethod
    def _notify_observers(cls, event_id: int, user_event: UserEvent):
        for eid, cb in cls._observers:
            if eid == event_id:
                try:
                    cb(user_event)
                except Exception:
                    pass

    @staticmethod
    def get_event_by_id(pk: int) -> Event | None:
        try:
            return Event.objects.get(pk=pk)
        except Event.DoesNotExist:
            return None

    @staticmethod
    def get_event_by_string(event_str: str) -> Event | None:
        try:
            return Event.objects.get(event=event_str)
        except Event.DoesNotExist:
            return None

    @classmethod
    def send_event(
        cls,
        event_or_id: Event | int | str,
        user_id: int,
        value=None,
        meta_data=None,
        request_entity_id=None,
        target_entity_id=None,
    ) -> UserEvent | None:
        """
        Send event. event_or_id can be Event, event_id (int), or event string.
        """
        if isinstance(event_or_id, Event):
            ev = event_or_id
        elif isinstance(event_or_id, int):
            ev = cls.get_event_by_id(event_or_id)
        else:
            ev = cls.get_event_by_string(str(event_or_id))
        if ev is None:
            return None
        user_event = UserEvent.objects.create(
            event=ev,
            user_id=user_id,
            value=value,
            meta_data=meta_data or {},
            request_entity_id=request_entity_id or "",
            target_entity_id=target_entity_id or "",
        )
        cls._notify_observers(ev.id, user_event)
        if ev.prize_id:
            try:
                from apps.resources.models import Resource, ResourceType
                from apps.resources.services import UserResourceService
                r = Resource.objects.filter(pk=ev.prize_id).first()
                if r and r.type in (ResourceType.ASSET, ResourceType.DATA):
                    UserResourceService.give(user_id, ev.prize_id)
            except Exception:
                pass
        return user_event

    @classmethod
    def get_all(
        cls,
        event_id=None,
        event_str=None,
        user_id=None,
        request_entity_id=None,
        target_entity_id=None,
        calc_type=None,
        start=None,
        end=None,
    ):
        """
        GetAll with optional EventCalculate type.
        Returns queryset or aggregated value based on calc_type.
        """
        qs = UserEvent.objects.select_related("event", "user")
        if event_id:
            qs = qs.filter(event_id=event_id)
        elif event_str:
            qs = qs.filter(event__event=event_str)
        if user_id:
            qs = qs.filter(user_id=user_id)
        if request_entity_id:
            qs = qs.filter(request_entity_id=request_entity_id)
        if target_entity_id:
            qs = qs.filter(target_entity_id=target_entity_id)
        if start:
            qs = qs.filter(created_at__gte=start)
        if end:
            qs = qs.filter(created_at__lte=end)

        if calc_type == EventCalculate.COUNT:
            return qs.count()
        if calc_type == EventCalculate.HIGH_VALUE:
            values = [ue.value for ue in qs if isinstance(ue.value, (int, float))]
            return max(values) if values else None
        if calc_type == EventCalculate.SUM_VALUE:
            values = [ue.value for ue in qs if isinstance(ue.value, (int, float))]
            return sum(values)
        return qs

    @classmethod
    def get_count(cls, event_id: int, start=None, end=None) -> int:
        qs = UserEvent.objects.filter(event_id=event_id)
        if start:
            qs = qs.filter(created_at__gte=start)
        if end:
            qs = qs.filter(created_at__lte=end)
        return qs.count()

    @classmethod
    def get_latest(
        cls,
        event_id: int,
        user_id=None,
        request_entity_id=None,
        target_entity_id=None,
        start=None,
        end=None,
    ) -> UserEvent | None:
        qs = UserEvent.objects.filter(event_id=event_id).order_by("-created_at")
        if user_id:
            qs = qs.filter(user_id=user_id)
        if request_entity_id:
            qs = qs.filter(request_entity_id=request_entity_id)
        if target_entity_id:
            qs = qs.filter(target_entity_id=target_entity_id)
        if start:
            qs = qs.filter(created_at__gte=start)
        if end:
            qs = qs.filter(created_at__lte=end)
        return qs.first()
