DJANGO_SETTINGS_MODULE ?= test_settings
PYTHONPATH ?= .

.PHONY: makemessages compilemessages

makemessages:
	cd wagtail_thumbnail_choice_block && \
	  PYTHONPATH=$(CURDIR) DJANGO_SETTINGS_MODULE=$(DJANGO_SETTINGS_MODULE) \
	  django-admin makemessages --all --no-wrap

compilemessages:
	PYTHONPATH=$(PYTHONPATH) DJANGO_SETTINGS_MODULE=$(DJANGO_SETTINGS_MODULE) \
	  django-admin compilemessages
