"""
Standard API response format per .cursor/docs/architecture/response.md

{ code: SUCCESS | NOT_FOUND | SERVER_ERROR | ...; meta?: JSON; data?: JSON }
"""
from rest_framework.response import Response


class ResponseCode:
    SUCCESS = "SUCCESS"
    NOT_FOUND = "NOT_FOUND"
    SERVER_ERROR = "SERVER_ERROR"
    # Auth / Update codes
    CURRENT_PASSWORD_IS_WRONG = "CURRENT_PASSWORD_IS_WRONG"
    PHONE_NUMBER_IS_NOT_VALID = "PHONE_NUMBER_IS_NOT_VALID"
    EMAIL_IS_NOT_VALID = "EMAIL_IS_NOT_VALID"
    PHONE_NUMBER_IS_SAME = "PHONE_NUMBER_IS_SAME"
    EMAIL_IS_SAME = "EMAIL_IS_SAME"
    DEVICE_ID_NOT_FOUND = "DEVICE_ID_NOT_FOUND"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    PASSWORD_IS_WRONG = "PASSWORD_IS_WRONG"
    RESOURCE_IS_NOT_CONSUMABLE = "RESOURCE_IS_NOT_CONSUMABLE"
    RESOURCE_IS_NOT_ENOUGH = "RESOURCE_IS_NOT_ENOUGH"
    RESOURNCE_IS_NOT_ENOUGH = "RESOURNCE_IS_NOT_ENOUGH"  # Docs spelling


def api_response(code: str, data=None, meta=None, status: int = 200) -> Response:
    """Return standard {code, meta?, data?} response."""
    payload = {"code": code}
    if meta is not None:
        payload["meta"] = meta
    if data is not None:
        payload["data"] = data
    return Response(payload, status=status)
