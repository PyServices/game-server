"""
Exception handling for standard response format per response.md
"""
from rest_framework.views import exception_handler
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response

from .response import ResponseCode, api_response


def standard_exception_handler(exc, context):
    """Wrap DRF exceptions in {code, meta?, data?} format."""
    response = exception_handler(exc, context)
    if response is None:
        return api_response(
            ResponseCode.SERVER_ERROR,
            meta={"detail": str(exc)},
            status=500,
        )
    code = ResponseCode.SERVER_ERROR
    if isinstance(exc, NotFound):
        code = ResponseCode.NOT_FOUND
    elif isinstance(exc, ValidationError):
        code = "VALIDATION_ERROR"
    return api_response(
        code,
        meta={"detail": response.data} if response.data else None,
        status=response.status_code,
    )
