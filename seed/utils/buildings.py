import datetime

from django.db.models import Q

from seed import models
from seed.models import (
    ASSESSED_RAW,
    ELECTRICITY,
    NATURAL_GAS,
    UTILITY_NAMES,
    UTILITY_ACCOUNTS,
    BuildingSnapshot,
    Meter,
    UtilityAccount,
    obj_to_dict,
)
from seed import search
from seed.utils import time
from seed.utils.mapping import get_mappable_types
from seed.utils.constants import ASSESSOR_FIELDS_BY_COLUMN

from surveys.models import SurveyAnswer, Survey, ENUM, SurveyBuilding


def get_source_type(import_file, source_type=''):
    """Used for converting ImportFile source_type into an int."""
    source_type_str = getattr(import_file, 'source_type', '') or ''
    source_type_str = source_type or source_type_str
    source_type_str = source_type_str.upper().replace(' ', '_')

    return getattr(models, source_type_str, ASSESSED_RAW)


def serialize_building_snapshot(b, pm_cb, building):
    """returns a dict that's safe to JSON serialize"""
    b_as_dict = b.__dict__.copy()
    for key, val in b_as_dict.items():
        if type(val) == datetime.datetime or type(val) == datetime.date:
            b_as_dict[key] = time.convert_to_js_timestamp(val)
    del(b_as_dict['_state'])
    # check if they're matched
    if b.canonical_building == pm_cb:
        b_as_dict['matched'] = True
    else:
        b_as_dict['matched'] = False
    if '_canonical_building_cache' in b_as_dict:
        del(b_as_dict['_canonical_building_cache'])
    return b_as_dict


def get_buildings_for_user_count(user):
    """returns the number of buildings in a user's orgs"""
    building_snapshots = BuildingSnapshot.objects.filter(
        super_organization__in=user.orgs.all(),
        canonicalbuilding__active=True,
    ).distinct('pk')

    return building_snapshots.count()


def get_search_query(user, params):
    other_search_params = params.get('filter_params', {})
    q = other_search_params.get('q', '')
    order_by = params.get('order_by', 'pk')
    sort_reverse = params.get('sort_reverse', False)
    project_slug = other_search_params.get('project__slug', None)

    mappable_types = get_mappable_types()

    if project_slug:
        mappable_types['project__slug'] = 'string'

    if order_by:
        if sort_reverse:
            order_by = "-%s" % order_by
        building_snapshots = BuildingSnapshot.objects.order_by(
            order_by
        ).filter(
            super_organization__in=user.orgs.all(),
            canonicalbuilding__active=True,
        )
    else:
        building_snapshots = BuildingSnapshot.objects.filter(
            super_organization__in=user.orgs.all(),
            canonicalbuilding__active=True,
        )

    buildings_queryset = search.search_buildings(
        q, queryset=building_snapshots
    )

    buildings_queryset = search.filter_other_params(
        buildings_queryset, other_search_params, mappable_types
    )

    return buildings_queryset


def get_columns(is_project, org_id, all_fields=False):
    """gets default columns, to be overriden in future

        title: HTML presented title of column
        sort_column: semantic name used by js and for searching DB
        class: HTML CSS class for row td elements
        title_class: HTML CSS class for column td elements
        type: 'string', 'number', 'date'
        min, max: the django filter key e.g. gross_floor_area__gte
        field_type: assessor, pm, or compliance (currently not used)
        sortable: determines if the column is sortable
        checked: initial state of "edit columns" modal
        static: True if option can be toggle (ID is false because it is
            always needed to link to the building detail page)
        link: signifies that the cell's data should link to a building detail
            page

    """
    cols = []
    translator = {
        '': 'string',
        'date': 'date',
        'float': 'number',
        'string': 'string',
        'decimal': 'number',
        'datetime': 'date',
    }
    field_types = {}
    for k, v in get_mappable_types().items():
        d = {
            "title": k.title().replace('_', ' '),
            "sort_column": k,
            "type": translator[v],
            "class": "is_aligned_right",
            "field_type": "assessor",
            "sortable": True,
            "checked": False,
            "static": False,
            "field_type": field_types.get(k),
            "link": True if '_id' in k or 'address' in k.lower() else False,
        }
        if d['sort_column'] == 'gross_floor_area':
            d['type'] = 'floor_area'
            d['subtitle'] = u"ft" + u"\u00B2"
        if d['type'] != 'string':
            d["min"] = "{0}__gte".format(k)
            d["max"] = "{0}__lte".format(k)

        cols.append(d)

    for col in cols:
        if col['sort_column'] in ASSESSOR_FIELDS_BY_COLUMN:
            assessor_field = ASSESSOR_FIELDS_BY_COLUMN[col['sort_column']]
            col['field_type'] = assessor_field['field_type']

    if all_fields:
        qs = models.Column.objects.filter(is_extra_data=True).filter(
            Q(organization=None) |
            Q(mapped_mappings__super_organization=org_id)
        ).select_related('unit').distinct()
    else:
        qs = models.Column.objects.filter(is_extra_data=True).filter(
            mapped_mappings__super_organization=org_id
        ).select_related('unit').distinct()
    for c in qs:
        t = c.unit.get_unit_type_display().lower() if c.unit else 'string'
        link = False
        if '_id' in c.column_name or 'address' in c.column_name.lower():
            link = True
        d = {
            "title": c.column_name,
            "sort_column": c.column_name,
            "type": translator[t],
            "class": "is_aligned_right",
            "field_type": "assessor",
            "sortable": True,
            "checked": False,
            "static": False,
            "link": link,
            "is_extra_data": True,
        }
        if d['type'] != 'string':
            d["min"] = "{0}__gte".format(c.column_name)
            d["max"] = "{0}__lte".format(c.column_name)
        cols.append(d)

    cols.sort(key=lambda x: x['title'])
    if is_project:
        cols.insert(0, {
            "title": "Status",
            "sort_column": "project_building_snapshots__status_label__name",
            "class": "",
            "title_class": "",
            "type": "string",
            "field_type": "assessor",
            "sortable": True,
            "checked": True,
            "static": True
        })
    columns = {
        'fields': cols,
    }

    return columns


