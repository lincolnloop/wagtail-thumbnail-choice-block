"""
Block classes for Wagtail Thumbnail Choice Block.
"""

from wagtail import blocks

from .widgets import ThumbnailRadioSelect


class ThumbnailChoiceBlock(blocks.ChoiceBlock):
    """
    A Wagtail ChoiceBlock that displays thumbnail images for each choice.

    This block extends Wagtail's ChoiceBlock to show thumbnail previews,
    making it easier for content editors to visually select options.

    Example:
        ```python
        from wagtail_thumbnail_choice_block import ThumbnailChoiceBlock

        class MySettings(blocks.StructBlock):
            theme = ThumbnailChoiceBlock(
                choices=[
                    ('light', 'Light Theme'),
                    ('dark', 'Dark Theme'),
                ],
                thumbnails={
                    'light': '/static/images/theme-light-thumb.png',
                    'dark': '/static/images/theme-dark-thumb.png',
                }
            )
        ```

    Args:
        choices: List of (value, label) tuples for the choices
        thumbnails: Dictionary mapping choice values to thumbnail URLs/paths
        **kwargs: Additional arguments passed to ChoiceBlock
    """

    def __init__(self, choices=None, thumbnails=None, **kwargs):
        self.thumbnails = thumbnails or {}
        # Store the widget for later use
        self._custom_widget = ThumbnailRadioSelect(thumbnail_mapping=self.thumbnails)
        # Pass the widget to parent - it will be used in field creation
        kwargs["widget"] = self._custom_widget
        super().__init__(choices=choices, **kwargs)
