"""
Tests for ThumbnailRadioSelect widget.
"""

from unittest.mock import patch

from django.test import TestCase

from wagtail_thumbnail_choice_block.widgets import ThumbnailRadioSelect


class TestThumbnailRadioSelect(TestCase):
    """Test the ThumbnailRadioSelect widget."""

    def test_widget_initialization(self):
        """Test that widget initializes correctly."""
        widget = ThumbnailRadioSelect(
            choices=[("a", "Option A"), ("b", "Option B")],
            thumbnail_mapping={"a": "/test/a.png", "b": "/test/b.png"},
            thumbnail_size=40,
        )

        assert widget.thumbnail_mapping == {"a": "/test/a.png", "b": "/test/b.png"}
        assert list(widget.choices) == [("a", "Option A"), ("b", "Option B")]
        assert widget.thumbnail_size == 40

    def test_widget_initialization_without_thumbnails(self):
        """Test that widget works without thumbnail mapping."""
        widget = ThumbnailRadioSelect(
            choices=[("a", "Option A"), ("b", "Option B")], thumbnail_size=40
        )

        assert widget.thumbnail_mapping == {}
        assert list(widget.choices) == [("a", "Option A"), ("b", "Option B")]

    def test_create_option_adds_thumbnail_url(self):
        """Test that create_option adds thumbnail_url to option context."""
        widget = ThumbnailRadioSelect(
            choices=[("a", "Option A")],
            thumbnail_mapping={"a": "/test/a.png"},
            thumbnail_size=40,
        )

        option = widget.create_option("test", "a", "Option A", True, 0)

        assert option["thumbnail_url"] == "/test/a.png"
        assert option["value"] == "a"
        assert option["label"] == "Option A"

    def test_create_option_handles_missing_thumbnail(self):
        """Test that create_option handles missing thumbnails gracefully."""
        widget = ThumbnailRadioSelect(
            choices=[("a", "Option A")], thumbnail_mapping={}, thumbnail_size=40
        )

        option = widget.create_option("test", "a", "Option A", True, 0)

        assert option["thumbnail_url"] == ""

    def test_widget_renders_html(self):
        """Test that widget renders HTML with thumbnails."""
        widget = ThumbnailRadioSelect(
            choices=[("a", "Option A"), ("b", "Option B")],
            thumbnail_mapping={"a": "/test/a.png", "b": "/test/b.png"},
            thumbnail_size=40,
        )

        html = widget.render("test_field", "a", attrs={"id": "test-id"})

        expected_html = """
            <div id="test-id" class="thumbnail-radio-select" style="--thumbnail-size: 40px;">
                <div class="thumbnail-filter-wrapper">
                    <div class="thumbnail-selected-preview"></div>
                    <input type="text" class="thumbnail-filter-input" placeholder="Select an option..." autocomplete="off" readonly>
                </div>
                <div class="thumbnail-dropdown">
                    <label for="test-id_0" class="thumbnail-radio-option selected" data-label="option a">
                        <input type="radio" name="test_field" value="a" id="test-id_0" checked>
                        <span class="thumbnail-wrapper">
                            <img src="/test/a.png" alt="Option A" class="thumbnail-image">
                        </span>
                        <span class="thumbnail-label">Option A</span>
                    </label>
                    <label for="test-id_1" class="thumbnail-radio-option" data-label="option b">
                        <input type="radio" name="test_field" value="b" id="test-id_1">
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

    def test_widget_renders_selected_option(self):
        """Test that selected option has correct attributes."""
        widget = ThumbnailRadioSelect(
            choices=[("a", "Option A"), ("b", "Option B")],
            thumbnail_mapping={"a": "/test/a.png", "b": "/test/b.png"},
            thumbnail_size=40,
        )

        html = widget.render("test_field", "b", attrs={"id": "test-id"})

        # Option B should be checked
        assert "checked" in html
        assert "selected" in html  # CSS class
        # Verify dropdown structure is present
        assert "thumbnail-dropdown" in html
        assert "thumbnail-filter-input" in html

    def test_widget_template_name(self):
        """Test that widget uses correct template."""
        widget = ThumbnailRadioSelect(thumbnail_size=40)

        assert (
            widget.template_name
            == "wagtail_thumbnail_choice_block/widgets/thumbnail_radio_select.html"
        )

    def test_widget_requires_thumbnail_size(self):
        """Test that widget raises ValueError when thumbnail_size is not provided."""
        with self.assertRaises(ValueError) as context:
            ThumbnailRadioSelect(
                choices=[("a", "Option A"), ("b", "Option B")],
                thumbnail_mapping={"a": "/test/a.png", "b": "/test/b.png"},
                # No thumbnail_size provided
            )

        assert "thumbnail_size is required" in str(context.exception)

    def test_widget_initialization_with_custom_thumbnail_size(self):
        """Test that widget initializes with custom thumbnail size."""
        widget = ThumbnailRadioSelect(
            choices=[("a", "Option A"), ("b", "Option B")],
            thumbnail_mapping={"a": "/test/a.png", "b": "/test/b.png"},
            thumbnail_size=60,
        )

        assert widget.thumbnail_size == 60

    def test_widget_get_context_includes_thumbnail_size(self):
        """Test that get_context adds thumbnail_size to the context."""
        widget = ThumbnailRadioSelect(
            choices=[("a", "Option A")],
            thumbnail_mapping={"a": "/test/a.png"},
            thumbnail_size=50,
        )

        context = widget.get_context("test_field", "a", attrs={"id": "test-id"})

        assert "widget" in context
        assert context["widget"]["thumbnail_size"] == 50

    def test_widget_renders_with_css_variable(self):
        """Test that widget renders with CSS variable for thumbnail size."""
        widget = ThumbnailRadioSelect(
            choices=[("a", "Option A")],
            thumbnail_mapping={"a": "/test/a.png"},
            thumbnail_size=80,
        )

        html = widget.render("test_field", "a", attrs={"id": "test-id"})

        # Verify the CSS variable is present in the rendered HTML
        assert 'style="--thumbnail-size: 80px;"' in html

    def test_widget_initialization_with_thumbnail_templates(self):
        """Test that widget initializes correctly with thumbnail templates."""
        widget = ThumbnailRadioSelect(
            choices=[("star", "Star"), ("check", "Check")],
            thumbnail_template_mapping={
                "star": "components/star.html",
                "check": {
                    "template": "components/check.html",
                    "context": {"icon": "check"},
                },
            },
            thumbnail_size=40,
        )

        assert widget.thumbnail_template_mapping == {
            "star": "components/star.html",
            "check": {
                "template": "components/check.html",
                "context": {"icon": "check"},
            },
        }
        assert list(widget.choices) == [("star", "Star"), ("check", "Check")]

    def test_widget_initialization_without_thumbnail_templates(self):
        """Test that widget works without thumbnail template mapping."""
        widget = ThumbnailRadioSelect(
            choices=[("a", "Option A"), ("b", "Option B")], thumbnail_size=40
        )

        assert widget.thumbnail_template_mapping == {}
        assert list(widget.choices) == [("a", "Option A"), ("b", "Option B")]

    def test_create_option_adds_thumbnail_template_html_empty(self):
        """Test that create_option adds empty thumbnail_template_html when no template."""
        widget = ThumbnailRadioSelect(
            choices=[("a", "Option A")],
            thumbnail_template_mapping={},
            thumbnail_size=40,
        )

        option = widget.create_option("test", "a", "Option A", True, 0)

        assert option["thumbnail_template_html"] == ""
        assert option["value"] == "a"
        assert option["label"] == "Option A"

    @patch("wagtail_thumbnail_choice_block.widgets.render_to_string")
    def test_widget_renders_html_with_thumbnail_template_mapping_string(
        self, mock_render
    ):
        """Test that widget renders HTML with template path (string)."""
        # Mock render_to_string to return specific HTML
        mock_template_value = '<span class="icon-star">★</span>'
        mock_render.return_value = mock_template_value

        widget = ThumbnailRadioSelect(
            choices=[("star", "Star")],
            thumbnail_template_mapping={"star": "components/star.html"},
            thumbnail_size=100,
        )

        html = widget.render("test_field", "star", attrs={"id": "test-id"})

        # Verify render_to_string was called with correct arguments
        mock_render.assert_called_once_with(
            "components/star.html", {"value": "star", "label": "Star"}
        )

        # Verify the rendered HTML contains the mock_template_value.
        expected_html = f"""
            <div id="test-id" class="thumbnail-radio-select" style="--thumbnail-size: 100px;">
                <div class="thumbnail-filter-wrapper">
                    <div class="thumbnail-selected-preview"></div>
                    <input type="text" class="thumbnail-filter-input" placeholder="Select an option..." autocomplete="off" readonly>
                </div>
                <div class="thumbnail-dropdown">
                    <label for="test-id_0" class="thumbnail-radio-option selected" data-label="star">
                        <input type="radio" name="test_field" value="star" id="test-id_0" checked>
                        <span class="thumbnail-wrapper">
                            {mock_template_value}
                        </span>
                        <span class="thumbnail-label">Star</span>
                    </label>
                    <div class="thumbnail-no-results" style="display: none;">No matching options found.</div>
                </div>
            </div>
        """
        assert expected_html.replace(" ", "").replace("\n", "") == html.replace(
            " ", ""
        ).replace("\n", "")

    @patch("wagtail_thumbnail_choice_block.widgets.render_to_string")
    def test_widget_renders_html_with_thumbnail_template_mapping_dict(
        self, mock_render
    ):
        """Test that widget renders HTML with template dict (template + context)."""
        # Mock render_to_string to return specific HTML
        mock_template_value = '<span class="icon-check custom">✓</span>'
        mock_render.return_value = mock_template_value

        widget = ThumbnailRadioSelect(
            choices=[("check", "Check")],
            thumbnail_template_mapping={
                "check": {
                    "template": "components/check.html",
                    "context": {"icon": "check", "custom_class": "custom"},
                },
            },
            thumbnail_size=20,
        )

        html = widget.render("test_field", "check", attrs={"id": "test-id"})

        # Verify render_to_string was called with correct arguments
        # The context should include both the provided context and default value/label
        expected_context = {
            "icon": "check",
            "custom_class": "custom",
            "value": "check",
            "label": "Check",
        }
        mock_render.assert_called_once_with("components/check.html", expected_context)

        # Verify the rendered HTML contains the mock_template_value.
        expected_html = f"""
            <div id="test-id" class="thumbnail-radio-select" style="--thumbnail-size: 20px;">
                <div class="thumbnail-filter-wrapper">
                    <div class="thumbnail-selected-preview"></div>
                    <input type="text" class="thumbnail-filter-input" placeholder="Select an option..." autocomplete="off" readonly>
                </div>
                <div class="thumbnail-dropdown">
                    <label for="test-id_0" class="thumbnail-radio-option selected" data-label="check">
                        <input type="radio" name="test_field" value="check" id="test-id_0" checked>
                        <span class="thumbnail-wrapper">
                            {mock_template_value}
                        </span>
                        <span class="thumbnail-label">Check</span>
                    </label>
                    <div class="thumbnail-no-results" style="display: none;">No matching options found.</div>
                </div>
            </div>
        """
        assert expected_html.replace(" ", "").replace("\n", "") == html.replace(
            " ", ""
        ).replace("\n", "")

    @patch("wagtail_thumbnail_choice_block.widgets.render_to_string")
    def test_widget_template_takes_precedence_over_thumbnail(self, mock_render):
        """Test that template HTML takes precedence over thumbnail URL."""
        # Mock render_to_string to return specific HTML
        mock_render.return_value = '<span class="template-icon">T</span>'

        widget = ThumbnailRadioSelect(
            choices=[("option", "Option")],
            thumbnail_mapping={"option": "/test/image.png"},
            thumbnail_template_mapping={"option": "components/icon.html"},
            thumbnail_size=40,
        )

        html = widget.render("test_field", "option", attrs={"id": "test-id"})

        # Template should be used, not the image
        assert '<span class="template-icon">T</span>' in html
        # Image should not appear since template takes precedence
        assert "/test/image.png" not in html

    @patch("wagtail_thumbnail_choice_block.widgets.render_to_string")
    def test_create_option_with_template_rendering(self, mock_render):
        """Test that create_option properly renders templates for options."""
        # Mock render_to_string to return specific HTML
        mock_render.return_value = '<i class="icon-star"></i>'

        widget = ThumbnailRadioSelect(
            choices=[("star", "Star")],
            thumbnail_template_mapping={"star": "components/star.html"},
            thumbnail_size=40,
        )

        option = widget.create_option("test", "star", "Star", False, 0)

        # Verify the option has the rendered template HTML
        assert option["thumbnail_template_html"] == '<i class="icon-star"></i>'
        assert option["thumbnail_url"] == ""

        # Verify render_to_string was called
        mock_render.assert_called_once_with(
            "components/star.html", {"value": "star", "label": "Star"}
        )

    @patch("wagtail_thumbnail_choice_block.widgets.render_to_string")
    def test_create_option_handles_template_error_gracefully(self, mock_render):
        """If a template is not found, an empty value is rendered for the thumbnail."""
        # Mock render_to_string to raise an exception
        mock_render.side_effect = Exception("Template not found")

        widget = ThumbnailRadioSelect(
            choices=[("star", "Star")],
            thumbnail_template_mapping={"star": "components/missing.html"},
            thumbnail_size=50,
        )

        option = widget.create_option("test", "star", "Star", False, 0)

        # Should gracefully handle the error and return empty string
        assert option["thumbnail_template_html"] == ""
        assert option["thumbnail_url"] == ""
        html = widget.render("test_field", "option", attrs={"id": "test-id"})
        # Verify the rendered HTML contains the placeholder value (this is
        # <span class="thumbnail-placeholder"></span>).
        expected_html = """
            <div id="test-id" class="thumbnail-radio-select" style="--thumbnail-size: 50px;">
                <div class="thumbnail-filter-wrapper">
                    <div class="thumbnail-selected-preview"></div>
                    <input type="text" class="thumbnail-filter-input" placeholder="Select an option..." autocomplete="off" readonly>
                </div>
                <div class="thumbnail-dropdown">
                    <label for="test-id_0" class="thumbnail-radio-option" data-label="star">
                        <input type="radio" name="test_field" value="star" id="test-id_0">
                        <span class="thumbnail-wrapper">
                            <span class="thumbnail-placeholder"></span>
                        </span>
                        <span class="thumbnail-label">Star</span>
                    </label>
                    <div class="thumbnail-no-results" style="display: none;">No matching options found.</div>
                </div>
            </div>
        """
        assert expected_html.replace(" ", "").replace("\n", "") == html.replace(
            " ", ""
        ).replace("\n", "")
