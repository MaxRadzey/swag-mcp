class SwagError(Exception):
    """Base error for swag domain failures."""


class ServiceNotFoundError(SwagError):
    """Raised when a service id is missing from the catalog."""


class SpecFetchError(SwagError):
    """Raised when an HTTP request for a spec document fails."""


class SpecDecodeError(SwagError):
    """Raised when spec body cannot be decoded as JSON."""


class SpecValidationError(SwagError):
    """Raised when decoded JSON is not a recognizable OpenAPI/Swagger document."""
