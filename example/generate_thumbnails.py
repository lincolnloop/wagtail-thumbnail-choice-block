#!/usr/bin/env python
"""
Generate thumbnail images for the demo project.
This script creates PNG images for all the thumbnail choices.
"""

import os
from PIL import Image, ImageDraw, ImageFont


def create_theme_thumbnails(output_dir):
    """Create theme thumbnails."""
    os.makedirs(output_dir, exist_ok=True)

    # Light theme
    img = Image.new("RGB", (120, 80), color="#ffffff")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 119, 79], outline="#e0e0e0", width=2)
    # Draw sun
    draw.ellipse([48, 13, 72, 37], fill="#FFD700")
    # Draw text
    font = ImageFont.load_default()
    draw.text((60, 55), "Light", fill="#333333", anchor="mm", font=font)
    img.save(os.path.join(output_dir, "light.png"))

    # Dark theme
    img = Image.new("RGB", (120, 80), color="#1a1a1a")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 119, 79], outline="#404040", width=2)
    # Draw moon
    draw.ellipse([48, 13, 72, 37], fill="#f0f0f0")
    draw.ellipse([54, 16, 75, 37], fill="#1a1a1a")
    draw.text((60, 55), "Dark", fill="#e0e0e0", anchor="mm", font=font)
    img.save(os.path.join(output_dir, "dark.png"))

    # Auto theme
    img = Image.new("RGB", (120, 80), color="#f5f5f5")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 119, 79], outline="#cccccc", width=2)
    # Half sun, half moon
    draw.pieslice([48, 13, 72, 37], 90, 270, fill="#FFD700")
    draw.pieslice([48, 13, 72, 37], 270, 90, fill="#404040")
    draw.text((60, 55), "Auto", fill="#333333", anchor="mm", font=font)
    img.save(os.path.join(output_dir, "auto.png"))

    print(f"✓ Created theme thumbnails in {output_dir}")


def create_layout_thumbnails(output_dir):
    """Create layout thumbnails."""
    os.makedirs(output_dir, exist_ok=True)

    # Grid layout
    img = Image.new("RGB", (120, 80), color="#ffffff")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 119, 79], outline="#e0e0e0", width=2)
    # Draw grid
    for i in range(2):
        for j in range(3):
            x = 15 + j * 35
            y = 15 + i * 30
            draw.rectangle([x, y, x + 25, y + 20], fill="#3498db", outline="#2980b9")
    img.save(os.path.join(output_dir, "grid.png"))

    # List layout
    img = Image.new("RGB", (120, 80), color="#ffffff")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 119, 79], outline="#e0e0e0", width=2)
    # Draw list items
    for i in range(3):
        y = 15 + i * 20
        draw.rectangle([15, y, 105, y + 15], fill="#3498db", outline="#2980b9")
    img.save(os.path.join(output_dir, "list.png"))

    # Masonry layout
    img = Image.new("RGB", (120, 80), color="#ffffff")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 119, 79], outline="#e0e0e0", width=2)
    # Draw masonry items
    draw.rectangle([15, 15, 50, 40], fill="#3498db", outline="#2980b9")
    draw.rectangle([55, 15, 105, 35], fill="#3498db", outline="#2980b9")
    draw.rectangle([15, 45, 50, 65], fill="#3498db", outline="#2980b9")
    draw.rectangle([55, 40, 105, 65], fill="#3498db", outline="#2980b9")
    img.save(os.path.join(output_dir, "masonry.png"))

    print(f"✓ Created layout thumbnails in {output_dir}")


def create_color_thumbnails(output_dir):
    """Create color scheme thumbnails as SVG (smaller and vector-based)."""
    os.makedirs(output_dir, exist_ok=True)

    colors = {
        "blue": ("#667eea", "#764ba2"),
        "green": ("#0ba360", "#3cba92"),
        "red": ("#f857a6", "#ff5858"),
        "purple": ("#a8edea", "#fed6e3"),
    }

    for name, (color1, color2) in colors.items():
        svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
  <defs>
    <linearGradient id="grad_{name}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{color1};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{color2};stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="100" height="100" fill="url(#grad_{name})" rx="8"/>
</svg>"""
        with open(os.path.join(output_dir, f"{name}.svg"), "w") as f:
            f.write(svg_content)

    print(f"✓ Created color scheme thumbnails in {output_dir}")


def create_button_thumbnails(output_dir):
    """Create button style thumbnails."""
    os.makedirs(output_dir, exist_ok=True)

    font = ImageFont.load_default()

    # Solid button
    img = Image.new("RGB", (120, 80), color="#f5f5f5")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 119, 79], outline="#e0e0e0", width=2)
    draw.rounded_rectangle([20, 25, 100, 55], radius=6, fill="#3498db")
    draw.text((60, 40), "Button", fill="#ffffff", anchor="mm", font=font)
    img.save(os.path.join(output_dir, "solid.png"))

    # Outline button
    img = Image.new("RGB", (120, 80), color="#f5f5f5")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 119, 79], outline="#e0e0e0", width=2)
    draw.rounded_rectangle([20, 25, 100, 55], radius=6, outline="#3498db", width=2)
    draw.text((60, 40), "Button", fill="#3498db", anchor="mm", font=font)
    img.save(os.path.join(output_dir, "outline.png"))

    # Ghost button
    img = Image.new("RGB", (120, 80), color="#f5f5f5")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 119, 79], outline="#e0e0e0", width=2)
    draw.text((60, 40), "Button", fill="#3498db", anchor="mm", font=font)
    img.save(os.path.join(output_dir, "ghost.png"))

    # Gradient button
    img = Image.new("RGB", (120, 80), color="#f5f5f5")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 119, 79], outline="#e0e0e0", width=2)
    # Create gradient effect (simplified)
    for i in range(30):
        color_val = int(102 + (118 - 102) * (i / 30))  # From #667eea to #764ba2
        draw.rectangle([20, 25 + i, 100, 26 + i], fill=(color_val, 126, 234 - i))
    draw.rounded_rectangle([20, 25, 100, 55], radius=6, outline="#5568d3", width=1)
    draw.text((60, 40), "Button", fill="#ffffff", anchor="mm", font=font)
    img.save(os.path.join(output_dir, "gradient.png"))

    print(f"✓ Created button thumbnails in {output_dir}")


def main():
    """Generate all thumbnails."""
    print("Generating thumbnails for demo project...")
    print()

    base_dir = os.path.join(os.path.dirname(__file__), "demo", "static", "thumbnails")

    create_theme_thumbnails(os.path.join(base_dir, "themes"))
    create_layout_thumbnails(os.path.join(base_dir, "layouts"))
    create_color_thumbnails(os.path.join(base_dir, "colors"))
    create_button_thumbnails(os.path.join(base_dir, "buttons"))

    print()
    print("✅ All thumbnails generated successfully!")
    print(f"   Output directory: {base_dir}")


if __name__ == "__main__":
    main()
