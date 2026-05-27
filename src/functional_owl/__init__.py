"""An implementation of the Functional OWL (OFN) object model."""

from .api import hello, square

# being explicit about exports is important!
__all__ = [
    "hello",
    "square",
]
