"""
Tests for ThumbnailChoiceBlock.
"""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.test import TestCase, override_settings

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
                    <label class="thumbnail-radio-option" data-label="---" data-depth="0">
                        <input type="radio" name="test_field" value="">
                        <span class="thumbnail-wrapper">
                            <span class="thumbnail-placeholder"></span>
                        </span>
                        <span class="thumbnail-label">---</span>
                    </label>
                    <label class="thumbnail-radio-option selected" data-label="option a" data-depth="0">
                        <input type="radio" name="test_field" value="a" checked>
                        <span class="thumbnail-wrapper">
                            <img src="/test/a.png" alt="Option A" class="thumbnail-image">
                        </span>
                        <span class="thumbnail-label">Option A</span>
                    </label>
                    <label class="thumbnail-radio-option" data-label="option b" data-depth="0">
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


class TestThumbnailChoiceBlockDirectoryMode(TestCase):
    """Tests for ThumbnailChoiceBlock with thumbnail_directory parameter."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.icons_dir = Path(self.tmp_dir) / "icons"
        self.icons_dir.mkdir()
        ThumbnailChoiceBlock._scan_cache.clear()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)
        ThumbnailChoiceBlock._scan_cache.clear()

    def _make_block(self, directory="icons", **kwargs):
        """Create a block with _find_static_directory patched to return self.icons_dir."""
        with patch.object(
            ThumbnailChoiceBlock,
            "_find_static_directory",
            return_value=self.icons_dir,
        ):
            block = ThumbnailChoiceBlock(
                thumbnail_directory=directory, thumbnail_size=40, **kwargs
            )
        return block

    # --- scanning ---

    def test_scans_flat_directory(self):
        """Icons in a directory become choices for the block."""
        (self.icons_dir / "sun.svg").write_text("<svg/>")
        (self.icons_dir / "moon.svg").write_text("<svg/>")

        block = self._make_block()
        choices = list(block.field.choices)
        values = [v for v, _ in choices]

        assert "sun" in values
        assert "moon" in values
        assert "sun" in block.field.widget.thumbnail_mapping
        assert "moon" in block.field.widget.thumbnail_mapping

    def test_scans_nested_directories(self):
        """Icons in a subdirectory become choices for the block, displayed under a heading."""
        arrows = self.icons_dir / "arrows"
        arrows.mkdir()
        (arrows / "left.svg").write_text("<svg/>")
        (arrows / "right.svg").write_text("<svg/>")

        block = self._make_block()
        tree = block.field.widget._tree_items

        types = [item["type"] for item in tree]

        # Assert that the items have a heading and 2 options.
        assert "heading" in types
        assert ["heading", "option", "option"] == types

        # Assert that the heading is "Arrows".
        heading = next(item for item in tree if item["type"] == "heading")
        assert heading["label"] == "Arrows"
        assert heading["depth"] == 0

        # Assert that the optionss are the 2 SVGs created in this test.
        option_values = [item["value"] for item in tree if item["type"] == "option"]
        assert ["arrows/left", "arrows/right"] == option_values

    def test_value_is_relative_path_without_extension(self):
        arrows = self.icons_dir / "arrows"
        arrows.mkdir()
        (arrows / "left_arrow.svg").write_text("<svg/>")

        block = self._make_block()
        values = [v for v, _ in block.field.choices]
        assert "arrows/left_arrow" in values

    def test_thumbnail_url_uses_static_url(self):
        (self.icons_dir / "sun.svg").write_text("<svg/>")

        block = self._make_block()
        assert block.field.widget.thumbnail_mapping["sun"] == "/static/icons/sun.svg"

    def test_thumbnail_url_nested(self):
        arrows = self.icons_dir / "arrows"
        arrows.mkdir()
        (arrows / "left.svg").write_text("<svg/>")

        block = self._make_block()
        assert (
            block.field.widget.thumbnail_mapping["arrows/left"]
            == "/static/icons/arrows/left.svg"
        )

    # --- label and sort ---

    def test_default_label_fn_title_cases(self):
        (self.icons_dir / "left_arrow.svg").write_text("<svg/>")

        block = self._make_block()
        labels = {value: label for value, label in block.field.choices}
        assert labels.get("left_arrow") == "Left Arrow"

    def test_default_sort_key_alphabetical(self):
        (self.icons_dir / "cherry.svg").write_text("<svg/>")
        (self.icons_dir / "apple.svg").write_text("<svg/>")
        (self.icons_dir / "banana.svg").write_text("<svg/>")

        block = self._make_block()
        # Choices may start with blank; strip it and check order
        values = [v for v, _ in block.field.choices if v]
        assert values == ["apple", "banana", "cherry"]

    def test_custom_label_fn(self):
        (self.icons_dir / "star.svg").write_text("<svg/>")
        arrows = self.icons_dir / "arrows"
        arrows.mkdir()
        (arrows / "left.svg").write_text("<svg/>")

        block = self._make_block(thumbnail_directory_label_fn=lambda stem: stem.upper())

        labels = {value: label for value, label in block.field.choices if value}
        assert labels["star"] == "STAR"
        assert labels["arrows/left"] == "LEFT"

        # Heading label also uses label_fn
        headings = [
            item for item in block.field.widget._tree_items if item["type"] == "heading"
        ]
        assert any(h["label"] == "ARROWS" for h in headings)

    def test_custom_sort_key(self):
        # reverse-alphabetical sort key
        (self.icons_dir / "apple.svg").write_text("<svg/>")
        (self.icons_dir / "banana.svg").write_text("<svg/>")
        (self.icons_dir / "cherry.svg").write_text("<svg/>")

        block = self._make_block(
            thumbnail_directory_sort_key=lambda p: [-ord(c) for c in p.name]
        )
        values = [v for v, _ in block.field.choices if v]
        assert values == ["cherry", "banana", "apple"]

    # --- mutual exclusivity ---

    def test_mutually_exclusive_with_choices(self):
        """A ThumbnailChoiceBlock may not define thumbnail_directory and choices."""
        with self.assertRaises(ValueError):
            ThumbnailChoiceBlock(
                thumbnail_directory="icons",
                choices=[("a", "A")],
                thumbnail_size=40,
            )

    def test_mutually_exclusive_with_thumbnails(self):
        """A ThumbnailChoiceBlock may not define thumbnail_directory and thumbnails."""
        with self.assertRaises(ValueError):
            ThumbnailChoiceBlock(
                thumbnail_directory="icons",
                thumbnails={"a": "/a.svg"},
                thumbnail_size=40,
            )

    def test_mutually_exclusive_with_thumbnail_templates(self):
        """A ThumbnailChoiceBlock may not define thumbnail_directory and thumbnail_templates."""
        with self.assertRaises(ValueError):
            ThumbnailChoiceBlock(
                thumbnail_directory="icons",
                thumbnail_templates={"a": "icon.html"},
                thumbnail_size=40,
            )

    # --- auto_reload ---

    def test_auto_reload_false_caches_scan(self):
        (self.icons_dir / "sun.svg").write_text("<svg/>")

        scan_calls = []
        original_scan = ThumbnailChoiceBlock._scan_directory

        def counting_scan(self_inner):
            result = original_scan(self_inner)
            scan_calls.append(1)
            return result

        with patch.object(
            ThumbnailChoiceBlock, "_find_static_directory", return_value=self.icons_dir
        ):
            with patch.object(ThumbnailChoiceBlock, "_scan_directory", counting_scan):
                block1 = ThumbnailChoiceBlock(
                    thumbnail_directory="icons",
                    thumbnail_size=40,
                    thumbnail_directory_auto_reload=False,
                )
                block1.get_form_state("")
                block2 = ThumbnailChoiceBlock(
                    thumbnail_directory="icons",
                    thumbnail_size=40,
                    thumbnail_directory_auto_reload=False,
                )
                block2.get_form_state("")

        assert len(scan_calls) == 1

    def test_auto_reload_true_rescans_on_render(self):
        (self.icons_dir / "sun.svg").write_text("<svg/>")

        scan_calls = []
        original_scan = ThumbnailChoiceBlock._scan_directory

        def counting_scan(self_inner):
            result = original_scan(self_inner)
            scan_calls.append(1)
            return result

        with patch.object(
            ThumbnailChoiceBlock, "_find_static_directory", return_value=self.icons_dir
        ):
            with patch.object(ThumbnailChoiceBlock, "_scan_directory", counting_scan):
                block = ThumbnailChoiceBlock(
                    thumbnail_directory="icons",
                    thumbnail_size=40,
                    thumbnail_directory_auto_reload=True,
                )

                # Add a new file before the rescan
                (self.icons_dir / "moon.svg").write_text("<svg/>")

                block.get_form_state("")

        assert len(scan_calls) == 2

        # Widget should be updated with the new file
        option_values = [
            item["value"]
            for item in block.field.widget._tree_items
            if item["type"] == "option"
        ]
        assert "moon" in option_values
        assert "moon" in block.field.widget.thumbnail_mapping

        # Blank choice present since required=False (default)
        assert block.field.widget.choices[0] == ("", "---")

    # --- filtering ---

    def test_skips_hidden_files_and_dirs(self):
        (self.icons_dir / "sun.svg").write_text("<svg/>")
        (self.icons_dir / ".hidden.svg").write_text("<svg/>")
        hidden_dir = self.icons_dir / ".hidden"
        hidden_dir.mkdir()
        (hidden_dir / "visible.svg").write_text("<svg/>")

        block = self._make_block()
        values = [v for v, _ in block.field.choices if v]
        assert values == ["sun"]

    def test_skips_non_image_extensions(self):
        (self.icons_dir / "sun.svg").write_text("<svg/>")
        (self.icons_dir / "readme.txt").write_text("text")
        (self.icons_dir / "data.json").write_text("{}")
        (self.icons_dir / "script.py").write_text("")

        block = self._make_block()
        values = [v for v, _ in block.field.choices if v]
        assert values == ["sun"]

    def test_empty_subdirectory_emits_no_heading(self):
        (self.icons_dir / "sun.svg").write_text("<svg/>")
        empty_dir = self.icons_dir / "empty"
        empty_dir.mkdir()
        # Only non-image files inside
        (empty_dir / "readme.txt").write_text("text")

        block = self._make_block()
        headings = [
            item for item in block.field.widget._tree_items if item["type"] == "heading"
        ]
        heading_labels = [h["label"] for h in headings]
        assert "Empty" not in heading_labels

    # --- blank choice ---

    def test_blank_choice_added_when_not_required(self):
        """When the field is not required, a blank choice is automatically added."""
        (self.icons_dir / "sun.svg").write_text("<svg/>")

        block = self._make_block(required=False)
        choices = list(block.field.choices)
        assert choices[0] == ("", "---")

    def test_required_true_no_blank_choice(self):
        """When the field is required, a blank choice is NOT automatically added."""
        (self.icons_dir / "sun.svg").write_text("<svg/>")

        block = self._make_block(required=True)
        choices = list(block.field.choices)
        assert ("", "---") not in choices
        assert choices[0][0] == "sun"

    # --- finder discovery ---

    def test_finds_directory_via_staticfiles_finders(self):
        (self.icons_dir / "sun.svg").write_text("<svg/>")

        # Simulate AppDirectoriesFinder: has 'storages' with a storage whose location
        # is the parent of the thumbnail_directory.
        from unittest.mock import MagicMock

        mock_storage = MagicMock()
        mock_storage.location = str(self.tmp_dir)
        mock_finder = MagicMock()
        mock_finder.storages = {"app": mock_storage}
        mock_finder.locations = []

        with patch(
            "django.contrib.staticfiles.finders.get_finders", return_value=[mock_finder]
        ):
            with override_settings(STATIC_ROOT="/nonexistent"):
                block = ThumbnailChoiceBlock(
                    thumbnail_directory="icons", thumbnail_size=40
                )

        values = [v for v, _ in block.field.choices if v]
        assert "sun" in values

    def test_directory_not_found_raises(self):
        with patch("django.contrib.staticfiles.finders.get_finders", return_value=[]):
            with override_settings(STATIC_ROOT="/nonexistent"):
                with self.assertRaises(ImproperlyConfigured):
                    ThumbnailChoiceBlock(thumbnail_directory="icons", thumbnail_size=40)

    # --- widget integration ---

    def test_tree_items_on_widget(self):
        (self.icons_dir / "sun.svg").write_text("<svg/>")
        arrows = self.icons_dir / "arrows"
        arrows.mkdir()
        (arrows / "left.svg").write_text("<svg/>")

        block = self._make_block()
        tree = block.field.widget._tree_items

        assert tree is not None
        assert any(item["type"] == "heading" for item in tree)
        assert any(item["type"] == "option" and item["value"] == "sun" for item in tree)
        assert any(
            item["type"] == "option" and item["value"] == "arrows/left" for item in tree
        )
