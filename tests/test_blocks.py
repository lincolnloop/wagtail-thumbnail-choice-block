"""
Tests for ThumbnailChoiceBlock.
"""

from django.core.exceptions import ValidationError
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
        assert block._thumbnail_size == 40  # Default size

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
            <div class="thumbnail-radio-select" style="--thumbnail-size: 40px;">
                <div class="thumbnail-filter-wrapper">
                    <div class="thumbnail-selected-preview"></div>
                    <input type="text" class="thumbnail-filter-input" placeholder="Select an option..." autocomplete="off" readonly>
                </div>
                <div class="thumbnail-dropdown">
                    <label class="thumbnail-radio-option" data-label="---">
                        <input type="radio" name="test_field" value="">
                        <span class="thumbnail-wrapper">
                            <span class="thumbnail-placeholder"></span>
                        </span>
                        <span class="thumbnail-label">---</span>
                    </label>
                    <label class="thumbnail-radio-option selected" data-label="option a">
                        <input type="radio" name="test_field" value="a" checked>
                        <span class="thumbnail-wrapper">
                            <img src="/test/a.png" alt="Option A" class="thumbnail-image">
                        </span>
                        <span class="thumbnail-label">Option A</span>
                    </label>
                    <label class="thumbnail-radio-option" data-label="option b">
                        <input type="radio" name="test_field" value="b">
                        <span class="thumbnail-wrapper">
                            <img src="/test/b.png" alt="Option B" class="thumbnail-image">
                        </span>
                        <span class="thumbnail-label">Option B</span>
                    </label>
                    <div class="thumbnail-no-results" style="display: none;">No matching options found.</div>
                </div>
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

    def test_block_initialization_with_custom_thumbnail_size(self):
        """Test that block initializes with custom thumbnail size."""
        block = ThumbnailChoiceBlock(
            choices=[("a", "Option A"), ("b", "Option B")],
            thumbnails={"a": "/test/a.png", "b": "/test/b.png"},
            thumbnail_size=60,
        )

        assert block._thumbnail_size == 60

    def test_block_widget_has_custom_thumbnail_size(self):
        """Test that block's widget receives the custom thumbnail size."""
        block = ThumbnailChoiceBlock(
            choices=[("a", "Option A"), ("b", "Option B")],
            thumbnails={"a": "/test/a.png", "b": "/test/b.png"},
            thumbnail_size=80,
        )

        field = block.field
        assert isinstance(field.widget, ThumbnailRadioSelect)
        assert field.widget.thumbnail_size == 80

    def test_block_renders_with_custom_thumbnail_size(self):
        """Test that block renders with custom thumbnail size CSS variable."""
        block = ThumbnailChoiceBlock(
            choices=[("a", "Option A")],
            thumbnails={"a": "/test/a.png"},
            thumbnail_size=100,
        )

        field = block.field
        html = str(field.widget.render("test_field", "a"))

        # Verify the CSS variable is present in the rendered HTML
        assert 'style="--thumbnail-size: 100px;"' in html

    def test_block_default_not_required(self):
        """Test that block is not required by default."""
        choices_value = [("a", "Option A"), ("b", "Option B")]
        block = ThumbnailChoiceBlock(
            choices=choices_value,
            thumbnails={"a": "/test/a.png", "b": "/test/b.png"},
        )

        # Check that required is False by default
        assert block._required is False
        assert block.field.required is False

    def test_block_with_required_true(self):
        """Test that block can be explicitly set to required."""
        block = ThumbnailChoiceBlock(
            choices=[("a", "Option A"), ("b", "Option B")],
            thumbnails={"a": "/test/a.png", "b": "/test/b.png"},
            required=True,
        )

        # Check that required is True
        assert block._required is True
        assert block.field.required is True

    def test_block_adds_blank_choice_when_explicitly_not_required(self):
        """Test that block adds a blank choice when not required."""
        block = ThumbnailChoiceBlock(
            choices=[("a", "Option A"), ("b", "Option B")],
            thumbnails={"a": "/test/a.png", "b": "/test/b.png"},
            required=False,
        )

        field = block.field
        choices = list(field.choices)

        # Check that blank choice is first
        assert choices[0] == ("", "---")
        assert ("a", "Option A") in choices
        assert ("b", "Option B") in choices
        assert len(choices) == 3  # blank + 2 options

    def test_block_adds_blank_choice_when_implicitly_not_required(self):
        """Test that block adds a blank choice when not required."""
        block = ThumbnailChoiceBlock(
            choices=[("a", "Option A"), ("b", "Option B")],
            thumbnails={"a": "/test/a.png", "b": "/test/b.png"},
            # Note: we did not pass a required parameter.
        )

        field = block.field
        choices = list(field.choices)

        # Check that blank choice is first
        assert choices[0] == ("", "---")
        assert ("a", "Option A") in choices
        assert ("b", "Option B") in choices
        assert len(choices) == 3  # blank + 2 options

    def test_block_no_blank_choice_when_required(self):
        """Test that block does not add blank choice when required."""
        block = ThumbnailChoiceBlock(
            choices=[("a", "Option A"), ("b", "Option B")],
            thumbnails={"a": "/test/a.png", "b": "/test/b.png"},
            required=True,
        )

        field = block.field
        choices = list(field.choices)

        # Check that there's no blank choice
        assert ("", "---") not in choices
        assert ("a", "Option A") in choices
        assert ("b", "Option B") in choices
        assert len(choices) == 2  # Only the 2 options

    def test_block_blank_choice_with_callable_choices(self):
        """Test that blank choice is added correctly with callable choices."""

        def get_choices():
            return [("x", "Option X"), ("y", "Option Y")]

        block = ThumbnailChoiceBlock(
            choices=get_choices, thumbnails={"x": "/test/x.png"}, required=False
        )

        field = block.field
        choices = list(field.choices)

        # Check that blank choice is present
        assert choices[0] == ("", "---")  # First option is the blank option.
        assert ("x", "Option X") in choices
        assert ("y", "Option Y") in choices
        assert len(choices) == 3

    def test_block_accepts_empty_value_when_not_required(self):
        """Test that block accepts empty string value when not required."""
        block = ThumbnailChoiceBlock(
            choices=[("a", "Option A"), ("b", "Option B")],
            thumbnails={"a": "/test/a.png", "b": "/test/b.png"},
            required=False,
        )

        # Empty value should be valid for optional field
        assert block.clean("") == ""

    def test_block_rejects_empty_value_when_required(self):
        """Test that block rejects empty string value when required."""
        block = ThumbnailChoiceBlock(
            choices=[("a", "Option A"), ("b", "Option B")],
            thumbnails={"a": "/test/a.png", "b": "/test/b.png"},
            required=True,
        )

        # Empty value should raise ValidationError for required field
        with self.assertRaises(ValidationError):
            block.clean("")

    def test_block_does_not_duplicate_blank_choice(self):
        """Test that block doesn't add duplicate blank choice."""
        # Manually add blank choice to test data
        block = ThumbnailChoiceBlock(
            choices=[("", "Custom Empty"), ("a", "Option A")],
            thumbnails={"a": "/test/a.png"},
            required=False,
        )

        field = block.field
        choices = list(field.choices)

        # Should only have one blank choice (the original one, not added)
        blank_choices = [c for c in choices if c[0] == ""]
        assert len(blank_choices) == 1
        assert blank_choices[0] == ("", "Custom Empty")
