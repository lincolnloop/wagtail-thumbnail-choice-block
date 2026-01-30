"""
Wagtail Thumbnail Choice Block

A reusable Wagtail block that displays thumbnail images for choice fields,
making it easier for content editors to visually select options.
"""

__version__ = "0.1.4"

from .blocks import ThumbnailChoiceBlock  # noqa: F401
from .widgets import ThumbnailRadioSelect  # noqa: F401

__all__ = ["ThumbnailChoiceBlock", "ThumbnailRadioSelect"]
