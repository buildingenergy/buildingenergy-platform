"""
:copyright: (c) 2014 Building Energy Inc
:license: Apache v2, see LICENSE for more details.
"""
from django.test import TestCase

from superperms.orgs.models import Organization

from landing.models import SEEDUser as User


from seed.tests.util import FakeRequest
from contacts.models import get_contact_types, Contact, ENERGY_AUDITOR


class ContactsViewTests(TestCase):
    """
    Tests of the SEED project views: get_project, get_projects, create_project,
    delete_project, update_project, add_buildings_to_project,
    remove_buildings_from_project, get_project_count
    """

    def setUp(self):
        user_details = {
            'username': 'test_user@demo.com',
            'password': 'test_pass',
            'email': 'test_user@demo.com',
            'first_name': 'Johnny',
            'last_name': 'Energy',
        }
        self.user = User.objects.create_user(**user_details)
        self.org = Organization.objects.create(name='my org')
        self.org.add_member(self.user)
        self.client.login(**user_details)
        self.fake_request = FakeRequest(user=self.user)

    def test_get_contact_types(self):
        types = [
            'Owner',
            'Property Manager',
            'Occupant',
            'Energy Auditor',
            'Energy Modeler',
            'Contractor',
            'Other'
        ]
        self.assertEqual(get_contact_types(), types)

    def test_model(self):
        c = Contact.objects.create(
            contact_type=ENERGY_AUDITOR,
            company='SEED_ORG',
            name='Howard Duty',
            street_address='123 willow way',
            city='Portland',
            postal_code='97204',
            state='OR',
            email_address='hd@s.org',
            telephone_number='777-777-7777',
            super_organization=self.org,
        )
        contact = Contact.objects.get(pk=c.pk)
        self.assertEqual(contact.name, 'Howard Duty')
        self.assertEqual(self.org.contacts.first(), contact)
        self.assertEqual(
            'Contact: Energy Auditor <Howard Duty> (%s)' % contact.pk,
            str(contact)
        )
