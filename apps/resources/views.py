from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema

from .services import ResourceService, UserResourceService
from .serializers import (
    ResourceSerializer,
    UserResourceSerializer,
    UserResourceAddSerializer,
    UserResourceSetSerializer,
    UserResourceUseSerializer,
    UserResourceGiveSerializer,
)
from .filters import ResourceFilter as ResourceFilterSet
from apps.commons.mixins import StandardResponseMixin
from apps.commons.response import api_response


class ResourceViewSet(StandardResponseMixin, viewsets.ModelViewSet):
    serializer_class = ResourceSerializer
    filterset_class = ResourceFilterSet
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return ResourceService.list_all()


@extend_schema(responses={200: UserResourceSerializer(many=True)})
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_user_resources(request):
    """List current user's resources."""
    qs = UserResourceService.list_for_user(request.user.id)
    serializer = UserResourceSerializer(qs, many=True)
    return api_response("SUCCESS", data=serializer.data)


@extend_schema(request=UserResourceAddSerializer, responses={200: None})
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def user_resource_add(request):
    serializer = UserResourceAddSerializer(data=request.data)
    if not serializer.is_valid():
        return api_response("VALIDATION_ERROR", meta=serializer.errors, status=400)
    result = UserResourceService.add(
        request.user.id,
        serializer.validated_data["resourceId"],
        serializer.validated_data["value"],
    )
    status = 200 if result["code"] == "SUCCESS" else 400
    if result["code"] in ("RESOURCE_IS_NOT_ENOUGH", "RESOURNCE_IS_NOT_ENOUGH"):
        status = 409
    return api_response(result["code"], data=result.get("data"), meta=result.get("meta"), status=status)


@extend_schema(request=UserResourceSetSerializer, responses={200: None})
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def user_resource_set(request):
    serializer = UserResourceSetSerializer(data=request.data)
    if not serializer.is_valid():
        return api_response("VALIDATION_ERROR", meta=serializer.errors, status=400)
    result = UserResourceService.set_val(
        request.user.id,
        serializer.validated_data["resourceId"],
        serializer.validated_data["value"],
    )
    return api_response(result["code"], data=result.get("data"), meta=result.get("meta"), status=200)


@extend_schema(request=UserResourceUseSerializer, responses={200: None})
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def user_resource_use(request):
    serializer = UserResourceUseSerializer(data=request.data)
    if not serializer.is_valid():
        return api_response("VALIDATION_ERROR", meta=serializer.errors, status=400)
    result = UserResourceService.use(
        request.user.id,
        serializer.validated_data["resourceId"],
        serializer.validated_data.get("value"),
    )
    status = 200 if result["code"] == "SUCCESS" else 400
    if result["code"] in ("RESOURCE_IS_NOT_ENOUGH", "RESOURNCE_IS_NOT_ENOUGH"):
        status = 409
    return api_response(result["code"], data=result.get("data"), meta=result.get("meta"), status=status)


@extend_schema(request=UserResourceGiveSerializer, responses={200: None})
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def user_resource_give(request):
    serializer = UserResourceGiveSerializer(data=request.data)
    if not serializer.is_valid():
        return api_response("VALIDATION_ERROR", meta=serializer.errors, status=400)
    result = UserResourceService.give(
        request.user.id,
        serializer.validated_data["resourceId"],
    )
    return api_response(result["code"], data=result.get("data"), meta=result.get("meta"), status=200)
