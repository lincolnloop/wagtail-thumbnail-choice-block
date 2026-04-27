"""
Block classes for Wagtail Thumbnail Choice Block.
"""

import posixpath
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from wagtail import blocks

from .widgets import ThumbnailRadioSelect

IMAGE_EXTENSIONS = {".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp"}


class ThumbnailChoiceBlock(blocks.ChoiceBlock):
    # Class-level cache keyed by thumbnail_directory string. Populated the first
    # time a given directory is scanned (auto_reload=False). Avoids redundant
    # filesystem walks when many block instances share the same directory (e.g.
    # multiple fields on the same page model or across Telepath serialisation).
    _scan_cache: dict = {}
    """
    A Wagtail ChoiceBlock that displays thumbnail images for each choice.

    This block extends Wagtail's ChoiceBlock to show thumbnail previews,
    making it easier for content editors to visually select options.

    Both `choices`, `thumbnails`, and `thumbnail_templates` can be either static
    data or callables that return the data. If callables are provided, they will be
    evaluated at render time, allowing for dynamic choices based on database queries
    or other runtime data.

    Example (static `thumbnails`):
        ```python
        from wagtail_thumbnail_choice_block import ThumbnailChoiceBlock

        class MySettings(blocks.StructBlock):
            theme = ThumbnailChoiceBlock(
                choices=[
                    ('light', 'Light Theme'),
                    ('dark', 'Dark Theme'),
                ],
                thumbnails={
                    'light': static('images/theme-light-thumb.png'),
                    'dark': static('images/theme-dark-thumb.png'),
                }
            )
        ```

    Example (dynamic `thumbnails`):
        ```python
        from wagtail_thumbnail_choice_block import ThumbnailChoiceBlock

        def get_user_choices() -> list[tuple[str, str]]:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            return [(user.username, user.get_full_name() or user.username)
                    for user in User.objects.all()]

        def get_user_thumbnails() -> dict[str, str]:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            return {user.username: user.profile.avatar.url
                    for user in User.objects.all() if hasattr(user, 'profile')}

        class MySettings(blocks.StructBlock):
            user = ThumbnailChoiceBlock(
                choices=get_user_choices,
                thumbnails=get_user_thumbnails,
            )
        ```

    Example (static `thumbnail_templates` with simple template path and template + context):
        ```python
        from wagtail_thumbnail_choice_block import ThumbnailChoiceBlock

        class MySettings(blocks.StructBlock):
            icon = ThumbnailChoiceBlock(
                choices=[
                    ('star', 'Star'),
                    ('check', 'Check'),
                ],
                thumbnail_templates={
                    # simple template path
                    'star': 'components/icon.html',
                    # template + context
                    'check': {
                        'template': 'components/icon.html',
                        'context': {'icon_name': 'check', 'extra_class': 'thumbnail-icon'}
                    },
                }
            )
        ```

    Example (dynamic `thumbnail_templates` with template + context):
        ```python
        from wagtail_thumbnail_choice_block import ThumbnailChoiceBlock

        def get_thumbnail_choices() -> list[tuple[str, str]]:
            return [
                (icon_name, icon_name.capitalize())
                for icon_name in ["star", "check"]
            ]

        def get_thumbnail_templates() -> dict[str, str]:
            return {
                icon_name: {
                    'template': 'components/icon.html',
                    'context': {'icon_name': icon_name, 'extra_class': 'thumbnail-icon'}
                }
                for icon_name in ["star", "check"]
            }

        class MySettings(blocks.StructBlock):
            icon = ThumbnailChoiceBlock(
                choices=get_thumbnail_choices,
                thumbnail_templates=get_thumbnail_templates
            )
        ```

    Example (directory-based choices):
        ```python
        from wagtail_thumbnail_choice_block import ThumbnailChoiceBlock

        class MySettings(blocks.StructBlock):
            icon = ThumbnailChoiceBlock(
                thumbnail_directory="icons",
                thumbnail_size=40,
            )
        ```

    Example (directory-based with value_fn to strip size suffix):
        ```python
        import re
        from wagtail_thumbnail_choice_block import ThumbnailChoiceBlock

        def icon_value(rel_path: str) -> str:
            # "arrows/forward-16" -> "arrows/forward"
            # "sun-16"            -> "sun"
            return re.sub(r"-\d+$", "", rel_path)

        class MySettings(blocks.StructBlock):
            icon = ThumbnailChoiceBlock(
                thumbnail_directory="icons",
                thumbnail_directory_value_fn=icon_value,
                thumbnail_size=40,
            )
        ```

    Args:
        choices: List of (value, label) tuples for the choices, or a callable
                 that returns such a list
        thumbnails: Dictionary mapping choice values to thumbnail URLs/paths,
                   or a callable that returns such a dictionary
        thumbnail_templates: Dictionary mapping choice values to either:
                            - A string (template path), or
                            - A dict with 'template' (path) and 'context' (dict) keys
                            Can also be a callable that returns such a dictionary
        thumbnail_directory: Path relative to a staticfiles-findable location
                            (app static/, STATICFILES_DIRS, or STATIC_ROOT).
                            Mutually exclusive with choices, thumbnails, and
                            thumbnail_templates.
        thumbnail_directory_auto_reload: When True (and thumbnail_directory is set), re-scan the
                    thumbnail_directory on each get_form_state call. Useful
                    in development when adding new files without restarting the server.
        thumbnail_directory_sort_key: Callable(pathlib.Path) -> sort key for ordering files and
                 directories. Defaults to case-insensitive filename sort.
        thumbnail_directory_label_fn: Callable(str) -> str for generating labels from file/directory
                 stems. Defaults to replacing _/- with spaces and title-casing.
        thumbnail_directory_value_fn: Optional callable(rel_path: str) -> str. When provided,
                 called for each discovered file with the file's relative path from the directory
                 root, without the file extension (e.g. ``"arrows/forward-16"`` for
                 ``arrows/forward-16.svg``). Its return value becomes the stored choice value.
                 Must produce a unique value for every file in the directory tree. Raises
                 ImproperlyConfigured at startup on collision. This is intentional: the library
                 will not silently reassign a stored value from one file to another as the
                 directory contents change. When a new file causes a collision, update
                 thumbnail_directory_value_fn to return a different value for the new path
                 (use more path components to distinguish it), or rename/remove one of the files.
                 When thumbnail_directory_auto_reload=True, the directory is re-scanned on every
                 admin form render, so a collision introduced by adding a new file raises
                 ImproperlyConfigured on the next render rather than at startup.
                 Defaults to None (the rel_path is stored as-is, which is the existing behaviour).

                 Use a module-level function rather than a lambda. Each lambda literal is a
                 distinct object, so two block instances using syntactically identical lambdas will
                 not share a scan-cache entry and will each trigger a full filesystem scan.
        **kwargs: Additional arguments passed to ChoiceBlock

    Please note: if you are using thumbnail_templates, the Wagtail interface
    may not be set up to load all of the CSS files that your regular pages load,
    so using an icon template may lead to an empty icon in Wagtail. In this case,
    you will need to update the CSS that is loaded in Wagtail to include the
    necessary CSS styles.
    For example, an HTML template like <span class="icon icon-android"></span>
    will need to use the 'icon' and 'icon-android' CSS classes. Make sure that
    they are being loaded in Wagtail.
    """

    def __init__(
        self,
        choices=None,
        thumbnails=None,
        thumbnail_templates=None,
        thumbnail_size=40,
        required=False,
        thumbnail_directory=None,
        thumbnail_directory_auto_reload=False,
        thumbnail_directory_sort_key=None,
        thumbnail_directory_label_fn=None,
        thumbnail_directory_value_fn=None,
        **kwargs,
    ):
        if thumbnail_directory is not None and any(
            [choices, thumbnails, thumbnail_templates]
        ):
            raise ValueError(
                "'thumbnail_directory' is mutually exclusive with 'choices', 'thumbnails', "
                "and 'thumbnail_templates'."
            )

        # Store sources (may be callable in non-directory mode)
        self._choices_source = choices
        self._thumbnails_source = thumbnails
        self._thumbnail_templates_source = thumbnail_templates
        self._thumbnail_size = thumbnail_size
        self._required = required
        self._thumbnail_directory = thumbnail_directory
        self._thumbnail_directory_auto_reload = thumbnail_directory_auto_reload
        self._thumbnail_directory_sort_key = (
            thumbnail_directory_sort_key or self._default_sort_key
        )
        self._thumbnail_directory_label_fn = (
            thumbnail_directory_label_fn or self._default_label_fn
        )
        self._thumbnail_directory_value_fn = thumbnail_directory_value_fn

        if self._thumbnail_directory:
            # Cache key includes value_fn so two blocks pointing at the same directory
            # but with different value_fns do not share a cache entry. Module-level
            # functions are hashable by identity; None is also hashable. Lambdas are
            # hashable but have a distinct identity per literal — two block instances
            # with semantically identical lambdas will not share the cache (performance
            # concern, not a correctness bug; use a module-level function to avoid this).
            cache_key = (self._thumbnail_directory, self._thumbnail_directory_value_fn)
            if (
                not self._thumbnail_directory_auto_reload
                and cache_key in ThumbnailChoiceBlock._scan_cache
            ):
                resolved_choices, thumbnail_map, tree_items = (
                    ThumbnailChoiceBlock._scan_cache[cache_key]
                )
            else:
                resolved_choices, thumbnail_map, tree_items = self._scan_directory()
                if not self._thumbnail_directory_auto_reload:
                    ThumbnailChoiceBlock._scan_cache[cache_key] = (
                        resolved_choices,
                        thumbnail_map,
                        tree_items,
                    )
            self._tree_items = tree_items
            self._thumbnails_source = thumbnail_map
            self._choices_source = (
                resolved_choices  # store raw (no blank) for bookkeeping
            )
        else:
            self._tree_items = None
            resolved_choices = self._resolve_callable(choices)

        # Both paths converge here
        resolved_choices = self._add_blank_choice(resolved_choices, required)
        super().__init__(choices=resolved_choices, required=required, **kwargs)

    @staticmethod
    def _default_label_fn(stem: str) -> str:
        """'left_arrow' -> 'Left Arrow'"""
        return stem.replace("_", " ").replace("-", " ").title()

    @staticmethod
    def _default_sort_key(path) -> str:
        return path.name.lower()

    def _find_static_directory(self) -> Path:
        """
        Locate thumbnail_directory on the filesystem via staticfiles finders,
        falling back to STATIC_ROOT for production deployments.

        Note: Only Django's built-in AppDirectoriesFinder and FileSystemFinder are
        actively searched via their internal 'storages' and 'locations' attributes.
        These are not part of Django's public staticfiles API; getattr with safe
        defaults is intentional — if a future Django version renames them, or a
        custom finder lacks them, the finder is silently skipped rather than
        crashing. STATIC_ROOT remains the guaranteed fallback.

        STATICFILES_DIRS entries with a URL prefix (e.g. [('myprefix', '/path/')])
        are not supported.
        """
        from django.contrib.staticfiles.finders import get_finders

        for finder in get_finders():
            for storage in getattr(finder, "storages", {}).values():
                loc = getattr(storage, "location", None)
                if loc:
                    candidate = Path(loc) / self._thumbnail_directory
                    if candidate.is_dir():
                        return candidate
            for _prefix, root in getattr(finder, "locations", []):
                candidate = Path(root) / self._thumbnail_directory
                if candidate.is_dir():
                    return candidate

        # Production fallback: STATIC_ROOT
        static_root = getattr(settings, "STATIC_ROOT", None)
        if static_root:
            candidate = Path(static_root) / self._thumbnail_directory
            if candidate.is_dir():
                return candidate

        raise ImproperlyConfigured(
            f"ThumbnailChoiceBlock: thumbnail_directory '{self._thumbnail_directory}' not found "
            f"in any staticfiles location or STATIC_ROOT."
        )

    def _scan_directory(self) -> tuple:
        """
        Walk self._thumbnail_directory, located via staticfiles finders (STATIC_ROOT fallback).

        Returns:
            choices       — [(value, label), ...] for field validation
            thumbnail_map — {value: url, ...}
            tree_items    — [{"type": "heading"|"option", "label": str,
                              "depth": int, "value": str,
                              "thumbnail_url": str}, ...]
        """
        root = self._find_static_directory()
        static_url = getattr(settings, "STATIC_URL", "/static/").rstrip("/")
        dir_prefix = f"{static_url}/{self._thumbnail_directory}"

        choices = []
        thumbnail_map = {}
        tree_items = []
        seen = {}  # {transformed_value: Path} — populated only when value_fn is set

        def walk(path, depth, rel_parts):
            local_items = []
            local_choices = []
            local_thumbnail_map = {}

            entries = sorted(path.iterdir(), key=self._thumbnail_directory_sort_key)
            for entry in entries:
                if entry.name.startswith("."):
                    continue
                if entry.is_dir():
                    sub_items, sub_choices, sub_map = walk(
                        entry, depth + 1, rel_parts + [entry.name]
                    )
                    if sub_items:  # only emit heading if directory has descendants
                        heading_label = self._thumbnail_directory_label_fn(entry.name)
                        local_items.append(
                            {"type": "heading", "label": heading_label, "depth": depth}
                        )
                        local_items.extend(sub_items)
                        local_choices.extend(sub_choices)
                        local_thumbnail_map.update(sub_map)
                elif entry.is_file() and entry.suffix.lower() in IMAGE_EXTENSIONS:
                    stem = entry.stem
                    value_parts = rel_parts + [stem]
                    rel_path_without_ext = posixpath.join(*value_parts)

                    if self._thumbnail_directory_value_fn:
                        value = self._thumbnail_directory_value_fn(rel_path_without_ext)
                        if value in seen:
                            raise ImproperlyConfigured(
                                f"ThumbnailChoiceBlock: thumbnail_directory_value_fn produced the "
                                f"duplicate value {value!r} for both '{seen[value]}' and '{entry}' "
                                f"inside '{self._thumbnail_directory}'. The first file scanned has "
                                f"already claimed this value. To resolve this, either: (1) update "
                                f"thumbnail_directory_value_fn to return a different value for one "
                                f"of these paths — use more path components to distinguish them — "
                                f"or (2) rename or remove one of the files."
                            )
                        seen[value] = entry
                    else:
                        value = rel_path_without_ext

                    label = self._thumbnail_directory_label_fn(stem)
                    rel_with_ext = posixpath.join(*(rel_parts + [entry.name]))
                    thumbnail_url = f"{dir_prefix}/{rel_with_ext}"
                    local_items.append(
                        {
                            "type": "option",
                            "label": label,
                            "depth": depth,
                            "value": value,
                            "thumbnail_url": thumbnail_url,
                        }
                    )
                    local_choices.append((value, label))
                    local_thumbnail_map[value] = thumbnail_url

            return local_items, local_choices, local_thumbnail_map

        tree_items, choices, thumbnail_map = walk(root, depth=0, rel_parts=[])
        return choices, thumbnail_map, tree_items

    def get_thumbnail_url(self, value: str) -> str:
        """Return the static URL for the thumbnail for the given stored value, or '' if not found."""
        thumbnails = self._resolve_callable(self._thumbnails_source) or {}
        return thumbnails.get(value, "")

    def _resolve_callable(self, value):
        """
        Resolve a value that may be a callable or static data.

        Args:
            value: Either a static value or a callable that returns the value

        Returns:
            The resolved value
        """
        if callable(value):
            return value()
        return value

    def _add_blank_choice(self, choices, required):
        """
        Add a blank choice to the beginning of choices list if field is not required.

        Args:
            choices: List of (value, label) tuples
            required: Boolean indicating if field is required

        Returns:
            Choices list with blank option prepended if not required
        """
        if required or choices is None:
            return choices

        # Convert to list if needed
        choices_list = list(choices) if choices else []

        # Check if blank choice already exists
        has_blank = any(choice[0] == "" for choice in choices_list)

        # Prepend blank choice if it doesn't exist
        if not has_blank:
            choices_list.insert(0, ("", "---"))

        return choices_list

    def get_form_state(self, value):
        """
        Override to ensure we have fresh choices and thumbnails when rendering the form.
        This is called when the block is rendered in the admin interface.
        """
        if self._thumbnail_directory and self._thumbnail_directory_auto_reload:
            choices, thumbnail_map, tree_items = self._scan_directory()
            choices_with_blank = self._add_blank_choice(choices, self._required)
            self._tree_items = tree_items
            self._thumbnails_source = thumbnail_map
            self._choices_source = choices  # store raw (without blank) for consistency
            # Push changes to the already-constructed widget
            self.field.widget._tree_items = tree_items
            self.field.widget.choices = choices_with_blank
            self.field.widget.thumbnail_mapping = thumbnail_map
            self.field.choices = choices_with_blank
        else:
            # Resolve choices, thumbnails, and thumbnail_templates at render time
            resolved_choices = self._resolve_callable(self._choices_source)
            resolved_thumbnails = self._resolve_callable(self._thumbnails_source) or {}
            resolved_thumbnail_templates = (
                self._resolve_callable(self._thumbnail_templates_source) or {}
            )

            # Add blank choice if field is not required
            resolved_choices = self._add_blank_choice(resolved_choices, self._required)

            # Update the field's choices if they've changed
            if resolved_choices is not None:
                self.field.choices = resolved_choices
                self.field.widget.choices = resolved_choices

            # Update the thumbnail mapping in the widget
            if hasattr(self.field.widget, "thumbnail_mapping"):
                self.field.widget.thumbnail_mapping = resolved_thumbnails

            # Update the thumbnail template mapping in the widget
            if hasattr(self.field.widget, "thumbnail_template_mapping"):
                self.field.widget.thumbnail_template_mapping = (
                    resolved_thumbnail_templates
                )

        return super().get_form_state(value)

    def get_field(self, **kwargs):
        """
        Override get_field to create widget with current thumbnails.
        This is called by the parent ChoiceBlock during initialization.
        """
        if self._thumbnail_directory:
            # Directory mode: thumbnail_map is already in self._thumbnails_source (a dict)
            resolved_thumbnails = self._thumbnails_source or {}
            resolved_thumbnail_templates = {}
            resolved_choices = self._add_blank_choice(
                self._choices_source, self._required
            )
        else:
            # Resolve thumbnails and thumbnail_templates at field creation time
            resolved_thumbnails = self._resolve_callable(self._thumbnails_source) or {}
            resolved_thumbnail_templates = (
                self._resolve_callable(self._thumbnail_templates_source) or {}
            )

            # Resolve choices and add blank choice if not required
            resolved_choices = self._resolve_callable(self._choices_source)
            resolved_choices = self._add_blank_choice(resolved_choices, self._required)

        # Update the stored choices with the resolved ones
        # This must happen before calling parent's get_field
        if resolved_choices is not None:
            self.choices = resolved_choices

        # Create the custom widget with the resolved choices
        widget = ThumbnailRadioSelect(
            choices=resolved_choices if resolved_choices else [],
            thumbnail_mapping=resolved_thumbnails,
            thumbnail_template_mapping=resolved_thumbnail_templates,
            thumbnail_size=self._thumbnail_size,
            tree_items=self._tree_items,
        )

        # Pass the widget to parent's get_field
        kwargs["widget"] = widget

        # Get the field from the parent
        field = super().get_field(**kwargs)

        # Override the field's choices to ensure no extra blank choices are added
        if resolved_choices is not None:
            field.choices = resolved_choices
            field.widget.choices = resolved_choices

        return field
