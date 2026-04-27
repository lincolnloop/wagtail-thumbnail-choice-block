import re

from django.db import models
from django.templatetags.static import static

from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail import blocks

from wagtail_thumbnail_choice_block import ThumbnailChoiceBlock
from wagtail_thumbnail_choice_block.widgets import ThumbnailRadioSelect


def _icon_label_fn(stem: str) -> str:
    """Convert a filename stem to a display label, stripping trailing size suffixes.

    Examples:
        "right-16"  -> "Right"
        "left_arrow" -> "Left Arrow"
    """
    stem = re.sub(r"-\d+$", "", stem)
    return stem.replace("_", " ").replace("-", " ").title()


def _icon_value_fn(rel_path: str) -> str:
    """Produce a short stored value from a file's relative path.

    Strips the trailing size suffix and directory components, but prefixes
    "mobile-" for icons under mobile/ so they remain distinct from their
    desktop counterparts with the same stem.

    Examples:
        "arrows/right-16"        -> "right"
        "mobile/arrows/right-16" -> "mobile-right"
        "sun-16"                 -> "sun"
        "shapes/circles/circle"  -> "circle"
    """
    parts = rel_path.split("/")
    stem = re.sub(r"-\d+$", "", parts[-1])
    if "mobile" in parts:
        return f"mobile-{stem}"
    return stem


# --- Collision demonstration ---
# The icons/ directory contains two files with the same filename stem in
# different subdirectories:
#
#   arrows/right-16.svg        → stored as "right"        (via _icon_value_fn)
#   mobile/arrows/right-16.svg → stored as "mobile-right"
#
# _icon_value_fn uses path context ("mobile" in the path parts) to produce
# distinct values, so both files coexist without error.
#
# If a naive stem-only function were used instead:
#
#   thumbnail_directory_value_fn=lambda p: re.sub(r"-\d+$", "", p.split("/")[-1])
#
# both files would produce "right", and ThumbnailChoiceBlock would raise
# ImproperlyConfigured at startup:
#
#   ThumbnailChoiceBlock: thumbnail_directory_value_fn produced the duplicate
#   value 'right' for both '.../arrows/right-16.svg' and
#   '.../mobile/arrows/right-16.svg' inside 'icons'. The first file scanned
#   has already claimed this value. To resolve this, either: (1) update
#   thumbnail_directory_value_fn to return a different value for one of these
#   paths — use more path components to distinguish them — or (2) rename or
#   remove one of the files.

# Directory-based block created at module level so its widget (with pre-scanned
# tree_items) can be reused in the FieldPanel below.
_directory_icon_block = ThumbnailChoiceBlock(
    thumbnail_directory="icons",
    thumbnail_size=40,
    thumbnail_directory_label_fn=_icon_label_fn,
    thumbnail_directory_value_fn=_icon_value_fn,
)


def get_icon_choices():
    """Return available icon choices."""
    return [
        ("star", "Star"),
        ("heart", "Heart"),
        ("check", "Check"),
        ("info", "Info"),
    ]


def get_icon_thumbnail_templates():
    """Return icon thumbnail template mappings."""
    return {
        "star": "home/icons/inline/star.html",
        "heart": "home/icons/inline/heart.html",
        "check": "home/icons/inline/check.html",
        "info": "home/icons/inline/info.html",
    }


def get_color_scheme_choices():
    """Return available color scheme choices."""
    return [
        ("blue", "Blue Scheme"),
        ("green", "Green Scheme"),
        ("red", "Red Scheme"),
        ("purple", "Purple Scheme"),
    ]


def get_color_scheme_thumbnails():
    """Return color scheme thumbnail mappings."""
    from django.templatetags.static import static

    return {
        "blue": static("thumbnails/colors/blue.svg"),
        "green": static("thumbnails/colors/green.svg"),
        "red": static("thumbnails/colors/red.svg"),
        "purple": static("thumbnails/colors/purple.svg"),
    }


