from datetime import UTC, datetime


def build_health_status() -> dict[str, str]:
    return {
        "service": "eye-care-api",
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "0.1.0",
    }

