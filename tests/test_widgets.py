"""
Tests for ThumbnailRadioSelect widget.
"""

from django.test import TestCase

from wagtail_thumbnail_choice_block.widgets import ThumbnailRadioSelect


class TestThumbnailRadioSelect(TestCase):
    """Test the ThumbnailRadioSelect widget."""

    def test_widget_initialization(self):
        """Test that widget initializes correctly."""
        widget = ThumbnailRadioSelect(
            choices=[("a", "Option A"), ("b", "Option B")],
            thumbnail_mapping={"a": "/test/a.png", "b": "/test/b.png"},
        )

        assert widget.thumbnail_mapping == {"a": "/test/a.png", "b": "/test/b.png"}
        assert list(widget.choices) == [("a", "Option A"), ("b", "Option B")]

    def test_widget_initialization_without_thumbnails(self):
        """Test that widget works without thumbnail mapping."""
        widget = ThumbnailRadioSelect(choices=[("a", "Option A"), ("b", "Option B")])

        assert widget.thumbnail_mapping == {}
        assert list(widget.choices) == [("a", "Option A"), ("b", "Option B")]

    def test_create_option_adds_thumbnail_url(self):
        """Test that create_option adds thumbnail_url to option context."""
        widget = ThumbnailRadioSelect(
            choices=[("a", "Option A")], thumbnail_mapping={"a": "/test/a.png"}
        )

        option = widget.create_option("test", "a", "Option A", True, 0)

        assert option["thumbnail_url"] == "/test/a.png"
        assert option["value"] == "a"
        assert option["label"] == "Option A"

    def test_create_option_handles_missing_thumbnail(self):
        """Test that create_option handles missing thumbnails gracefully."""
        widget = ThumbnailRadioSelect(choices=[("a", "Option A")], thumbnail_mapping={})

        option = widget.create_option("test", "a", "Option A", True, 0)

        assert option["thumbnail_url"] == ""

    def test_widget_renders_html(self):
        """Test that widget renders HTML with thumbnails."""
        widget = ThumbnailRadioSelect(
            choices=[("a", "Option A"), ("b", "Option B")],
            thumbnail_mapping={"a": "/test/a.png", "b": "/test/b.png"},
        )

        html = widget.render("test_field", "a", attrs={"id": "test-id"})

        expected_html = """
            <div id="test-id" class="thumbnail-radio-select">
                <label for="test-id_0" class="thumbnail-radio-option selected">
                    <input type="radio" name="test_field" value="a" id="test-id_0" checked>
                    <span class="thumbnail-wrapper">
                        <img src="/test/a.png" alt="Option A" class="thumbnail-image">
                    </span>
                    <span class="thumbnail-label">Option A</span>
                </label>
                <label for="test-id_1" class="thumbnail-radio-option">
                    <input type="radio" name="test_field" value="b" id="test-id_1">
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

    def test_widget_renders_selected_option(self):
        """Test that selected option has correct attributes."""
        widget = ThumbnailRadioSelect(
            choices=[("a", "Option A"), ("b", "Option B")],
            thumbnail_mapping={"a": "/test/a.png", "b": "/test/b.png"},
        )

        html = widget.render("test_field", "b", attrs={"id": "test-id"})

        # Option B should be checked
        assert "checked" in html
        assert "selected" in html  # CSS class

    def test_widget_template_name(self):
        """Test that widget uses correct template."""
        widget = ThumbnailRadioSelect()

        assert (
            widget.template_name
            == "wagtail_thumbnail_choice_block/widgets/thumbnail_radio_select.html"
        )
