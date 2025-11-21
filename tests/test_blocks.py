"""
Tests for ThumbnailChoiceBlock.
"""

from django.test import TestCase

from wagtail_thumbnail_choice_block import ThumbnailChoiceBlock
from wagtail_thumbnail_choice_block.widgets import ThumbnailRadioSelect


class TestThumbnailChoiceBlock(TestCase):
    """Test the ThumbnailChoiceBlock."""

    def test_block_initialization(self):
        """Test that block initializes correctly."""
        block = ThumbnailChoiceBlock(
            choices=[("a", "Option A"), ("b", "Option B")],
            thumbnails={"a": "/test/a.png", "b": "/test/b.png"},
        )

        assert block._thumbnails_source == {"a": "/test/a.png", "b": "/test/b.png"}

    def test_block_initialization_without_thumbnails(self):
        """Test that block works without thumbnails."""
        block = ThumbnailChoiceBlock(choices=[("a", "Option A"), ("b", "Option B")])

        assert block._thumbnails_source is None

    def test_block_uses_custom_widget(self):
        """Test that block uses ThumbnailRadioSelect widget."""
        block = ThumbnailChoiceBlock(
            choices=[("a", "Option A")], thumbnails={"a": "/test/a.png"}
        )

        field = block.field

        assert isinstance(field.widget, ThumbnailRadioSelect)
        assert field.widget.thumbnail_mapping == {"a": "/test/a.png"}

    def test_block_field_choices(self):
        """Test that block field has correct choices."""
        block = ThumbnailChoiceBlock(
            choices=[("a", "Option A"), ("b", "Option B")],
            thumbnails={"a": "/test/a.png", "b": "/test/b.png"},
        )

        field = block.field
        choices = list(field.choices)

        assert ("a", "Option A") in choices
        assert ("b", "Option B") in choices

    def test_block_with_default_value(self):
        """Test that block respects default value."""
        block = ThumbnailChoiceBlock(
            choices=[("a", "Option A"), ("b", "Option B")],
            thumbnails={"a": "/test/a.png", "b": "/test/b.png"},
            default="b",
        )

        assert block.get_default() == "b"

    def test_block_clean_valid_value(self):
        """Test that block cleans valid values correctly."""
        block = ThumbnailChoiceBlock(
            choices=[("a", "Option A"), ("b", "Option B")],
            thumbnails={"a": "/test/a.png", "b": "/test/b.png"},
        )

        assert block.clean("a") == "a"

    def test_block_value_from_form(self):
        """Test that block can extract value from form data."""
        block = ThumbnailChoiceBlock(
            choices=[("a", "Option A"), ("b", "Option B")],
            thumbnails={"a": "/test/a.png", "b": "/test/b.png"},
        )

        assert block.value_from_datadict({"test": "b"}, {}, "test") == "b"

    def test_block_render_form(self):
        """Test that block renders form HTML with thumbnails."""
        block = ThumbnailChoiceBlock(
            choices=[("a", "Option A"), ("b", "Option B")],
            thumbnails={"a": "/test/a.png", "b": "/test/b.png"},
        )

        # Render the field widget directly (this is what the block uses internally)
        field = block.field
        html = str(field.widget.render("test_field", "a"))

        expected_html = """
            <div class="thumbnail-radio-select">
                <label class="thumbnail-radio-option">
                    <input type="radio" name="test_field" value="">
                    <span class="thumbnail-wrapper">
                        <span class="thumbnail-placeholder"></span>
                    </span>
                    <span class="thumbnail-label">---------</span>
                </label>
                <label class="thumbnail-radio-option selected">
                    <input type="radio" name="test_field" value="a" checked>
                    <span class="thumbnail-wrapper">
                        <img src="/test/a.png" alt="Option A" class="thumbnail-image">
                    </span>
                    <span class="thumbnail-label">Option A</span>
                </label>
                <label class="thumbnail-radio-option">
                    <input type="radio" name="test_field" value="b">
                    <span class="thumbnail-wrapper">
                        <img src="/test/b.png" alt="Option B" class="thumbnail-image">
                    </span>
                    <span class="thumbnail-label">Option B</span>
                </label>
            </div>
        """
        assert expected_html.replace(" ", "").replace("\n", "") == html.replace(
            " ", ""
        ).replace("\n", "")

    def test_block_with_callable_choices(self):
        """Test that block works with callable choices."""

        def get_choices():
            return [("x", "Option X"), ("y", "Option Y"), ("z", "Option Z")]

        block = ThumbnailChoiceBlock(
            choices=get_choices, thumbnails={"x": "/test/x.png"}
        )

        # Check that choices are resolved
        field = block.field
        choices = list(field.choices)

        assert ("x", "Option X") in choices
        assert ("y", "Option Y") in choices
        assert ("z", "Option Z") in choices

    def test_block_with_callable_thumbnails(self):
        """Test that block works with callable thumbnails."""

        def get_thumbnails():
            return {"a": "/dynamic/a.png", "b": "/dynamic/b.png"}

        block = ThumbnailChoiceBlock(
            choices=[("a", "Option A"), ("b", "Option B")], thumbnails=get_thumbnails
        )

        # Check that thumbnails are resolved
        field = block.field
        assert field.widget.thumbnail_mapping == {
            "a": "/dynamic/a.png",
            "b": "/dynamic/b.png",
        }

    def test_block_with_both_callable(self):
        """Test that block works with both choices and thumbnails as callables."""

        def get_choices():
            return [("m", "Option M"), ("n", "Option N")]

        def get_thumbnails():
            return {"m": "/dynamic/m.png", "n": "/dynamic/n.png"}

        block = ThumbnailChoiceBlock(choices=get_choices, thumbnails=get_thumbnails)

        # Check that both are resolved
        field = block.field
        choices = list(field.choices)

        assert ("m", "Option M") in choices
        assert ("n", "Option N") in choices
        assert field.widget.thumbnail_mapping == {
            "m": "/dynamic/m.png",
            "n": "/dynamic/n.png",
        }

    def test_callable_choices_evaluated_at_render_time(self):
        """Test that callable choices are evaluated at render time."""
        # Simulate a dynamic data source
        test_data = {"choices": [("a", "Initial A")]}

        def get_choices():
            return test_data["choices"]

        block = ThumbnailChoiceBlock(choices=get_choices, thumbnails={})

        # Initial render
        field = block.field
        choices = list(field.choices)
        assert ("a", "Initial A") in choices

        # Change the data source
        test_data["choices"] = [("b", "Updated B"), ("c", "Updated C")]

        # Get form state (simulating a new render)
        block.get_form_state("b")

        # Check that choices have been updated
        field = block.field
        choices = list(field.choices)
        assert ("b", "Updated B") in choices
        assert ("c", "Updated C") in choices

    def test_block_initialization_with_thumbnail_templates(self):
        """Test that block initializes correctly with thumbnail templates."""
        thumbnail_templates = {
            "star": "components/icon.html",
            "check": {"template": "components/icon.html", "context": {"icon": "check"}},
        }
        block = ThumbnailChoiceBlock(
            choices=[("star", "Star"), ("check", "Check")],
            thumbnail_templates=thumbnail_templates,
        )

        assert block._thumbnail_templates_source == thumbnail_templates

    def test_block_initialization_without_thumbnail_templates(self):
        """Test that block works without thumbnail templates."""
        block = ThumbnailChoiceBlock(choices=[("a", "Option A"), ("b", "Option B")])

        assert block._thumbnail_templates_source is None

    def test_block_uses_widget_with_thumbnail_templates(self):
        """Test that block passes thumbnail templates to widget."""
        thumbnail_templates = {"a": "components/icon.html"}
        block = ThumbnailChoiceBlock(
            choices=[("a", "Option A")], thumbnail_templates=thumbnail_templates
        )

        field = block.field

        assert isinstance(field.widget, ThumbnailRadioSelect)
        assert field.widget.thumbnail_template_mapping == thumbnail_templates

    def test_block_with_both_thumbnails_and_templates(self):
        """Test that block can use both thumbnails and thumbnail templates."""
        block = ThumbnailChoiceBlock(
            choices=[("a", "Option A"), ("b", "Option B")],
            thumbnails={"a": "/test/a.png"},
            thumbnail_templates={"b": "components/icon.html"},
        )

        field = block.field
        assert field.widget.thumbnail_mapping == {"a": "/test/a.png"}
        assert field.widget.thumbnail_template_mapping == {"b": "components/icon.html"}

    def test_block_with_callable_thumbnail_templates(self):
        """Test that block works with callable thumbnail templates."""

        def get_templates():
            return {
                "star": "components/star.html",
                "check": {
                    "template": "components/check.html",
                    "context": {"class": "icon-check"},
                },
            }

        block = ThumbnailChoiceBlock(
            choices=[("star", "Star"), ("check", "Check")],
            thumbnail_templates=get_templates,
        )

        # Check that thumbnail templates are resolved
        field = block.field
        assert field.widget.thumbnail_template_mapping == {
            "star": "components/star.html",
            "check": {
                "template": "components/check.html",
                "context": {"class": "icon-check"},
            },
        }

    def test_callable_thumbnail_templates_evaluated_at_render_time(self):
        """Test that callable thumbnail templates are evaluated at render time."""
        # Simulate a dynamic data source
        test_data = {
            "templates": {"a": "components/initial.html"},
        }

        def get_templates():
            return test_data["templates"]

        block = ThumbnailChoiceBlock(
            choices=[("a", "Option A"), ("b", "Option B")],
            thumbnail_templates=get_templates,
        )

        # Initial render
        field = block.field
        assert field.widget.thumbnail_template_mapping == {
            "a": "components/initial.html",
        }

        # Change the data source
        test_data["templates"] = {
            "a": "components/updated.html",
            "b": "components/new.html",
        }

        # Get form state (simulating a new render)
        block.get_form_state("a")

        # Check that templates have been updated
        field = block.field
        assert field.widget.thumbnail_template_mapping == {
            "a": "components/updated.html",
            "b": "components/new.html",
        }
