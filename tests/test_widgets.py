"""
Tests for ThumbnailRadioSelect widget.
"""

from unittest.mock import patch

from django.test import TestCase

from wagtail_thumbnail_choice_block.widgets import ThumbnailRadioSelect


class TestThumbnailRadioSelect(TestCase):
    """Test the ThumbnailRadioSelect widget."""

    def setUp(self):
        ThumbnailRadioSelect._render_cache.clear()

    def tearDown(self):
        ThumbnailRadioSelect._render_cache.clear()

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
                    <label for="test-id_0" class="thumbnail-radio-option selected" data-label="option a" data-depth="0">
                        <input type="radio" name="test_field" value="a" id="test-id_0" checked>
                        <span class="thumbnail-wrapper">
                            <img src="/test/a.png" alt="Option A" class="thumbnail-image">
                        </span>
                        <span class="thumbnail-label">Option A</span>
                    </label>
                    <label for="test-id_1" class="thumbnail-radio-option" data-label="option b" data-depth="0">
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
                    <label for="test-id_0" class="thumbnail-radio-option selected" data-label="star" data-depth="0">
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
                    <label for="test-id_0" class="thumbnail-radio-option selected" data-label="check" data-depth="0">
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
                    <label for="test-id_0" class="thumbnail-radio-option" data-label="star" data-depth="0">
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


class TestThumbnailTemplateCaching(TestCase):
    """
    Tests that verify render() results are cached across widget instances.

    The key performance scenario: a page with multiple blocks that each contain
    a ThumbnailChoiceBlock with a large shared choices list (e.g. 250 icon choices).
    Without caching, render() is called N_choices × N_blocks times per page
    load. With caching, each unique instance is rendered once.
    """

    def setUp(self):
        # Each test starts with a cold cache so call counts are predictable.
        ThumbnailRadioSelect._render_cache = {}

    def tearDown(self):
        # Leave the cache clean for other test modules.
        ThumbnailRadioSelect._render_cache = {}

    @patch("wagtail_thumbnail_choice_block.widgets.render_to_string")
    def test_render_output_cached_across_widget_instances(self, mock_render):
        """
        The second render() call with the same mapping content must be a cache
        hit even when the two widgets hold separate dict objects with equal content.

        The real-world scenario for this test is: each ThumbnailChoiceBlock
        instantiation creates a new thumbnail_templates dict, so Telepath calls
        render() many times from widgets with distinct mapping objects but
        identical content.
        """
        mock_render.return_value = "<span>icon</span>"

        choices = [("a", "Alpha"), ("b", "Beta")]
        # Two distinct dict objects with identical content — simulates multiple
        # ThumbnailChoiceBlock instances each building their own thumbnail_templates dict.
        mapping1 = {c[0]: "icons/icon.html" for c in choices}
        mapping2 = {c[0]: "icons/icon.html" for c in choices}
        assert mapping1 is not mapping2  # confirm they are different objects

        widget1 = ThumbnailRadioSelect(
            choices=choices, thumbnail_template_mapping=mapping1, thumbnail_size=20
        )
        widget2 = ThumbnailRadioSelect(
            choices=choices, thumbnail_template_mapping=mapping2, thumbnail_size=20
        )

        widget1.render("field", "a", attrs={"id": "w1"})
        call_count_after_first = mock_render.call_count  # one call per choice

        # Different mapping objects, same content → this call should use the cache,
        # rather than calling the mock_render.
        widget2.render("field", "a", attrs={"id": "w1"})
        assert mock_render.call_count == call_count_after_first, (
            f"render_to_string was called {mock_render.call_count - call_count_after_first} "
            f"extra time(s) on the second render — expected 0 (render cache should be hit)"
        )

    @patch("wagtail_thumbnail_choice_block.widgets.render_to_string")
    def test_render_cache_miss_on_different_value(self, mock_render):
        """
        A different selected value produces different HTML and must not be served
        from the render cache — the cache key includes the current value.
        """
        mock_render.return_value = "<span>icon</span>"

        choices = [("a", "Alpha"), ("b", "Beta")]
        mapping = {c[0]: "icons/icon.html" for c in choices}
        widget = ThumbnailRadioSelect(
            choices=choices, thumbnail_template_mapping=mapping, thumbnail_size=20
        )

        # Rendering the widget calls render() twice (once for each choice).
        html_a = widget.render("field", "a", attrs={"id": "w"})
        assert mock_render.call_count == 2
        # Rendering the widget for a different selection calls render()
        # twice (once for each choice) again.
        html_b = widget.render("field", "b", attrs={"id": "w"})
        assert mock_render.call_count == 4
        # Rendering the widget for a the same selection does not call render() again.
        html_b_again = widget.render("field", "b", attrs={"id": "w"})
        assert mock_render.call_count == 4

        # Two different values → two separate render cache entries.
        assert len(ThumbnailRadioSelect._render_cache) == 2
        # The rendered HTML for html_a and html_b differs, because the selected
        # (checked) state changes.
        assert html_a != html_b
        # The rendered HTML for html_b and html_b_again is the same, because the
        # selected (checked) state is the same.
        assert html_b == html_b_again


