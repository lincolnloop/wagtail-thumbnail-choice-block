from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WagtailThumbnailChoiceBlockAppConfig(AppConfig):
    name = "wagtail_thumbnail_choice_block"
    verbose_name = _("Wagtail Thumbnail Choice Block")
    default_auto_field = "django.db.models.BigAutoField"
