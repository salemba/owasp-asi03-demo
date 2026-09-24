class ShopSphereError(Exception):
    """Base project exception."""


class DependencyUnavailableError(ShopSphereError):
    """Raised when an external dependency check fails."""