def build_meter_payload(building_snapshot=None, business=None):
    """Returns meter and timeseries data as a dictionary.
    One of both of ``building_snapshot`` and ``business`` should be provided.
    Returns the set of both's meters.
    """
    meters = []
    qs = Meter.objects.none()
    if business:
        qs = business.meters.all()
    if building_snapshot:
        # SQL join business and building_snapshot's meters
        qs |= building_snapshot.meters.all()
    for meter in qs:
        m = meter.to_dict()
        timeseries_data = []
        for ts in meter.timeseries_data.all():
            timeseries_data.append(ts.to_dict())

        m['timeseries_data'] = timeseries_data

        meters.append(m)

    return meters


def build_survey_payload(building_snapshot):
    """Return survey payload for a building."""
    survey = {}
    s = Survey.objects.first()
    if not s:
        return survey
    sb = SurveyBuilding.objects.filter(
        canonical_building=building_snapshot.canonical_building,
        survey=s
    ).first()
    if sb:
        # important to dictify SurveyBuilding first to get the correct id in
        # the response Survey payload
        survey.update(obj_to_dict(sb))
    survey.update(obj_to_dict(s))
    question_payload = {}
    question_responses_payload = {}
    for q in s.questions.all():
        if q.question_type == ENUM:
            sa_qs = SurveyAnswer.objects.filter(
                canonical_building=building_snapshot.canonical_building,
                question=q
            )
        else:
            sa = SurveyAnswer.objects.filter(
                canonical_building=building_snapshot.canonical_building,
                question=q
            ).first()
        question_payload[q.pk] = obj_to_dict(q)
        question_payload[q.pk]['question_type'] = q.get_question_type_display()
        question_payload[q.pk]['options'] = [
            obj_to_dict(o) for o in q.question_options.all()
        ]
        if q.question_type == ENUM:
            question_responses_payload[q.pk] = {}
            for sa in sa_qs:
                # only storing the checked options, False should be deleted
                question_responses_payload[q.pk][sa.answer] = True
        else:
            question_responses_payload[q.pk] = obj_to_dict(sa) if sa else {}
            question_responses_payload[q.pk]['question_id'] = q.pk

    survey['questions'] = question_payload
    survey['question_responses'] = question_responses_payload

    return survey


def build_business_payload(building_snapshot):
    """Return business related data."""
    businesses = []
    for b in building_snapshot.businesses.all():
        business_dict = obj_to_dict(b)
        business_dict['meters'] = build_meter_payload(business=b)
        business_dict['contact'] = b.owner.to_dict()
        business_dict.update(
            build_utility_payload(building_snapshot, business=b)
        )
        businesses.append(business_dict)

    return businesses


def _get_utility_account_number(bs, utility):
    account_number = None
    try:
        account = UtilityAccount.objects.get(
            utility=utility,
            canonical_building=bs.canonical_building
        )
        account_number = account.account_number
    except UtilityAccount.DoesNotExist:
        pass

    return account_number


def build_utility_payload(building_snapshot, business=None):
    """Return Utility related data for a building."""
    utilities = {}

    # Get the utility name information.
    if business:
        elec_utilities = business.utilities.filter(
            utility_type=ELECTRICITY
        )
        gas_utilities = business.utilities.filter(
            utility_type=NATURAL_GAS
        )
    else:
        elec_utilities = building_snapshot.utilities.filter(
            utility_type=ELECTRICITY
        )
        gas_utilities = building_snapshot.utilities.filter(
            utility_type=NATURAL_GAS
        )
    elec_name, gas_name = UTILITY_NAMES
    elec_account, gas_account = UTILITY_ACCOUNTS
    for u in elec_utilities:
        utilities[elec_name] = u.name
        utilities[elec_account] = _get_utility_account_number(
            building_snapshot, u
        )

    for u in gas_utilities:
        utilities[gas_name] = u.name
        utilities[gas_account] = _get_utility_account_number(
            building_snapshot, u
        )

    return utilities
