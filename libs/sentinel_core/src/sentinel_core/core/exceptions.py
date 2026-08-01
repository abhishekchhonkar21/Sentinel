"""Domain and infrastructure exceptions — map to HTTP responses at the API boundary."""


class SentinelError(Exception):
    """Base exception for all Sentinel errors."""

    def __init__(self, message: str, *, code: str = "sentinel_error") -> None:
        super().__init__(message)
        self.message = message
        self.code = code


class NotFoundError(SentinelError):
    def __init__(self, resource: str, identifier: str) -> None:
        super().__init__(f"{resource} not found: {identifier}", code="not_found")
        self.resource = resource
        self.identifier = identifier


class ValidationError(SentinelError):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="validation_error")


class ExternalServiceError(SentinelError):
    def __init__(self, service: str, message: str) -> None:
        super().__init__(f"{service}: {message}", code="external_service_error")
        self.service = service


class LLMOutputError(SentinelError):
    """Raised when an LLM returns malformed or schema-invalid structured output."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="llm_output_error")
