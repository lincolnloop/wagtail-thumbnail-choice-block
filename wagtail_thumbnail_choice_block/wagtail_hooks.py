"""
Wagtail hooks for registering CSS and JS assets.
"""

from django.templatetags.static import static
from django.utils.html import format_html

from wagtail import hooks


@hooks.register("insert_global_admin_css")
def thumbnail_choice_block_css():
    """Register CSS for thumbnail choice blocks in Wagtail admin."""
    return format_html(
        '<link rel="stylesheet" href="{}">',
        static("wagtail_thumbnail_choice_block/css/thumbnail-choice-block.css"),
    )


@hooks.register("insert_global_admin_js")
def thumbnail_choice_block_js():
    """Register JavaScript for thumbnail choice blocks in Wagtail admin."""
    return format_html(
        '<script src="{}"></script>',
        static("wagtail_thumbnail_choice_block/js/thumbnail-choice-block.js"),
    )
