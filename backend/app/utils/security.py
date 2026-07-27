"""Application-local security controls for the single-machine prototype."""

from __future__ import annotations

import logging
import re
import threading
import time
import unicodedata
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from typing import Any

from flask import Flask, Response, current_app, request

from app.utils.responses import error_response

_SENSITIVE_KEY = re.compile(
    r"(?:password|passwd|secret|token|authorization|cookie|csrf|session)",
    re.IGNORECASE,
)
_LOG_SECRET = re.compile(
    r"(?i)\b(authorization|cookie|set-cookie|password|token|secret|csrf)"
    r"\b(\s*[:=]\s*)([^\s,;]+)"
)


def normalize_text(value: str, *, max_length: int, field_name: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).strip()
    if len(normalized) > max_length:
        raise ValueError(f"{field_name} must not exceed {max_length} characters.")
    if any(
        unicodedata.category(character) in {"Cc", "Cf"}
        for character in normalized
    ):
        raise ValueError(f"{field_name} contains unsupported control characters.")
    return normalized


def sanitize_mapping(value: Any, *, depth: int = 0) -> Any:
    if depth > 5:
        return "[TRUNCATED]"
    if isinstance(value, dict):
        return {
            str(key)[:80]: (
                "[REDACTED]"
                if _SENSITIVE_KEY.search(str(key))
                else sanitize_mapping(item, depth=depth + 1)
            )
            for key, item in list(value.items())[:50]
        }
    if isinstance(value, (list, tuple)):
        return [sanitize_mapping(item, depth=depth + 1) for item in value[:50]]
    if isinstance(value, str):
        return value[:500]
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return str(value)[:500]


class RedactingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = _LOG_SECRET.sub(r"\1\2[REDACTED]", record.msg)
        if isinstance(record.args, dict):
            record.args = sanitize_mapping(record.args)
        elif record.args:
            record.args = tuple(
                sanitize_mapping(item) if isinstance(item, (dict, list, tuple)) else item
                for item in record.args
            )
        return True


@dataclass(frozen=True)
class _Limit:
    count: int
    seconds: int


def _parse_limit(value: str) -> _Limit:
    match = re.fullmatch(
        r"\s*(\d+)\s+per\s+(?:(\d+)\s+)?(second|minute|hour)s?\s*",
        value,
        re.IGNORECASE,
    )
    if not match:
        raise RuntimeError(f"Invalid rate-limit value: {value!r}")
    count = int(match.group(1))
    multiplier = int(match.group(2) or "1")
    units = {"second": 1, "minute": 60, "hour": 3600}
    if count < 1 or multiplier < 1:
        raise RuntimeError("Rate-limit counts and windows must be positive.")
    return _Limit(count, multiplier * units[match.group(3).lower()])


class RateLimiter:
    """Thread-safe fixed-window limiter suitable for the packaged single process."""

    def __init__(self) -> None:
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def init_app(self, app: Flask) -> None:
        for key in (
            "RATELIMIT_DEFAULT",
            "RATELIMIT_LOGIN",
            "RATELIMIT_REGISTER",
            "RATELIMIT_REFRESH",
            "RATELIMIT_KNOWLEDGE_UPLOAD",
        ):
            _parse_limit(app.config[key])
        with self._lock:
            self._events.clear()
        app.extensions["rate_limiter"] = self
        app.before_request(self._check_default)

    def _key(self, scope: str) -> str:
        address = request.remote_addr or "unknown"
        return f"{scope}:{address}"

    def _allowed(self, key: str, limit: _Limit) -> tuple[bool, int]:
        now = time.monotonic()
        cutoff = now - limit.seconds
        with self._lock:
            events = self._events[key]
            while events and events[0] <= cutoff:
                events.popleft()
            if len(events) >= limit.count:
                retry_after = max(1, int(limit.seconds - (now - events[0])) + 1)
                return False, retry_after
            events.append(now)
            return True, 0

    def _enforce(self, scope: str, configured_limit: str):
        if not current_app.config["RATELIMIT_ENABLED"]:
            return None
        allowed, retry_after = self._allowed(self._key(scope), _parse_limit(configured_limit))
        if allowed:
            return None
        response, status = error_response(
            "Too many requests. Please wait before trying again.",
            429,
            "rate_limit_exceeded",
        )
        response.headers["Retry-After"] = str(retry_after)
        return response, status

    def _check_default(self):
        return self._enforce(
            (
                f"default:{request.endpoint}"
                if request.endpoint
                else "default:unmatched"
            ),
            current_app.config["RATELIMIT_DEFAULT"],
        )

    def limit(self, config_key: str) -> Callable:
        def decorator(function: Callable) -> Callable:
            @wraps(function)
            def wrapped(*args, **kwargs):
                blocked = self._enforce(
                    f"route:{request.endpoint}",
                    current_app.config[config_key],
                )
                return blocked or function(*args, **kwargs)

            return wrapped

        return decorator


rate_limiter = RateLimiter()


def configure_security(app: Flask) -> None:
    redactor = RedactingFilter()
    app.logger.addFilter(redactor)
    logging.getLogger("werkzeug").addFilter(redactor)
    rate_limiter.init_app(app)

    @app.after_request
    def add_security_headers(response: Response) -> Response:
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), payment=()"
        )
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
        )
        if request.path.startswith("/api/"):
            response.headers.setdefault("Cache-Control", "no-store")
        if request.is_secure:
            response.headers["Strict-Transport-Security"] = (
                f"max-age={app.config['SECURITY_HSTS_SECONDS']}; includeSubDomains"
            )
        return response
