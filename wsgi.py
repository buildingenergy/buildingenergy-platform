"""
:copyright: (c) 2014 Building Energy Inc
:license: see LICENSE for more details.
"""
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BE.settings.main")
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
