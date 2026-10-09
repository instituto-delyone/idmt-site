"""AIGAR Memory Lab: isolated, replaceable three-layer memory experiment.

Documents are read from the repository tree at runtime. This module does not
modify the cognitive core and fails soft: the API can continue answering when
the Memory Lab or a document source is unavailable.
"""
from .engine import MemoryLab, MEMORY_LAYERS

__all__ = ["MemoryLab", "MEMORY_LAYERS"]
