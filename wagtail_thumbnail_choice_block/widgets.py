"""
Widget classes for Wagtail Thumbnail Choice Block.
"""

from django.forms import RadioSelect


class ThumbnailRadioSelect(RadioSelect):
    """
    Custom radio select widget that displays thumbnails for each option.

    This widget extends Django's RadioSelect to include thumbnail images
    alongside each radio button option.

    Args:
        attrs: HTML attributes for the widget
        choices: Available choices for the radio select
        thumbnail_mapping: Dictionary mapping choice values to thumbnail URLs or paths

    Example:
        widget = ThumbnailRadioSelect(
            choices=[('light', 'Light Theme'), ('dark', 'Dark Theme')],
            thumbnail_mapping={
                'light': '/static/images/light-thumb.png',
                'dark': '/static/images/dark-thumb.png',
            }
        )
    """

    template_name = "wagtail_thumbnail_choice_block/widgets/thumbnail_radio_select.html"

    def __init__(self, attrs=None, choices=(), thumbnail_mapping=None):
        super().__init__(attrs, choices)
        self.thumbnail_mapping = thumbnail_mapping or {}

    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        """Override to add thumbnail URL to each option."""
        option = super().create_option(
            name, value, label, selected, index, subindex, attrs
        )
        # Add thumbnail URL to the option context
        option["thumbnail_url"] = self.thumbnail_mapping.get(value, "")
        return option
