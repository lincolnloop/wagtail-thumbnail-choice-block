"""
Automated accessibility tests using selenium-axe-python.

These tests use axe-core (via selenium-axe-python) to automatically detect
accessibility violations in the rendered widget.

To run these tests:
    pip install selenium selenium-axe-python
    pytest tests/test_accessibility_axe.py

Note: These tests require a web browser (Chrome/Firefox) to be available.
"""

import os

from django.test import LiveServerTestCase

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium_axe_python import Axe

from wagtail_thumbnail_choice_block.widgets import ThumbnailRadioSelect


@pytest.mark.accessibility
@pytest.mark.selenium
class TestAccessibilityWithAxe(LiveServerTestCase):
    """Test accessibility using axe-core via selenium."""

    @classmethod
    def setUpClass(cls):
        """Set up Selenium WebDriver for all tests."""
        super().setUpClass()

        # Configure Chrome to run in headless mode
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        """Clean up WebDriver."""
        cls.driver.quit()
        super().tearDownClass()

    def _render_widget_page(self, widget, name="test_field", value=None):
        """Helper to render a standalone HTML page with the widget."""
        html = widget.render(name, value, attrs={"id": "test-id"})

        # Create a complete HTML page with proper structure
        full_page = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Thumbnail Choice Widget Test</title>
            <style>
                {self._get_widget_css()}
            </style>
        </head>
        <body>
            <main>
                <form>
                    <fieldset>
                        <legend>Choose an option</legend>
                        {html}
                    </fieldset>
                </form>
            </main>
        </body>
        </html>
        """

        return full_page

    def _get_widget_css(self):
        """Get the widget CSS for rendering."""
        # Load the actual CSS file from the package
        css_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "wagtail_thumbnail_choice_block",
            "static",
            "wagtail_thumbnail_choice_block",
            "css",
            "thumbnail-choice-block.css",
        )
        with open(css_path, "r") as f:
            return f.read()

    def test_no_critical_violations(self):
        """Test that widget has no critical accessibility violations."""
        widget = ThumbnailRadioSelect(
            choices=[("a", "Option A"), ("b", "Option B")],
            thumbnail_mapping={
                "a": 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg"><rect fill="red"/></svg>',
                "b": 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg"><rect fill="blue"/></svg>',
            },
            thumbnail_size=40,
        )

        page_html = self._render_widget_page(widget, value="a")

        # Load the page
        self.driver.get(f"data:text/html;charset=utf-8,{page_html}")

        # Run axe accessibility tests
        axe = Axe(self.driver)
        axe.inject()
        results = axe.run()

        # Check for violations
        violations = results["violations"]

        # Assert no critical or serious violations
        critical_violations = [
            v for v in violations if v["impact"] in ("critical", "serious")
        ]

        if critical_violations:
            # Format violation details for debugging
            violation_details = "\n".join(
                [
                    f"- {v['id']}: {v['description']} (Impact: {v['impact']})\n  Help: {v['helpUrl']}\n  Affected elements: {len(v['nodes'])}"
                    for v in critical_violations
                ]
            )
            self.fail(
                f"Found {len(critical_violations)} critical accessibility violations:\n{violation_details}"
            )

    def test_wcag_aa_compliance(self):
        """Test that widget meets WCAG 2.1 Level AA standards."""
        widget = ThumbnailRadioSelect(
            choices=[("light", "Light Theme"), ("dark", "Dark Theme")],
            thumbnail_mapping={
                "light": 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg"><rect fill="white" stroke="black"/></svg>',
                "dark": 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg"><rect fill="black"/></svg>',
            },
            thumbnail_size=40,
        )

        page_html = self._render_widget_page(widget, value="light")
        self.driver.get(f"data:text/html;charset=utf-8,{page_html}")

        # Run axe with WCAG 2.1 Level AA rules
        axe = Axe(self.driver)
        axe.inject()
        results = axe.run(
            options={
                "runOnly": {
                    "type": "tag",
                    "values": ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"],
                }
            }
        )

        violations = results["violations"]

        if violations:
            violation_summary = "\n".join(
                [f"- {v['id']}: {v['description']}" for v in violations]
            )
            self.fail(f"WCAG 2.1 AA violations found:\n{violation_summary}")

    def test_keyboard_accessibility(self):
        """Test that all interactive elements are keyboard accessible."""
        widget = ThumbnailRadioSelect(
            choices=[("a", "Option A"), ("b", "Option B"), ("c", "Option C")],
            thumbnail_mapping={
                "a": 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg"><rect fill="red"/></svg>',
                "b": 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg"><rect fill="green"/></svg>',
                "c": 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg"><rect fill="blue"/></svg>',
            },
            thumbnail_size=40,
        )

        page_html = self._render_widget_page(widget, value="a")
        self.driver.get(f"data:text/html;charset=utf-8,{page_html}")

        # Run axe with keyboard accessibility rules
        axe = Axe(self.driver)
        axe.inject()
        results = axe.run(options={"runOnly": {"type": "tag", "values": ["keyboard"]}})

        violations = results["violations"]

        assert len(violations) == 0, f"Keyboard accessibility violations: {violations}"

    def test_screen_reader_compatibility(self):
        """Test that widget works well with screen readers."""
        widget = ThumbnailRadioSelect(
            choices=[("a", "Option A"), ("b", "Option B")],
            thumbnail_mapping={
                "a": 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg"><rect fill="red"/></svg>',
                "b": 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg"><rect fill="blue"/></svg>',
            },
            thumbnail_size=40,
        )

        page_html = self._render_widget_page(widget, value="a")
        self.driver.get(f"data:text/html;charset=utf-8,{page_html}")

        # Check for proper labeling and semantics
        axe = Axe(self.driver)
        axe.inject()
        results = axe.run(
            options={"runOnly": {"type": "tag", "values": ["best-practice", "forms"]}}
        )

        violations = [
            v for v in results["violations"] if v["impact"] in ("critical", "serious")
        ]

        assert len(violations) == 0, f"Screen reader compatibility issues: {violations}"

    def test_color_contrast(self):
        """Test that text and images have sufficient color contrast."""
        widget = ThumbnailRadioSelect(
            choices=[("a", "Option A"), ("b", "Option B")],
            thumbnail_mapping={
                "a": 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg"><rect fill="white" stroke="black"/></svg>',
                "b": 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg"><rect fill="black"/></svg>',
            },
            thumbnail_size=40,
        )

        page_html = self._render_widget_page(widget, value="a")
        self.driver.get(f"data:text/html;charset=utf-8,{page_html}")

        # Run color contrast checks
        axe = Axe(self.driver)
        axe.inject()
        results = axe.run(options={"runOnly": {"type": "tag", "values": ["cat.color"]}})

        violations = results["violations"]

        if violations:
            contrast_issues = "\n".join(
                [f"- {v['id']}: {v['description']}" for v in violations]
            )
            self.fail(f"Color contrast violations:\n{contrast_issues}")