class HomePage(Page):
    """
    Home page demonstrating ThumbnailChoiceBlock in various configurations.
    """

    # Example 1: Simple theme selector with image thumbnails
    theme = models.CharField(
        max_length=50,
        choices=[
            ("light", "Light Theme"),
            ("dark", "Dark Theme"),
            ("auto", "Auto (System Preference)"),
        ],
        default="light",
    )

    # Example: Directory-based icon picker — choices scanned automatically from static/icons/
    directory_icon = models.CharField(
        max_length=200,
        blank=True,
        help_text="Icon chosen from the static/icons/ directory.",
    )

    # Example 2: Layout choice with custom thumbnail size
    layout = models.CharField(
        max_length=50,
        choices=[
            ("grid", "Grid Layout"),
            ("list", "List Layout"),
            ("masonry", "Masonry Layout"),
        ],
        default="grid",
    )

    # Example 3: StreamField with multiple ThumbnailChoiceBlocks
    content = StreamField(
        [
            ("heading", blocks.CharBlock(classname="title")),
            ("paragraph", blocks.RichTextBlock()),
            # Icon selector example
            (
                "icon_block",
                blocks.StructBlock(
                    [
                        (
                            "icon",
                            ThumbnailChoiceBlock(
                                choices=get_icon_choices(),
                                thumbnail_templates=get_icon_thumbnail_templates(),
                                thumbnail_size=20,
                                label="Choose an icon",
                                help_text="Select an icon to display",
                            ),
                        ),
                        (
                            "text",
                            blocks.CharBlock(
                                required=False,
                                help_text="Optional text to display with the icon",
                            ),
                        ),
                    ],
                    icon="placeholder",
                ),
            ),
            # Color scheme example
            (
                "color_scheme",
                blocks.StructBlock(
                    [
                        (
                            "scheme",
                            ThumbnailChoiceBlock(
                                choices=get_color_scheme_choices,
                                thumbnails=get_color_scheme_thumbnails,
                                thumbnail_size=50,
                                label="Color Scheme",
                            ),
                        ),
                        ("title", blocks.CharBlock(required=False)),
                        ("content", blocks.TextBlock(required=False)),
                    ],
                    icon="color",
                ),
            ),
            # Button style example with larger thumbnails
            (
                "button_style",
                blocks.StructBlock(
                    [
                        (
                            "style",
                            ThumbnailChoiceBlock(
                                choices=[
                                    ("solid", "Solid Button"),
                                    ("outline", "Outline Button"),
                                    ("ghost", "Ghost Button"),
                                    ("gradient", "Gradient Button"),
                                ],
                                thumbnails={
                                    "solid": static("thumbnails/buttons/solid.png"),
                                    "outline": static("thumbnails/buttons/outline.png"),
                                    "ghost": static("thumbnails/buttons/ghost.png"),
                                    "gradient": static(
                                        "thumbnails/buttons/gradient.png"
                                    ),
                                },
                                thumbnail_size=80,
                                label="Button Style",
                            ),
                        ),
                        ("text", blocks.CharBlock(default="Click me")),
                        ("url", blocks.URLBlock(required=False)),
                    ],
                    icon="link",
                ),
            ),
            # Optional icon example - demonstrates required=False (default)
            (
                "optional_icon",
                blocks.StructBlock(
                    [
                        (
                            "icon",
                            ThumbnailChoiceBlock(
                                choices=get_icon_choices(),
                                thumbnail_templates=get_icon_thumbnail_templates(),
                                thumbnail_size=20,
                                required=False,  # This is now the default
                                label="Optional Icon",
                                help_text="You can leave this blank if you don't want an icon",
                            ),
                        ),
                        (
                            "heading",
                            blocks.CharBlock(
                                help_text="The heading text",
                            ),
                        ),
                    ],
                    icon="placeholder",
                ),
            ),
            # Directory-based icon selector - choices derived automatically from static files
            (
                "directory_icon",
                ThumbnailChoiceBlock(
                    thumbnail_directory="icons",
                    thumbnail_size=40,
                    thumbnail_directory_label_fn=_icon_label_fn,
                    thumbnail_directory_value_fn=_icon_value_fn,
                    label="Icon (from directory)",
                    help_text="Icons are loaded automatically from the static/icons/ folder.",
                ),
            ),
            # Required icon example - demonstrates required=True
            (
                "required_icon",
                blocks.StructBlock(
                    [
                        (
                            "icon",
                            ThumbnailChoiceBlock(
                                choices=get_icon_choices(),
                                thumbnail_templates=get_icon_thumbnail_templates(),
                                thumbnail_size=20,
                                required=True,  # Explicitly required
                                label="Required Icon",
                                help_text="You must select an icon",
                            ),
                        ),
                        (
                            "heading",
                            blocks.CharBlock(
                                help_text="The heading text",
                            ),
                        ),
                    ],
                    icon="placeholder",
                ),
            ),
        ],
        use_json_field=True,
        blank=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel(
            "directory_icon",
            widget=_directory_icon_block.field.widget,
        ),
        FieldPanel(
            "theme",
            widget=ThumbnailRadioSelect(
                choices=[
                    ("light", "Light Theme"),
                    ("dark", "Dark Theme"),
                    ("auto", "Auto (System Preference)"),
                ],
                thumbnail_mapping={
                    "light": static("thumbnails/themes/light.png"),
                    "dark": static("thumbnails/themes/dark.png"),
                    "auto": static("thumbnails/themes/auto.png"),
                },
                thumbnail_size=60,
            ),
        ),
        FieldPanel(
            "layout",
            widget=ThumbnailRadioSelect(
                choices=[
                    ("grid", "Grid Layout"),
                    ("list", "List Layout"),
                    ("masonry", "Masonry Layout"),
                ],
                thumbnail_mapping={
                    "grid": static("thumbnails/layouts/grid.png"),
                    "list": static("thumbnails/layouts/list.png"),
                    "masonry": static("thumbnails/layouts/masonry.png"),
                },
                thumbnail_size=100,
            ),
        ),
        FieldPanel("content"),
    ]

    class Meta:
        verbose_name = "Home Page"
