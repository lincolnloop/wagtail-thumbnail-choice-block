# Thumbnail Choice Block Demo

This is a demonstration project showing how to use the `wagtail-thumbnail-choice-block` package in a real Wagtail site.

## Features Demonstrated

This demo showcases multiple use cases for `ThumbnailChoiceBlock`:

1. **Page-level fields** - Theme and layout selectors using `ThumbnailRadioSelect` widget
2. **Icon selector** - Using template-based thumbnails for icon choices
3. **Color scheme selector** - Using SVG gradient thumbnails
4. **Button style selector** - Using PNG thumbnails with different button styles
5. **Custom thumbnail sizes** - Different blocks use different thumbnail sizes (40px, 60px, 80px, 100px)

## Quick Start

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Installation

1. **Create and activate a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Install the wagtail-thumbnail-choice-block package:**

   From the parent directory:
   ```bash
   pip install -e ..
   ```

   Or if you want to install from PyPI:
   ```bash
   pip install wagtail-thumbnail-choice-block
   ```

4. **Run migrations:**

   ```bash
   python manage.py migrate
   ```

5. **Set up the demo site:**

   ```bash
   python manage.py setup_demo
   ```

   This command will:
   - Create a superuser (username: `admin`, password: `admin`)
   - Create the home page with example content
   - Configure the Wagtail site

6. **Start the development server:**

   ```bash
   python manage.py runserver
   ```

7. **Visit the site:**

   - **Frontend:** http://localhost:8000/
   - **Admin:** http://localhost:8000/admin/ (login with `admin`/`admin`)

## Using the Demo

### In the Wagtail Admin

1. Go to http://localhost:8000/admin/ and log in
2. Click on "Pages" in the sidebar
3. Click on the home page to edit it
4. You'll see several examples of `ThumbnailChoiceBlock`:

   **Page Settings (top of the page):**
   - **Theme** - Choose between Light, Dark, or Auto theme with visual thumbnails
   - **Layout** - Select Grid, List, or Masonry layout with preview thumbnails

   **Content Blocks (StreamField):**
   - **Icon Block** - Select from 4 different icons (Star, Heart, Check, Info) using SVG templates
   - **Color Scheme** - Choose from 4 gradient color schemes
   - **Button Style** - Pick from 4 different button styles (Solid, Outline, Ghost, Gradient)

5. Try adding and editing different blocks to see how the thumbnails help you make visual choices
6. Save and publish the page to see your changes on the frontend

### Code Examples

The demo includes several patterns you can copy for your own projects:

#### 1. Page Field with Custom Widget

```python
from wagtail_thumbnail_choice_block.widgets import ThumbnailRadioSelect

class MyPage(Page):
    theme = models.CharField(max_length=50, choices=[...])

    content_panels = [
        FieldPanel('theme', widget=ThumbnailRadioSelect(
            choices=[...],
            thumbnails={...},
            thumbnail_size=60,
        )),
    ]
```

#### 2. StreamField Block

```python
from wagtail_thumbnail_choice_block import ThumbnailChoiceBlock

content = StreamField([
    ('icon', ThumbnailChoiceBlock(
        choices=[...],
        thumbnail_templates={...},
        thumbnail_size=60,
    )),
])
```

#### 3. Using Image Thumbnails

```python
ThumbnailChoiceBlock(
    choices=[
        ('option1', 'Option 1'),
        ('option2', 'Option 2'),
    ],
    thumbnails={
        'option1': '/static/thumbnails/option1.png',
        'option2': '/static/thumbnails/option2.png',
    },
    thumbnail_size=80,
)
```

#### 4. Using Template-based Thumbnails

```python
ThumbnailChoiceBlock(
    choices=[
        ('icon1', 'Icon 1'),
        ('icon2', 'Icon 2'),
    ],
    thumbnail_templates={
        'icon1': 'icons/icon1.html',
        'icon2': {
            'template': 'icons/icon2.html',
            'context': {'color': 'blue'},
        },
    },
    thumbnail_size=50,
)
```

## Project Structure

```
example/
├── manage.py                    # Django management script
├── generate_thumbnails.py       # Script to generate thumbnail images
├── demo/                        # Django project
│   ├── settings.py             # Django settings
│   ├── urls.py                 # URL configuration
│   ├── wsgi.py                 # WSGI application
│   ├── templates/              # Base templates
│   │   └── base.html
│   ├── static/                 # Static files
│   │   └── thumbnails/         # Generated thumbnails
│   │       ├── themes/         # Theme thumbnails (PNG)
│   │       ├── layouts/        # Layout thumbnails (PNG)
│   │       ├── colors/         # Color scheme thumbnails (SVG)
│   │       └── buttons/        # Button style thumbnails (PNG)
│   └── home/                   # Home app
│       ├── models.py           # Page models with examples
│       ├── templates/          # App templates
│       │   └── home/
│       │       ├── home_page.html
│       │       └── icons/      # Icon templates
│       └── management/         # Management commands
│           └── commands/
│               └── setup_demo.py
```

## Customization

### Adding Your Own Examples

1. **Edit `demo/home/models.py`** to add new field or block examples
2. **Create thumbnails** in `demo/static/thumbnails/`
3. **Update templates** in `demo/home/templates/` if needed
4. **Run migrations:** `python manage.py makemigrations && python manage.py migrate`

### Creating Custom Thumbnails

You can create thumbnails using any image editor or programmatically:

- **PNG images:** Use Pillow, Photoshop, GIMP, etc.
- **SVG images:** Use Inkscape, Illustrator, or write SVG XML directly
- **Templates:** Create Django template files that render HTML/SVG

The `generate_thumbnails.py` script shows how to create PNG images programmatically using Pillow.

## Troubleshooting

### Import Error for wagtail_thumbnail_choice_block

Make sure you've installed the package:
```bash
pip install -e ..  # From the example directory
```

### Missing Thumbnails

The thumbnails are included in the repository. If you need to regenerate them:
```bash
python generate_thumbnails.py
```

### Database Errors

Delete the database and start over:
```bash
rm db.sqlite3
python manage.py migrate
python manage.py setup_demo
```

### Static Files Not Loading

Collect static files:
```bash
python manage.py collectstatic --noinput
```

## Learn More

- **Main Package:** See the parent directory for the full package documentation
- **Wagtail Documentation:** https://docs.wagtail.org/
- **Django Documentation:** https://docs.djangoproject.com/

## License

This demo project is provided as an example and is not meant for production use.
