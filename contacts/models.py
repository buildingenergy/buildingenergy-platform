"""
:copyright: (c) 2014 Building Energy Inc
:license: Apache v2, see LICENSE for more details.
"""

# django imports
from django.db import models

# vendor imports
from django_extensions.db.models import TimeStampedModel
from superperms.orgs.models import (
    Organization as SuperOrganization,
)
from seed.models import BuildingSnapshot

OWNER = 0
PROPERTY_MANAGER = 1
OCCUMANT = 2
ENERGY_AUDITOR = 3
ENERGY_MODELER = 4
CONTRACTOR = 5
OTHER = 6

CONTACT_TYPES = (
    (OWNER, 'Owner'),
    (PROPERTY_MANAGER, 'Property Manager'),
    (OCCUMANT, 'Occupant'),
    (ENERGY_AUDITOR, 'Energy Auditor'),
    (ENERGY_MODELER, 'Energy Modeler'),
    (CONTRACTOR, 'Contractor'),
    (OTHER, 'Other'),
)


def get_contact_types():
    """returns a list of the contact types"""
    return map(lambda t: t[1], CONTACT_TYPES)


class Contact(TimeStampedModel):
    """BEDES compliant information relating to contact person"""
    contact_type = models.IntegerField(choices=CONTACT_TYPES)
    company = models.CharField(max_length=128, null=True, blank=True)
    name = models.CharField(max_length=128, null=True, blank=True)
    street_address = models.CharField(max_length=128, null=True, blank=True)
    city = models.CharField(max_length=128, null=True, blank=True)
    postal_code = models.CharField(max_length=128, null=True, blank=True)
    state = models.CharField(max_length=128, null=True, blank=True)
    email_address = models.CharField(max_length=128, null=True, blank=True)
    telephone_number = models.CharField(max_length=128, null=True, blank=True)
    super_organization = models.ForeignKey(
        SuperOrganization,
        related_name='contacts'
    )
    building_snapshots = models.ManyToManyField(
        BuildingSnapshot,
        null=True,
        blank=True,
        related_name='contacts',
    )

    def __unicode__(self):
        return u'Contact: {0} <{1}> ({2})'.format(
            self.get_contact_type_display(), self.name, self.pk
        )

    def to_dict(self):
        # avoid circular import
        from seed.models import obj_to_dict
        return obj_to_dict(self)