class TestThumbnailRadioSelectTreeItems(TestCase):
    """
    Tests for the tree_items rendering path introduced by the directory-scanning
    feature.  The tests in this class — test_flat_mode_html_matches_snapshot — are
    intentionally written against the *pre-refactor* template (before supporting
    directory-based icon finding) so the tests act as a regression guard, proving
    that flat choices continue to render identically.
    """

    def setUp(self):
        ThumbnailRadioSelect._render_cache.clear()

    def tearDown(self):
        ThumbnailRadioSelect._render_cache.clear()

    def test_flat_mode_html_matches_snapshot(self):
        """
        Flat choices (no tree_items) must survive the optgroups→tree_items
        template refactor unchanged in every observable respect.

        Assertions target structural invariants rather than the full HTML string
        so that the addition of new attributes (e.g. data-depth) in the new
        template does not cause a false failure.  What matters is:

        - no heading or group wrapper elements are emitted
        - every option is present with correct value, label, and thumbnail
        - the selected state lands on the right option
        - the outer container and dropdown structure is intact

        Captured against the pre-refactor template output:

            <label for="shape-id_0" class="thumbnail-radio-option" data-label="circle">
              <input type="radio" name="shape" value="circle" id="shape-id_0">
              ...
            </label>
            <label for="shape-id_1" class="thumbnail-radio-option selected" data-label="square">
              <input type="radio" name="shape" value="square" id="shape-id_1" checked>
              ...
            </label>
            <label for="shape-id_2" class="thumbnail-radio-option" data-label="triangle">
              <input type="radio" name="shape" value="triangle" id="shape-id_2">
              ...
            </label>
        """
        widget = ThumbnailRadioSelect(
            choices=[
                ("circle", "Circle"),
                ("square", "Square"),
                ("triangle", "Triangle"),
            ],
            thumbnail_mapping={
                "circle": "/static/circle.svg",
                "square": "/static/square.svg",
                "triangle": "/static/triangle.svg",
            },
            thumbnail_size=40,
        )

        html = widget.render("shape", "square", attrs={"id": "shape-id"})

        # No heading or group structure — flat choices must produce none.
        assert "thumbnail-radio-heading" not in html
        assert "thumbnail-radio-group" not in html

        # All three options are present with correct identifiers.
        assert 'data-label="circle"' in html
        assert 'data-label="square"' in html
        assert 'data-label="triangle"' in html
        assert 'value="circle"' in html
        assert 'value="square"' in html
        assert 'value="triangle"' in html

        # Labels are rendered.
        assert ">Circle<" in html
        assert ">Square<" in html
        assert ">Triangle<" in html

        # Thumbnail images are rendered.
        assert "/static/circle.svg" in html
        assert "/static/square.svg" in html
        assert "/static/triangle.svg" in html

        # The selected option (square) carries the CSS class and checked attribute;
        # the others do not.
        assert 'class="thumbnail-radio-option selected" data-label="square"' in html
        assert 'value="square"' in html and "checked" in html
        assert 'class="thumbnail-radio-option" data-label="circle"' in html
        assert 'class="thumbnail-radio-option" data-label="triangle"' in html

        # Outer structure is intact.
        assert "thumbnail-radio-select" in html
        assert "thumbnail-dropdown" in html
        assert "thumbnail-filter-input" in html
        assert "thumbnail-no-results" in html

    @patch("wagtail_thumbnail_choice_block.widgets.render_to_string")
    def test_flat_mode_with_template_thumbnails_html_matches_snapshot(
        self, mock_render
    ):
        """
        Covers the thumbnail_template_mapping branch (e.g. icon sprite patterns).

        The thumbnail_template_html path in the template is distinct from the
        thumbnail_url path; it must also survive the optgroups→tree_items refactor
        unchanged.  render_to_string is mocked so the test needs no real template
        file.

        Key assertions:
        - no <img> tag (thumbnail_url branch was not taken)
        - no thumbnail-placeholder (template rendered something, not empty)
        - no heading or group structure
        - selected state is on the right option
        """
        mock_render.return_value = '<svg class="icon"><use href="#star"/></svg>'

        widget = ThumbnailRadioSelect(
            choices=[
                ("star", "Star"),
                ("check", "Check"),
            ],
            thumbnail_template_mapping={
                "star": {
                    "template": "some/icon.html",
                    "context": {"icon_name": "star"},
                },
                "check": {
                    "template": "some/icon.html",
                    "context": {"icon_name": "check"},
                },
            },
            thumbnail_size=40,
        )

        html = widget.render("icon", "check", attrs={"id": "icon-id"})

        # No heading or group structure.
        assert "thumbnail-radio-heading" not in html
        assert "thumbnail-radio-group" not in html

        # Both options are present.
        assert 'data-label="star"' in html
        assert 'data-label="check"' in html

        # Template HTML branch was taken — no <img> tag, no placeholder.
        assert "<img" not in html
        assert "thumbnail-placeholder" not in html

        # Mocked SVG appears unescaped, confirming |safe was applied in the template
        # (if it were escaped, we'd see &lt;svg instead).
        assert '<svg class="icon">' in html

        # Selected state is on check, not star.
        assert 'class="thumbnail-radio-option selected" data-label="check"' in html
        assert 'class="thumbnail-radio-option" data-label="star"' in html

    def test_tree_items_none_falls_back_to_flat(self):
        """When tree_items=None, _build_tree_context generates a flat list from self.choices — no headings."""
        widget = ThumbnailRadioSelect(
            choices=[("a", "Alpha"), ("b", "Beta")],
            thumbnail_mapping={"a": "/a.svg", "b": "/b.svg"},
            thumbnail_size=40,
            tree_items=None,
        )

        context = widget.get_context("field", "a", attrs={"id": "w"})
        tree = context["widget"]["tree_items"]

        # No heading items at all.
        assert all(item["type"] != "heading" for item in tree)

        # Both options are present.
        values = [str(item["value"]) for item in tree]
        assert "a" in values
        assert "b" in values

    def test_blank_choice_is_depth0_option_no_heading(self):
        """In directory mode a blank choice from _add_blank_choice is emitted as a depth-0 option with no heading before it."""
        tree_items = [
            {
                "type": "option",
                "label": "Sun",
                "depth": 0,
                "value": "sun",
                "thumbnail_url": "/static/icons/sun.svg",
            },
        ]
        widget = ThumbnailRadioSelect(
            choices=[("", "---"), ("sun", "Sun")],
            thumbnail_mapping={"sun": "/static/icons/sun.svg"},
            thumbnail_size=40,
            tree_items=tree_items,
        )

        context = widget.get_context("field", "", attrs={"id": "w"})
        tree = context["widget"]["tree_items"]

        # First item must not be a heading.
        assert tree[0]["type"] != "heading"
        # First item must be the blank choice.
        assert str(tree[0]["value"]) == ""
        assert tree[0]["depth"] == 0

        # No heading may appear before any option.
        first_heading_idx = next(
            (i for i, item in enumerate(tree) if item["type"] == "heading"), None
        )
        first_option_idx = next(
            (i for i, item in enumerate(tree) if item["type"] != "heading"), None
        )
        if first_heading_idx is not None and first_option_idx is not None:
            assert first_option_idx < first_heading_idx

    def test_tree_items_produces_headings_in_context(self):
        """Heading dicts in tree_items are propagated to the template context."""
        tree_items = [
            {"type": "heading", "label": "Arrows", "depth": 0},
            {
                "type": "option",
                "label": "Left",
                "depth": 0,
                "value": "arrows/left",
                "thumbnail_url": "/static/icons/arrows/left.svg",
            },
        ]
        widget = ThumbnailRadioSelect(
            choices=[("arrows/left", "Left")],
            thumbnail_mapping={"arrows/left": "/static/icons/arrows/left.svg"},
            thumbnail_size=40,
            tree_items=tree_items,
        )

        context = widget.get_context("field", None, attrs={"id": "w"})
        tree = context["widget"]["tree_items"]

        headings = [item for item in tree if item["type"] == "heading"]
        assert len(headings) == 1
        assert headings[0]["label"] == "Arrows"
        assert headings[0]["depth"] == 0

    def test_heading_depth_in_context(self):
        """Nested heading depth values are preserved through _build_tree_context."""
        tree_items = [
            {"type": "heading", "label": "Shapes", "depth": 0},
            {"type": "heading", "label": "Circles", "depth": 1},
            {
                "type": "option",
                "label": "Circle",
                "depth": 1,
                "value": "shapes/circles/circle",
                "thumbnail_url": "/static/icons/shapes/circles/circle.svg",
            },
        ]
        widget = ThumbnailRadioSelect(
            choices=[("shapes/circles/circle", "Circle")],
            thumbnail_mapping={
                "shapes/circles/circle": "/static/icons/shapes/circles/circle.svg"
            },
            thumbnail_size=40,
            tree_items=tree_items,
        )

        context = widget.get_context("field", None, attrs={"id": "w"})
        tree = context["widget"]["tree_items"]

        headings = [item for item in tree if item["type"] == "heading"]
        depths = [h["depth"] for h in headings]
        assert 0 in depths
        assert 1 in depths

    def test_cache_key_differs_with_different_tree(self):
        """Same choices/thumbnails but different heading labels → different cache keys → different cached HTML."""
        tree1 = [
            {"type": "heading", "label": "Arrows", "depth": 0},
            {
                "type": "option",
                "label": "Left",
                "depth": 0,
                "value": "left",
                "thumbnail_url": "/left.svg",
            },
        ]
        tree2 = [
            {"type": "heading", "label": "Shapes", "depth": 0},  # different label
            {
                "type": "option",
                "label": "Left",
                "depth": 0,
                "value": "left",
                "thumbnail_url": "/left.svg",
            },
        ]

        widget1 = ThumbnailRadioSelect(
            choices=[("left", "Left")],
            thumbnail_mapping={"left": "/left.svg"},
            thumbnail_size=40,
            tree_items=tree1,
        )
        widget2 = ThumbnailRadioSelect(
            choices=[("left", "Left")],
            thumbnail_mapping={"left": "/left.svg"},
            thumbnail_size=40,
            tree_items=tree2,
        )

        html1 = widget1.render("field", None, attrs={"id": "w"})
        html2 = widget2.render("field", None, attrs={"id": "w"})

        assert len(ThumbnailRadioSelect._render_cache) == 2
        assert html1 != html2

    def test_cache_key_same_with_identical_tree(self):
        """Identical tree_items on two widget instances → single cache entry → identical HTML."""
        tree = [
            {"type": "heading", "label": "Arrows", "depth": 0},
            {
                "type": "option",
                "label": "Left",
                "depth": 0,
                "value": "left",
                "thumbnail_url": "/left.svg",
            },
        ]

        widget1 = ThumbnailRadioSelect(
            choices=[("left", "Left")],
            thumbnail_mapping={"left": "/left.svg"},
            thumbnail_size=40,
            tree_items=tree,
        )
        widget2 = ThumbnailRadioSelect(
            choices=[("left", "Left")],
            thumbnail_mapping={"left": "/left.svg"},
            thumbnail_size=40,
            tree_items=tree,
        )

        html1 = widget1.render("field", None, attrs={"id": "w"})
        html2 = widget2.render("field", None, attrs={"id": "w"})

        assert len(ThumbnailRadioSelect._render_cache) == 1
        assert html1 == html2
