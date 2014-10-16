def convert_choice_data(name, mapping):
    """Converts human name to interger for DB for Django choices.

    :parm name: str, the unit or type name from JS.
    :param mapping: tuple of tuples used for Django Meter choices.
    :returns: int, the intereger value of the string stored in the DB.

    ``mapping`` looks like ((3, 'Electricity'), (4, 'Natural Gas'))
    See ``ENERGY_TYPES`` and ``ENERGY_UNITS`` in ``seed.models``.
    """
    try:
        return filter(
            lambda x: x[1] == name, [t for t in mapping]
        )[0][0]
    except IndexError:
        return None
