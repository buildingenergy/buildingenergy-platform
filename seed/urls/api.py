"""
:copyright: (c) 2014 Building Energy Inc
:license: see LICENSE for more details.
"""
from django.conf.urls import patterns, url

urlpatterns = patterns(
    'seed.views.api',

    # api schema
    url(
        r'^get_api_schema/$',
        'get_api_schema',
        name='get_api_schema'
    ),
)
