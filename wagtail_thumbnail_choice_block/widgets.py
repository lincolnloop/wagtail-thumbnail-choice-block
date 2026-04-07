"""
Widget classes for Wagtail Thumbnail Choice Block.
"""

from django.forms import RadioSelect, Widget
from django.template.loader import render_to_string
from django.utils import translation


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
        tree_items=None,
    ):
        super().__init__(attrs, choices)
        self.thumbnail_mapping = thumbnail_mapping or {}
        self.thumbnail_template_mapping = thumbnail_template_mapping or {}
        self._tree_items = tree_items

        if thumbnail_size is None:
            raise ValueError(
                "thumbnail_size is required. Please provide a thumbnail size in pixels."
            )
        self.thumbnail_size = thumbnail_size

    def get_context(self, name, value, attrs):
        """Override to add thumbnail_size and tree_items to the template context.

        We call Widget.get_context directly (skipping Select.get_context which
        calls optgroups → create_option) because our template iterates over
        tree_items built by _build_tree_context, not optgroups. Calling
        Select.get_context would cause create_option to be invoked twice per
        option — once via optgroups and once via _build_tree_context — doubling
        any render_to_string calls for thumbnail_template_mapping entries.
        """
        context = Widget.get_context(self, name, value, attrs)
        context["widget"]["thumbnail_size"] = self.thumbnail_size
        context["widget"]["tree_items"] = self._build_tree_context(name, value, attrs)
        return context

    def _build_tree_context(self, name, value, attrs):
        """
        Build the flat list of heading/option dicts passed to the template.

        Flat-choices mode (self._tree_items is None):
            Iterates self.choices directly. The blank choice (if any) is already
            at index 0 via _add_blank_choice; no headings are emitted.

        Directory mode (self._tree_items is not None):
            The tree was built from the raw directory scan (no blank choice).
            If self.choices starts with ("", ...) a blank option is prepended at
            depth 0 before iterating the tree items.

        A running integer counter (option_index) is incremented for every option
        and passed as the `index` argument to create_option so that Django generates
        unique id attributes for each radio <input>.
        """
        # Build the full HTML attrs so create_option receives the widget id and
        # can generate per-option ids (e.g. "my-widget_0", "my-widget_1", …).
        full_attrs = self.build_attrs(self.attrs, attrs)

        result = []
        option_index = 0

        if self._tree_items is None:
            # Flat-choices mode: derive everything from self.choices
            for choice_value, choice_label in self.choices:
                selected = str(choice_value) == str(value)
                option = self.create_option(
                    name,
                    choice_value,
                    choice_label,
                    selected,
                    option_index,
                    attrs=full_attrs,
                )
                option["depth"] = 0
                result.append(option)
                option_index += 1
        else:
            # Directory mode: prepend blank choice if present in self.choices
            choices_list = list(self.choices)
            if choices_list and choices_list[0][0] == "":
                blank_value, blank_label = choices_list[0]
                selected = str(blank_value) == str(value)
                option = self.create_option(
                    name,
                    blank_value,
                    blank_label,
                    selected,
                    option_index,
                    attrs=full_attrs,
                )
                option["depth"] = 0
                result.append(option)
                option_index += 1

            for item in self._tree_items:
                if item["type"] == "heading":
                    result.append(
                        {
                            "type": "heading",
                            "label": item["label"],
                            "depth": item["depth"],
                        }
                    )
                else:
                    item_value = item["value"]
                    item_label = item["label"]
                    selected = str(item_value) == str(value)
                    option = self.create_option(
                        name,
                        item_value,
                        item_label,
                        selected,
                        option_index,
                        attrs=full_attrs,
                    )
                    option["depth"] = item.get("depth", 0)
                    result.append(option)
                    option_index += 1

        return result

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
            tree_key = tuple(
                (
                    item["type"],
                    item.get("label", ""),
                    item.get("value", ""),
                    item.get("depth", 0),
                )
                for item in (self._tree_items or [])
            )
            key = (
                name,
                value,
                tuple(sorted((attrs or {}).items())),
                tuple(c[0] for c in self.choices),
                thumbnail_mapping_key,
                template_mapping_key,
                translation.get_language(),
                tree_key,
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
