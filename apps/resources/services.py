"""Resource service - public API for other modules."""
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Resource, UserResource, ResourceType


def _emit_resource_event(event_name: str, user_id: int, resource_id: int, value=None):
    """Emit system event for Resource operations."""
    try:
        from apps.events.services import EventService
        ev = EventService.get_event_by_string(event_name)
        if ev:
            EventService.send_event(ev, user_id, value=value, meta_data={"entity_id": resource_id})
    except Exception:
        pass


class ResourceService:
    @staticmethod
    def get_by_id(pk: int) -> Resource:
        return get_object_or_404(Resource, pk=pk)

    @staticmethod
    def list_all():
        return Resource.objects.all()

    @staticmethod
    def get_all_filtered(owner_resource_id=None, resource_type=None, tag_ids=None, search=None):
        qs = Resource.objects.all()
        if owner_resource_id:
            qs = qs.filter(owner_resource_id=owner_resource_id)
        if resource_type:
            qs = qs.filter(type=resource_type)
        if tag_ids:
            qs = qs.filter(tags__id__in=tag_ids).distinct()
        if search:
            qs = qs.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        return qs


class UserResourceService:
    """Add, Set, Use, Give per resource type. Per .cursor/docs/core/resource/user-resource.md"""

    @staticmethod
    def _get_or_create(user_id: int, resource_id: int, owner_ur_id=None) -> tuple[UserResource, bool]:
        resource = Resource.objects.get(pk=resource_id)
        defaults = {"value": _default_value_for_resource(resource)}
        ur, created = UserResource.objects.get_or_create(
            user_id=user_id,
            resource_id=resource_id,
            owner_user_resource_id=owner_ur_id,
            defaults=defaults,
        )
        if created and resource.default_amount and resource.type in (ResourceType.CURRENCY, ResourceType.META):
            ur.value = {"value": resource.default_amount}
            ur.save()
        return ur, created

    @staticmethod
    def add(user_id: int, resource_id: int, value) -> dict:
        """Add value to Currency or Meta. Value must be positive."""
        if not isinstance(value, (int, float)) or value <= 0:
            return {"code": "VALIDATION_ERROR", "meta": {"value": "Must be positive number"}}
        try:
            resource = Resource.objects.get(pk=resource_id)
        except Resource.DoesNotExist:
            return {"code": "NOT_FOUND", "meta": {"resource": "Not found"}}
        if resource.type not in (ResourceType.CURRENCY, ResourceType.META):
            return {"code": "VALIDATION_ERROR", "meta": {"resource": "Add only for Currency/Meta"}}
        ur, _ = UserResourceService._get_or_create(user_id, resource_id)
        current = ur.value.get("value", 0) or 0
        ur.value = {"value": current + value}
        ur.save()
        _emit_resource_event("Resource:Add", user_id, resource_id, value)
        return {"code": "SUCCESS", "data": {"id": ur.id, "value": ur.value}}

    @staticmethod
    def set_val(user_id: int, resource_id: int, value) -> dict:
        """Set value for Currency, Meta, or Data. Data type=const is read-only."""
        try:
            resource = Resource.objects.get(pk=resource_id)
        except Resource.DoesNotExist:
            return {"code": "NOT_FOUND", "meta": {"resource": "Not found"}}
        if resource.type == ResourceType.ASSET:
            return {"code": "VALIDATION_ERROR", "meta": {"resource": "Set not for Asset"}}
        if resource.type == ResourceType.DATA:
            config_type = (resource.config or {}).get("type", "normal")
            if config_type == "const":
                return {"code": "VALIDATION_ERROR", "meta": {"resource": "Data type=const is read-only"}}
        ur, _ = UserResourceService._get_or_create(user_id, resource_id)
        if resource.type == ResourceType.DATA:
            ur.value = {"value": value, "valueType": type(value).__name__}
        else:
            ur.value = {"value": value}
        ur.save()
        _emit_resource_event("Resource:Set", user_id, resource_id, value)
        return {"code": "SUCCESS", "data": {"id": ur.id, "value": ur.value}}

    @staticmethod
    def use(user_id: int, resource_id: int, value=None) -> dict:
        """Use/consume resource. Currency/Meta: subtract value. Asset: remove if owned."""
        from apps.commons.response import ResponseCode
        try:
            resource = Resource.objects.get(pk=resource_id)
        except Resource.DoesNotExist:
            return {"code": "NOT_FOUND", "meta": {"resource": "Not found"}}
        if not resource.is_consumable:
            ur = UserResource.objects.filter(user_id=user_id, resource_id=resource_id).first()
            data = {"id": ur.id, "value": ur.value} if ur else None
            return {
                "code": ResponseCode.RESOURCE_IS_NOT_CONSUMABLE,
                "data": data,
            }
        if resource.type in (ResourceType.CURRENCY, ResourceType.META):
            ur = UserResource.objects.filter(user_id=user_id, resource_id=resource_id).first()
            if not ur:
                return {"code": ResponseCode.RESOURNCE_IS_NOT_ENOUGH, "data": None}
            current = ur.value.get("value", 0) or 0
            amount = value if value is not None else current
            if current < amount:
                return {"code": ResponseCode.RESOURNCE_IS_NOT_ENOUGH, "data": {"id": ur.id, "value": ur.value}}
            min_val = (resource.config or {}).get("minValue")
            if min_val is not None and current - amount < min_val:
                return {"code": ResponseCode.RESOURNCE_IS_NOT_ENOUGH, "data": {"id": ur.id, "value": ur.value}}
            ur.value = {"value": current - amount}
            ur.save()
            _emit_resource_event("Resource:Use", user_id, resource_id, amount)
            return {"code": "SUCCESS", "data": {"id": ur.id, "value": ur.value}}
        if resource.type == ResourceType.ASSET:
            ur = UserResource.objects.filter(user_id=user_id, resource_id=resource_id).first()
            if not ur:
                return {"code": ResponseCode.RESOURNCE_IS_NOT_ENOUGH, "data": None}
            ur.delete()
            _emit_resource_event("Resource:Use", user_id, resource_id)
            return {"code": "SUCCESS", "data": None}

    @staticmethod
    def give(user_id: int, resource_id: int) -> dict:
        """Give resource to user. For Asset and Data only."""
        try:
            resource = Resource.objects.get(pk=resource_id)
        except Resource.DoesNotExist:
            return {"code": "NOT_FOUND", "meta": {"resource": "Not found"}}
        if resource.type in (ResourceType.CURRENCY, ResourceType.META):
            return {"code": "VALIDATION_ERROR", "meta": {"resource": "Give not for Currency/Meta"}}
        ur, created = UserResourceService._get_or_create(user_id, resource_id)
        if not created:
            return {"code": "SUCCESS", "data": {"id": ur.id, "value": ur.value}}
        if resource.type == ResourceType.DATA:
            default = (resource.config or {}).get("value")
            ur.value = {"value": default, "valueType": type(default).__name__ if default is not None else "Null"}
            ur.save()
        _emit_resource_event("Resource:Give", user_id, resource_id)
        return {"code": "SUCCESS", "data": {"id": ur.id, "value": ur.value}}


def _default_value_for_resource(resource: Resource) -> dict:
    if resource.type in (ResourceType.CURRENCY, ResourceType.META):
        return {"value": resource.default_amount or 0}
    if resource.type == ResourceType.ASSET:
        return {"childs": []}
    if resource.type == ResourceType.DATA:
        return {"value": None, "valueType": "Null"}
    return {}
