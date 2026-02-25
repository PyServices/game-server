"""Event API - Event CRUD, SendEvent, GetAll, GetLatest."""
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema

from .models import Event, UserEvent
from .services import EventService, EventCalculate
from .serializers import EventSerializer, UserEventSerializer, SendEventSerializer
from .filters import EventFilter
from apps.commons.mixins import StandardResponseMixin
from apps.commons.response import ResponseCode, api_response


class EventViewSet(StandardResponseMixin, viewsets.ModelViewSet):
    """Admin CRUD for Event definitions."""
    serializer_class = EventSerializer
    filterset_class = EventFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "event"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Event.objects.all().prefetch_related("tags")


@extend_schema(request=SendEventSerializer, responses={201: UserEventSerializer})
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_event(request):
    """SendEvent(event, value?, metaData?, requestEntityId?, targetEntityId?)."""
    serializer = SendEventSerializer(data=request.data)
    if not serializer.is_valid():
        return api_response("VALIDATION_ERROR", meta=serializer.errors, status=400)
    data = serializer.validated_data
    ev = EventService.get_event_by_string(data["event"])
    if ev is None:
        return api_response(ResponseCode.NOT_FOUND, meta={"event": "Event not found"}, status=404)
    user_event = EventService.send_event(
        ev,
        user_id=request.user.id,
        value=data.get("value"),
        meta_data=data.get("metaData"),
        request_entity_id=data.get("requestEntityId") or "",
        target_entity_id=data.get("targetEntityId") or "",
    )
    return api_response(
        ResponseCode.SUCCESS,
        data=UserEventSerializer(user_event).data,
        status=201,
    )


@extend_schema(responses={200: UserEventSerializer})
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_latest_event(request):
    """GetLatest(event_id, requestEntityId?, targetEntityId?, userId?, start?, end?)."""
    event_id = request.query_params.get("eventId") or request.query_params.get("id")
    if not event_id:
        return api_response("VALIDATION_ERROR", meta={"eventId": "required"}, status=400)
    user_id = request.query_params.get("userId")
    request_entity_id = request.query_params.get("requestEntityId")
    target_entity_id = request.query_params.get("targetEntityId")
    start = request.query_params.get("start")
    end = request.query_params.get("end")
    ue = EventService.get_latest(
        event_id=int(event_id),
        user_id=user_id,
        request_entity_id=request_entity_id,
        target_entity_id=target_entity_id,
        start=start,
        end=end,
    )
    if ue is None:
        return api_response(ResponseCode.NOT_FOUND, status=404)
    return api_response(
        ResponseCode.SUCCESS,
        data=UserEventSerializer(ue).data,
        status=200,
    )


@extend_schema(responses={200: None})
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_events(request):
    """
    GetAll with filters. type=Count|HighValue|SumValue returns aggregated value.
    """
    event_id = request.query_params.get("id")
    event_str = request.query_params.get("event")
    user_id = request.query_params.get("userId") or (request.user.id if request.user.is_authenticated else None)
    request_entity_id = request.query_params.get("requestEntityId")
    target_entity_id = request.query_params.get("targetEntityId")
    calc_type = request.query_params.get("type")
    start = request.query_params.get("start")
    end = request.query_params.get("end")

    if not event_id and not event_str:
        return api_response("VALIDATION_ERROR", meta={"event": "event or id required"}, status=400)

    event_id_int = int(event_id) if event_id else None
    result = EventService.get_all(
        event_id=event_id_int,
        event_str=event_str,
        user_id=user_id,
        request_entity_id=request_entity_id,
        target_entity_id=target_entity_id,
        calc_type=calc_type,
        start=start,
        end=end,
    )

    if calc_type:
        return api_response(ResponseCode.SUCCESS, data={"value": result}, status=200)
    from apps.commons.pagination import StandardPagination
    paginator = StandardPagination()
    page_qs = paginator.paginate_queryset(result, request)
    if page_qs is not None:
        payload = paginator.get_paginated_response(
            UserEventSerializer(page_qs, many=True).data
        ).data
        return api_response(ResponseCode.SUCCESS, data=payload, status=200)
    return api_response(
        ResponseCode.SUCCESS,
        data=UserEventSerializer(result, many=True).data,
        status=200,
    )
