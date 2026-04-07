from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="homepage",
            name="directory_icon",
            field=models.CharField(
                blank=True,
                help_text="Icon chosen from the static/icons/ directory.",
                max_length=200,
            ),
        ),
    ]
