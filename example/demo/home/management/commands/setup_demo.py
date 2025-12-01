"""
Management command to set up the demo site with initial data.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from wagtail.models import Site, Page

from demo.home.models import HomePage


class Command(BaseCommand):
    help = "Set up the demo site with initial data"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Setting up demo site..."))
        self.stdout.write("")

        # Create superuser
        User = get_user_model()
        if not User.objects.filter(username="admin").exists():
            self.stdout.write("Creating superuser (admin/admin)...")
            User.objects.create_superuser(
                username="admin", email="admin@example.com", password="admin"
            )
            self.stdout.write(self.style.SUCCESS("✓ Superuser created"))
        else:
            self.stdout.write(self.style.WARNING("! Superuser already exists"))

        # Get the root page
        try:
            root_page = Page.objects.get(depth=1)
        except Page.DoesNotExist:
            self.stdout.write(
                self.style.ERROR("Root page not found. Please run migrations first.")
            )
            return

        # Delete the default Wagtail page if it exists
        home_pages = Page.objects.filter(slug="home", depth=2)
        for page in home_pages:
            if not isinstance(page.specific, HomePage):
                page.delete()
                self.stdout.write("Removed default Wagtail home page")
                # Refresh root_page from database after deletion
                root_page = Page.objects.get(depth=1)
                break

        # Create HomePage if it doesn't exist
        if not HomePage.objects.exists():
            self.stdout.write("Creating home page...")
            home_page = HomePage(
                title="Thumbnail Choice Block Demo",
                slug="home",
                theme="light",
                layout="grid",
            )
            root_page.add_child(instance=home_page)
            home_page.save_revision().publish()

            # Update site root page or create new site
            try:
                site = Site.objects.get(is_default_site=True)
                site.root_page = home_page
                site.save()
            except Site.DoesNotExist:
                Site.objects.create(
                    hostname="localhost",
                    port=8000,
                    root_page=home_page,
                    is_default_site=True,
                    site_name="Demo Site",
                )

            self.stdout.write(self.style.SUCCESS("✓ Home page created"))
        else:
            self.stdout.write(self.style.WARNING("! Home page already exists"))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write(self.style.SUCCESS("Demo site setup complete!"))
        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write("")
        self.stdout.write("You can now:")
        self.stdout.write("  1. Run the development server:")
        self.stdout.write("     python manage.py runserver")
        self.stdout.write("")
        self.stdout.write("  2. Visit the site:")
        self.stdout.write("     http://localhost:8000/")
        self.stdout.write("")
        self.stdout.write("  3. Log in to Wagtail admin:")
        self.stdout.write("     http://localhost:8000/admin/")
        self.stdout.write("     Username: admin")
        self.stdout.write("     Password: admin")
        self.stdout.write("")
