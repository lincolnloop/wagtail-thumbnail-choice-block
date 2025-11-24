"""
Wagtail hooks for the home app.
"""

from django.utils.html import format_html
from wagtail import hooks


@hooks.register("insert_global_admin_css")
def global_admin_css():
    """Insert custom CSS into the Wagtail admin."""
    return format_html(
        '<link rel="stylesheet" href="/static/css/demo.css">',
    )
