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

        assert block.thumbnails == {"a": "/test/a.png", "b": "/test/b.png"}

    def test_block_initialization_without_thumbnails(self):
        """Test that block works without thumbnails."""
        block = ThumbnailChoiceBlock(choices=[("a", "Option A"), ("b", "Option B")])

        assert block.thumbnails == {}

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
