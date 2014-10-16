"""
:copyright: (c) 2014 Building Energy Inc
:license: see LICENSE for more details.
"""
from django.conf import settings

if 'nose' not in settings.TEST_RUNNER:
    from .test_importfile import ImportRecordBaseTestCase
    from .test_importrecord import ImportRecordTestCase
    from .test_modutil import ImporterTest, FloatTestCase
