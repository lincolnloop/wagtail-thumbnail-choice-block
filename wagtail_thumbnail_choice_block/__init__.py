"""
Wagtail Thumbnail Choice Block

A reusable Wagtail block that displays thumbnail images for choice fields,
making it easier for content editors to visually select options.
"""

from .blocks import ThumbnailChoiceBlock  # noqa: F401
from .widgets import ThumbnailRadioSelect  # noqa: F401

__version__ = "0.2.0"

default_app_config = (
    "wagtail_thumbnail_choice_block.apps.WagtailThumbnailChoiceBlockAppConfig"
)

__all__ = ["ThumbnailChoiceBlock", "ThumbnailRadioSelect"]
