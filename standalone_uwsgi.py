"""
:copyright: (c) 2014 Building Energy Inc
:license: see LICENSE for more details.
"""
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BE.settings.dev")
from django.core.wsgi import get_wsgi_application
from dj_static import Cling
application = Cling(get_wsgi_application())
