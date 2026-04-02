"""
Widget classes for Wagtail Thumbnail Choice Block.
"""

from django.forms import RadioSelect
from django.template.loader import render_to_string


class ThumbnailRadioSelect(RadioSelect):
    """
    Custom radio select widget that displays thumbnails for each option.

    This widget extends Django's RadioSelect to include thumbnail images
    or template-rendered HTML alongside each radio button option.

    Args:
        attrs: HTML attributes for the widget
        choices: Available choices for the radio select
        thumbnail_mapping: Dictionary mapping choice values to thumbnail URLs or paths
        thumbnail_template_mapping: Dictionary mapping choice values to either:
                                   - A string (template path), or
                                   - A dict with 'template' and 'context' keys

    Example (with image URLs):
        widget = ThumbnailRadioSelect(
            choices=[('light', 'Light Theme'), ('dark', 'Dark Theme')],
            thumbnail_mapping={
                'light': static('images/light-thumb.png'),
                'dark': static('images/dark-thumb.png'),
            }
        )

    Example (with templates):
        widget = ThumbnailRadioSelect(
            choices=[('star', 'Star'), ('check', 'Check')],
            thumbnail_template_mapping={
                'star': {
                    'template': 'components/icon.html',
                    'context': {'icon_name': 'star'}
                },
                'check': 'components/icon.html',  # Simple template path
            }
        )
    """

    template_name = "wagtail_thumbnail_choice_block/widgets/thumbnail_radio_select.html"

    # Class-level cache shared across all instances. Keyed on the arguments that
    # fully determine the rendered HTML so that (Wagtail's) Telepath's repeated
    # per-instance render() calls (one per block occurrence in the page tree)
    # collapse to a single real render followed by fast dictionary lookups.
    _render_cache = {}

    class Media:
        css = {
            "all": ("wagtail_thumbnail_choice_block/css/thumbnail-choice-block.css",)
        }
        js = ("wagtail_thumbnail_choice_block/js/thumbnail-choice-block.js",)

    def __init__(
        self,
        attrs=None,
        choices=(),
        thumbnail_mapping=None,
        thumbnail_template_mapping=None,
        thumbnail_size=None,
    ):
        super().__init__(attrs, choices)
        self.thumbnail_mapping = thumbnail_mapping or {}
        self.thumbnail_template_mapping = thumbnail_template_mapping or {}

        if thumbnail_size is None:
            raise ValueError(
                "thumbnail_size is required. Please provide a thumbnail size in pixels."
            )
        self.thumbnail_size = thumbnail_size

    def get_context(self, name, value, attrs):
        """Override to add thumbnail_size to the template context."""
        context = super().get_context(name, value, attrs)
        context["widget"]["thumbnail_size"] = self.thumbnail_size
        return context

    def render(self, name, value, attrs=None, renderer=None):
        """
        Override to cache the full rendered HTML at the class level.

        Telepath (Wagtail's JS serialisation layer) calls render() once per block
        instance in the page tree. When many blocks share the same choices and
        thumbnail mappings, all but the first call are served from this cache.

        The cache key is based on mapping *content* rather than object identity so
        that distinct instances built from the same choices list (which each create
        a new dict object) correctly share a cache entry.
        """
        try:
            thumbnail_mapping_key = tuple(sorted(self.thumbnail_mapping.items()))
            template_mapping_key = tuple(
                sorted(
                    (
                        k,
                        v if isinstance(v, str) else tuple(sorted(v.items())),
                    )
                    for k, v in self.thumbnail_template_mapping.items()
                )
            )
            key = (
                name,
                value,
                tuple(sorted((attrs or {}).items())),
                tuple(c[0] for c in self.choices),
                thumbnail_mapping_key,
                template_mapping_key,
            )
            hash(key)  # verify the key is hashable before leaving the try block
        except TypeError:
            # Mapping values are not fully hashable (e.g. nested dicts with
            # non-hashable context values) — render without caching.
            return super().render(name, value, attrs, renderer)

        if key not in ThumbnailRadioSelect._render_cache:
            ThumbnailRadioSelect._render_cache[key] = super().render(
                name, value, attrs, renderer
            )
        return ThumbnailRadioSelect._render_cache[key]

    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        """Override to add thumbnail URL and/or rendered template HTML to each option."""
        option = super().create_option(
            name, value, label, selected, index, subindex, attrs
        )

        # Add thumbnail URL to the option context.
        option["thumbnail_url"] = self.thumbnail_mapping.get(value, "")

        # Add rendered template HTML to the option context.
        thumbnail_template_config = self.thumbnail_template_mapping.get(value)

        if thumbnail_template_config:
            # Handle both string (template path) and dict (template + context)
            if isinstance(thumbnail_template_config, str):
                template_path = thumbnail_template_config
                context = {"value": value, "label": label}
            elif isinstance(thumbnail_template_config, dict):
                template_path = thumbnail_template_config.get("template")
                context = thumbnail_template_config.get("context", {})
                # Add value and label to context by default
                context.setdefault("value", value)
                context.setdefault("label", label)
            else:
                template_path = None
                context = {}

            if template_path:
                try:
                    rendered_html = render_to_string(template_path, context)
                    option["thumbnail_template_html"] = rendered_html
                except Exception:
                    # Fallback gracefully if template rendering fails
                    option["thumbnail_template_html"] = ""
        else:
            option["thumbnail_template_html"] = ""

        return option
