import re


def extract_locatie_id(name: str) -> str:
    """
    :param name: e.g. B31_2_ontwerp_Some street - Other street.pdf
    :return: B31_2
    """
    matches = re.match(r'^(\w+\d+(_\d+)?)[_ ].+$', name)
    if matches:
        return matches.group(1)
    else:
        raise ValueError(f'Could not find location_id in {name}')
