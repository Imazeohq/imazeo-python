"""Typed Imazeo SDK errors mapped from API envelopes."""

from __future__ import annotations

from typing import Any


class ImazeoError(Exception):
    """Base error for all Imazeo SDK failures."""

    def __init__(
        self,
        message: str,
        *,
        status: int | None = None,
        code: str | None = None,
        request_id: str | None = None,
        details: Any = None,
        cause: BaseException | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status = status
        self.code = code
        self.request_id = request_id
        self.details = details
        if cause is not None:
            self.__cause__ = cause


class AuthenticationError(ImazeoError):
    """HTTP 401 — invalid or missing API key."""


class AuthorizationError(ImazeoError):
    """HTTP 403 — plan, subscription, or feature gate."""


class ValidationError(ImazeoError):
    """HTTP 400 / 413 / 415 — invalid request."""


class NotFoundError(ImazeoError):
    """HTTP 404."""


class ConflictError(ImazeoError):
    """HTTP 409."""


class RateLimitError(ImazeoError):
    """HTTP 429."""


class ApiError(ImazeoError):
    """Other 4xx/5xx with an Imazeo error envelope."""


class NetworkError(ImazeoError):
    """Transport failure or timeout."""


def map_http_error(
    *,
    status: int,
    message: str,
    code: str | None = None,
    request_id: str | None = None,
    details: Any = None,
) -> ImazeoError:
    kwargs = {
        "status": status,
        "code": code,
        "request_id": request_id,
        "details": details,
    }
    if status == 401:
        return AuthenticationError(message, **kwargs)
    if status == 403:
        return AuthorizationError(message, **kwargs)
    if status == 404:
        return NotFoundError(message, **kwargs)
    if status == 409:
        return ConflictError(message, **kwargs)
    if status == 429:
        return RateLimitError(message, **kwargs)
    if status in (400, 413, 415):
        return ValidationError(message, **kwargs)
    return ApiError(message, **kwargs)
