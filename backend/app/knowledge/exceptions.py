"""Knowledge-loading exceptions with safe, concise messages."""


class KnowledgeLoadError(RuntimeError):
    """Raised when the application cannot establish a valid active package."""

