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
                    'light': '/static/images/theme-light-thumb.png',
                    'dark': '/static/images/theme-dark-thumb.png',
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

    Args:
        choices: List of (value, label) tuples for the choices, or a callable
                 that returns such a list
        thumbnails: Dictionary mapping choice values to thumbnail URLs/paths,
                   or a callable that returns such a dictionary
        thumbnail_templates: Dictionary mapping choice values to either:
                            - A string (template path), or
                            - A dict with 'template' (path) and 'context' (dict) keys
                            Can also be a callable that returns such a dictionary
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
        self, choices=None, thumbnails=None, thumbnail_templates=None, **kwargs
    ):
        # Store the original choices, thumbnails, and thumbnail_templates (may be callable)
        self._choices_source = choices
        self._thumbnails_source = thumbnails
        self._thumbnail_templates_source = thumbnail_templates

        # For initialization, we need to resolve callables to get actual choices
        # This is needed for the parent ChoiceBlock's validation
        resolved_choices = self._resolve_callable(choices)

        # Don't pass widget in kwargs yet - we'll override get_form_state
        super().__init__(choices=resolved_choices, **kwargs)

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

    def get_form_state(self, value):
        """
        Override to ensure we have fresh choices and thumbnails when rendering the form.
        This is called when the block is rendered in the admin interface.
        """
        # Resolve choices, thumbnails, and thumbnail_templates at render time
        resolved_choices = self._resolve_callable(self._choices_source)
        resolved_thumbnails = self._resolve_callable(self._thumbnails_source) or {}
        resolved_thumbnail_templates = (
            self._resolve_callable(self._thumbnail_templates_source) or {}
        )

        # Update the field's choices if they've changed
        if resolved_choices is not None:
            self.field.choices = resolved_choices
            self.field.widget.choices = resolved_choices

        # Update the thumbnail mapping in the widget
        if hasattr(self.field.widget, "thumbnail_mapping"):
            self.field.widget.thumbnail_mapping = resolved_thumbnails

        # Update the thumbnail template mapping in the widget
        if hasattr(self.field.widget, "thumbnail_template_mapping"):
            self.field.widget.thumbnail_template_mapping = resolved_thumbnail_templates

        return super().get_form_state(value)

    def get_field(self, **kwargs):
        """
        Override get_field to create widget with current thumbnails.
        This is called by the parent ChoiceBlock during initialization.
        """
        # Resolve thumbnails and thumbnail_templates at field creation time
        resolved_thumbnails = self._resolve_callable(self._thumbnails_source) or {}
        resolved_thumbnail_templates = (
            self._resolve_callable(self._thumbnail_templates_source) or {}
        )

        # Create the custom widget
        widget = ThumbnailRadioSelect(
            thumbnail_mapping=resolved_thumbnails,
            thumbnail_template_mapping=resolved_thumbnail_templates,
        )

        # Pass the widget to parent's get_field
        kwargs["widget"] = widget

        return super().get_field(**kwargs)
